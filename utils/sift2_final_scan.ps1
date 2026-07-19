Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class W4 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@

function Click([int]$x, [int]$y) {
    [W4]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [W4]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [W4]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 200
}

function SS([string]$name) {
    $bmp = New-Object System.Drawing.Bitmap(1536, 864)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$name")
    $g.Dispose(); $bmp.Dispose()
    Write-Output "SS: $name"
}

$p  = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) {
    Write-Output "Launching Sift2..."
    Start-Process "C:\Program Files\Sift2\sift2.exe"
    Start-Sleep -Seconds 5
    $p = Get-Process sift2
}
$hw = $p.MainWindowHandle

# Bring Sift2 to front using AttachThreadInput
$siftTid = 0
[W4]::GetWindowThreadProcessId($hw, [ref]$siftTid) | Out-Null
$myTid = [W4]::GetCurrentThreadId()
[W4]::AttachThreadInput($myTid, $siftTid, $true) | Out-Null
[W4]::ShowWindow($hw, 9) | Out-Null
[W4]::BringWindowToTop($hw) | Out-Null
[W4]::SetForegroundWindow($hw) | Out-Null
[W4]::AttachThreadInput($myTid, $siftTid, $false) | Out-Null
Start-Sleep -Milliseconds 1000

SS "scan_before.png"

# Check if dialog is already open
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") { $dlg = $w; break }
}

if ($dlg) {
    Write-Output "Dialog already open: '$($dlg.Current.Name)'"
} else {
    Write-Output "Clicking Connections button at logical (1386, 804)..."
    Click 1386 804
    Start-Sleep -Milliseconds 500

    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Milliseconds 400
        foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
            if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") { $dlg = $w; break }
        }
        if ($dlg) { Write-Output "Dialog found at try $i"; break }
        Write-Output "  wait $i"
    }
    if (-not $dlg) { SS "scan_nodlg.png"; Write-Output "ERROR: dialog not found"; exit 1 }
}

SS "scan_dlg_open.png"
Write-Output "Dialog: '$($dlg.Current.Name)'"

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
    $n  = $el.Current.Name

    if ($t -eq "ControlType.CheckBox") {
        $ts = "?"; try { $ts = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        Write-Output ("CHK [{0}] St=[{1}] log=({2},{3})" -f $n, $ts, $lx, $ly)
        $checks.Add([PSCustomObject]@{N=$n;State=$ts;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly;El=$el})
    }
    if ($t -eq "ControlType.Edit") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $edits.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly})
        if ($v) { Write-Output ("EDIT [{0}] [{1}] log=({2},{3})" -f $n, $v, $lx, $ly) }
    }
    if ($t -eq "ControlType.ComboBox") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $combos.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly})
        Write-Output ("COMBO [{0}] [{1}] log=({2},{3})" -f $n, $v, $lx, $ly)
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
    if ($dartChk  -and $dartChk.State  -eq "On") { $tag += "  <<< DART (D) PORT"  }
    $chkStr = ($rchks | ForEach-Object { ("{0}=[{1}]" -f $_.N, $_.State) }) -join "  "
    Write-Output ("  Port=[{0}]{1}" -f $port, $tag)
    Write-Output ("    {0}" -f $chkStr)
    Write-Output ""
}
Write-Output "Scan complete. Dialog remains open."
