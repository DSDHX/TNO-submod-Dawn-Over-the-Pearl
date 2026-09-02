param(
    [Parameter(Mandatory = $true)][int]$ProcessId,
    [string]$OutputPath = 'output/testing/hoi4_window.png'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4WindowCapture {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
}
"@
$process = Get-Process -Id $ProcessId -ErrorAction Stop
$handle = $process.MainWindowHandle
if ($handle -eq [IntPtr]::Zero) { throw "Process $ProcessId has no main window." }
$rect = New-Object DOPHoi4WindowCapture+RECT
if (-not [DOPHoi4WindowCapture]::GetWindowRect($handle, [ref]$rect)) { throw 'GetWindowRect failed.' }
$width = [Math]::Max(1, $rect.Right - $rect.Left)
$height = [Math]::Max(1, $rect.Bottom - $rect.Top)
$bitmap = New-Object System.Drawing.Bitmap $width,$height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
try {
    $hdc = $graphics.GetHdc()
    try {
        if (-not [DOPHoi4WindowCapture]::PrintWindow($handle, $hdc, 2)) { throw 'PrintWindow failed.' }
    }
    finally { $graphics.ReleaseHdc($hdc) }
    $full = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $full)) | Out-Null
    $bitmap.Save($full, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output "$full|${width}x${height}"
}
finally {
    $graphics.Dispose()
    $bitmap.Dispose()
}
