Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WU3 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    public struct RECT { public int L, T, R, B; }
}
"@

$p  = Get-Process sift2
$hw = $p.MainWindowHandle

# Restore and foreground
[WU3]::ShowWindow($hw, 9) | Out-Null
Start-Sleep -Milliseconds 500
[WU3]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 500

$rc = New-Object WU3+RECT
[WU3]::GetWindowRect($hw, [ref]$rc) | Out-Null
Write-Output "Window logical rect: ($($rc.L),$($rc.T),$($rc.R),$($rc.B))"

# ── Scale factor: physical desktop 1920x1080, logical 1536x864, scale=1.25 ─
# UIA BoundingRectangle = physical pixels.  SetCursorPos = logical pixels.
# Connections btn physical center: (1732, 1005) → logical: (1386, 804)
$scale = 1.25
$root  = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$all   = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
             [System.Windows.Automation.Condition]::TrueCondition)

$connBtn = $null
foreach ($el in $all) {
    if ($el.Current.AutomationId -match "connectionButton") { $connBtn = $el; break }
}

if ($null -eq $connBtn) { Write-Output "connectionButton not found"; exit 1 }

$br   = $connBtn.Current.BoundingRectangle
$phyX = [int]($br.Left + $br.Width  / 2)
$phyY = [int]($br.Top  + $br.Height / 2)
$logX = [int]($phyX / $scale)
$logY = [int]($phyY / $scale)
Write-Output "Connections btn physical=($phyX,$phyY) logical=($logX,$logY)"

# Click at logical coordinates
[WU3]::SetCursorPos($logX, $logY) | Out-Null
Start-Sleep -Milliseconds 200
[WU3]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 100
[WU3]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 2000

# Screenshot to check if dialog opened
$bmp = New-Object System.Drawing.Bitmap(1536, 864)
$g   = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size(1536, 864)))
$bmp.Save('C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_conn_click.png')
$g.Dispose(); $bmp.Dispose()
Write-Output "Screenshot: sift2_conn_click.png"

# Check for dialog via UIA on desktop
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w.Current.ProcessId -eq $p.Id) {
        Write-Output "Sift2 window: '$($w.Current.Name)' ($($w.Current.ControlType.ProgrammaticName))"
    }
}
