Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class W5 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
}
"@

function Click([int]$x, [int]$y) {
    [W5]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [W5]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [W5]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 250
}

function SS([string]$f) {
    $bmp = New-Object System.Drawing.Bitmap(1536, 864)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$f")
    $g.Dispose(); $bmp.Dispose()
    Write-Output "Screenshot: $f"
}

$p  = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2not running"; exit 1 }
$hw = $p.MainWindowHandle

[W5]::ShowWindow($hw, 9) | Out-Null
[W5]::BringWindowToTop($hw) | Out-Null
[W5]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 800

# -- Search for dialog as DESCENDANT of root window (Qt modal dialogs are children) --
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Root descendants: $($all.Count)"

$dlg = $null
foreach ($el in $all) {
    $t = $el.Current.ControlType.ProgrammaticName
    $n = $el.Current.Name
    if ($t -eq "ControlType.Window") {
        Write-Output ("Found child window: Name=[{0}] Aid=[{1}]" -f $n, $el.Current.AutomationId)
        if ($n -match "Printer|Connection") { $dlg = $el }
    }
}

# Also try desktop top-level
if (-not $dlg) {
    $desktop = [System.Windows.Automation.AutomationElement]::RootElement
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
            [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
            Write-Output ("Desktop child: Name=[{0}]" -f $w.Current.Name)
            $dlg = $w
        }
    }
}

SS "dlg_search.png"

if (-not $dlg) {
    Write-Output "Dialog not found in UIA - clicking Connections button to open it..."

    # Find Connections button in root descendants
    $connBtn = $null
    foreach ($el in $all) {
        if ($el.Current.AutomationId -match "connectionButton") { $connBtn = $el; break }
    }

    if (-not $connBtn) {
        Write-Output "Button not found either - opening by click at physical (1732,1005) [no scale]..."
        # UIA returns physical coords, SetCursorPos takes logical. DPI=96 so scale=1 on this system.
        Click 1732 1005
    } else {
        $br  = $connBtn.Current.BoundingRectangle
        $phX = [int]($br.Left + $br.Width  / 2)
        $phY = [int]($br.Top  + $br.Height / 2)
        Write-Output ("Button at physical ({0},{1}) - clicking..." -f $phX, $phY)
        Click $phX $phY
    }

    Start-Sleep -Milliseconds 2000
    SS "after_open.png"

    # Re-search for dialog
    $root2 = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
    $all2  = $root2.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all2) {
        if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window") {
            $n = $el.Current.Name
            Write-Output ("Child window: [{0}]" -f $n)
            if ($n -match "Printer|Connection") { $dlg = $el }
        }
    }
    $desktop2 = [System.Windows.Automation.AutomationElement]::RootElement
    foreach ($w in $desktop2.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") { $dlg = $w }
    }
}

if (-not $dlg) { Write-Output "ERROR: Cannot find Printer Connections dialog"; exit 1 }
Write-Output ("DIALOG: [{0}]" -f $dlg.Current.Name)

# -- Read all elements in dialog --
$els    = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
Write-Output ("Dialog elements: {0}" -f $els.Count)

$edits  = [System.Collections.Generic.List[PSObject]]::new()
$combos = [System.Collections.Generic.List[PSObject]]::new()
$checks = [System.Collections.Generic.List[PSObject]]::new()

foreach ($el in $els) {
    $t = $el.Current.ControlType.ProgrammaticName
    $b = $el.Current.BoundingRectangle
    if ($b.Width -le 0) { continue }
    # Use physical coords as-is (DPI=96 so physical=logical)
    $cx = [int]($b.Left + $b.Width  / 2)
    $cy = [int]($b.Top  + $b.Height / 2)
    $n  = $el.Current.Name

    if ($t -eq "ControlType.CheckBox") {
        $ts = "Off"; try { $ts = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        $checks.Add([PSCustomObject]@{N=$n;State=$ts;PhyT=[int]$b.Top;PhyL=[int]$b.Left;CX=$cx;CY=$cy;El=$el})
        Write-Output ("CHK [{0}] [{1}] ctr=({2},{3})" -f $n, $ts, $cx, $cy)
    }
    if ($t -eq "ControlType.Edit") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $edits.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;CX=$cx;CY=$cy})
        if ($v) { Write-Output ("EDIT [{0}] [{1}] ctr=({2},{3})" -f $n, $v, $cx, $cy) }
    }
    if ($t -eq "ControlType.ComboBox") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $combos.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;CX=$cx;CY=$cy})
        Write-Output ("COMBO [{0}] [{1}] ctr=({2},{3})" -f $n, $v, $cx, $cy)
    }
    if ($t -eq "ControlType.Button") {
        Write-Output ("BTN [{0}] ctr=({1},{2})" -f $n, $cx, $cy)
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
Write-Output "Dialog is still open."
