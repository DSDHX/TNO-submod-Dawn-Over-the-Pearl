param(
    [int]$ProcessId = 42724,
    [Parameter(Mandatory = $true)][int]$X,
    [Parameter(Mandatory = $true)][int]$Y,
    [int]$WaitMilliseconds = 1800
)
$ErrorActionPreference = 'Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4PhysicalMoveV2 {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
}
"@
[DOPHoi4PhysicalMoveV2]::SetProcessDPIAware() | Out-Null
$process = Get-Process -Id $ProcessId -ErrorAction Stop
[DOPHoi4PhysicalMoveV2]::SetForegroundWindow($process.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 450
[DOPHoi4PhysicalMoveV2]::SetCursorPos($X - 2, $Y) | Out-Null
Start-Sleep -Milliseconds 120
[DOPHoi4PhysicalMoveV2]::SetCursorPos($X, $Y) | Out-Null
[DOPHoi4PhysicalMoveV2]::mouse_event(0x0001, 1, 0, 0, [UIntPtr]::Zero)
[DOPHoi4PhysicalMoveV2]::mouse_event(0x0001, 0, 1, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds $WaitMilliseconds
