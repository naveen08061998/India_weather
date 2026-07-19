Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WU5 {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@

function Click($x, $y) {
    [WU5]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -Milliseconds 120
    [WU5]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 70
    [WU5]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 250
    Write-Output "Clicked ($x,$y)"
}

function Screenshot($name) {
    $bmp = New-Object System.Drawing.Bitmap(1536, 864)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size(1536, 864)))
    $bmp.Save("C:\Users\ReddyA41\Desktop\AgenticAgent\reports\$name")
    $g.Dispose(); $bmp.Dispose()
    Write-Output "Screenshot: $name"
}

# ── Step 1: Restore + focus Sift2 ─────────────────────────────────────────
$p  = Get-Process sift2
$hw = $p.MainWindowHandle
[WU5]::ShowWindow($hw, 9) | Out-Null
[WU5]::SetForegroundWindow($hw) | Out-Null
Start-Sleep -Milliseconds 600

# ── Step 2: Click Connections button at logical (1386, 804) ───────────────
Write-Output "Clicking Connections button..."
Click 1386 804
Start-Sleep -Milliseconds 1500

Screenshot "sift2_dlg_step1.png"

# ── Step 3: Check if dialog appeared via UIA ──────────────────────────────
$scale   = 1.25
$root    = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$desktop = [System.Windows.Automation.AutomationElement]::RootElement

function FindDlg {
    # Check both: dialog as top-level child of desktop and as child of root
    foreach ($w in $desktop.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($w.Current.ProcessId -eq $p.Id) {
            $n = $w.Current.Name
            if ($n -ne "Sift2") { return $w }
        }
    }
    # Fallback: search root window descendants for a window with "Printer" name
    foreach ($w in $root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition)) {
        $t = $w.Current.ControlType.ProgrammaticName
        $n = $w.Current.Name
        if ($t -eq "ControlType.Window" -and $n -match "Printer|Connect") {
            return $w
        }
    }
    return $null
}

$dlg = FindDlg
if ($null -eq $dlg) {
    Write-Output "Dialog not found after click — retrying click..."
    Click 1386 804
    Start-Sleep -Milliseconds 1500
    $dlg = FindDlg
}

if ($null -eq $dlg) {
    Write-Output "Dialog still not found via UIA — using coordinate-based approach"
    # Dialog IS visible in screenshot, use hard-coded coordinates
    # These are based on the actual screenshot sift2_conn_click.png analysis:
    #   Row 8 (15.77.36.63) is at logical y≈490
    #   Shell checkbox column is at logical x≈968
    #   OK button at logical x≈870, y≈745
} else {
    Write-Output "Found dialog: '$($dlg.Current.Name)'"
    [WU5]::SetForegroundWindow($dlg.Current.NativeWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 300
}

# ── Step 4: Click Shell checkbox for row 8 ────────────────────────────────
# From screenshot analysis: Shell col x≈968, row-8 y≈490 (logical coords)
Write-Output "Checking Shell checkbox for row 8 (15.77.36.63)..."
Click 968 490
Start-Sleep -Milliseconds 400

Screenshot "sift2_dlg_step2_shell.png"

# ── Step 5: Click OK button ───────────────────────────────────────────────
Write-Output "Clicking OK..."
Click 870 745
Start-Sleep -Milliseconds 1500

Screenshot "sift2_dlg_step3_ok.png"

# ── Step 6: Verify portSelector now shows 15.77.36.63 ─────────────────────
$root2 = [System.Windows.Automation.AutomationElement]::FromHandle($hw)
$cond  = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    'QApplication.SiftWindow.centralWidget.portSelector')
$ps = $root2.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if ($ps) {
    $val = ""
    try { $val = $ps.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
    Write-Output "portSelector current value: '$val'"
    Write-Output "portSelector items:"
    foreach ($item in $ps.FindAll([System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition)) {
        Write-Output "  - '$($item.Current.Name)'"
    }
} else {
    Write-Output "portSelector not found"
}

Write-Output "Complete"
