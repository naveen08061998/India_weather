Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System; using System.Runtime.InteropServices;
public class WH3 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
}
"@

$p = Get-Process sift2
$desktop = [System.Windows.Automation.AutomationElement]::RootElement

# List all Sift2 windows first
$wins = $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $wins) {
    if ($w.Current.ProcessId -eq $p.Id) {
        Write-Output "Sift2 window: '$($w.Current.Name)'"
    }
}

# Bring Sift2 to front and click Connections button by position
[WH3]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[WH3]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500

$root = [System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
$all  = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition)

Write-Output "--- All buttons with positions ---"
$connX = 0; $connY = 0
foreach ($el in $all) {
    if ($el.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button) {
        $br = $el.Current.BoundingRectangle
        Write-Output "Btn '$($el.Current.Name)' @ ($([int]$br.Left),$([int]$br.Top))"
        if ($el.Current.Name -eq "Connections") {
            $connX = [int]($br.Left + $br.Width/2)
            $connY = [int]($br.Top  + $br.Height/2)
        }
    }
}

if ($connX -gt 0) {
    Write-Output "Clicking Connections at ($connX, $connY)"
    [WH3]::SetCursorPos($connX, $connY) | Out-Null
    Start-Sleep -Milliseconds 300
    [WH3]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    [WH3]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 2000

    # Read dialog
    $wins2 = $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($w in $wins2) {
        if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
            Write-Output "=== Dialog: '$($w.Current.Name)' ==="
            $dlgEls = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants,
                [System.Windows.Automation.Condition]::TrueCondition)
            foreach ($el in $dlgEls) {
                $type = $el.Current.ControlType.ProgrammaticName
                $n    = $el.Current.Name
                $val  = ""; try { $val = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
                $br   = $el.Current.BoundingRectangle
                if ($n -or $val) {
                    Write-Output "  $type | N=[$n] | V=[$val] | Pos=($([int]$br.Left),$([int]$br.Top))"
                }
            }
        }
    }
} else {
    Write-Output "Connections button not found"
}
