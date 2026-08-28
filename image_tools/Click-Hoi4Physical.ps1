param(
    [int]$ProcessId = 42724,
    [Parameter(Mandatory = $true)][int]$X,
    [Parameter(Mandatory = $true)][int]$Y
)
$ErrorActionPreference = 'Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4PhysicalClick {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  public static void Click() {
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
    System.Threading.Thread.Sleep(220);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
}
"@
[DOPHoi4PhysicalClick]::SetProcessDPIAware() | Out-Null
$process = Get-Process -Id $ProcessId -ErrorAction Stop
[DOPHoi4PhysicalClick]::SetForegroundWindow($process.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 600
[DOPHoi4PhysicalClick]::SetCursorPos($X, $Y) | Out-Null
Start-Sleep -Milliseconds 300
[DOPHoi4PhysicalClick]::Click()
Start-Sleep -Milliseconds 700
