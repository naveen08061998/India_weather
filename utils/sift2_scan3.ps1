Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class W32 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int pid2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) {
    Write-Output "Launching Sift2..."
    Start-Process "C:\Program Files\Sift2\sift2.exe"
    Start-Sleep -Seconds 5
    $p = Get-Process sift2
}
$hw = $p.MainWindowHandle
Write-Output "Sift2 PID=$($p.Id) HWND=$hw"

# -- Step 1: Press Win+D to show desktop, then restore Sift2 --
[System.Windows.Forms.SendKeys]::SendWait("^{ESC}")   # clear any Start menu first
Start-Sleep -Milliseconds 300
Add-Type -TypeDefinition "using System; using System.Runtime.InteropServices; public class KE { [DllImport(`"user32.dll`")] public static extern void keybd_event(byte k, byte s, uint f, IntPtr e); }"
# Win+D = minimize all
[KE]::keybd_event(0x5B, 0, 0, [IntPtr]::Zero)   # VK_LWIN down
[KE]::keybd_event(0x44, 0, 0, [IntPtr]::Zero)   # 'D' down
[KE]::keybd_event(0x44, 0, 1, [IntPtr]::Zero)   # 'D' up
[KE]::keybd_event(0x5B, 0, 2, [IntPtr]::Zero)   # VK_LWIN up
Start-Sleep -Milliseconds 700

# Restore Sift2
$siftTid = 0
[W32]::GetWindowThreadProcessId($hw, [ref]$siftTid) | Out-Null
$myTid = [W32]::GetCurrentThreadId()
[W32]::AttachThreadInput($myTid, $siftTid, $true) | Out-Null
[W32]::ShowWindow($hw, 9)  | Out-Null
[W32]::BringWindowToTop($hw) | Out-Null
[W32]::SetForegroundWindow($hw) | Out-Null
[W32]::AttachThreadInput($myTid, $siftTid, $false) | Out-Null
Start-Sleep -Milliseconds 1000

# Screenshot to confirm Sift2 is visible
$bmp = New-Object System.Drawing.Bitmap(1536, 864)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_front.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "Screenshot: sift2_front.png"

# -- Step 2: Find Connections button by scanning all elements --
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$allEls = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Total UIA elements: $($allEls.Count)"

$connBtn = $null
foreach ($el in $allEls) {
    $aid = $el.Current.AutomationId
    $nm  = $el.Current.Name
    $t   = $el.Current.ControlType.ProgrammaticName
    if (($aid -match "connectionButton" -or $nm -eq "Connections") -and $t -eq "ControlType.Button") {
        $br  = $el.Current.BoundingRectangle
        Write-Output "Found button: N=[$nm] ID=[$aid] Phy=($([int]$br.Left),$([int]$br.Top),$([int]$br.Right),$([int]$br.Bottom))"
        $connBtn = $el; break
    }
}

if (-not $connBtn) {
    Write-Output "Connections button NOT found. Listing all buttons:"
    foreach ($el in $allEls) {
        if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Button") {
            $br = $el.Current.BoundingRectangle
            if ($br.Width -gt 0) {
                Write-Output "  BTN N=[$($el.Current.Name)] ID=[$($el.Current.AutomationId)] Phy=($([int]$br.Left),$([int]$br.Top))"
            }
        }
    }
    exit 1
}

# -- Step 3: Click the Connections button --
$br   = $connBtn.Current.BoundingRectangle
$logX = [int](($br.Left + $br.Width  / 2) / 1.25)
$logY = [int](($br.Top  + $br.Height / 2) / 1.25)
Write-Output "Clicking at logical ($logX, $logY)..."
[W32]::SetCursorPos($logX, $logY) | Out-Null
Start-Sleep -Milliseconds 200
[W32]::mouse_event(2, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 100
[W32]::mouse_event(4, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 300
Write-Output "Clicked."

# -- Step 4: Wait for dialog --
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 400
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
            [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
            $dlg = $w; break
        }
    }
    if ($dlg) { Write-Output "Dialog found at try $i"; break }
    if ($i -eq 5) { Write-Output "  (still waiting - retrying click)"; [W32]::mouse_event(2,0,0,0,[IntPtr]::Zero); Start-Sleep -ms 100; [W32]::mouse_event(4,0,0,0,[IntPtr]::Zero) }
    Write-Output "  wait $i"
}

if (-not $dlg) {
    $bmp2 = New-Object System.Drawing.Bitmap(1536, 864)
    $g2   = [System.Drawing.Graphics]::FromImage($bmp2)
    $g2.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
    $bmp2.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\conn_fail2.png')
    $g2.Dispose(); $bmp2.Dispose()
    Write-Output "Dialog not found. Screenshot: conn_fail2.png"; exit 1
}

Write-Output "Dialog: '$($dlg.Current.Name)'"
$bmp3 = New-Object System.Drawing.Bitmap(1536, 864)
$g3   = [System.Drawing.Graphics]::FromImage($bmp3)
$g3.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp3.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\conn_open2.png')
$g3.Dispose(); $bmp3.Dispose()
Write-Output "Screenshot: conn_open2.png"

# -- Step 5: Read dialog elements --
$els    = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Elements: $($els.Count)"

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

    if ($t -eq "ControlType.Edit") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $edits.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly})
        Write-Output "EDIT  [$n] V=[$v] log=($lx,$ly)"
    }
    if ($t -eq "ControlType.ComboBox") {
        $v = ""; try { $v = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        $combos.Add([PSCustomObject]@{N=$n;Val=$v;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly})
        Write-Output "COMBO [$n] V=[$v] log=($lx,$ly)"
    }
    if ($t -eq "ControlType.CheckBox") {
        $ts = "?"; try { $ts = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch {}
        $checks.Add([PSCustomObject]@{N=$n;State=$ts;PhyT=[int]$b.Top;PhyL=[int]$b.Left;LX=$lx;LY=$ly;El=$el;Aid=$aid})
        Write-Output "CHK   [$n] St=[$ts] log=($lx,$ly)"
    }
    if ($t -eq "ControlType.Button") { Write-Output "BTN   [$n] log=($lx,$ly)" }
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
    $re    = $edits  | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1
    $rc    = $combos | Where-Object { [Math]::Abs($_.PhyT - $rY) -lt 25 } | Sort-Object PhyL | Select-Object -First 1
    $port  = if ($re) { $re.Val } elseif ($rc) { $rc.Val } else { "<empty>" }
    $prefix= if ($rc) { $rc.Val } else { "" }
    $shellChk = $rchks | Where-Object { $_.N -match "Shell" } | Select-Object -First 1
    $dartChk  = $rchks | Where-Object { $_.N -match "Dart"  } | Select-Object -First 1
    $tag = ""
    if ($shellChk -and $shellChk.State -eq "On") { $tag += " <<< SHELL (#) PORT" }
    if ($dartChk  -and $dartChk.State  -eq "On") { $tag += " <<< DART (D) PORT" }
    $chkStr = ($rchks | ForEach-Object { "$($_.N)=[$($_.State)]" }) -join "  "
    Write-Output "  Port=[$port] Prefix=[$prefix]$tag"
    Write-Output "    $chkStr"
    Write-Output ""
}
Write-Output "Scan complete - dialog still open."
