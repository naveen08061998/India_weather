Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition "using System;using System.Runtime.InteropServices;public class SE{[DllImport(""user32.dll"")]public static extern bool ShowWindow(IntPtr h,int c);[DllImport(""user32.dll"")]public static extern bool SetForegroundWindow(IntPtr h);[DllImport(""user32.dll"")]public static extern bool BringWindowToTop(IntPtr h);[DllImport(""user32.dll"")]public static extern bool SetCursorPos(int x,int y);[DllImport(""user32.dll"")]public static extern void mouse_event(uint f,int x,int y,uint d,IntPtr e);[DllImport(""user32.dll"")]public static extern int GetWindowThreadProcessId(IntPtr h,out int p2);[DllImport(""user32.dll"")]public static extern bool AttachThreadInput(uint a,uint b,bool c);[DllImport(""kernel32.dll"")]public static extern uint GetCurrentThreadId();}"

function Click([int]$x,[int]$y) {
    [SE]::SetCursorPos($x,$y)|Out-Null
    Start-Sleep -Milliseconds 150
    [SE]::mouse_event(2,0,0,0,[IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [SE]::mouse_event(4,0,0,0,[IntPtr]::Zero)
    Start-Sleep -Milliseconds 400
    Write-Output "Clicked $x,$y"
}

function FocusHwnd([IntPtr]$h) {
    $t1=0;[SE]::GetWindowThreadProcessId($h,[ref]$t1)|Out-Null
    $t0=[SE]::GetCurrentThreadId()
    [SE]::AttachThreadInput($t0,$t1,$true)|Out-Null
    [SE]::ShowWindow($h,9)|Out-Null
    [SE]::BringWindowToTop($h)|Out-Null
    [SE]::SetForegroundWindow($h)|Out-Null
    [SE]::AttachThreadInput($t0,$t1,$false)|Out-Null
    Start-Sleep -Milliseconds 500
}

function Screenshot([string]$name) {
    $path = "C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$name"
    $bmp = New-Object System.Drawing.Bitmap(1920,1080)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0,0,0,0,[System.Drawing.Size]::new(1920,1080))
    $bmp.Save($path);$g.Dispose();$bmp.Dispose()
    Write-Output "Screenshot: $name"
}

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Error "Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle
Write-Output "Sift2 PID=$($p.Id)"
FocusHwnd $hw

$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$root    = [System.Windows.Automation.AutomationElement]::FromHandle($hw)

function FindDialog {
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") { return $w }
    }
    return $null
}

$dlg = FindDialog
if (-not $dlg) {
    Write-Output "Opening Connections dialog..."
    $cond = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty, "Connections")
    $btn = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
    if (-not $btn) { Write-Error "Connections button not found"; exit 1 }
    $br = $btn.Current.BoundingRectangle
    Click ([int]($br.Left+$br.Width/2)) ([int]($br.Top+$br.Height/2))
    Start-Sleep -Milliseconds 2000
    $dlg = FindDialog
}

if (-not $dlg) { Write-Error "Dialog not found"; Screenshot "dlg_fail.png"; exit 1 }
Write-Output "Dialog: $($dlg.Current.Name)"
$dlgH = [IntPtr]$dlg.Current.NativeWindowHandle
FocusHwnd $dlgH

Screenshot "step1_dialog_open.png"

# --- Find all ComboBoxes (port rows) and CheckBoxes ---
$els = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)

Write-Output "=== Port ComboBoxes ==="
$combos = @()
foreach ($el in $els) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.ComboBox") {
        $br = $el.Current.BoundingRectangle
        $val = ""
        try { $val = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $cx = [int]$br.Left; $cy = [int]$br.Top
        Write-Output ("  Combo val={0} pos={1},{2}" -f $val, $cx, $cy)
        $combos += [PSCustomObject]@{ Val=$val; X=$cx; Y=$cy; El=$el }
    }
}

Write-Output "=== CheckBoxes ==="
$checks = @()
foreach ($el in $els) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.CheckBox") {
        $br = $el.Current.BoundingRectangle
        $st = "Unknown"
        try { $st = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState.ToString() } catch {}
        $cx = [int]$br.Left; $cy = [int]$br.Top
        Write-Output ("  CB name={0} state={1} pos={2},{3}" -f $el.Current.Name, $st, $cx, $cy)
        $checks += [PSCustomObject]@{ Name=$el.Current.Name; State=$st; X=$cx; Y=$cy; El=$el }
    }
}

Write-Output "=== Buttons ==="
foreach ($el in $els) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Button") {
        $br = $el.Current.BoundingRectangle
        $bx=[int]$br.Left;$by=[int]$br.Top
        Write-Output ("  Btn={0} pos={1},{2}" -f $el.Current.Name, $bx, $by)
    }
}
