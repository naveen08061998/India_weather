Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Mouse {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int L, T, R, B; }
    public const uint LEFTDOWN = 0x0002;
    public const uint LEFTUP   = 0x0004;
}
"@

$OX = -6; $OY = -5

function Click($imgX, $imgY) {
    [Mouse]::SetCursorPos($imgX + $OX, $imgY + $OY) | Out-Null
    Start-Sleep -Milliseconds 150
    [Mouse]::mouse_event([Mouse]::LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 100
    [Mouse]::mouse_event([Mouse]::LEFTUP,   0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 400
}

function Screenshot($path) {
    $p  = Get-Process sift2
    $rc = New-Object Mouse+RECT
    [Mouse]::GetWindowRect($p.MainWindowHandle, [ref]$rc) | Out-Null
    $w = $rc.R - $rc.L; $h = $rc.B - $rc.T
    $bmp = New-Object System.Drawing.Bitmap($w,$h)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($rc.L,$rc.T,0,0,(New-Object System.Drawing.Size($w,$h)))
    $bmp.Save($path); $g.Dispose(); $bmp.Dispose()
    Write-Output "Screenshot: $path"
}

$p = Get-Process sift2
[Mouse]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[Mouse]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 600

# Step 1: Click on row 8's Printer Connections field and press Enter to commit IP
Write-Output "Step 1: Committing IP by pressing Enter..."
Click 830 509
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 500

# Step 2: Click Shell checkbox for row 8 — try x=1007 (tighter to checkbox center)
Write-Output "Step 2: Clicking Shell checkbox (row 8) at x=1007..."
Click 1007 509
Start-Sleep -Milliseconds 400
Screenshot "C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_shellcheck.png"

# Step 3: Click Dart checkbox for row 8 at x=1204
Write-Output "Step 3: Clicking Dart checkbox (row 8) at x=1204..."
Click 1204 509
Start-Sleep -Milliseconds 400

# Step 4: Open Prefix dropdown for row 8 and select "#"
Write-Output "Step 4: Opening Prefix dropdown for row 8..."
Click 600 509       # click the dropdown arrow portion
Start-Sleep -Milliseconds 800
Screenshot "C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_prefix_open.png"
