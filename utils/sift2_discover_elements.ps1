# Dumps all Edit/Text UIA elements in Sift2 main window so we can find
# the UDW command input and output areas.
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class WD { [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
                  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }
"@

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "ERROR: Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle
[WD]::ShowWindow($hw, 9) | Out-Null
[WD]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 800

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)

Write-Output "=== All UIA elements in Sift2 main window ==="
Write-Output "Total: $($all.Count)"
Write-Output ""

foreach ($el in $all) {
    $t   = $el.Current.ControlType.ProgrammaticName
    $n   = $el.Current.Name
    $aid = $el.Current.AutomationId
    $br  = $el.Current.BoundingRectangle

    # Print Edit, ComboBox, and Document types (command input / output candidates)
    if ($t -in @("ControlType.Edit","ControlType.Document","ControlType.Text","ControlType.Custom") `
        -and $br.Width -gt 50) {
        $val = ""
        try { $val = ($el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).Current.Value } catch {}
        Write-Output ("{0,-30} Name=[{1}] Aid=[{2}] Val=[{3}] Rect=({4},{5},{6},{7})" `
            -f $t, $n, $aid, ($val.Substring(0,[Math]::Min(60,$val.Length))),
               [int]$br.Left,[int]$br.Top,[int]$br.Right,[int]$br.Bottom)
    }
}

Write-Output ""
Write-Output "=== All Buttons ==="
foreach ($el in $all) {
    $t = $el.Current.ControlType.ProgrammaticName
    if ($t -eq "ControlType.Button") {
        $br = $el.Current.BoundingRectangle
        Write-Output ("BTN Name=[{0}] Aid=[{1}] Rect=({2},{3})" `
            -f $el.Current.Name, $el.Current.AutomationId,
               [int]$br.Left, [int]$br.Top)
    }
}
