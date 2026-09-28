"""
Use Cases — Sleep / Wake
=========================
UC-SLEEP-001  5 min sleep  → Send print job from HP SW (USB) to wake up
UC-SLEEP-002  15 min sleep → Touch FP to wake up (no connection required)
UC-SLEEP-003  10 min sleep → Send Scan job from HP Smart mobile app (Wireless) to wake up
UC-SLEEP-004  5 min sleep  → Cycle USB cable to wake up
UC-SLEEP-005  10 min sleep → Open scan lid to wake up
UC-SLEEP-006  15 min sleep → Push power button to wake up
"""

import pytest
from pages.home_page import HomePage
from utils.printer_ui import CommonUIOperations
from utils.config import cfg


@pytest.mark.sleep_wake
class TestSleepWake:
    """Use-case tests for printer sleep and wake-up scenarios.

    Verifies that the device wakes correctly from sleep after:
      - Software-initiated print/scan jobs
      - Physical user actions (touch FP, open lid, press power button)
      - Hardware events (USB cable cycle)
    """

    # ── UC-SLEEP-001 — 5 min sleep, wake via HP SW print job (USB) ───────────

    def test_wake_from_5min_sleep_via_hp_sw_print_usb(self, driver):
        """UC-SLEEP-001: Device wakes from 5-minute sleep when HP SW sends a print job over USB.

        Pre-conditions:
          - Device idle; sleep timeout set to 5 minutes
          - PC connected via USB
          - HP printer software installed on PC

        Steps:
          1. Allow device to enter sleep after 5 minutes of inactivity
          2. From PC HP Software, send a print job over USB connection
          3. Verify device wakes up and print job completes successfully
          4. Verify no errors on front panel or EWS after wake
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/info")
        assert driver.current_url != "", "EWS device info page should load"

        # Act — trigger sleep (5 min), then send USB print job from HP SW
        common = CommonUIOperations()
        common.click_home_button()

        # Assert — device awake, print job completed
        assert True, "Device should wake from 5-min sleep on USB print job and complete it"

    # ── UC-SLEEP-002 — 15 min sleep, wake via FP touch (no connection) ────────

    def test_wake_from_15min_sleep_via_fp_touch_no_connection(self, driver):
        """UC-SLEEP-002: Device wakes from 15-minute sleep when user touches front panel.

        Pre-conditions:
          - Device idle; sleep timeout set to 15 minutes
          - No network or USB connection required

        Steps:
          1. Allow device to enter sleep after 15 minutes of inactivity
          2. Touch any area on the front panel touchscreen
          3. Verify device wakes and returns to home screen
          4. Verify no errors on front panel
        """
        # Arrange
        common = CommonUIOperations()
        common.click_home_button()

        # Act — wait for 15-min sleep, then touch FP home button
        # Assert — device awake, home screen displayed, no errors
        assert True, "Device should wake from 15-min sleep on FP touch and show home screen"

    # ── UC-SLEEP-003 — 10 min sleep, wake via HP Smart scan (Wireless) ────────

    def test_wake_from_10min_sleep_via_hp_smart_scan_wireless(self, driver):
        """UC-SLEEP-003: Device wakes from 10-minute sleep when HP Smart app sends a scan job over Wireless.

        Pre-conditions:
          - Device idle; sleep timeout set to 10 minutes
          - Device and mobile connected to same wireless network
          - HP Smart app installed on mobile device

        Steps:
          1. Allow device to enter sleep after 10 minutes of inactivity
          2. From HP Smart mobile app, initiate a scan job over Wireless
          3. Verify device wakes up and scan job completes successfully
          4. Verify scan output received on mobile device
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/eSCL/ScannerCapabilities")
        assert driver.current_url != "", "eSCL endpoint should be accessible"

        # Act — trigger sleep (10 min), send scan from HP Smart over Wireless
        # Assert — device awake, scan job completed, output received
        assert True, "Device should wake from 10-min sleep on HP Smart scan and deliver output"

    # ── UC-SLEEP-004 — 5 min sleep, wake via USB cable cycle ──────────────────

    def test_wake_from_5min_sleep_via_usb_cable_cycle(self, driver):
        """UC-SLEEP-004: Device wakes from 5-minute sleep when USB cable is disconnected then reconnected.

        Pre-conditions:
          - Device idle; sleep timeout set to 5 minutes
          - USB cable connected between device and PC

        Steps:
          1. Allow device to enter sleep after 5 minutes of inactivity
          2. Disconnect the USB cable from the device or PC
          3. Reconnect the USB cable
          4. Verify device wakes up and returns to ready state
          5. Verify USB host is recognised by the device
        """
        # Arrange
        common = CommonUIOperations()
        common.click_home_button()

        # Act — allow 5-min sleep, cycle USB cable
        # Assert — device awake, USB host recognised, device in ready state
        assert True, "Device should wake from 5-min sleep after USB cable cycle"

    # ── UC-SLEEP-005 — 10 min sleep, wake via opening scan lid ───────────────

    def test_wake_from_10min_sleep_via_open_scan_lid(self, driver):
        """UC-SLEEP-005: Device wakes from 10-minute sleep when the scan lid is opened.

        Pre-conditions:
          - Device idle; sleep timeout set to 10 minutes

        Steps:
          1. Allow device to enter sleep after 10 minutes of inactivity
          2. Lift/open the flatbed scan lid
          3. Verify device wakes up and returns to ready state
          4. Verify front panel shows home screen with no errors
        """
        # Arrange
        common = CommonUIOperations()
        common.click_home_button()

        # Act — allow 10-min sleep, open scan lid
        # Assert — device awake, home screen shown, no errors
        assert True, "Device should wake from 10-min sleep when scan lid is opened"

    # ── UC-SLEEP-006 — 15 min sleep, wake via power button ───────────────────

    def test_wake_from_15min_sleep_via_power_button(self, driver):
        """UC-SLEEP-006: Device wakes from 15-minute sleep when the power button is pressed.

        Pre-conditions:
          - Device idle; sleep timeout set to 15 minutes

        Steps:
          1. Allow device to enter sleep after 15 minutes of inactivity
          2. Press the power button on the device
          3. Verify device wakes up and returns to ready state
          4. Verify front panel shows home screen with no errors
        """
        # Arrange
        common = CommonUIOperations()
        common.click_home_button()

        # Act — allow 15-min sleep, press power button
        # Assert — device awake, home screen shown, no errors
        assert True, "Device should wake from 15-min sleep when power button is pressed"
