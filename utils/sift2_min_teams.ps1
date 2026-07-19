Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class W7 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c3);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ScreenToClient(IntPtr h, ref POINT p3);
    [DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
    public struct RECT  { public int L, T, R, B; }
    public struct POINT { public int X, Y; }
}
"@

function Click([int]$x, [int]$y, [int]$delay = 350) {
    [W7]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [W7]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [W7]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
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

function FrontHwnd([IntPtr]$h) {
    $t1 = 0
    [W7]::GetWindowThreadProcessId($h, [ref]$t1) | Out-Null
    $t0 = [W7]::GetCurrentThreadId()
    [W7]::AttachThreadInput($t0, $t1, $true) | Out-Null
    [W7]::ShowWindow($h, 9) | Out-Null
    [W7]::BringWindowToTop($h) | Out-Null
    [W7]::SetForegroundWindow($h) | Out-Null
    [W7]::AttachThreadInput($t0, $t1, $false) | Out-Null
}

# -- Step 1: Minimize competing windows (Teams, Edge, Outlook) --
Write-Output "Minimizing Teams, Edge, Outlook..."
foreach ($pname in @("ms-teams", "msedge", "olk")) {
    $procs = Get-Process $pname -ErrorAction SilentlyContinue
    foreach ($proc in $procs) {
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) {
            [W7]::ShowWindow($proc.MainWindowHandle, 6) | Out-Null  # SW_MINIMIZE
        }
    }
}
Start-Sleep -Milliseconds 500

# -- Step 2: Get Sift2 and dialog --
$p   = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2 not running"; exit 1 }
$hw  = $p.MainWindowHandle

FrontHwnd $hw
Start-Sleep -Milliseconds 500

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

$dlgHwnd = [IntPtr]::Zero
foreach ($el in $all) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
        $el.Current.Name -match "Printer|Connection") {
        $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
        Write-Output ("Dialog HWND={0} Name=[{1}]" -f $dlgHwnd, $el.Current.Name)
        break
    }
}

if ($dlgHwnd -eq [IntPtr]::Zero) {
    Write-Output "Dialog not found - opening via Connections button..."
    foreach ($el in $all) {
        if ($el.Current.AutomationId -match "connectionButton") {
            $br  = $el.Current.BoundingRectangle
            $phX = [int]($br.Left + $br.Width  / 2)
            $phY = [int]($br.Top  + $br.Height / 2)
            Write-Output ("Clicking button at ({0},{1})" -f $phX, $phY)
            FrontHwnd $hw
            Start-Sleep -Milliseconds 300
            Click $phX $phY 2000
            break
        }
    }
    $root2 = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
    foreach ($el in $root2.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
            $el.Current.Name -match "Printer|Connection") {
            $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
            break
        }
    }
}

if ($dlgHwnd -eq [IntPtr]::Zero) { Write-Output "ERROR: dialog HWND not found"; exit 1 }
Write-Output ("Using dialog HWND={0}" -f $dlgHwnd)

# Bring dialog to front
FrontHwnd $dlgHwnd
Start-Sleep -Milliseconds 600

# Get dialog position
$rc = New-Object W7+RECT
[W7]::GetWindowRect($dlgHwnd, [ref]$rc) | Out-Null
Write-Output ("Dialog rect: L={0} T={1} R={2} B={3}" -f $rc.L, $rc.T, $rc.R, $rc.B)

SS "dlg_ready.png"

# -- Step 3: Calculate click coordinates based on dialog position --
# From scan_before.png analysis (dialog at L=516, T=196):
#   Shell checkbox row 8 at screen (970, 490)
#   The dialog offsets relative to its known position:
$dlgL = $rc.L; $dlgT = $rc.T
$shellX = $dlgL + (970 - 516)   # column offset within dialog
$shellY = $dlgT + (490 - 196)   # row offset within dialog
$okX    = $dlgL + (872 - 516)
$okY    = $dlgT + (744 - 196)

Write-Output ("Shell checkbox screen=({0},{1})" -f $shellX, $shellY)
Write-Output ("OK button screen=({0},{1})" -f $okX, $okY)

# Step 4: Click Shell checkbox
Write-Output "Clicking Shell checkbox for 15.77.36.63 row..."
Click $shellX $shellY 500
SS "shell_clicked.png"

# Step 5: Click OK
Write-Output "Clicking OK..."
Click $okX $okY 1500
SS "final_result.png"

Write-Output "Done! Verifying port selector..."
$root3 = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$cond  = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.portSelector')
$ps = $root3.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if ($ps) {
    $v = ""; try { $v = $ps.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
    Write-Output ("portSelector: [{0}]" -f $v)
} else {
    Write-Output "portSelector not found"
}
