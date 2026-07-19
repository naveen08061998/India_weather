# sift2_udw_cmd.ps1
# Sends a UDW command to the device via Sift2's serial shell and captures the response
# by enabling Sift2 file logging to a temp file, sending the command, then reading it.
# Usage: .\sift2_udw_cmd.ps1 -Command "WebSocket PUB_getPingPongStatus 1"
param(
    [Parameter(Mandatory=$true)][string]$Command,
    [int]$WaitMs = 4000,
    [double]$DpiScale = 1.25
)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class UDW2 {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern int  GetWindowThreadProcessId(IntPtr h, out int p2);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool c);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, IntPtr extra);
    [DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
}
"@

$p = Get-Process sift2 -ErrorAction SilentlyContinue
if (-not $p) { Write-Error "Sift2 not running"; exit 1 }
$hw = $p.MainWindowHandle

# ── Bring Sift2 to foreground ────────────────────────────────────────────────
$st = 0; [UDW2]::GetWindowThreadProcessId($hw, [ref]$st) | Out-Null
$mt = [UDW2]::GetCurrentThreadId()
[UDW2]::AttachThreadInput($mt, $st, $true)  | Out-Null
[UDW2]::ShowWindow($hw, 9)                  | Out-Null
[UDW2]::BringWindowToTop($hw)               | Out-Null
[UDW2]::SetForegroundWindow($hw)            | Out-Null
[UDW2]::AttachThreadInput($mt, $st, $false) | Out-Null
Start-Sleep -Milliseconds 700

$root = [System.Windows.Automation.AutomationElement]::FromHandle($hw)

function FindById([string]$id) {
    $cond = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty, $id)
    return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
}

function ClickEl($el) {
    $br = $el.Current.BoundingRectangle
    $lx = [int](($br.Left + $br.Width  / 2) / $DpiScale)
    $ly = [int](($br.Top  + $br.Height / 2) / $DpiScale)
    [UDW2]::SetCursorPos($lx, $ly) | Out-Null
    Start-Sleep -Milliseconds 100
    [UDW2]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [UDW2]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 300
}

function InvokeBtn([string]$id) {
    $el = FindById $id
    if ($el) {
        try { ($el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); return }
        catch {}
        ClickEl $el
    }
}

# ── 1. Set log file path — click the field then type via keybd_event ─────────
$logPath = [System.IO.Path]::Combine($env:TEMP, "sift2_udw_$PID.log")
if (Test-Path $logPath) { Remove-Item $logPath -Force }

$logField = FindById "QApplication.SiftWindow.centralWidget.splitter.horizontalLayoutWidget.Tabs.qt_tabwidget_stackedwidget.commandTab.loggingToFile"
if ($logField) {
    ClickEl $logField   # mouse click to focus
    Start-Sleep -Milliseconds 300
    # Select all existing text via PostMessage Ctrl+A to main HWND
    [UDW2]::PostMessage($hw, 0x0100, [IntPtr]0x41, [IntPtr]0x001D0001) | Out-Null  # Ctrl+A
    Start-Sleep -Milliseconds 150
    # Type path via PostMessage WM_CHAR for each character
    foreach ($ch in $logPath.ToCharArray()) {
        $code = [int][char]$ch
        [UDW2]::PostMessage($hw, 0x0102, [IntPtr]$code, [IntPtr]0) | Out-Null  # WM_CHAR
        Start-Sleep -Milliseconds 5
    }
    Start-Sleep -Milliseconds 300
    Write-Host "Log path typed: $logPath"
}

# ── 2. Record existing ADS streams on the ERROR file so we can identify the new one ──
$adsBase = "C:\Users\ReddyA41\ERROR"
$adsBefore = @()
try {
    $adsBefore = (Get-Item $adsBase -Stream * -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty Stream) -ne ':$DATA'
} catch {}

# ── 3. Click Start Logging ────────────────────────────────────────────────────
InvokeBtn "QApplication.SiftWindow.centralWidget.splitter.horizontalLayoutWidget.Tabs.qt_tabwidget_stackedwidget.commandTab.logOnButton"
Start-Sleep -Milliseconds 600

# ── 4. Send command via textInput ─────────────────────────────────────────────
$fullCmd = 'runUw mainApp "' + $Command + '"'
$inputEl = FindById "QApplication.SiftWindow.centralWidget.textInput.QLineEdit"
if (-not $inputEl) { Write-Error "Command input not found"; exit 1 }

$inputEl.SetFocus()
Start-Sleep -Milliseconds 300
try {
    ($inputEl.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).SetValue($fullCmd)
} catch {
    [System.Windows.Forms.SendKeys]::SendWait("^a{DELETE}")
    Start-Sleep -Milliseconds 100
    foreach ($ch in $fullCmd.ToCharArray()) {
        [System.Windows.Forms.SendKeys]::SendWait([string]$ch -replace '([+^%~(){}\[\]])', '{$1}')
    }
}
Start-Sleep -Milliseconds 200
# Send ENTER to the main Sift2 window HWND — Qt routes it to the focused widget
[UDW2]::PostMessage($hw, 0x0100, [IntPtr]0x0D, [IntPtr]0) | Out-Null  # WM_KEYDOWN VK_RETURN
Start-Sleep -Milliseconds 60
[UDW2]::PostMessage($hw, 0x0101, [IntPtr]0x0D, [IntPtr]0) | Out-Null  # WM_KEYUP VK_RETURN
Write-Host "ENTER sent via PostMessage to main HWND"

# ── 5. Wait for async UDW response ───────────────────────────────────────────
Start-Sleep -Milliseconds $WaitMs

# ── 6. Stop logging ───────────────────────────────────────────────────────────
InvokeBtn "QApplication.SiftWindow.centralWidget.splitter.horizontalLayoutWidget.Tabs.qt_tabwidget_stackedwidget.commandTab.logOffButton"
Start-Sleep -Milliseconds 600

# ── 7. Find the new ADS stream and read it ───────────────────────────────────
$adsAfter = @()
try {
    $adsAfter = (Get-Item $adsBase -Stream * -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty Stream) -ne ':$DATA'
} catch {}

# Find the new stream created after start logging
$newStreams = $adsAfter | Where-Object { $adsBefore -notcontains $_ } 
$logStream = $newStreams | Select-Object -Last 1

$lines = @()
if ($logStream) {
    Write-Host "Reading ADS: $adsBase`:$logStream"
    $lines = Get-Content "$adsBase" -Stream "$logStream" -ErrorAction SilentlyContinue
} else {
    # Fallback: read the most recently updated stream
    $logStream = $adsAfter | Select-Object -Last 1
    if ($logStream) {
        Write-Host "Fallback reading ADS: $adsBase`:$logStream"
        $lines = Get-Content "$adsBase" -Stream "$logStream" -ErrorAction SilentlyContinue
    }
}

if (-not $lines) { Write-Output "RESPONSE:"; exit 0 }
$cmdIdx = -1
for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    if ($lines[$i] -match [regex]::Escape($Command)) { $cmdIdx = $i; break }
}

$responseLines = @()
if ($cmdIdx -ge 0 -and $cmdIdx -lt $lines.Count - 1) {
    $responseLines = $lines[($cmdIdx + 1)..($lines.Count - 1)] |
        Where-Object { $_.Trim() -ne "" -and $_ -notmatch "^\d{2}/\d{2}/\d{2}-\d{2}:\d{2}:\d{2} #:\[root@" }
} else {
    # Return last 10 non-empty, non-prompt lines
    $responseLines = $lines |
        Where-Object { $_.Trim() -ne "" -and $_ -notmatch "^\d{2}/\d{2}/\d{2}-\d{2}:\d{2}:\d{2} #:\[root@" } |
        Select-Object -Last 10
}

$response = ($responseLines -join "`n").Trim()
Write-Output "RESPONSE:$response"
