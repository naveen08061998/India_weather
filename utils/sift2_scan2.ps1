Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool AllowSetForegroundWindow(int pid);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int pid);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint tid, uint tid2, bool attach);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@

$p  = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) {
    Write-Output "Launching Sift2..."
    Start-Process "C:\Program Files\Sift2\sift2.exe"
    Start-Sleep -Seconds 4
    $p = Get-Process sift2
}
$hw = $p.MainWindowHandle
Write-Output "Sift2 PID=$($p.Id) HWND=$hw"

# -- Step 1: Force Sift2 to front --
[Win32]::AllowSetForegroundWindow($p.Id) | Out-Null
[Win32]::ShowWindow($hw, 9)  | Out-Null  # SW_RESTORE
[Win32]::ShowWindow($hw, 5)  | Out-Null  # SW_SHOW
[Win32]::BringWindowToTop($hw) | Out-Null

# Attach to Sift2 thread input so SetForegroundWindow works cross-thread
$siftTid = 0
[Win32]::GetWindowThreadProcessId($hw, [ref]$siftTid) | Out-Null
$myTid   = [Win32]::GetCurrentThreadId()
[Win32]::AttachThreadInput($myTid, $siftTid, $true) | Out-Null
[Win32]::SetForegroundWindow($hw) | Out-Null
[Win32]::BringWindowToTop($hw) | Out-Null
[Win32]::AttachThreadInput($myTid, $siftTid, $false) | Out-Null
Start-Sleep -Milliseconds 800

# -- Step 2: Screenshot to verify Sift2 is in front --
$bmp = New-Object System.Drawing.Bitmap(1536, 864)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\before_conn.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "Screenshot: before_conn.png"

# -- Step 3: Find Connections button via UIA, click via mouse --
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$ac   = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
            'QApplication.SiftWindow.centralWidget.connectionButton')
$btn  = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $ac)
if (-not $btn) { Write-Output "ERROR: Connections button not found"; exit 1 }

$br  = $btn.Current.BoundingRectangle
# Use physical UIA coords directly with mouse_event (MOUSEEVENTF_ABSOLUTE uses normalised 0-65535)
# But easier: just use SetCursorPos with logical coords (scale=1.25)
$logCX = [int](($br.Left + $br.Width  / 2) / 1.25)
$logCY = [int](($br.Top  + $br.Height / 2) / 1.25)
Write-Output "Connections button logical center: ($logCX, $logCY)"

[Win32]::SetCursorPos($logCX, $logCY) | Out-Null
Start-Sleep -Milliseconds 200
[Win32]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)  # MOUSEEVENTF_LEFTDOWN
Start-Sleep -Milliseconds 100
[Win32]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)  # MOUSEEVENTF_LEFTUP
Start-Sleep -Milliseconds 300
Write-Output "Button clicked."

# -- Step 4: Wait for Printer Connections dialog --
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Milliseconds 400
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
            [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
            $dlg = $w; break
        }
    }
    if ($dlg) { Write-Output "Dialog found at try $i"; break }
    Write-Output "  waiting ($i)..."
}

if (-not $dlg) {
    # Screenshot to see what happened
    $bmp2 = New-Object System.Drawing.Bitmap(1536, 864)
    $g2   = [System.Drawing.Graphics]::FromImage($bmp2)
    $g2.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
    $bmp2.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\after_conn_fail.png')
    $g2.Dispose(); $bmp2.Dispose()
    Write-Output "Dialog not found. Screenshot: after_conn_fail.png"
    exit 1
}

Write-Output "Dialog: '$($dlg.Current.Name)'"

# Screenshot with dialog open
$bmp3 = New-Object System.Drawing.Bitmap(1536, 864)
$g3   = [System.Drawing.Graphics]::FromImage($bmp3)
$g3.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp3.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\conn_open.png')
$g3.Dispose(); $bmp3.Dispose()
Write-Output "Screenshot: conn_open.png"

# -- Step 5: Read all dialog elements --
$els    = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
              [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Dialog elements: $($els.Count)"
Write-Output ""

$edits  = [System.Collections.Generic.List[PSObject]]::new()
$combos = [System.Collections.Generic.List[PSObject]]::new()
$checks = [System.Collections.Generic.List[PSObject]]::new()

foreach ($el in $els) {
    $t    = $el.Current.ControlType.ProgrammaticName
    $n    = $el.Current.Name
    $aid  = $el.Current.AutomationId
    $b    = $el.Current.BoundingRectangle
    if ($b.Width -le 0) { continue }
    $lx   = [int](($b.Left + $b.Width  / 2) / 1.25)
    $ly   = [int](($b.Top  + $b.Height / 2) / 1.25)
    $phyT = [int]$b.Top
    $phyL = [int]$b.Left

    if ($t -eq "ControlType.Edit") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $edits.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=$phyT;PhyL=$phyL;LX=$lx;LY=$ly})
        Write-Output "EDIT  N=[$n] V=[$v] log=($lx,$ly)"
    }
    if ($t -eq "ControlType.ComboBox") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $combos.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=$phyT;PhyL=$phyL;LX=$lx;LY=$ly})
        Write-Output "COMBO N=[$n] V=[$v] log=($lx,$ly)"
    }
    if ($t -eq "ControlType.CheckBox") {
        $ts = "?"; try { $ts = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        $checks.Add([PSCustomObject]@{N=$n;State=$ts;PhyT=$phyT;PhyL=$phyL;LX=$lx;LY=$ly;El=$el;Aid=$aid})
        Write-Output "CHK   N=[$n] St=[$ts] log=($lx,$ly) id=[$aid]"
    }
    if ($t -eq "ControlType.Button") {
        Write-Output "BTN   N=[$n] log=($lx,$ly)"
    }
}

# -- Step 6: Port analysis --
Write-Output ""
Write-Output "==========================================="
Write-Output "  PORT ANALYSIS: Shell(#) and Dart(D)"
Write-Output "==========================================="

$rowBands = $checks | Group-Object { [int]($_.PhyT / 30) } | Sort-Object { [int]$_.Name }
foreach ($band in $rowBands) {
    $rchks = $band.Group | Sort-Object { $_.PhyL }
    $rY    = ($rchks | Measure-Object -Property PhyT -Average).Average

    $re = $edits  | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1
    $rc = $combos | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1

    $port   = if ($re) { $re.Val } elseif ($rc) { $rc.Val } else { "<empty>" }
    $prefix = if ($rc) { $rc.Val } else { "" }

    $shellChk = $rchks | Where-Object { $_.N -match "Shell" } | Select-Object -First 1
    $dartChk  = $rchks | Where-Object { $_.N -match "Dart"  } | Select-Object -First 1

    $tag = ""
    if ($shellChk -and $shellChk.State -eq "On") { $tag += " <<< SHELL (#) PORT" }
    if ($dartChk  -and $dartChk.State  -eq "On") { $tag += " <<< DART (D) PORT"  }

    $chkStr = ($rchks | ForEach-Object { "$($_.N)=[$($_.State)]" }) -join "  "
    Write-Output "  Port=[$port] Prefix=[$prefix]$tag"
    Write-Output "    $chkStr"
    Write-Output ""
}
Write-Output "Scan complete. Dialog is still open."
