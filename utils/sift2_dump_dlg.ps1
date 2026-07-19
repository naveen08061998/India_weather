Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WU6 {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@

$p  = Get-Process sift2
$hw = $p.MainWindowHandle
[WU6]::ShowWindow($hw, 9) | Out-Null
[WU6]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 500

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)

function Click($x, $y) {
    [WU6]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 100
    [WU6]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [WU6]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 200
}

# ── Open Connections dialog ────────────────────────────────────────────────
$scale = 1.25
$cond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.connectionButton')
$connBtn = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
$br = $connBtn.Current.BoundingRectangle
$logX = [int](($br.Left + $br.Width/2) / $scale)
$logY = [int](($br.Top + $br.Height/2) / $scale)
Write-Output "Clicking Connections at logical ($logX,$logY)..."
Click $logX $logY

# ── Find the dialog with retries ───────────────────────────────────────────
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
for ($i = 0; $i -lt 8; $i++) {
    Start-Sleep -Milliseconds 600
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
            $dlg = $w; break
        }
    }
    if ($dlg) { Write-Output "Found at try $i"; break }
    # Also check inside root descendants
    foreach ($w in $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition)) {
        $t2 = $w.Current.ControlType.ProgrammaticName
        $n2 = $w.Current.Name
        if ($t2 -eq "ControlType.Window" -and $n2 -match "Printer|Connect") {
            Write-Output "Found inside root: '$n2'"
            $dlg = $w; break
        }
    }
    if ($dlg) { break }
    Write-Output "Retry $i — not found yet"
}
if ($null -eq $dlg) { Write-Output "Dialog not found after retries"; exit 1 }
Write-Output "Dialog: '$($dlg.Current.Name)' hwnd=$($dlg.Current.NativeWindowHandle)"

# ── Dump ALL dialog elements with bounding rects (logical) ────────────────
$dlgEls = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Elements in dialog: $($dlgEls.Count)"
$checkboxes = @()
foreach ($el in $dlgEls) {
    $type = $el.Current.ControlType.ProgrammaticName
    $n    = $el.Current.Name
    $aid  = $el.Current.AutomationId
    $br2  = $el.Current.BoundingRectangle
    $lx   = [int]($br2.Left   / $scale)
    $ly   = [int]($br2.Top    / $scale)
    $lr   = [int]($br2.Right  / $scale)
    $lb   = [int]($br2.Bottom / $scale)
    $cx   = [int](($br2.Left + $br2.Width/2)  / $scale)
    $cy   = [int](($br2.Top  + $br2.Height/2) / $scale)

    # Print checkboxes with their logical coords
    if ($type -eq "ControlType.CheckBox") {
        $chkVal = ""
        try { $chkVal = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        Write-Output "CHK: N=[$n] ID=[$aid] logical=($lx,$ly,$lr,$lb) center=($cx,$cy) state=$chkVal"
        $checkboxes += $el
    }
    # Print combos (IP address fields)
    if ($type -eq "ControlType.ComboBox" -or $type -eq "ControlType.Edit") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        if ($v -ne "") { Write-Output "EDIT: N=[$n] V=[$v] logical=($lx,$ly,$lr,$lb) center=($cx,$cy)" }
    }
    if ($type -eq "ControlType.Button" -and ($n -match "OK|Cancel|Refresh|Populate")) {
        Write-Output "BTN: N=[$n] logical=($lx,$ly,$lr,$lb) center=($cx,$cy)"
    }
}
