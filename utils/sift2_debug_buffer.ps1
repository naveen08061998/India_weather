# Diagnose the deviceBuffer and textInput after sending a UDW command
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class WD2 { [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
                   [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }
"@

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle
[WD2]::ShowWindow($hw, 9) | Out-Null
[WD2]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 600

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)

# --- Find deviceBuffer ---
$bufCond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.splitter.BufferTabs.qt_tabwidget_stackedwidget.deviceBuffer')
$bufEl = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $bufCond)

if (-not $bufEl) { Write-Output "deviceBuffer NOT found"; exit 1 }
Write-Output "deviceBuffer found: ControlType=$($bufEl.Current.ControlType.ProgrammaticName)"

# --- Try ValuePattern ---
try {
    $vp = $bufEl.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    Write-Output "ValuePattern value: '$($vp.Current.Value.Substring(0, [Math]::Min(200, $vp.Current.Value.Length)))'"
} catch { Write-Output "No ValuePattern: $_" }

# --- Try TextPattern ---
try {
    $tp = $bufEl.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
    $range = $tp.DocumentRange
    $text = $range.GetText(-1)
    Write-Output "TextPattern text (first 500): '$($text.Substring(0, [Math]::Min(500, $text.Length)))'"
} catch { Write-Output "No TextPattern: $_" }

# --- Enumerate children ---
$children = $bufEl.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Direct children: $($children.Count)"
foreach ($c in $children) {
    Write-Output "  Child: Type=$($c.Current.ControlType.ProgrammaticName) Name='$($c.Current.Name)' Aid='$($c.Current.AutomationId)'"
    try {
        $cv = ($c.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).Current.Value
        Write-Output "    Value: '$($cv.Substring(0, [Math]::Min(100, $cv.Length)))'"
    } catch {}
}

# --- Dump all descendants ---
$all = $bufEl.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Total descendants: $($all.Count)"
foreach ($el in $all) {
    $t = $el.Current.ControlType.ProgrammaticName
    $n = $el.Current.Name
    $aid = $el.Current.AutomationId
    if ($n -or $aid) {
        Write-Output "  $t Name='$n' Aid='$aid'"
    }
}

# ---- Now send a command and re-check ----
Write-Output ""
Write-Output "=== Sending command ==="
$inputCond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.textInput.QLineEdit')
$inputEl = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $inputCond)
if (-not $inputEl) { Write-Output "Input not found"; exit 1 }

$inputEl.SetFocus()
Start-Sleep -Milliseconds 300
try {
    $vp = $inputEl.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    $vp.SetValue("WebSocket PUB_getPingPongStatus 1")
    Write-Output "SetValue succeeded"
} catch {
    Write-Output "SetValue failed, using SendKeys"
    [System.Windows.Forms.SendKeys]::SendWait("^a{DELETE}")
    Start-Sleep -Milliseconds 100
    foreach ($ch in "WebSocket PUB_getPingPongStatus 1".ToCharArray()) {
        [System.Windows.Forms.SendKeys]::SendWait([string]$ch)
    }
}
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 3000

Write-Output "=== After command - deviceBuffer ==="
try {
    $vp2 = $bufEl.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    Write-Output "ValuePattern (last 500): '$($vp2.Current.Value.Substring([Math]::Max(0,$vp2.Current.Value.Length-500)))'"
} catch { Write-Output "No ValuePattern after cmd" }
try {
    $tp2 = $bufEl.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
    $text2 = $tp2.DocumentRange.GetText(-1)
    Write-Output "TextPattern (last 500): '$($text2.Substring([Math]::Max(0,$text2.Length-500)))'"
} catch { Write-Output "No TextPattern after cmd" }
