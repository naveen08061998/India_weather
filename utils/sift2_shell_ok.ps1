Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class W9 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c3);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@

$p    = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "Sift2 not running"; exit 1 }
$hw   = $p.MainWindowHandle
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)

$dlgHwnd = [IntPtr]::Zero
foreach ($el in $all) {
    if ($el.Current.ControlType.ProgrammaticName -eq "ControlType.Window" -and
        $el.Current.Name -match "Printer") {
        $dlgHwnd = [IntPtr]$el.Current.NativeWindowHandle
    }
}
if ($dlgHwnd -eq [IntPtr]::Zero) { Write-Output "No dialog open"; exit 1 }
Write-Output ("Dialog HWND={0}" -f $dlgHwnd)

$t1 = 0
[W9]::GetWindowThreadProcessId($dlgHwnd, [ref]$t1) | Out-Null
$t0 = [W9]::GetCurrentThreadId()
[W9]::AttachThreadInput($t0, $t1, $true)  | Out-Null
[W9]::ShowWindow($dlgHwnd, 9)             | Out-Null
[W9]::BringWindowToTop($dlgHwnd)          | Out-Null
[W9]::SetForegroundWindow($dlgHwnd)       | Out-Null
[W9]::AttachThreadInput($t0, $t1, $false) | Out-Null
Start-Sleep -Milliseconds 700

# Minimize Teams so it can't steal focus
$teams = Get-Process ms-teams -ErrorAction SilentlyContinue
if ($teams) { foreach ($t in $teams) { [W9]::ShowWindow($t.MainWindowHandle, 6) | Out-Null } }
Start-Sleep -Milliseconds 300

# Shell checkbox for 15.77.36.63 row at screen (977, 490)
Write-Output "Clicking Shell at (977,490)..."
[W9]::SetCursorPos(977, 490) | Out-Null
Start-Sleep -Milliseconds 150
[W9]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 100
[W9]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 500

$bmp = New-Object System.Drawing.Bitmap(1536, 864)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\shell_check2.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "SS: shell_check2.png"

# Click OK at (872,744)
Write-Output "Clicking OK at (872,744)..."
[W9]::SetCursorPos(872, 744) | Out-Null
Start-Sleep -Milliseconds 150
[W9]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 100
[W9]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 1500

$bmp2 = New-Object System.Drawing.Bitmap(1536, 864)
$g2   = [System.Drawing.Graphics]::FromImage($bmp2)
$g2.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new(1536, 864))
$bmp2.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\after_ok2.png')
$g2.Dispose(); $bmp2.Dispose()
Write-Output "SS: after_ok2.png"
Write-Output "Done"
