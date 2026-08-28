param(
    [int]$ProcessId = 42724,
    [Parameter(Mandatory = $true)][int]$X,
    [Parameter(Mandatory = $true)][int]$Y
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4ScreenClick {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  public static void Click() {
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
    System.Threading.Thread.Sleep(220);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
}
"@
$shell = New-Object -ComObject WScript.Shell
if (-not $shell.AppActivate($ProcessId)) { throw "Could not activate process $ProcessId." }
Start-Sleep -Milliseconds 750
[DOPHoi4ScreenClick]::SetCursorPos($X, $Y) | Out-Null
Start-Sleep -Milliseconds 350
[DOPHoi4ScreenClick]::Click()
Start-Sleep -Milliseconds 750
$cursor = [System.Windows.Forms.Cursor]::Position
$foreground = [DOPHoi4ScreenClick]::GetForegroundWindow()
Write-Output "cursor=$($cursor.X),$($cursor.Y);foreground=$foreground"
