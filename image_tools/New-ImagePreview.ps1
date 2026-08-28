param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [int]$Width = 1300,
    [int]$Height = 750,
    [int]$Quality = 82
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$sourcePath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $InputPath))
$targetPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
[System.IO.Directory]::CreateDirectory((Split-Path -Parent $targetPath)) | Out-Null
$source = [System.Drawing.Image]::FromFile($sourcePath)
$target = New-Object System.Drawing.Bitmap $Width,$Height
$graphics = [System.Drawing.Graphics]::FromImage($target)
try {
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.DrawImage($source, 0, 0, $Width, $Height)
    $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
    $parameters = New-Object System.Drawing.Imaging.EncoderParameters 1
    $parameters.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]$Quality)
    $target.Save($targetPath, $codec, $parameters)
}
finally {
    $graphics.Dispose()
    $target.Dispose()
    $source.Dispose()
}
Write-Output $targetPath
