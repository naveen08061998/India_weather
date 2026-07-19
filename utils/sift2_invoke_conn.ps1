Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition "using System; using System.Runtime.InteropServices; public class SUA3 { [DllImport(`"user32.dll`")] public static extern bool ShowWindow(IntPtr h, int c); [DllImport(`"user32.dll`")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport(`"user32.dll`")] public static extern bool SetCursorPos(int x, int y); [DllImport(`"user32.dll`")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e); }"

$p  = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle
[SUA3]::ShowWindow($hw, 9)  | Out-Null
[SUA3]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 900

$bmp = New-Object System.Drawing.Bitmap(1536, 864)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_state.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "Screenshot: sift2_state.png"

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$c    = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
            'QApplication.SiftWindow.centralWidget.connectionButton')
$btn  = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $c)

if (-not $btn) { Write-Output "Button not found"; exit 1 }

$br = $btn.Current.BoundingRectangle
Write-Output "Button physical BoundingRect: L=$([int]$br.Left) T=$([int]$br.Top) R=$([int]$br.Right) B=$([int]$br.Bottom)"

# Try InvokePattern first
try {
    $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
    Write-Output "InvokePattern: success"
} catch {
    Write-Output "InvokePattern failed: $_"
    # Fallback: mouse click at physical-to-logical coords (scale=1.25)
    $cx = [int](($br.Left + $br.Width  / 2) / 1.25)
    $cy = [int](($br.Top  + $br.Height / 2) / 1.25)
    Write-Output "Mouse click at logical ($cx, $cy)..."
    [SUA3]::SetCursorPos($cx, $cy) | Out-Null
    Start-Sleep -Milliseconds 120
    [SUA3]::mouse_event(2, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [SUA3]::mouse_event(4, 0, 0, 0, [IntPtr]::Zero)
}

Start-Sleep -Milliseconds 2000
$bmp2 = New-Object System.Drawing.Bitmap(1536, 864)
$g2   = [System.Drawing.Graphics]::FromImage($bmp2)
$g2.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp2.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_after_invoke.png')
$g2.Dispose(); $bmp2.Dispose()
Write-Output "Screenshot: sift2_after_invoke.png"

$desktop = [System.Windows.Automation.AutomationElement]::RootElement
foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w.Current.ProcessId -eq $p.Id) {
        Write-Output "Window: '$($w.Current.Name)' type=$($w.Current.ControlType.ProgrammaticName)"
    }
}
