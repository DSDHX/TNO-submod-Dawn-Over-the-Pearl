param(
    [Parameter(Mandatory = $true)][int]$ProcessId,
    [Parameter(Mandatory = $true)][string]$Command
)
$ErrorActionPreference = 'Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4ConsoleTextOnly {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr wp, IntPtr lp);
  public static void Tap(IntPtr h, int vk, long down, long up) {
    PostMessage(h, 0x0100, (IntPtr)vk, (IntPtr)(uint)down);
    PostMessage(h, 0x0101, (IntPtr)vk, (IntPtr)(uint)up);
  }
  public static void Char(IntPtr h, char c) { PostMessage(h, 0x0102, (IntPtr)(int)c, (IntPtr)1); }
}
"@
$handle = (Get-Process -Id $ProcessId -ErrorAction Stop).MainWindowHandle
if ($handle -eq [IntPtr]::Zero) { throw "Process $ProcessId has no main window." }
1..3 | ForEach-Object {
    [DOPHoi4ConsoleTextOnly]::Tap($handle, 0x08, 0x000E0001, 0xC00E0001)
    Start-Sleep -Milliseconds 45
}
foreach ($character in [char[]]$Command) {
    [DOPHoi4ConsoleTextOnly]::Char($handle, $character)
    Start-Sleep -Milliseconds 24
}
[DOPHoi4ConsoleTextOnly]::Tap($handle, 0x0D, 0x001C0001, 0xC01C0001)
Start-Sleep -Milliseconds 500
