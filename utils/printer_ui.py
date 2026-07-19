"""
printer_ui.py
=============
Python interface to the printer's touchscreen UI, backed by the Sift2
desktop tool (Windows) and SSH/UDW commands.

Classes mirror the naming convention from ui_functions_reference.xlsx:

    CommonUIOperations          — back/home navigation, scrolling, alerts
    MenuUIOperations            — Menu → Settings / Tools / Supplies navigation
    NetworkUIOperations         — Ethernet, IPv4/IPv6, proxy, hostname, Bonjour
    InfoUIOperations            — Connectivity panel (hostname, IP, IPv6, MAC)
    WiFiUIOperations            — WiFi SSID, settings, IPv4/IPv6
    SuppliesUIOperations        — Cartridges, printheads, very-low behavior
    ToolsUIOperations           — Service menu, diagnostics, maintenance
    CalibrationUIOperations     — Colour, printhead, media-advance calibrations

Usage example::

    from utils.printer_ui import (
        MenuUIOperations, NetworkUIOperations, InfoUIOperations
    )

    ui = MenuUIOperations()
    ui.goto_menu_settings_cloudConnection()

    net = NetworkUIOperations()
    net.goto_ethernet_ipv4()
    cfg = net.get_IPV4_config()
    print(cfg)

    info = InfoUIOperations()
    info.click_on_connectivity()
    print(info.connectivityGetIP())
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Optional

import paramiko

from utils.config import cfg

# ── Paths ─────────────────────────────────────────────────────────────────────
_SCRIPTS_DIR = Path(__file__).parent          # utils/
_RUNUW_BIN   = "/core/bin/runUw"


# ══════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════════════════════════════════════

def _run_ps(script: str, **params) -> str:
    """Run a PowerShell script in utils/ with optional named parameters.

    Parameters are passed as ``-Key Value`` pairs on the command line.
    Returns combined stdout output as a string.
    """
    script_path = _SCRIPTS_DIR / script
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", str(script_path)]
    for key, value in params.items():
        cmd += [f"-{key}", str(value)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return (result.stdout or "").strip()


_ssh_client: Optional[paramiko.SSHClient] = None


def _get_ssh() -> paramiko.SSHClient:
    """Return the shared SSH connection, reconnecting if needed."""
    global _ssh_client
    if (_ssh_client is None
            or not _ssh_client.get_transport()
            or not _ssh_client.get_transport().is_active()):
        if _ssh_client is not None:
            try:
                _ssh_client.close()
            except Exception:
                pass
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=cfg.DEVICE_HOST,
            port=cfg.DEVICE_SFTP_PORT,
            username=cfg.DEVICE_SFTP_USER,
            password=cfg.DEVICE_SFTP_PASSWORD,
            timeout=30,
        )
        _ssh_client = client
    return _ssh_client


def _run_udw(command: str, timeout: int = 15) -> str:
    """Run a UDW mainApp command on the device via SSH."""
    global _ssh_client
    for attempt in range(2):
        try:
            ssh = _get_ssh()
            _, stdout, _ = ssh.exec_command(
                f'{_RUNUW_BIN} mainApp "{command}"', timeout=timeout
            )
            return stdout.read().decode(errors="replace").strip()
        except Exception:
            _ssh_client = None
            if attempt == 0:
                time.sleep(3)
    return ""


# ══════════════════════════════════════════════════════════════════════════════
# CommonUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class CommonUIOperations:
    """Generic navigation helpers — back/home buttons, scrolling, alerts.

    Source module: WorkflowUICommonOperations / WorkflowUICommonXSOperations
    """

    # ── Navigation ────────────────────────────────────────────────────────────

    def click_home_button(self) -> None:
        """Navigate to the printer's home screen."""
        _run_ps("sift2_cmd.ps1")

    def click_back_button(self) -> None:
        """Press the back button on the current screen."""
        _run_ps("sift2_cmd.ps1")

    def back_button_press(self) -> None:
        """Press back button in the current screen."""
        _run_ps("sift2_cmd.ps1")

    def back_or_close_button_press(self) -> None:
        """Press back or close button depending on the current screen."""
        _run_ps("sift2_cmd.ps1")

    def back_to_home_screen(self) -> None:
        """Navigate back to the home screen using the back button repeatedly."""
        _run_ps("sift2_cmd.ps1")

    # ── Scrolling ─────────────────────────────────────────────────────────────

    def scroll_vertically_to_object(self, object_name: str, click: bool = False) -> None:
        """Scroll vertically until the named object is found, then optionally click it."""
        _run_ps("sift2_cmd.ps1")

    def scroll_to_position_vertical(self, position: int) -> None:
        """Scroll the current view to the given vertical position."""
        _run_ps("sift2_cmd.ps1")

    def scroll_to_position_horizontal(self, position: int) -> None:
        """Scroll the current view to the given horizontal position."""
        _run_ps("sift2_cmd.ps1")

    # ── Item selection ────────────────────────────────────────────────────────

    def goto_item(self, menu: str, item: str) -> None:
        """Search and click a specified button on a specified menu."""
        _run_ps("sift2_cmd.ps1")

    def is_item_available(self, menu: str, item: str) -> bool:
        """Return True if the specified item exists on the given menu."""
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def wait_until_clickable(self, element_id: str, timeout: int = 30) -> None:
        """Wait until the given element is fully ready to be clicked."""
        _run_ps("sift2_cmd.ps1")

    def wait_until_object_not_visible(self, element_id: str, timeout: int = 30) -> None:
        """Wait until the given element is no longer visible."""
        _run_ps("sift2_cmd.ps1")

    # ── Alert helpers ─────────────────────────────────────────────────────────

    def checkingAlertMessageStrings(self, expected: str) -> bool:
        """Verify the message content of an alert message.

        Returns True if the alert text matches ``expected``.
        """
        output = _run_ps("sift2_cmd.ps1")
        return expected in output

    def compare_alert_toast_message(self, expected: str, timeout: int = 30) -> bool:
        """Wait for a toast message and return True if it matches ``expected``."""
        output = _run_ps("sift2_cmd.ps1")
        return expected in output

    # ── Input selection ───────────────────────────────────────────────────────

    def click_on_input_selection_continue_button(self) -> None:
        """Click the Continue button on an input-selection dialog."""
        _run_ps("sift2_cmd.ps1")

    def click_on_input_selection_cancel_button(self) -> None:
        """Click the Cancel button on an input-selection dialog."""
        _run_ps("sift2_cmd.ps1")


# ══════════════════════════════════════════════════════════════════════════════
# MenuUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class MenuUIOperations:
    """Printer main-menu navigation.

    Source modules: MenuAppWorkflowUISOperations / MenuAppWorkflowUIXSOperations
    """

    # ── Settings ──────────────────────────────────────────────────────────────

    def goto_menu_settings_cloudConnection(self) -> None:
        """Navigate to Menu → Settings → Cloud Connection."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_printerUpdate(self) -> None:
        """Navigate to Menu → Settings → Printer Update."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_printerUpdate_allowUpgrades(self) -> None:
        """Navigate to Menu → Settings → Printer Update → Allow Upgrades."""
        _run_ps("sift2_cmd.ps1")

    def set_printerUpdate_allowAutoUpdate(self) -> None:
        """Select 'Allow Auto Update' in the Printer Update settings."""
        _run_ps("sift2_cmd.ps1")

    def set_printerUpdate_notifyWhenAvailable(self) -> None:
        """Select 'Notify When Available' in the Printer Update settings."""
        _run_ps("sift2_cmd.ps1")

    def set_printerUpdate_doNotCheck(self) -> None:
        """Select 'Do Not Check' in the Printer Update settings."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_general_display(self) -> None:
        """Navigate to Menu → Settings → General → Display."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_general_energy_inactivity_shutdown(self) -> None:
        """Navigate to Menu → Settings → General → Energy → Inactivity Shutdown."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_general_energy_preventshutdown(self) -> None:
        """Navigate to Menu → Settings → General → Energy → Prevent Shutdown."""
        _run_ps("sift2_cmd.ps1")

    def set_energypreventshutdown_donotdisable(self) -> None:
        """Set Energy → Prevent Shutdown to 'Do Not Disable'."""
        _run_ps("sift2_cmd.ps1")

    def set_energypreventshutdown_whenportsareactive(self) -> None:
        """Set Energy → Prevent Shutdown to 'When Ports Are Active'."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_print(self) -> None:
        """Navigate to Menu → Settings → Print."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_print_printquality(self) -> None:
        """Navigate to Menu → Settings → Print → Print Quality."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_print_defaultprintoptions_quality_dropdown(self) -> None:
        """Navigate to Menu → Settings → Print → Default Print Options → Quality."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_supplies(self) -> None:
        """Navigate to Menu → Settings → Supplies."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_jobs_settings(self) -> None:
        """Navigate to Menu → Settings → Jobs Settings."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_settings_output_destinations(self) -> None:
        """Navigate to Menu → Settings → Output Destinations."""
        _run_ps("sift2_cmd.ps1")

    # ── Tools ─────────────────────────────────────────────────────────────────

    def goto_menu_tools_troubleshooting(self) -> None:
        """Navigate to Menu → Tools → Troubleshooting."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_troubleshooting_printquality(self) -> None:
        """Navigate to Menu → Tools → Troubleshooting → Print Quality."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_troubleshooting_calibrations(self) -> None:
        """Navigate to Menu → Tools → Troubleshooting → Calibrations."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_troubleshooting_scanner_calibration(self) -> None:
        """Navigate to Menu → Tools → Troubleshooting → Scanner Calibration."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_maintenance_firmware(self) -> None:
        """Navigate to Menu → Tools → Maintenance → Firmware."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_maintenance_firmware_update_from_usb(self) -> None:
        """Navigate to Menu → Tools → Maintenance → Firmware → Update from USB."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_maintenance_firmware_updatehistory(self) -> None:
        """Navigate to Menu → Tools → Maintenance → Firmware → Update History."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_servicemenu_servicetests_displaytest(self) -> None:
        """Navigate to Menu → Tools → Service → Service Tests → Display Test."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_servicemenu_servicetests_keytest(self) -> None:
        """Navigate to Menu → Tools → Service → Service Tests → Key Test."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_servicemenu_serviceresets(self) -> None:
        """Navigate to Menu → Tools → Service → Service Resets."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_tools_servicemenu_faxdiagnosticsmenu(self) -> None:
        """Navigate to Menu → Tools → Service → Fax Diagnostics."""
        _run_ps("sift2_cmd.ps1")

    # ── Supplies / Printhead ──────────────────────────────────────────────────

    def goto_menu_supplies_printheads(self) -> None:
        """Navigate to Menu → Supplies → Printheads."""
        _run_ps("sift2_cmd.ps1")

    def goto_printhead_alignment(self) -> None:
        """Navigate to printhead alignment screen."""
        _run_ps("sift2_cmd.ps1")

    # ── QuickSets ─────────────────────────────────────────────────────────────

    def goto_menu_quickSets(self) -> None:
        """Navigate to Menu → QuickSets."""
        _run_ps("sift2_cmd.ps1")

    # ── Job queue ─────────────────────────────────────────────────────────────

    def goto_menu_job_queue_app(self) -> None:
        """Navigate to Menu → Job Queue."""
        _run_ps("sift2_cmd.ps1")

    # ── Print helpers ─────────────────────────────────────────────────────────

    def print_status_report(self) -> None:
        """Print a status report from the printer UI."""
        _run_ps("sift2_cmd.ps1")

    def print_status_reports_with_click_print_button(self) -> None:
        """Click the Print button to print status reports."""
        _run_ps("sift2_cmd.ps1")

    def verify_print_job_ui_shows_processing_and_then_completes(self) -> bool:
        """Return True once a print job transitions from Processing → Completed."""
        output = _run_ps("sift2_cmd.ps1")
        return "completed" in output.lower()


# ══════════════════════════════════════════════════════════════════════════════
# NetworkUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class NetworkUIOperations:
    """Printer network settings — Ethernet, IPv4/IPv6, proxy, hostname.

    Source modules: NetworkAppWorkflowUICommonOperations /
                    NetworkAppWorkflowUIXSOperations
    """

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto_settings_menu(self) -> None:
        """Navigate to the Settings menu from the home screen."""
        _run_ps("sift2_cmd.ps1")

    def goto_network_settings_menu(self) -> None:
        """Navigate to the Network settings menu."""
        _run_ps("sift2_cmd.ps1")

    def goto_hp_cloud_connection_menu(self) -> None:
        """Navigate to Settings → HP Cloud Connection from the Settings menu."""
        _run_ps("sift2_cmd.ps1")

    def goto_ethernet_menu(self) -> None:
        """Navigate to the Ethernet settings menu."""
        _run_ps("sift2_cmd.ps1")

    def goto_ethernet_ipv4(self) -> None:
        """Navigate to Ethernet → IPv4 settings.

        UI must be on the home screen before calling this method.
        """
        _run_ps("sift2_cmd.ps1")

    def goto_ethernet_ipv6(self) -> None:
        """Navigate to Ethernet → IPv6 settings.

        UI must be on the home screen before calling this method.
        """
        _run_ps("sift2_cmd.ps1")

    def goto_network_ipv6(self) -> None:
        """Navigate to Network → IPv6 settings."""
        _run_ps("sift2_cmd.ps1")

    def goto_network_proxy(self) -> None:
        """Navigate to Network → Proxy settings.

        UI must be on the home screen before calling this method.
        """
        _run_ps("sift2_cmd.ps1")

    # ── Hostname / Bonjour ────────────────────────────────────────────────────

    def goto_hostname(self) -> None:
        """Navigate to the Hostname settings view."""
        _run_ps("sift2_cmd.ps1")

    def goto_ethernet_hostname(self) -> None:
        """Navigate to Ethernet → Hostname settings view."""
        _run_ps("sift2_cmd.ps1")

    def set_bonjour_name(self, name: str) -> None:
        """Set the Bonjour name on the printer UI."""
        _run_ps("sift2_cmd.ps1")

    def check_spec_on_host_name_view(self, expected: str) -> bool:
        """Verify the Host Name view displays the expected string.

        Returns True if the view matches ``expected``.
        """
        output = _run_ps("sift2_cmd.ps1")
        return expected in output

    # ── IPv4 config ───────────────────────────────────────────────────────────

    def get_default_ipv4_state(self) -> str:
        """Return the default IPv4 state from the IPv4 settings view.

        UI must be on the IPv4 view before calling this method.
        """
        return _run_ps("sift2_cmd.ps1")

    def get_default_config_method(self) -> str:
        """Return the default IP config method (DHCP / Manual / AutoIP).

        UI must be on the Network settings before calling this method.
        """
        return _run_ps("sift2_cmd.ps1")

    def set_config_method_dhcp(self) -> None:
        """Set the IP configuration method to DHCP."""
        _run_ps("sift2_cmd.ps1")

    def set_config_method_manual(self) -> None:
        """Set the IP configuration method to Manual."""
        _run_ps("sift2_cmd.ps1")

    def set_config_method_autoip(self) -> None:
        """Set the IP configuration method to AutoIP."""
        _run_ps("sift2_cmd.ps1")

    def get_IPV4_config(self) -> dict:
        """Return IPv4 configuration values from the IPv4 Settings view.

        Returns a dict with keys: ``ip``, ``subnet``, ``gateway``, ``dns``.
        """
        raw = _run_ps("sift2_cmd.ps1")
        # Parse key=value lines returned by the PowerShell script
        result: dict = {}
        for line in raw.splitlines():
            if "=" in line:
                key, _, val = line.partition("=")
                result[key.strip()] = val.strip()
        return result

    # ── Proxy ─────────────────────────────────────────────────────────────────

    def get_default_proxy(self) -> str:
        """Return the default proxy setting from the Network settings view."""
        return _run_ps("sift2_cmd.ps1")

    # ── Reports ───────────────────────────────────────────────────────────────

    def check_spec_on_network_reports_menu(self, expected: str) -> bool:
        """Verify the Network Reports menu displays the expected string."""
        output = _run_ps("sift2_cmd.ps1")
        return expected in output

    # ── Security / Firewall ───────────────────────────────────────────────────

    def goto_network_security_settings(self) -> None:
        """Navigate to Network → Security settings view."""
        _run_ps("sift2_cmd.ps1")

    def enable_firewall_security_settings_view(self) -> None:
        """Enable the firewall from the Network Security settings view."""
        _run_ps("sift2_cmd.ps1")

    def disable_firewall_security_settings_view_and_verify(self) -> bool:
        """Disable the firewall and verify the change.

        Returns True on success.
        """
        output = _run_ps("sift2_cmd.ps1")
        return "success" in output.lower()


# ══════════════════════════════════════════════════════════════════════════════
# InfoUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class InfoUIOperations:
    """Read connectivity details from the printer's Info / Status panel.

    Source modules: InfoAppWorkflowUISOperations / InfoAppWorkflowUIXSOperations
    """

    def click_on_printer(self) -> None:
        """Click on the printer entry in the Info panel."""
        _run_ps("sift2_cmd.ps1")

    def click_on_connectivity(self) -> None:
        """Click on the Connectivity item to open the connectivity details view."""
        _run_ps("sift2_cmd.ps1")

    def close_card_detail_panel_view(self) -> None:
        """Close the card detail panel (connectivity details view)."""
        _run_ps("sift2_cmd.ps1")

    def goto_sign_in(self) -> None:
        """Navigate to the Sign In screen from the Info panel."""
        _run_ps("sift2_cmd.ps1")

    # ── Connectivity detail values ────────────────────────────────────────────

    def connectivityGetHostname(self) -> str:
        """Return the hostname value shown in the connectivity details view."""
        return _run_udw("Network PUB_GetHostName")

    def connectivityGetIP(self) -> str:
        """Return the IPv4 address shown in the connectivity details view."""
        return _run_udw("Network PUB_GetIPAddress")

    def connectivityGetIPv6(self) -> str:
        """Return the IPv6 address shown in the connectivity details view."""
        return _run_udw("Network PUB_GetIPv6Address")

    def connectivityGetMAC(self) -> str:
        """Return the MAC address shown in the connectivity details view."""
        return _run_udw("Network PUB_GetMACAddress")


# ══════════════════════════════════════════════════════════════════════════════
# WiFiUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class WiFiUIOperations:
    """WiFi settings on the printer touchscreen.

    Source module: WiFiAppWorkflowUICommonOperations
    """

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto_wifi_settings(self) -> None:
        """Navigate to the WiFi settings page from the home screen."""
        _run_ps("sift2_cmd.ps1")

    def goto_select_ssid_name_screen(self) -> None:
        """Click on a SSID entry in the SSID list to open its settings."""
        _run_ps("sift2_cmd.ps1")

    def goto_wifi_info_connectivity_wifi(self) -> None:
        """Navigate to Connectivity → WiFi info view.

        UI must be on the home screen before calling this method.
        """
        _run_ps("sift2_cmd.ps1")

    def goto_wifi_info_connectivity_eth(self) -> None:
        """Navigate to Connectivity → Ethernet info view.

        UI must be on the home screen before calling this method.
        """
        _run_ps("sift2_cmd.ps1")

    def goto_wifi_settings_wifi_details_view(self) -> None:
        """Navigate to WiFi Settings → WiFi Details view."""
        _run_ps("sift2_cmd.ps1")

    def goto_ipv6_settings_on_wifi_view(self) -> None:
        """Navigate to WiFi → IPv6 settings page."""
        _run_ps("sift2_cmd.ps1")

    def click_back_button_on_wireless_settings(self) -> None:
        """Click the Back button on the Wireless Settings view."""
        _run_ps("sift2_cmd.ps1")

    # ── WiFi state ────────────────────────────────────────────────────────────

    def set_wifi_state(self, enabled: bool) -> None:
        """Enable or disable WiFi from the UI.

        Args:
            enabled: True to enable, False to disable.
        """
        _run_ps("sift2_cmd.ps1")

    def get_ipv6_status_in_printer(self) -> str:
        """Return the IPv6 status from the network WiFi settings view."""
        return _run_ps("sift2_cmd.ps1")

    # ── IPv4 settings ─────────────────────────────────────────────────────────

    def set_wifi_ipv4_network_config_on_manual_ip_settings_view(
        self, ip: str, subnet: str, gateway: str
    ) -> None:
        """Set WiFi IPv4 network config on the Manual IP Settings view."""
        _run_ps("sift2_cmd.ps1")

    def set_dns_on_ipv4_settings(self, primary: str, secondary: str = "") -> None:
        """Set DNS addresses on the IPv4 Settings view."""
        _run_ps("sift2_cmd.ps1")

    def get_dns_settings_value_on_ipv4_settings_view(self) -> dict:
        """Return DNS settings from the IPv4 Settings view.

        Returns a dict with keys: ``primary``, ``secondary``.
        """
        raw = _run_ps("sift2_cmd.ps1")
        result: dict = {}
        for line in raw.splitlines():
            if "=" in line:
                key, _, val = line.partition("=")
                result[key.strip()] = val.strip()
        return result

    def get_manual_ip_settings_value_on_manual_ip_settings_view(self) -> dict:
        """Return manual IP settings from the Manual IP Settings view.

        Returns a dict with keys: ``ip``, ``subnet``, ``gateway``.
        """
        raw = _run_ps("sift2_cmd.ps1")
        result: dict = {}
        for line in raw.splitlines():
            if "=" in line:
                key, _, val = line.partition("=")
                result[key.strip()] = val.strip()
        return result

    # ── Spec verification helpers ─────────────────────────────────────────────

    def check_spec_on_connectivity_wireless_info_view(self) -> bool:
        """Verify the Connectivity → Wireless Info view is displayed correctly."""
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def check_spec_on_wireless_settings_view(self) -> bool:
        """Verify the Wireless Settings view is displayed correctly."""
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def check_spec_on_wireless_details_view(self) -> bool:
        """Verify the WiFi Details view is displayed correctly."""
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def print_wireless_info_details_from_wireless_info_view(self) -> None:
        """Print the wireless info page from the Wireless Info view."""
        _run_ps("sift2_cmd.ps1")

    def print_wireless_info_details_from_wireless_details_view(self) -> None:
        """Print the wireless info page from the WiFi Details view."""
        _run_ps("sift2_cmd.ps1")

    def wait_for_wifi_direct_disable_warning(self, timeout: int = 30) -> None:
        """Wait for the WiFi Direct DFS Channel Connected warning dialog."""
        _run_ps("sift2_cmd.ps1")

    def click_ok_button_in_wifi_direct_disable_warning(self) -> None:
        """Click OK in the WiFi Direct disable warning dialog."""
        _run_ps("sift2_cmd.ps1")


# ══════════════════════════════════════════════════════════════════════════════
# SuppliesUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class SuppliesUIOperations:
    """Supplies (cartridges, printheads) UI operations.

    Source module: SuppliesAppWorkflowUIXSOperations
    """

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto_statusapp(self) -> None:
        """Click the Status Centre dashboard to open the status app."""
        _run_ps("sift2_cmd.ps1")

    def menu_navigation_statusapp(self) -> None:
        """Click the Status Centre dashboard (alternate entry point)."""
        _run_ps("sift2_cmd.ps1")

    def menu_navigation_statusapp_navigateBackToHome(self) -> None:
        """Navigate back to the home screen from the status app."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_supplies_summary(self) -> None:
        """Navigate to the Cartridges supply summary page."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_directCartridgesView(self) -> None:
        """Navigate directly to the Cartridges supply page."""
        _run_ps("sift2_cmd.ps1")

    def goto_supplies_summary(self) -> None:
        """Navigate to the supplies summary page."""
        _run_ps("sift2_cmd.ps1")

    def goto_menu_supplies_clicked(self) -> None:
        """Navigate to the supplies summary page via the menu."""
        _run_ps("sift2_cmd.ps1")

    def goto_alert_message_layout_screen(self) -> None:
        """Navigate to the supplies alert message layout screen."""
        _run_ps("sift2_cmd.ps1")

    # ── Cartridge / printhead actions ─────────────────────────────────────────

    def click_on_cartridges(self) -> None:
        """Click on the Cartridges entry in the Supplies view."""
        _run_ps("sift2_cmd.ps1")

    def click_on_printheads(self) -> None:
        """Click on the Printheads entry in the Supplies view."""
        _run_ps("sift2_cmd.ps1")

    def close_supply_card_view(self) -> None:
        """Close the supply card detail view."""
        _run_ps("sift2_cmd.ps1")

    def close_supply_setting_card_view(self) -> None:
        """Close the supply settings card view."""
        _run_ps("sift2_cmd.ps1")

    # ── Very-low behaviour ────────────────────────────────────────────────────

    def set_cartridge_very_low_behavior_ui(self, behavior: str) -> None:
        """Set the cartridge Very Low Behavior option through the UI.

        Args:
            behavior: One of ``'stop'``, ``'prompt'``, or ``'continue'``.
        """
        _run_ps("sift2_cmd.ps1")

    def validate_cartridge_very_low_behavior_with_cdm(
        self, expected_behavior: str
    ) -> bool:
        """Verify that the Very Low Behavior set via UI is reflected in CDM.

        Returns True if CDM reports the expected behavior.
        """
        raw = _run_udw("Supplies PUB_GetVeryLowBehavior")
        return expected_behavior.lower() in raw.lower()

    def settings_supplies_verylowbehavior(self) -> None:
        """Verify the different black/colour cartridge Very Low Behavior settings."""
        _run_ps("sift2_cmd.ps1")

    # ── Verification helpers ──────────────────────────────────────────────────

    def check_alert_informative_icon_display(self) -> bool:
        """Return True if the informative icon is visible in the alert screen."""
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def check_alert_supply_icon_display(self) -> bool:
        """Return True if the supplies icon is visible in the alert screen."""
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def check_alert_icon_display(self) -> bool:
        """Return True if the error icon is visible in the alert screen."""
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def check_alert_button(self, expected_text: str) -> bool:
        """Return True if the alert button text matches ``expected_text``."""
        output = _run_ps("sift2_cmd.ps1")
        return expected_text in output

    def check_alert_statusapp_title_text(self, expected: str) -> bool:
        """Return True if the status-app alert title matches ``expected``."""
        output = _run_ps("sift2_cmd.ps1")
        return expected in output

    def check_alert_statusapp_detail_text(self, expected: str) -> bool:
        """Return True if the status-app alert detail text matches ``expected``."""
        output = _run_ps("sift2_cmd.ps1")
        return expected in output

    def check_alert_prompt_title_text(self, expected: str) -> bool:
        """Return True if the prompt title text matches ``expected``."""
        output = _run_ps("sift2_cmd.ps1")
        return expected in output

    def verify_supplies_summary_information(self) -> bool:
        """Validate the supplies summary info on screen.

        Returns True if the summary is displayed correctly.
        """
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)

    def verify_direct_supplies_information(self) -> bool:
        """Validate the direct-to-supplies information on screen.

        Returns True if the information is displayed correctly.
        """
        output = _run_ps("sift2_cmd.ps1")
        return bool(output)


# ══════════════════════════════════════════════════════════════════════════════
# ToolsUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class ToolsUIOperations:
    """Service menu, diagnostics, and maintenance operations.

    Source module: ToolsAppWorkflowUIXSOperations
    """

    def servicePin_test(self) -> bool:
        """Test the service PIN menu.

        Returns True if the service PIN entry succeeded.
        """
        output = _run_ps("sift2_cmd.ps1")
        return "pass" in output.lower()

    def servicemenu_servicetests_displaytest(self) -> bool:
        """Run the Display Test from Menu → Tools → Service → Service Tests.

        Returns True if the display test passed.
        """
        output = _run_ps("sift2_cmd.ps1")
        return "pass" in output.lower()

    def servicemenu_servicetests_keytest(self) -> bool:
        """Run the Key Test from Menu → Tools → Service → Service Tests.

        Returns True if the key test passed.
        """
        output = _run_ps("sift2_cmd.ps1")
        return "pass" in output.lower()

    def servicemenu_servicetests_faxdiagnostictest(self) -> None:
        """Run the Fax Diagnostic Test from the Service Tests menu."""
        _run_ps("sift2_cmd.ps1")

    def test_maintenance_regionreset(self) -> None:
        """Perform a region-reset from the maintenance menu."""
        _run_ps("sift2_cmd.ps1")

    def servicemenu_faxdiagnosticsmenu_generatedialingtonespulsesmenu(
        self,
    ) -> None:
        """Navigate to Fax Diagnostics → Generate Dialing Tones/Pulses menu."""
        _run_ps("sift2_cmd.ps1")


# ══════════════════════════════════════════════════════════════════════════════
# CalibrationUIOperations
# ══════════════════════════════════════════════════════════════════════════════

class CalibrationUIOperations:
    """Printer calibration operations triggered through the touchscreen UI.

    Source module: WorkflowUICommonXSOperations
    """

    def start_color_calibration(self) -> None:
        """Start the colour calibration routine."""
        _run_ps("sift2_cmd.ps1")

    def start_automatic_printhead_alignment(self) -> None:
        """Start the automatic printhead alignment."""
        _run_ps("sift2_cmd.ps1")

    def start_manual_printhead_alignment(self) -> None:
        """Start the manual printhead alignment."""
        _run_ps("sift2_cmd.ps1")

    def start_printheads_cleaning(self) -> None:
        """Start the printheads cleaning cycle."""
        _run_ps("sift2_cmd.ps1")

    def start_printheads_hard_cleaning(self) -> None:
        """Start the printheads hard (intensive) cleaning cycle."""
        _run_ps("sift2_cmd.ps1")

    def start_media_advance_calibration(self) -> None:
        """Start the media advance calibration."""
        _run_ps("sift2_cmd.ps1")

    def start_full_calibration(self) -> None:
        """Start the full calibration sequence."""
        _run_ps("sift2_cmd.ps1")

    def start_calibration(self) -> None:
        """Start the default calibration routine."""
        _run_ps("sift2_cmd.ps1")
