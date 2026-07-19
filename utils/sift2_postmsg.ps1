Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WM {
    [DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern bool  ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool  SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool  BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern int   GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool  AttachThreadInput(uint a, uint b, bool c3);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool  GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool  SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void  mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    public struct RECT { public int L, T, R, B; }
}
"@

function SS([string]$f) {
    $bmp = New-Object System.Drawing.Bitmap(1536, 864)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$f")
    $g.Dispose(); $bmp.Dispose()
    Write-Output "SS: $f"
}

# PostMessage click — works without focus
function PMClick([IntPtr]$hwnd, [int]$clientX, [int]$clientY) {
    $lParam = [IntPtr](($clientY -shl 16) -bor ($clientX -band 0xFFFF))
    [WM]::PostMessage($hwnd, 0x0201, [IntPtr]1, $lParam) | Out-Null   # WM_LBUTTONDOWN
    Start-Sleep -Milliseconds 50
    [WM]::PostMessage($hwnd, 0x0202, [IntPtr]0, $lParam) | Out-Null   # WM_LBUTTONUP
    Start-Sleep -Milliseconds 200
    Write-Output ("PMClick hwnd={0} client=({1},{2})" -f $hwnd, $clientX, $clientY)
}

# Get dialog HWND
$p    = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2 not running"; exit 1 }
$hw   = $p.MainWindowHandle
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)

$dlgHwnd = [IntPtr]::Zero
foreach ($el in $all) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
        $el.Current.Name -match "Printer") {
        $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
    }
}
if ($dlgHwnd -eq [IntPtr]::Zero) { Write-Output "No dialog open"; exit 1 }
Write-Output ("Dialog HWND={0}" -f $dlgHwnd)

$rc = New-Object WM+RECT
[WM]::GetWindowRect($dlgHwnd, [ref]$rc) | Out-Null
Write-Output ("Dialog screen rect: L={0} T={1} R={2} B={3}" -f $rc.L, $rc.T, $rc.R, $rc.B)

# Bring dialog to front to make it visible
$t1 = 0
[WM]::GetWindowThreadProcessId($dlgHwnd, [ref]$t1) | Out-Null
$t0 = [WM]::GetCurrentThreadId()
[WM]::AttachThreadInput($t0, $t1, $true)  | Out-Null
[WM]::ShowWindow($dlgHwnd, 9)             | Out-Null
[WM]::BringWindowToTop($dlgHwnd)          | Out-Null
[WM]::SetForegroundWindow($dlgHwnd)       | Out-Null
[WM]::AttachThreadInput($t0, $t1, $false) | Out-Null
Start-Sleep -Milliseconds 800

# Minimize Teams
foreach ($tp in (Get-Process ms-teams -ErrorAction SilentlyContinue)) {
    [WM]::ShowWindow($tp.MainWindowHandle, 6) | Out-Null
}
Start-Sleep -Milliseconds 300

SS "pm_before.png"

# Compute client coordinates for the Shell checkbox of row 8
# Dialog screen: L=541, T=195  (from multiple screenshots)
# Shell column screen X = 977  -> client X = 977 - 541 = 436
# Row 8 screen Y = 490         -> client Y = 490 - 195 = 295
$dlgLeft = $rc.L; $dlgTop = $rc.T
$shellClientX = 977 - $dlgLeft    # Shell column offset
$row8ClientY  = 490 - $dlgTop     # Row 8 offset

Write-Output ("Shell client coords: ({0},{1})" -f $shellClientX, $row8ClientY)

# Also try exact COM3 Shell position to calibrate:
# COM3 shell: screen (977, 396) -> client (436, 201)
$com3ClientY = 396 - $dlgTop
Write-Output ("COM3 Shell client Y for reference: {0}" -f $com3ClientY)

# Click Shell checkbox for row 8 via PostMessage
Write-Output "PMClick: Shell checkbox for 15.77.36.63..."
PMClick $dlgHwnd $shellClientX $row8ClientY
Start-Sleep -Milliseconds 300
PMClick $dlgHwnd $shellClientX $row8ClientY   # double-click in case first toggled off
Start-Sleep -Milliseconds 300

SS "pm_shell_click.png"

# Click OK button
# OK button screen (872, 744) -> client: (872-541, 744-195) = (331, 549)
$okClientX = 872 - $dlgLeft
$okClientY  = 744 - $dlgTop
Write-Output ("PMClick: OK at client ({0},{1})..." -f $okClientX, $okClientY)
PMClick $dlgHwnd $okClientX $okClientY
Start-Sleep -Milliseconds 1500

SS "pm_result.png"
Write-Output "Done"
