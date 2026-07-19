Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition "using System; using System.Runtime.InteropServices; public class SUA { [DllImport(`"user32.dll`")] public static extern bool ShowWindow(IntPtr h, int c); [DllImport(`"user32.dll`")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport(`"user32.dll`")] public static extern bool SetCursorPos(int x, int y); [DllImport(`"user32.dll`")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e); }"

function Click([int]$x, [int]$y) {
    [SUA]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 100
    [SUA]::mouse_event(2, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 70
    [SUA]::mouse_event(4, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 250
}

$SC = 1.25
function L([double]$v) { [int]($v / $SC) }

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) {
    Write-Output "Launching Sift2..."
    Start-Process "C:\Program Files\Sift2\sift2.exe"
    Start-Sleep -Seconds 4
    $p = Get-Process sift2 -ErrorAction SilentlyContinue
    if (-not $p) { Write-Output "ERROR: Sift2 not found"; exit 1 }
}
$hw = $p.MainWindowHandle
Write-Output "Sift2 PID=$($p.Id)"
[SUA]::ShowWindow($hw, 9) | Out-Null
[SUA]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 700

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$ac = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.connectionButton')
$connBtn = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $ac)
if (-not $connBtn) { Write-Output "ERROR: connectionButton not found"; exit 1 }

$br = $connBtn.Current.BoundingRectangle
$cx = L($br.Left + $br.Width / 2)
$cy = L($br.Top + $br.Height / 2)
Write-Output "Clicking Connections button at logical ($cx, $cy)..."
Click $cx $cy

$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Milliseconds 400
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
            $dlg = $w; break
        }
    }
    if ($dlg) { break }
    Write-Output "  waiting... ($i)"
}
if (-not $dlg) { Write-Output "ERROR: dialog not found"; exit 1 }
Write-Output "Dialog opened: '$($dlg.Current.Name)'"

$bmp = New-Object System.Drawing.Bitmap(1536, 864)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\conn_dialog.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "Screenshot: conn_dialog.png"

$els = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Total dialog elements: $($els.Count)"

$edits  = New-Object System.Collections.Generic.List[PSObject]
$combos = New-Object System.Collections.Generic.List[PSObject]
$checks = New-Object System.Collections.Generic.List[PSObject]

Write-Output ""
foreach ($el in $els) {
    $t   = $el.Current.ControlType.ProgrammaticName
    $n   = $el.Current.Name
    $aid = $el.Current.AutomationId
    $b   = $el.Current.BoundingRectangle
    if ($b.Width -le 0) { continue }
    $lx   = L($b.Left + $b.Width  / 2)
    $ly   = L($b.Top  + $b.Height / 2)
    $phyT = [int]$b.Top
    $phyL = [int]$b.Left

    if ($t -eq "ControlType.Edit") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        Write-Output "EDIT  N=[$n] V=[$v] Lctr=($lx,$ly)"
        $edits.Add([PSCustomObject]@{Name=$n;Value=$v;PhyT=$phyT;PhyL=$phyL;LogCX=$lx;LogCY=$ly})
    }
    if ($t -eq "ControlType.ComboBox") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        Write-Output "COMBO N=[$n] V=[$v] Lctr=($lx,$ly)"
        $combos.Add([PSCustomObject]@{Name=$n;Value=$v;PhyT=$phyT;PhyL=$phyL;LogCX=$lx;LogCY=$ly})
    }
    if ($t -eq "ControlType.CheckBox") {
        $ts = "Unknown"; try { $ts = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        Write-Output "CHK   N=[$n] State=[$ts] Lctr=($lx,$ly) Aid=[$aid]"
        $checks.Add([PSCustomObject]@{Name=$n;State=$ts;PhyT=$phyT;PhyL=$phyL;LogCX=$lx;LogCY=$ly;El=$el})
    }
    if ($t -eq "ControlType.Button") {
        Write-Output "BTN   N=[$n] Lctr=($lx,$ly)"
    }
}

Write-Output ""
Write-Output "==========================================="
Write-Output "  PORT ANALYSIS: Shell(#) and Dart(D)"
Write-Output "==========================================="

$rowBands = $checks | Group-Object { [int]($_.PhyT / 30) } | Sort-Object { [int]$_.Name }

foreach ($band in $rowBands) {
    $rchks  = $band.Group | Sort-Object { $_.PhyL }
    $rY     = ($rchks | Measure-Object -Property PhyT -Average).Average

    $redit  = $edits  | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1
    $rcombo = $combos | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1

    $port   = if ($redit) { $redit.Value } elseif ($rcombo) { $rcombo.Value } else { "<empty>" }
    $prefix = if ($rcombo) { $rcombo.Value } else { "" }

    $chkStr = ($rchks | ForEach-Object { "$($_.Name)=[$($_.State)]" }) -join "  "

    $shellChk = $rchks | Where-Object { $_.Name -match "Shell" } | Select-Object -First 1
    $dartChk  = $rchks | Where-Object { $_.Name -match "Dart"  } | Select-Object -First 1

    $tag = ""
    if ($shellChk -and $shellChk.State -eq "On") { $tag += " <<< SHELL(#) PORT" }
    if ($dartChk  -and $dartChk.State  -eq "On") { $tag += " <<< DART(D) PORT" }

    Write-Output "  Port=[$port] Prefix=[$prefix]$tag"
    Write-Output "    $chkStr"
}
Write-Output ""
Write-Output "Scan complete. Dialog is still open."
