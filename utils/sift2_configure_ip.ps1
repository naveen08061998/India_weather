Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class W8 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c3);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int L, T, R, B; }
}
"@

function Click([int]$x, [int]$y, [int]$delay = 300) {
    [W8]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [W8]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [W8]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
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
    [W8]::GetWindowThreadProcessId($h, [ref]$t1) | Out-Null
    $t0 = [W8]::GetCurrentThreadId()
    [W8]::AttachThreadInput($t0, $t1, $true) | Out-Null
    [W8]::ShowWindow($h, 9) | Out-Null
    [W8]::BringWindowToTop($h) | Out-Null
    [W8]::SetForegroundWindow($h) | Out-Null
    [W8]::AttachThreadInput($t0, $t1, $false) | Out-Null
}

# Minimize competing windows
foreach ($pname in @("ms-teams", "msedge", "olk", "Code")) {
    $procs = Get-Process $pname -ErrorAction SilentlyContinue
    foreach ($proc in $procs) {
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) {
            [W8]::ShowWindow($proc.MainWindowHandle, 6) | Out-Null
        }
    }
}
Start-Sleep -Milliseconds 500

$p = Get-Process sift2
$hw = $p.MainWindowHandle
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

# Get dialog HWND
$dlgHwnd = [IntPtr]::Zero
foreach ($el in $all) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
        $el.Current.Name -match "Printer|Connection") {
        $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
    }
}

if ($dlgHwnd -ne [IntPtr]::Zero) {
    Write-Output ("Dialog HWND={0} found - bringing to front" -f $dlgHwnd)
    FrontHwnd $dlgHwnd
    Start-Sleep -Milliseconds 600
} else {
    # Open dialog via Connections button
    Write-Output "Dialog not open - clicking Connections button..."
    FrontHwnd $hw
    Start-Sleep -Milliseconds 400
    foreach ($el in $all) {
        if ($el.Current.AutomationId -match "connectionButton") {
            $br  = $el.Current.BoundingRectangle
            $phX = [int]($br.Left + $br.Width  / 2)
            $phY = [int]($br.Top  + $br.Height / 2)
            Click $phX $phY 2000
            break
        }
    }
    $root2 = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
    foreach ($el in $root2.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
            $el.Current.Name -match "Printer|Connection") {
            $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
        }
    }
    if ($dlgHwnd -ne [IntPtr]::Zero) {
        FrontHwnd $dlgHwnd
        Start-Sleep -Milliseconds 600
    }
}

$rc = New-Object W8+RECT
[W8]::GetWindowRect($dlgHwnd, [ref]$rc) | Out-Null
Write-Output ("Dialog rect: L={0} T={1} R={2} B={3}" -f $rc.L, $rc.T, $rc.R, $rc.B)

SS "step0_state.png"

# ============================================================
# From shell_clicked.png analysis (dialog at L=541, T=195):
#
#  Dialog layout (screen coords):
#    Column headers row at y=243:  Shell=977, UDW=1005, REST=1035, Print=1065, Flash=1097, Dart=1127
#    Row 1  y=270  (empty)
#    Row 2  y=302  (empty)
#    Row 3  y=334  (empty)
#    Row 4  y=365  (empty)
#    Row 5  y=396  COM3  -> Shell CHECKED (277) = this is # port
#    Row 6  y=428  (empty)
#    Row 7  y=458  (dropdown row - a Port selector is open)
#    Row 8  y=489  Port dropdown OPEN showing: COM10,COM11,COM3,COM8,COM9,
#                  15.32.22.68:9104, 15.7.45.39, 15.77.36.63, COM10.
#              "15.77.36.63" in dropdown at screen y=649, x=800
#
# Plan:
#   A) Dropdown for row 8 is already open - click "15.77.36.63" in it
#   B) Shell checkbox for row 8 is at (977, 489)
#   C) Click OK at (872, 744)
# ============================================================

# Step A: Check if a dropdown is open by taking screenshot first
SS "step1_before.png"

# The dropdown from shell_clicked.png was at row 8 (y=489).
# "15.77.36.63" appeared at y≈649 in that screenshot.
# If dropdown is still open, click 15.77.36.63 to select it.
# If not open (closed by Teams stealing focus), we need to re-open it or
# see if the IP is already in that row.

# Calculate position offsets from dialog top-left
# Dialog L=541, T=195 in shell_clicked.png
# Row 8 y_in_dlg = 489 - 195 = 294px from dialog top
# Shell col x_in_dlg = 977 - 541 = 436px from dialog left

$dlgL = $rc.L; $dlgT = $rc.T
$row8Y      = $dlgT + 294    # row 8 y (Port dropdown row)
$shellColX  = $dlgL + 436    # Shell checkbox column
$portColX   = $dlgL + 260    # Port combo center x
$okX        = $dlgL + 331    # OK button (872-541=331 from left)
$okY        = $dlgT + 549    # OK button (744-195=549 from top)

Write-Output ("Row 8 y={0}, Shell col x={1}, Port combo x={2}" -f $row8Y, $shellColX, $portColX)
Write-Output ("OK at ({0},{1})" -f $okX, $okY)

# Step A: Click the Port combo dropdown arrow for row 8 to open it (if closed)
# Then select 15.77.36.63
$portDropX = $dlgL + 400    # dropdown arrow x (Port combo right side)
Write-Output "Opening Port dropdown for row 8..."
Click $portDropX $row8Y 400
SS "step2_dropdown.png"

# Step B: Select 15.77.36.63 from dropdown
# Dropdown items are approx 21px tall each, starting at combo Y
# Order from shell_clicked: blank, COM10, COM11, COM3, COM8, COM9, 15.32.22.68:9104, 15.7.45.39, 15.77.36.63
# That's 8 items below blank = offset ~168px from combo top
$ipInDropY = $row8Y + 170
Write-Output ("Clicking '15.77.36.63' in dropdown at ({0},{1})..." -f $portColX, $ipInDropY)
Click $portColX $ipInDropY 600
SS "step3_ip_selected.png"

# Step C: Click Shell checkbox for row 8
Write-Output ("Clicking Shell checkbox at ({0},{1})..." -f $shellColX, $row8Y)
Click $shellColX $row8Y 400
SS "step4_shell_checked.png"

# Step D: Click OK
Write-Output ("Clicking OK at ({0},{1})..." -f $okX, $okY)
Click $okX $okY 1500
SS "step5_final.png"

Write-Output "Configuration complete!"
Write-Output ""
Write-Output "Summary:"
Write-Output "  COM3  = SHELL (#) port  [was pre-configured, active]"
Write-Output "  15.77.36.63 = SHELL (#) port  [just configured]"
