Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WU2 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    public struct RECT { public int L, T, R, B; }
}
"@

$p = Get-Process sift2
$hw = $p.MainWindowHandle
Write-Output "Sift2 PID=$($p.Id) HWND=$hw"

# Restore (SW_RESTORE=9, SW_SHOWMAXIMIZED=3, SW_SHOWNORMAL=1)
[WU2]::ShowWindow($hw, 9) | Out-Null
Start-Sleep -Milliseconds 800
[WU2]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 800

$rc = New-Object WU2+RECT
[WU2]::GetWindowRect($hw, [ref]$rc) | Out-Null
Write-Output "After restore: ($($rc.L),$($rc.T),$($rc.R),$($rc.B)) Size=$(($rc.R-$rc.L))x$(($rc.B-$rc.T))"

# Capture entire desktop to see where Sift2 is
Add-Type -AssemblyName System.Drawing
$sw = [System.Windows.Forms.SystemInformation]::VirtualScreen
Write-Output "Desktop: $($sw.Width)x$($sw.Height) at ($($sw.Left),$($sw.Top))"

$bmp = New-Object System.Drawing.Bitmap($sw.Width, $sw.Height)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($sw.Left, $sw.Top, 0, 0, (New-Object System.Drawing.Size($sw.Width, $sw.Height)))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_desktop2.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "Saved sift2_desktop2.png"

# Re-check window position after restore
[WU2]::GetWindowRect($hw, [ref]$rc) | Out-Null
Write-Output "Final rect: ($($rc.L),$($rc.T),$($rc.R),$($rc.B))"
