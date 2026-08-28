param(
    [Parameter(Mandatory = $true)][string]$InputDirectory,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [double]$ConnectThreshold = 55.0,
    [double]$TargetRedMinusGreen = 2.9,
    [double]$TargetGreenMinusBlue = 16.1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Get-BackgroundColor([Drawing.Bitmap]$bitmap) {
    $cornerWidth = [Math]::Max(1, [Math]::Round($bitmap.Width * 0.12))
    $cornerHeight = [Math]::Max(1, [Math]::Round($bitmap.Height * 0.12))
    [double]$red = 0
    [double]$green = 0
    [double]$blue = 0
    $count = 0

    for ($y = 0; $y -lt $cornerHeight; $y++) {
        for ($x = 0; $x -lt $cornerWidth; $x++) {
            foreach ($sampleX in @($x, ($bitmap.Width - 1 - $x))) {
                $color = $bitmap.GetPixel($sampleX, $y)
                $red += $color.R
                $green += $color.G
                $blue += $color.B
                $count++
            }
        }
    }

    [pscustomobject]@{
        Red = $red / $count
        Green = $green / $count
        Blue = $blue / $count
    }
}

function Limit-Byte([double]$value) {
    [int][Math]::Round([Math]::Max(0.0, [Math]::Min(255.0, $value)))
}

function Convert-Portrait([string]$inputPath, [string]$outputPath) {
    $source = [Drawing.Bitmap]::FromFile($inputPath)
    try {
        $width = $source.Width
        $height = $source.Height
        $count = $width * $height
        $backgroundColor = Get-BackgroundColor $source
        $candidate = [bool[]]::new($count)
        $background = [bool[]]::new($count)

        for ($y = 0; $y -lt $height; $y++) {
            for ($x = 0; $x -lt $width; $x++) {
                $index = $y * $width + $x
                $color = $source.GetPixel($x, $y)
                $dr = $backgroundColor.Red - $color.R
                $dg = $backgroundColor.Green - $color.G
                $db = $backgroundColor.Blue - $color.B
                $distance = [Math]::Sqrt($dr * $dr + $dg * $dg + $db * $db)
                $candidate[$index] = $distance -le $ConnectThreshold
            }
        }

        $queue = [Collections.Generic.Queue[int]]::new()
        function Add-Seed([int]$seedX, [int]$seedY) {
            $seedIndex = $seedY * $width + $seedX
            if ($candidate[$seedIndex] -and -not $background[$seedIndex]) {
                $background[$seedIndex] = $true
                $queue.Enqueue($seedIndex)
            }
        }

        for ($x = 0; $x -lt $width; $x++) {
            Add-Seed $x 0
            Add-Seed $x ($height - 1)
        }
        for ($y = 0; $y -lt $height; $y++) {
            Add-Seed 0 $y
            Add-Seed ($width - 1) $y
        }

        $neighbors = @(
            @(-1, -1), @(0, -1), @(1, -1),
            @(-1, 0),             @(1, 0),
            @(-1, 1),  @(0, 1),  @(1, 1)
        )

        while ($queue.Count -gt 0) {
            $index = $queue.Dequeue()
            $x = $index % $width
            $y = [Math]::Floor($index / $width)
            foreach ($offset in $neighbors) {
                $nextX = $x + $offset[0]
                $nextY = $y + $offset[1]
                if ($nextX -lt 0 -or $nextX -ge $width -or $nextY -lt 0 -or $nextY -ge $height) {
                    continue
                }
                $nextIndex = $nextY * $width + $nextX
                if ($candidate[$nextIndex] -and -not $background[$nextIndex]) {
                    $background[$nextIndex] = $true
                    $queue.Enqueue($nextIndex)
                }
            }
        }

        $redOffset = $TargetRedMinusGreen
        $greenOffset = 0.0
        $blueOffset = -$TargetGreenMinusBlue
        $lumaOffset = 0.2126 * $redOffset + 0.7152 * $greenOffset + 0.0722 * $blueOffset
        $redOffset -= $lumaOffset
        $greenOffset -= $lumaOffset
        $blueOffset -= $lumaOffset

        $output = [Drawing.Bitmap]::new($width, $height, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
        try {
            for ($y = 0; $y -lt $height; $y++) {
                for ($x = 0; $x -lt $width; $x++) {
                    $index = $y * $width + $x
                    $color = $source.GetPixel($x, $y)
                    if (-not $background[$index]) {
                        $output.SetPixel($x, $y, $color)
                        continue
                    }

                    $luma = 0.2126 * $color.R + 0.7152 * $color.G + 0.0722 * $color.B
                    $newRed = Limit-Byte ($luma + $redOffset)
                    $newGreen = Limit-Byte ($luma + $greenOffset)
                    $newBlue = Limit-Byte ($luma + $blueOffset)
                    $output.SetPixel($x, $y, [Drawing.Color]::FromArgb($color.A, $newRed, $newGreen, $newBlue))
                }
            }

            $output.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
        }
        finally {
            $output.Dispose()
        }

        [pscustomobject]@{
            File = [IO.Path]::GetFileName($inputPath)
            SourceBackgroundRgb = @(
                [Math]::Round($backgroundColor.Red, 1),
                [Math]::Round($backgroundColor.Green, 1),
                [Math]::Round($backgroundColor.Blue, 1)
            )
            Output = $outputPath
        }
    }
    finally {
        $source.Dispose()
    }
}

$inputRoot = (Resolve-Path -LiteralPath $InputDirectory).Path
$outputRoot = [IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputDirectory))
[IO.Directory]::CreateDirectory($outputRoot) | Out-Null

$results = foreach ($file in Get-ChildItem -LiteralPath $inputRoot -Filter '*.png' -File | Sort-Object Name) {
    Convert-Portrait $file.FullName (Join-Path $outputRoot $file.Name)
}

$results | ConvertTo-Json -Depth 4
