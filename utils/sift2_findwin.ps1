Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public class WU {
    public delegate bool EnumWinProc(IntPtr h, IntPtr p);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWinProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int pid);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    public struct RECT { public int L, T, R, B; }
}
"@

$p       = Get-Process sift2
$siftPid = $p.Id

# Enumerate ALL top-level windows belonging to Sift2 process
$hwnds = [System.Collections.Generic.List[IntPtr]]::new()
$cb = [WU+EnumWinProc]{
    param([IntPtr]$h, [IntPtr]$lp)
    $wpid2 = 0
    [WU]::GetWindowThreadProcessId($h, [ref]$wpid2) | Out-Null
    if ($wpid2 -eq $script:siftPid -and [WU]::IsWindowVisible($h)) { $script:hwnds.Add($h) }
    return $true
}
[WU]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
Write-Output "Found $($hwnds.Count) visible windows for Sift2 (pid=$pid):"

$toolbarHwnd = $null
foreach ($hw in $hwnds) {
    $rc = New-Object WU+RECT
    [WU]::GetWindowRect($hw, [ref]$rc) | Out-Null
    $w = $rc.R - $rc.L; $h2 = $rc.B - $rc.T
    $el = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
    $name = $el.Current.Name
    Write-Output "  HWND=$hw Name='$name' Rect=($($rc.L),$($rc.T),$($rc.R),$($rc.B)) Size=$($w)x$($h2)"
    # The toolbar window is the one containing the Connections button (approx y=991)
    if ($rc.T -gt 900 -or ($rc.B -gt 990 -and $rc.T -gt 800)) {
        $toolbarHwnd = $hw
        Write-Output "  ^ This looks like the toolbar panel"
    }
}

# Bring ALL Sift2 windows to front
foreach ($hw in $hwnds) {
    [WU]::ShowWindow($hw, 9)  | Out-Null
    [WU]::SetForegroundWindow($hw) | Out-Null
}
Start-Sleep -Milliseconds 600

if ($toolbarHwnd) {
    Write-Output "Focusing toolbar HWND=$toolbarHwnd..."
    [WU]::SetForegroundWindow($toolbarHwnd) | Out-Null
    Start-Sleep -Milliseconds 300
}

# Click Connections button at screen (1732, 1005)
$cx = 1732; $cy = 1005
Write-Output "Clicking at ($cx, $cy)..."
[WU]::SetCursorPos($cx, $cy) | Out-Null
Start-Sleep -Milliseconds 200
[WU]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 80
[WU]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 2000

# Screenshot the ENTIRE desktop area where Sift2 lives (including y=991 area)
$bmp = New-Object System.Drawing.Bitmap(1920, 1080)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size(1920, 1080)))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_desktop.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "Screenshot saved: sift2_desktop.png"
