param(
    [int]$ProcessId = 42724,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [Parameter(Mandatory = $true)][string]$Prefix,
    [int[]]$EdgeX = @(590, 760, 930, 1100, 1268),
    [int]$EdgeY = 740
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4TooltipEdgeCapture {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
}
"@
[DOPHoi4TooltipEdgeCapture]::SetProcessDPIAware() | Out-Null
$process = Get-Process -Id $ProcessId -ErrorAction Stop
[DOPHoi4TooltipEdgeCapture]::SetForegroundWindow($process.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 450
$targetDirectory = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputDirectory))
[System.IO.Directory]::CreateDirectory($targetDirectory) | Out-Null
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
for ($i = 0; $i -lt $EdgeX.Count; $i++) {
    [DOPHoi4TooltipEdgeCapture]::SetCursorPos($EdgeX[$i] - 2, $EdgeY) | Out-Null
    Start-Sleep -Milliseconds 100
    [DOPHoi4TooltipEdgeCapture]::SetCursorPos($EdgeX[$i], $EdgeY) | Out-Null
    [DOPHoi4TooltipEdgeCapture]::mouse_event(0x0001, 1, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 1450
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
