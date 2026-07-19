Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr FindWindow(string cls, string title);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int cmd);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

$p = Get-Process sift2 -ErrorAction Stop
$hwnd = $p.MainWindowHandle

# Restore and bring to foreground
[Win32]::ShowWindow($hwnd, 9) | Out-Null   # SW_RESTORE
[Win32]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 800

# Get Sift2 window rect for screenshot
$rect = New-Object Win32+RECT
[Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
Write-Output "Sift2 window: $($rect.Left),$($rect.Top) -> $($rect.Right),$($rect.Bottom)"

# Use UIA to find Connections button by partial AutomationId match
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
$allEls = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)

$connBtn = $null
foreach ($el in $allEls) {
    if ($el.Current.Name -eq "Connections" -and
        $el.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button) {
        $connBtn = $el
        Write-Output "Found Connections button: $($el.Current.AutomationId)"
        break
    }
}

if ($null -eq $connBtn) { Write-Output "ERROR: Connections button not found"; exit 1 }

# Click via InvokePattern
try {
    $connBtn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
    Write-Output "Invoked Connections button"
} catch {
    # Fallback: click via mouse at element's bounding rect center
    $br = $connBtn.Current.BoundingRectangle
    $cx = [int]($br.Left + $br.Width/2)
    $cy = [int]($br.Top  + $br.Height/2)
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($cx, $cy)
    Start-Sleep -Milliseconds 200
    $mouse = New-Object System.Windows.Forms.MouseEventArgs([System.Windows.Forms.MouseButtons]::Left, 1, $cx, $cy, 0)
    [System.Windows.Forms.Application]::DoEvents()
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait(" ")
    Write-Output "Clicked via mouse at $cx,$cy"
}
Start-Sleep -Milliseconds 2000

# Find Printer Connections dialog
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$wins = $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)

$dlg = $null
foreach ($w in $wins) {
    if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
        Write-Output "Found window: '$($w.Current.Name)'"
        $dlg = $w
    }
}

if ($null -eq $dlg) { Write-Output "No dialog found"; exit 1 }

Write-Output "=== '$($dlg.Current.Name)' Elements ==="
$all = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
foreach ($el in $all) {
    $n   = $el.Current.Name
    $aid = $el.Current.AutomationId
    $type= $el.Current.ControlType.ProgrammaticName
    $val = ""; try { $val = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
    Write-Output "$type | N=[$n] | ID=[$aid] | V=[$val]"
}
