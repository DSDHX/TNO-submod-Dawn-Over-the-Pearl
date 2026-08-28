param([int]$ProcessId = 42724)
$ErrorActionPreference = 'Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4Geometry {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT rect);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT rect);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT point);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
}
"@
[DOPHoi4Geometry]::SetProcessDPIAware() | Out-Null
$handle = (Get-Process -Id $ProcessId -ErrorAction Stop).MainWindowHandle
$window = New-Object DOPHoi4Geometry+RECT
$client = New-Object DOPHoi4Geometry+RECT
$origin = New-Object DOPHoi4Geometry+POINT
[DOPHoi4Geometry]::GetWindowRect($handle, [ref]$window) | Out-Null
[DOPHoi4Geometry]::GetClientRect($handle, [ref]$client) | Out-Null
[DOPHoi4Geometry]::ClientToScreen($handle, [ref]$origin) | Out-Null
[pscustomobject]@{
  Window = "$($window.Left),$($window.Top),$($window.Right),$($window.Bottom)"
  Client = "$($client.Left),$($client.Top),$($client.Right),$($client.Bottom)"
  ClientOrigin = "$($origin.X),$($origin.Y)"
  Dpi = [DOPHoi4Geometry]::GetDpiForWindow($handle)
}
