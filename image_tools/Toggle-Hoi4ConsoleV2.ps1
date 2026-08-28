param([int]$ProcessId = 42724)
$ErrorActionPreference = 'Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4ConsoleToggleV2 {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr wp, IntPtr lp);
  public static void Tap(IntPtr h, long down, long up) {
    PostMessage(h, 0x0100, (IntPtr)0xC0, (IntPtr)(uint)down);
    PostMessage(h, 0x0101, (IntPtr)0xC0, (IntPtr)(uint)up);
  }
}
"@
$process = Get-Process -Id $ProcessId -ErrorAction Stop
if ($process.MainWindowHandle -eq [IntPtr]::Zero) { throw "Process $ProcessId has no main window." }
[DOPHoi4ConsoleToggleV2]::Tap($process.MainWindowHandle, 0x00290001, 0xC0290001)
Start-Sleep -Milliseconds 400
