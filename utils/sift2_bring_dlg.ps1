Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class W6 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int L, T, R, B; }
}
"@

function Click([int]$x, [int]$y, [int]$delay = 300) {
    [W6]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [W6]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [W6]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds $delay
    Write-Output ("Clicked ({0},{1})" -f $x, $y)
}

function SS([string]$f) {
    $bmp = New-Object System.Drawing.Bitmap(1536, 864)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$f")
    $g.Dispose(); $bmp.Dispose()
    Write-Output "SS: $f"
}

function BringHwndFront([IntPtr]$h) {
    $t1 = 0
    [W6]::GetWindowThreadProcessId($h, [ref]$t1) | Out-Null
    $t0 = [W6]::GetCurrentThreadId()
    [W6]::AttachThreadInput($t0, $t1, $true) | Out-Null
    [W6]::ShowWindow($h, 9) | Out-Null
    [W6]::BringWindowToTop($h) | Out-Null
    [W6]::SetForegroundWindow($h) | Out-Null
    [W6]::AttachThreadInput($t0, $t1, $false) | Out-Null
    Start-Sleep -Milliseconds 600
}

# -- Find Sift2 and dialog via UIA --
$p    = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2 not running"; exit 1 }
$hw   = $p.MainWindowHandle

# First bring main window up so UIA tree loads
BringHwndFront $hw
Start-Sleep -Milliseconds 400

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

$dlgHwnd = [IntPtr]::Zero
foreach ($el in $all) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window") {
        $n = $el.Current.Name
        if ($n -match "Printer|Connection") {
            $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
            Write-Output ("Dialog HWND: {0} Name: [{1}]" -f $dlgHwnd, $n)
        }
    }
}

if ($dlgHwnd -eq [IntPtr]::Zero) {
    # Dialog not open - open it by clicking the Connections button
    $connBtn = $null
    foreach ($el in $all) {
        if ($el.Current.AutomationId -match "connectionButton") { $connBtn = $el; break }
    }
    if (-not $connBtn) { Write-Output "Cannot find Connections button"; exit 1 }
    $br  = $connBtn.Current.BoundingRectangle
    $phX = [int]($br.Left + $br.Width  / 2)
    $phY = [int]($br.Top  + $br.Height / 2)
    Write-Output ("Clicking Connections button at physical ({0},{1})" -f $phX, $phY)
    Click $phX $phY 2000

    $root2 = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
    $all2  = $root2.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all2) {
        if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window") {
            $n = $el.Current.Name
            if ($n -match "Printer|Connection") {
                $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
                Write-Output ("Dialog HWND after open: {0}" -f $dlgHwnd)
            }
        }
    }
    if ($dlgHwnd -eq [IntPtr]::Zero) { Write-Output "Still no dialog HWND"; exit 1 }
}

# Bring dialog to front
Write-Output ("Bringing dialog HWND {0} to front..." -f $dlgHwnd)
BringHwndFront $dlgHwnd

# Verify position
$rc = New-Object W6+RECT
[W6]::GetWindowRect($dlgHwnd, [ref]$rc) | Out-Null
Write-Output ("Dialog logical rect: L={0} T={1} R={2} B={3} W={4} H={5}" -f $rc.L, $rc.T, $rc.R, $rc.B, ($rc.R-$rc.L), ($rc.B-$rc.T))

SS "dlg_front.png"

# -- From screenshot scan_before.png analysis (1536x864 logical coords):
#    Row 8 (15.77.36.63):
#      Shell checkbox center: (970, 490)
#      Dart  checkbox center: (1163, 490)
#    OK button center: (872, 744)
# --
# Adjust based on actual dialog position (if dialog moved)
$dlgOffX = $rc.L - 516   # expected left was 516 in scan_before
$dlgOffY = $rc.T - 196   # expected top was 196 in scan_before
Write-Output ("Dialog offset from expected: dx={0} dy={1}" -f $dlgOffX, $dlgOffY)

$shellX = 970 + $dlgOffX
$shellY = 490 + $dlgOffY
$okX    = 872 + $dlgOffX
$okY    = 744 + $dlgOffY

Write-Output ("Shell checkbox for row 8 at ({0},{1})" -f $shellX, $shellY)
Write-Output ("OK button at ({0},{1})" -f $okX, $okY)

# Click Shell checkbox
Write-Output "Clicking Shell checkbox for 15.77.36.63..."
Click $shellX $shellY 400
SS "after_shell_click.png"

# Click OK
Write-Output "Clicking OK..."
Click $okX $okY 1500
SS "after_ok.png"

Write-Output "Done."
