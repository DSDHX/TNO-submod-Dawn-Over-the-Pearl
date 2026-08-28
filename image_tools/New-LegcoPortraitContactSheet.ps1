param(
    [Parameter(Mandatory = $true)]
    [string[]]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [int]$Columns = 5,
    [int]$CellWidth = 240,
    [int]$CellHeight = 320,
    [int]$LabelHeight = 42,
    [switch]$HideLabels
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$files = foreach ($path in $InputPath) {
    Get-ChildItem -Path $path -File | Where-Object {
        $_.Extension -match '^\.(png|jpe?g|bmp|gif|tif?f)$'
    } | Sort-Object FullName
}

if (-not $files) {
    throw 'No input images were found.'
}

$rows = [Math]::Ceiling($files.Count / [double]$Columns)
$labelPixels = if ($HideLabels) { 0 } else { $LabelHeight }
$sheet = [System.Drawing.Bitmap]::new($Columns * $CellWidth, $rows * ($CellHeight + $labelPixels))
$graphics = [System.Drawing.Graphics]::FromImage($sheet)
$graphics.Clear([System.Drawing.Color]::FromArgb(28, 30, 30))
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$font = [System.Drawing.Font]::new('Segoe UI', 11, [System.Drawing.FontStyle]::Regular)
$brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::Gainsboro)
$border = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(80, 84, 84), 1)

try {
    for ($index = 0; $index -lt $files.Count; $index++) {
        $column = $index % $Columns
        $row = [Math]::Floor($index / $Columns)
        $x = $column * $CellWidth
        $y = $row * ($CellHeight + $labelPixels)

        $image = [System.Drawing.Image]::FromFile($files[$index].FullName)
        try {
            $scale = [Math]::Min($CellWidth / [double]$image.Width, $CellHeight / [double]$image.Height)
            $width = [int][Math]::Round($image.Width * $scale)
            $height = [int][Math]::Round($image.Height * $scale)
            $drawX = $x + [int](($CellWidth - $width) / 2)
            $drawY = $y + [int](($CellHeight - $height) / 2)
            $graphics.DrawImage($image, $drawX, $drawY, $width, $height)
            $graphics.DrawRectangle($border, $x, $y, $CellWidth - 1, $CellHeight - 1)
        }
        finally {
            $image.Dispose()
        }

        if (-not $HideLabels) {
            $label = [System.IO.Path]::GetFileNameWithoutExtension($files[$index].Name)
            $labelRect = [System.Drawing.RectangleF]::new($x + 5, $y + $CellHeight + 3, $CellWidth - 10, $LabelHeight - 4)
            $graphics.DrawString($label, $font, $brush, $labelRect)
        }
    }

    $outputDirectory = Split-Path -Parent $OutputPath
    if ($outputDirectory) {
        New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
    }
    $sheet.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $border.Dispose()
    $brush.Dispose()
    $font.Dispose()
    $graphics.Dispose()
    $sheet.Dispose()
}
