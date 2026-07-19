Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WF {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c3);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool BlockInput(bool block);
    public struct RECT { public int L, T, R, B; }
}
"@

$log = "C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_detached.log"
"[$(Get-Date)] Starting detached script..." | Out-File $log

function Log($msg) { "[$(Get-Date -f HH:mm:ss)] $msg" | Tee-Object $log -Append | Write-Output }
function SS([string]$f) {
    $bmp = New-Object System.Drawing.Bitmap(1536, 864)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$f")
    $g.Dispose(); $bmp.Dispose()
    Log "SS: $f"
}
function FrontHwnd([IntPtr]$h) {
    $t1 = 0; [WF]::GetWindowThreadProcessId($h, [ref]$t1) | Out-Null
    $t0 = [WF]::GetCurrentThreadId()
    [WF]::AttachThreadInput($t0, $t1, $true)  | Out-Null
    [WF]::ShowWindow($h, 9) | Out-Null
    [WF]::BringWindowToTop($h) | Out-Null
    [WF]::SetForegroundWindow($h) | Out-Null
    [WF]::AttachThreadInput($t0, $t1, $false) | Out-Null
}
function ClickAbs([int]$x, [int]$y, [int]$ms = 350) {
    [WF]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 80
    [WF]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [WF]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds $ms
    Log ("Click ($x,$y)")
}

Start-Sleep -Milliseconds 1500  # let caller (VS Code terminal) settle

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Log "ERROR: Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle

# Minimize ALL competing windows
foreach ($pname in @("ms-teams","msedge","olk","Code")) {
    $procs = Get-Process $pname -ErrorAction SilentlyContinue
    foreach ($proc in $procs) {
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) {
            [WF]::ShowWindow($proc.MainWindowHandle, 6) | Out-Null
        }
    }
}
Start-Sleep -Milliseconds 800

# Get/open dialog
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
$dlgHwnd = [IntPtr]::Zero
foreach ($el in $all) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
        $el.Current.Name -match "Printer") { $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle }
}

if ($dlgHwnd -eq [IntPtr]::Zero) {
    Log "Dialog not open - clicking Connections button..."
    FrontHwnd $hw
    foreach ($el in $all) {
        if ($el.Current.AutomationId -match "connectionButton") {
            $br  = $el.Current.BoundingRectangle
            ClickAbs ([int]($br.Left + $br.Width/2)) ([int]($br.Top + $br.Height/2)) 2000
            break
        }
    }
    $root2 = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
    foreach ($el in $root2.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
            $el.Current.Name -match "Printer") { $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle }
    }
}
if ($dlgHwnd -eq [IntPtr]::Zero) { Log "ERROR: No dialog HWND"; exit 1 }
Log ("Dialog HWND={0}" -f $dlgHwnd)

# Bring dialog to front exclusively
FrontHwnd $dlgHwnd
Start-Sleep -Milliseconds 800

$rc = New-Object WF+RECT
[WF]::GetWindowRect($dlgHwnd, [ref]$rc) | Out-Null
Log ("Dialog rect: L={0} T={1} R={2} B={3}" -f $rc.L, $rc.T, $rc.R, $rc.B)
SS "detach_start.png"

# Block user input to prevent interference
[WF]::BlockInput($true) | Out-Null
Log "Input blocked"

try {
    $dlgL = $rc.L; $dlgT = $rc.T

    # Step 1: Click somewhere neutral in the dialog (empty area) to commit any pending edit
    $neutralX = $dlgL + 200   # middle left area of dialog
    $neutralY = $dlgT + 450   # middle of dialog, not on a control
    Log ("Neutral click at ({0},{1}) to clear focus..." -f $neutralX, $neutralY)
    ClickAbs $neutralX $neutralY 400

    # Step 2: Click row 8 Shell checkbox (15.77.36.63)
    # Shell col x = dlgL + 436, Row 8 y = dlgT + 295
    $shellX = $dlgL + 436
    $shellY = $dlgT + 295
    Log ("Shell checkbox click at screen ({0},{1})..." -f $shellX, $shellY)
    ClickAbs $shellX $shellY 500
    SS "detach_shell.png"

    # Step 3: Click OK
    $okX = $dlgL + 331
    $okY = $dlgT + 549
    Log ("OK click at screen ({0},{1})..." -f $okX, $okY)
    ClickAbs $okX $okY 1500
    SS "detach_ok.png"
    Log "Done!"

} finally {
    [WF]::BlockInput($false) | Out-Null
    Log "Input unblocked"
}
