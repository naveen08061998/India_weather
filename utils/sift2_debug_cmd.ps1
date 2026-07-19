# Send a runUw command, screenshot before/after, and dump all elements under the viewport
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class WD3 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c3);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
}
"@

function SS([string]$f) {
    $bmp = New-Object System.Drawing.Bitmap(1920, 1080)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0,0,0,0,[System.Drawing.Size]::new(1920,1080))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$f")
    $g.Dispose(); $bmp.Dispose()
    Write-Output "Screenshot: $f"
}

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle

$siftTid = 0; $myTid = [WD3]::GetCurrentThreadId()
[WD3]::GetWindowThreadProcessId($hw,[ref]$siftTid) | Out-Null
[WD3]::AttachThreadInput($myTid,$siftTid,$true) | Out-Null
[WD3]::ShowWindow($hw,9) | Out-Null; [WD3]::BringWindowToTop($hw) | Out-Null
[WD3]::SetForegroundWindow($hw) | Out-Null
[WD3]::AttachThreadInput($myTid,$siftTid,$false) | Out-Null
Start-Sleep -Milliseconds 800

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)

# -- Send the runUw command --
$inputCond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.textInput.QLineEdit')
$inputEl = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $inputCond)

SS "before_cmd.png"

$inputEl.SetFocus()
Start-Sleep -Milliseconds 300
try {
    ($inputEl.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).SetValue('runUw mainApp "WebSocket PUB_getPingPongStatus 1"')
} catch {}
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 4000

SS "after_cmd.png"
Write-Output "Screenshots saved. Checking viewport children..."

# -- Find the viewport and its children --
$vpCond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.splitter.BufferTabs.qt_tabwidget_stackedwidget.deviceBuffer.qt_scrollarea_viewport')
$vpEl = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $vpCond)

Write-Output "Viewport found: $($null -ne $vpEl)"
if ($vpEl) {
    $vpChildren = $vpEl.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition)
    Write-Output "Viewport descendants: $($vpChildren.Count)"
    foreach ($el in $vpChildren) {
        $t = $el.Current.ControlType.ProgrammaticName
        $n = $el.Current.Name
        $aid = $el.Current.AutomationId
        Write-Output "  $t | Name='$n' | Aid='$aid'"
    }

    # Try clicking inside viewport and then Ctrl+A, Ctrl+C
    $br = $vpEl.Current.BoundingRectangle
    $cx = [int]($br.Left + $br.Width/2); $cy = [int]($br.Top + $br.Height/2)
    Write-Output "Clicking viewport at ($cx,$cy)"
    [WD3]::SetCursorPos($cx,$cy) | Out-Null
    Start-Sleep -Milliseconds 100
    [WD3]::mouse_event(0x0002,0,0,0,[IntPtr]::Zero); Start-Sleep -Milliseconds 60
    [WD3]::mouse_event(0x0004,0,0,0,[IntPtr]::Zero)
    Start-Sleep -Milliseconds 400

    [System.Windows.Forms.Clipboard]::Clear()
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait("^c")
    Start-Sleep -Milliseconds 500

    $clip = [System.Windows.Forms.Clipboard]::GetText()
    Write-Output "Clipboard after Ctrl+A/C (first 600): '$($clip.Substring(0,[Math]::Min(600,$clip.Length)))'"
}
