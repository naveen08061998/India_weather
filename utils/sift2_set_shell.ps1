Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WU4 {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int L, T, R, B; }
}
"@

function Click($x, $y) {
    [WU4]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 150
    [WU4]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [WU4]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 300
    Write-Output "Clicked ($x, $y)"
}

function Screenshot($name) {
    Add-Type -AssemblyName System.Drawing
    $bmp = New-Object System.Drawing.Bitmap(1536, 864)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size(1536, 864)))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$name")
    $g.Dispose(); $bmp.Dispose()
    Write-Output "Screenshot: $name"
}

# ── Verify the dialog is still open via UIA ────────────────────────────────
$p   = Get-Process sift2
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$dlg = $null
foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w.Current.ProcessId -eq $p.Id -and $w.Current.Name -ne "Sift2") {
        Write-Output "Found dialog: '$($w.Current.Name)'"
        $dlg = $w
    }
}

if ($null -eq $dlg) { Write-Output "No dialog found - exiting"; exit 1 }

# ── Read dialog elements to find row 8 (15.77.36.63) Shell checkbox ────────
$scale = 1.25
$dlgEls = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)

Write-Output "Dialog has $($dlgEls.Count) elements"
$row8Shell = $null
$row8Dart  = $null
$okBtn     = $null
$ipRow     = $null

foreach ($el in $dlgEls) {
    $n    = $el.Current.Name
    $aid  = $el.Current.AutomationId
    $type = $el.Current.ControlType.ProgrammaticName
    $br   = $el.Current.BoundingRectangle
    $logX = [int]($br.Left  / $scale)
    $logY = [int]($br.Top   / $scale)
    $logR = [int]($br.Right / $scale)
    $logB = [int]($br.Bottom/ $scale)

    # Find the IP input that has 15.77.36.63
    if ($type -eq "ControlType.Edit" -or $type -eq "ControlType.ComboBox") {
        $val = ""
        try { $val = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
        if ($val -match "15\.77\.36\.63") {
            Write-Output "IP field: $type N=[$n] V=[$val] Logical=($logX,$logY,$logR,$logB)"
            $ipRow = $el
        }
    }
    if ($n -eq "OK" -and $type -eq "ControlType.Button") {
        Write-Output "OK button at logical ($logX,$logY,$logR,$logB)"
        $okBtn = $el
    }
}

# If we found the IP row, find Shell checkbox in same row Y band
if ($ipRow) {
    $ipBr   = $ipRow.Current.BoundingRectangle
    $rowPhyY = $ipBr.Top + $ipBr.Height / 2  # physical center Y of row 8

    Write-Output "Row 8 physical center Y=$rowPhyY"

    # Find all checkboxes in the dialog and pick the Shell one on same row
    foreach ($el in $dlgEls) {
        $type = $el.Current.ControlType.ProgrammaticName
        $br   = $el.Current.BoundingRectangle
        if ($type -eq "ControlType.CheckBox" -and [Math]::Abs($br.Top - $ipBr.Top) -lt 20) {
            $logX2 = [int]($br.Left  / $scale)
            $logY2 = [int]($br.Top   / $scale)
            $n2    = $el.Current.Name
            Write-Output "Checkbox in row 8: N=[$n2] logical=($logX2,$logY2) aid=$($el.Current.AutomationId)"
        }
    }
}

# ── Use image-coordinate click (known from screenshots) ──────────────────
# The full-desktop screenshot captured at (0,0) → image coords = logical screen coords
# Row 8 Shell checkbox in previous screenshot image at approx (968, 490)
# Row 8 Dart  checkbox at approx (1160, 490)
# OK button at approx (870, 745)

Write-Output "`nFocusing dialog..."
[WU4]::SetForegroundWindow($dlg.Current.NativeWindowHandle) | Out-Null
Start-Sleep -Milliseconds 400

# Click Shell checkbox for row 8 (15.77.36.63)
Write-Output "Checking Shell for row 8..."
Click 968 490
Start-Sleep -Milliseconds 300
Screenshot "sift2_shell_checked.png"

# Click OK
Write-Output "Clicking OK..."
Click 870 745
Start-Sleep -Milliseconds 1500
Screenshot "sift2_after_ok.png"
Write-Output "Done"
