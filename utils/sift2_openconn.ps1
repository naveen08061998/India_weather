Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MW {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int L, T, R, B; }
}
"@

$p = Get-Process sift2
[MW]::ShowWindow($p.MainWindowHandle, 9)  | Out-Null
[MW]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 600

$root = [System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)

function ClickEl($el) {
    $br = $el.Current.BoundingRectangle
    $cx = [int]($br.Left + $br.Width  / 2)
    $cy = [int]($br.Top  + $br.Height / 2)
    [MW]::SetCursorPos($cx, $cy) | Out-Null
    Start-Sleep -Milliseconds 150
    [MW]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [MW]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 400
    Write-Output "Clicked at ($cx, $cy)"
}

function Screenshot($path) {
    $rc = New-Object MW+RECT
    [MW]::GetWindowRect($p.MainWindowHandle, [ref]$rc) | Out-Null
    $w = $rc.R - $rc.L; $h = $rc.B - $rc.T
    $bmp = New-Object System.Drawing.Bitmap($w,$h)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($rc.L,$rc.T,0,0,(New-Object System.Drawing.Size($w,$h)))
    $bmp.Save($path); $g.Dispose(); $bmp.Dispose()
    Write-Output "Screenshot: $path"
}

# ── Find Connections button by scanning all elements ──────────────────────
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)

Write-Output "Total elements: $($all.Count)"
$connBtn = $null
foreach ($el in $all) {
    $aid  = $el.Current.AutomationId
    $n    = $el.Current.Name
    $type = $el.Current.ControlType.ProgrammaticName
    $br   = $el.Current.BoundingRectangle
    # Print ALL elements with non-empty names or IDs containing "connect"
    if ($aid -match "connect" -or $n -match "Connect") {
        Write-Output "MATCH: $type N=[$n] ID=[$aid] Rect=($([int]$br.Left),$([int]$br.Top),$([int]$br.Right),$([int]$br.Bottom))"
        if ($connBtn -eq $null) { $connBtn = $el }
    }
    # Also print buttons with valid bounding rects
    if ($type -eq "ControlType.Button" -and $br.Width -gt 0) {
        Write-Output "BTN: N=[$n] ID=[$aid] Rect=($([int]$br.Left),$([int]$br.Top),$([int]$br.Right),$([int]$br.Bottom))"
    }
}

if ($connBtn) {
    Write-Output "Clicking Connections button..."
    ClickEl $connBtn
} else {
    Write-Output "Not found via UIA - trying by keyboard shortcut Ctrl+K..."
    [MW]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait("^k")
}
Start-Sleep -Milliseconds 1800
Screenshot "C:\Users\ReddyA41\Desktop\AgenticAgent\reports\sift2_after_conn.png"
