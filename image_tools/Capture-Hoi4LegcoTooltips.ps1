param(
    [int]$ProcessId = 42724,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [Parameter(Mandatory = $true)][string]$Prefix,
    [int[]]$CardCentersX = @(658, 832, 998, 1166, 1337),
    [int]$CardCenterY = 830
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4TooltipCapture {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@
[DOPHoi4TooltipCapture]::SetProcessDPIAware() | Out-Null
$process = Get-Process -Id $ProcessId -ErrorAction Stop
[DOPHoi4TooltipCapture]::SetForegroundWindow($process.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
$targetDirectory = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputDirectory))
[System.IO.Directory]::CreateDirectory($targetDirectory) | Out-Null
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
for ($i = 0; $i -lt $CardCentersX.Count; $i++) {
    [DOPHoi4TooltipCapture]::SetCursorPos($CardCentersX[$i], $CardCenterY) | Out-Null
    Start-Sleep -Milliseconds 950
    $bitmap = New-Object System.Drawing.Bitmap $bounds.Width,$bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
        $path = Join-Path $targetDirectory ("{0}_{1}.png" -f $Prefix, ($i + 1))
        $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Output $path
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}
