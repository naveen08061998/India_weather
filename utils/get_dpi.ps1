Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class DH {
    [DllImport("user32.dll")] public static extern IntPtr GetDC(IntPtr h);
    [DllImport("gdi32.dll")]  public static extern int GetDeviceCaps(IntPtr h, int n);
    [DllImport("user32.dll")] public static extern int ReleaseDC(IntPtr h, IntPtr d);
}
"@
$h   = [DH]::GetDC([IntPtr]::Zero)
$dpi = [DH]::GetDeviceCaps($h, 88)  # LOGPIXELSX
[DH]::ReleaseDC([IntPtr]::Zero, $h) | Out-Null
$scale = $dpi / 96.0
Write-Output "DPI=$dpi Scale=$scale"
# Connections button physical rect from UIA: (1668,991,1797,1019)
$physX = 1732; $physY = 1005
$logX  = [int]($physX / $scale)
$logY  = [int]($physY / $scale)
Write-Output "Connections button logical center: ($logX, $logY)"
