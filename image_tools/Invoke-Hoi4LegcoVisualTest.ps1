param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Capture', 'Console', 'Move', 'Click', 'Escape', 'Close')]
    [string]$Action,

    [int]$ProcessId = 42724,
    [string]$Command,
    [int]$X = 0,
    [int]$Y = 0,
    [string]$OutputPath = 'output/imagegen/legco_leaders/qa/hoi4_current.png'
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DOPHoi4Native {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr wp, IntPtr lp);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  public static void Tap(IntPtr h, int vk, long down, long up) {
    PostMessage(h, 0x0100, (IntPtr)vk, (IntPtr)(uint)down);
    PostMessage(h, 0x0101, (IntPtr)vk, (IntPtr)(uint)up);
  }
  public static void Char(IntPtr h, char c) {
    PostMessage(h, 0x0102, (IntPtr)(int)c, (IntPtr)1);
  }
  public static void ClickInPlace() {
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
    System.Threading.Thread.Sleep(180);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
}
"@

$process = Get-Process -Id $ProcessId -ErrorAction Stop
$handle = $process.MainWindowHandle
if ($handle -eq [IntPtr]::Zero) {
    throw "Process $ProcessId does not have a main window."
}

function Focus-Hoi4 {
    [DOPHoi4Native]::ShowWindowAsync($handle, 9) | Out-Null
    [DOPHoi4Native]::SetForegroundWindow($handle) | Out-Null
    Start-Sleep -Milliseconds 350
}

function Save-Hoi4Capture([string]$Path) {
    $full = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
    $dir = Split-Path -Parent $full
    [System.IO.Directory]::CreateDirectory($dir) | Out-Null
    $bitmap = New-Object System.Drawing.Bitmap 2600,1500
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $dc = $graphics.GetHdc()
        try {
            [DOPHoi4Native]::PrintWindow($handle, $dc, 2) | Out-Null
        }
        finally {
            $graphics.ReleaseHdc($dc)
        }
        $bitmap.Save($full, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
    Write-Output $full
}

switch ($Action) {
    'Capture' {
        Save-Hoi4Capture $OutputPath
    }
    'Console' {
        if ([string]::IsNullOrWhiteSpace($Command)) { throw 'Command is required.' }
        Focus-Hoi4
        [DOPHoi4Native]::Tap($handle, 0xC0, 0x00290001, 0xC0290001)
        Start-Sleep -Milliseconds 300
        1..3 | ForEach-Object { [DOPHoi4Native]::Tap($handle, 0x08, 0x000E0001, 0xC00E0001); Start-Sleep -Milliseconds 50 }
        foreach ($character in [char[]]$Command) {
            [DOPHoi4Native]::Char($handle, $character)
            Start-Sleep -Milliseconds 28
        }
        [DOPHoi4Native]::Tap($handle, 0x0D, 0x001C0001, 0xC01C0001)
        Start-Sleep -Milliseconds 500
        Save-Hoi4Capture $OutputPath
    }
    'Move' {
        Focus-Hoi4
        [DOPHoi4Native]::SetCursorPos($X, $Y) | Out-Null
        Start-Sleep -Milliseconds 500
        Save-Hoi4Capture $OutputPath
    }
    'Click' {
        Focus-Hoi4
        [DOPHoi4Native]::SetCursorPos($X, $Y) | Out-Null
        Start-Sleep -Milliseconds 180
        [DOPHoi4Native]::ClickInPlace()
        Start-Sleep -Milliseconds 650
        Save-Hoi4Capture $OutputPath
    }
    'Escape' {
        Focus-Hoi4
        [DOPHoi4Native]::Tap($handle, 0x1B, 0x00010001, 0xC0010001)
        Start-Sleep -Milliseconds 350
        Save-Hoi4Capture $OutputPath
    }
    'Close' {
        [DOPHoi4Native]::PostMessage($handle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
    }
}
