Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class SB2 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int L, T, R, B; }
}
"@

function Click([int]$x, [int]$y) {
    [SB2]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [SB2]::mouse_event(2, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [SB2]::mouse_event(4, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 350
    Write-Output "Clicked ($x,$y)"
}

function SS([string]$fname) {
    $path = "C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$fname"
    $bmp = New-Object System.Drawing.Bitmap(1920, 1080)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1920, 1080))
    $bmp.Save($path)
    $g.Dispose(); $bmp.Dispose()
    Write-Output "Screenshot: $fname"
}

# Bring Sift2 to foreground
$p  = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Error "Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle
$t1 = 0
[SB2]::GetWindowThreadProcessId($hw, [ref]$t1) | Out-Null
$t0 = [SB2]::GetCurrentThreadId()
[SB2]::AttachThreadInput($t0, $t1, $true)  | Out-Null
[SB2]::ShowWindow($hw, 9)                  | Out-Null
[SB2]::BringWindowToTop($hw)               | Out-Null
[SB2]::SetForegroundWindow($hw)            | Out-Null
[SB2]::AttachThreadInput($t0, $t1, $false) | Out-Null
Start-Sleep -Milliseconds 600

# Try to find the Connections dialog
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
        $dlg = $w; break
    }
}

# If dialog is closed, re-open it
if (-not $dlg) {
    Write-Output "Dialog closed — re-opening via Connections button..."
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
    $cond = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty, "Connections")
    $connBtn = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
    if ($connBtn) {
        $br = $connBtn.Current.BoundingRectangle
        Click ([int]($br.Left + $br.Width/2)) ([int]($br.Top + $br.Height/2))
    }
    Start-Sleep -Milliseconds 1500
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
            $dlg = $w; break
        }
    }
}

if (-not $dlg) { Write-Error "Connections dialog not found"; SS "dialog_not_found.png"; exit 1 }

Write-Output "Dialog: '$($dlg.Current.Name)'"
$dlgHwnd = [IntPtr]$dlg.Current.NativeWindowHandle
[SB2]::SetForegroundWindow($dlgHwnd) | Out-Null
Start-Sleep -Milliseconds 400

$rc = New-Object SB2+RECT
[SB2]::GetWindowRect($dlgHwnd, [ref]$rc) | Out-Null
Write-Output "Dialog rect: L=$($rc.L) T=$($rc.T) R=$($rc.R) B=$($rc.B)"

SS "dialog_before.png"

# Dump all checkboxes and combo-boxes to identify row positions
$els = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "--- CheckBoxes ---"
$checkboxes = @()
foreach ($el in $els) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.CheckBox") {
        $br = $el.Current.BoundingRectangle
        $state = ""
        try { $state = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        $bx = [int]$br.Left; $by = [int]$br.Top
        $nm = $el.Current.Name; $aid = $el.Current.AutomationId
        Write-Output ("  CB name='{0}' aid='{1}' state={2} pos={3},{4}" -f $nm, $aid, $state, $bx, $by)
        $checkboxes += [PSCustomObject]@{ El=$el; X=[int]$br.Left; Y=[int]$br.Top; State=$state; Name=$el.Current.Name }
    }
}

Write-Output "--- ComboBoxes (port selectors) ---"
foreach ($el in $els) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.ComboBox") {
        $br = $el.Current.BoundingRectangle
        $val = ""
        try { $val = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        try { $val = $el.GetCurrentPattern([System.Windows.Automation.SelectionPattern]::Pattern).Current.GetSelection()[0].Current.Name } catch {}
        $cx = [int]$br.Left; $cy = [int]$br.Top
        $caid = $el.Current.AutomationId
        Write-Output ("  Combo val='{0}' aid='{1}' pos={2},{3}" -f $val, $caid, $cx, $cy)
    }
}

Write-Output "--- Buttons in dialog ---"
foreach ($el in $els) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Button") {
        $br = $el.Current.BoundingRectangle
        $btnx = [int]$br.Left; $btny = [int]$br.Top
        $bname = $el.Current.Name
        Write-Output ("  Btn '{0}' pos={1},{2}" -f $bname, $btnx, $btny)
    }
}
