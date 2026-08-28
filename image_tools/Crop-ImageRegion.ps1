param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [int]$X,
    [int]$Y,
    [int]$Width,
    [int]$Height
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$source = [System.Drawing.Image]::FromFile([System.IO.Path]::GetFullPath((Join-Path (Get-Location) $InputPath)))
$target = New-Object System.Drawing.Bitmap $Width,$Height
$graphics = [System.Drawing.Graphics]::FromImage($target)
try {
    $graphics.DrawImage($source, [System.Drawing.Rectangle]::new(0,0,$Width,$Height), [System.Drawing.Rectangle]::new($X,$Y,$Width,$Height), [System.Drawing.GraphicsUnit]::Pixel)
    $full = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $full)) | Out-Null
    $target.Save($full, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output $full
}
finally {
    $graphics.Dispose()
    $target.Dispose()
    $source.Dispose()
}
