Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition "using System; using System.Runtime.InteropServices; public class W3 { [DllImport(`"user32.dll`")] public static extern bool SetCursorPos(int x, int y); [DllImport(`"user32.dll`")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e); }"

$p       = Get-Process sift2
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg     = $null

foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
        $dlg = $w; break
    }
}
if (-not $dlg) { Write-Output "No dialog found"; exit 1 }
Write-Output "Dialog: $($dlg.Current.Name)"

$els = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Elements: $($els.Count)"
Write-Output ""

$edits  = [System.Collections.Generic.List[PSObject]]::new()
$combos = [System.Collections.Generic.List[PSObject]]::new()
$checks = [System.Collections.Generic.List[PSObject]]::new()

foreach ($el in $els) {
    $t = $el.Current.ControlType.ProgrammaticName
    $b = $el.Current.BoundingRectangle
    if ($b.Width -le 0) { continue }
    $lx = [int](($b.Left + $b.Width  / 2) / 1.25)
    $ly = [int](($b.Top  + $b.Height / 2) / 1.25)
    $n  = $el.Current.Name; $aid = $el.Current.AutomationId

    if ($t -eq "ControlType.CheckBox") {
        $ts = "?"; try { $ts = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        Write-Output ("CHK [{0}] [{1}] log=({2},{3})" -f $n, $ts, $lx, $ly)
        $checks.Add([PSCustomObject]@{N=$n;State=$ts;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly;El=$el})
    }
    if ($t -eq "ControlType.Edit") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        if ($v) { Write-Output ("EDIT [{0}] [{1}] log=({2},{3})" -f $n, $v, $lx, $ly) }
        $edits.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly})
    }
    if ($t -eq "ControlType.ComboBox") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        Write-Output ("COMBO [{0}] [{1}] log=({2},{3})" -f $n, $v, $lx, $ly)
        $combos.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly})
    }
    if ($t -eq "ControlType.Button") {
        Write-Output ("BTN [{0}] log=({1},{2})" -f $n, $lx, $ly)
    }
}

Write-Output ""
Write-Output "==========================================="
Write-Output "  PORT ANALYSIS: Shell(#) and Dart(D)"
Write-Output "==========================================="

$rowBands = $checks | Group-Object { [int]($_.PhyT / 30) } | Sort-Object { [int]$_.Name }
foreach ($band in $rowBands) {
    $rchks = $band.Group | Sort-Object { $_.PhyL }
    $rY    = ($rchks | Measure-Object -Property PhyT -Average).Average
    $re    = $edits  | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1
    $rc    = $combos | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1
    $port  = if ($re) { $re.Val } elseif ($rc) { $rc.Val } else { "<empty>" }
    $shellChk = $rchks | Where-Object { $_.N -match "Shell" } | Select-Object -First 1
    $dartChk  = $rchks | Where-Object { $_.N -match "Dart"  } | Select-Object -First 1
    $tag = ""
    if ($shellChk -and $shellChk.State -eq "On") { $tag += "  <<< SHELL (#) PORT" }
    if ($dartChk  -and $dartChk.State  -eq "On") { $tag += "  <<< DART (D) PORT" }
    $chkStr = ($rchks | ForEach-Object { ("{0}=[{1}]" -f $_.N, $_.State) }) -join "  "
    Write-Output ("  Port=[{0}]{1}" -f $port, $tag)
    Write-Output ("    {0}" -f $chkStr)
    Write-Output ""
}
Write-Output "Dialog still open - ready to configure."
