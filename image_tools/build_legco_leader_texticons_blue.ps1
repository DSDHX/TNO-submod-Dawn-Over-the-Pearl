param(
    [Parameter(Mandatory = $true)][string]$TemplatePath,
    [Parameter(Mandatory = $true)][string]$PortraitDirectory,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [int]$RedOffset = -12,
    [int]$GreenOffset = 12,
    [int]$BlueOffset = 12
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Limit-Byte([int]$value) {
    [byte][Math]::Max(0, [Math]::Min(255, $value))
}

$template = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $TemplatePath).Path)
$ddsHeaderLength = 128
$canvasWidth = [BitConverter]::ToInt32($template, 16)
$canvasHeight = [BitConverter]::ToInt32($template, 12)
$bitsPerPixel = [BitConverter]::ToInt32($template, 88)

if ($canvasWidth -ne 170 -or $canvasHeight -ne 224 -or $bitsPerPixel -ne 32) {
    throw "Unexpected DDS template: ${canvasWidth}x${canvasHeight}, ${bitsPerPixel}bpp."
}

$expectedLength = $ddsHeaderLength + ($canvasWidth * $canvasHeight * 4)
if ($template.Length -ne $expectedLength) {
    throw "Unexpected DDS byte length: $($template.Length), expected $expectedLength."
}

[IO.Directory]::CreateDirectory($OutputDirectory) | Out-Null
$outputRoot = (Resolve-Path -LiteralPath $OutputDirectory).Path
$portraitRoot = (Resolve-Path -LiteralPath $PortraitDirectory).Path
$assets = [ordered]@{
    'DOP_Yeung_Kwong.png' = 'DOP_Yeung_Kwong_texticon.dds'
    'DOP_Yamashita_Toshihiko.png' = 'DOP_Yamashita_Toshihiko_texticon.dds'
    'DOP_Fok_Ying_Tung.png' = 'DOP_Fok_Ying_Tung_texticon.dds'
    'DOP_Niwa_Uichiro.png' = 'DOP_Niwa_Uichiro_texticon.dds'
}

$results = foreach ($entry in $assets.GetEnumerator()) {
    $portraitPath = Join-Path $portraitRoot $entry.Key
    $bitmap = [Drawing.Bitmap]::new([string]$portraitPath)
    try {
        if ($bitmap.Width -ne 156 -or $bitmap.Height -ne 210) {
            throw "Unexpected portrait dimensions for $($entry.Key): $($bitmap.Width)x$($bitmap.Height)."
        }

        $bytes = [byte[]]$template.Clone()
        for ($y = 0; $y -lt 210; $y++) {
            for ($x = 0; $x -lt 156; $x++) {
                $color = $bitmap.GetPixel($x, $y)
                $filteredRed = Limit-Byte ($color.R + $RedOffset)
                $filteredGreen = Limit-Byte ($color.G + $GreenOffset)
                $filteredBlue = Limit-Byte ($color.B + $BlueOffset)
                $destinationX = $x + 7
                $destinationY = $y + 7
                $offset = $ddsHeaderLength + (($destinationY * $canvasWidth + $destinationX) * 4)
                $bytes[$offset] = $filteredBlue
                $bytes[$offset + 1] = $filteredGreen
                $bytes[$offset + 2] = $filteredRed
                $bytes[$offset + 3] = $color.A
            }
        }

        $outputPath = Join-Path $outputRoot $entry.Value
        [IO.File]::WriteAllBytes($outputPath, $bytes)
        [pscustomobject]@{
            Portrait = $entry.Key
            Texticon = $entry.Value
            FilterRgbOffset = @($RedOffset, $GreenOffset, $BlueOffset)
            Width = $canvasWidth
            Height = $canvasHeight
            Bytes = $bytes.Length
        }
    }
    finally {
        $bitmap.Dispose()
    }
}

$results
