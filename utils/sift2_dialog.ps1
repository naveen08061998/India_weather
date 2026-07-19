Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Drawing;
using System.Runtime.InteropServices;
public class WinHelper2 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int x, int y, uint data, IntPtr extra);
    public struct RECT { public int L, T, R, B; }
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP   = 0x0004;
}
"@
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$p = Get-Process sift2
[WinHelper2]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[WinHelper2]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500

# Click Connections button via its BoundingRectangle (found via UIA in same process)
$root = [System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition)

$connBtn = $null
foreach ($el in $all) {
    if ($el.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and
        $el.Current.Name -eq "Connections") {
        $connBtn = $el; break
    }
}

if ($null -ne $connBtn) {
    $br = $connBtn.Current.BoundingRectangle
    $cx = [int]($br.Left + $br.Width/2)
    $cy = [int]($br.Top  + $br.Height/2)
    Write-Output "Clicking Connections at ($cx, $cy)"
    [WinHelper2]::SetCursorPos($cx, $cy) | Out-Null
    Start-Sleep -Milliseconds 200
    [WinHelper2]::mouse_event(0x0002, $cx, $cy, 0, [IntPtr]::Zero)
    [WinHelper2]::mouse_event(0x0004, $cx, $cy, 0, [IntPtr]::Zero)
} else {
    Write-Output "Connections button not found by UIA, listing all buttons:"
    foreach ($el in $all) {
        if ($el.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button) {
            $br = $el.Current.BoundingRectangle
            Write-Output "  Btn '$($el.Current.Name)' at ($([int]$br.Left),$([int]$br.Top))"
        }
    }
    exit 1
}
Start-Sleep -Milliseconds 2000

# Find Printer Connections dialog
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
$wins = $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $wins) {
    if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
        Write-Output "Child window: '$($w.Current.Name)'"
        $dlg = $w
    }
}

if ($null -eq $dlg) { Write-Output "Dialog not found"; exit 1 }

Write-Output "=== '$($dlg.Current.Name)' - $($dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition).Count) elements ==="
$dlgAll = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
foreach ($el in $dlgAll) {
    $n    = $el.Current.Name
    $aid  = $el.Current.AutomationId
    $type = $el.Current.ControlType.ProgrammaticName
    $val  = ""; try { $val = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
    $br   = $el.Current.BoundingRectangle
    if ($n -or $val -or ($type -match "Button|ComboBox|CheckBox|Edit")) {
        Write-Output "$type | N=[$n] | ID=[$aid] | V=[$val] | Pos=($([int]$br.Left),$([int]$br.Top),$([int]$br.Right),$([int]$br.Bottom))"
    }
}
