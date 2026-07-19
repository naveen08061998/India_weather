Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Drawing; using System.Runtime.InteropServices;
public class WinHelper {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int x, int y, uint data, IntPtr extra);
    public struct RECT { public int L,T,R,B; }
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP   = 0x0004;
    public const uint MOUSEEVENTF_MOVE     = 0x0001;
    public const uint MOUSEEVENTF_ABSOLUTE = 0x8000;
}
"@
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$p = Get-Process sift2
[WinHelper]::ShowWindow($p.MainWindowHandle, 9)  | Out-Null
[WinHelper]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 1000

# Screenshot
$rc = New-Object WinHelper+RECT
[WinHelper]::GetWindowRect($p.MainWindowHandle, [ref]$rc) | Out-Null
$w = $rc.R - $rc.L; $h = $rc.B - $rc.T
Write-Output "Window: ${w}x${h} at $($rc.L),$($rc.T)"
$bmp = New-Object System.Drawing.Bitmap($w,$h)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($rc.L, $rc.T, 0, 0, (New-Object System.Drawing.Size($w,$h)))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_full.png')
Write-Output "Screenshot saved"

# Find Connections button via UIA in this process context
$root = [System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition)

foreach ($el in $all) {
    if ($el.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button) {
        $br = $el.Current.BoundingRectangle
        Write-Output "Btn '$($el.Current.Name)' at ($([int]$br.Left),$([int]$br.Top),$([int]$br.Right),$([int]$br.Bottom))"
    }
}
