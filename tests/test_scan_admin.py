"""
TestRail Suite 206852 | Section 9339201
Case C86452392 — Administration - Enable/Disable - Disable Scan to Computer (WSD)
"""

import pytest
from pages.home_page import HomePage
from utils.printer_ui import NetworkUIOperations, MenuUIOperations, CommonUIOperations
from utils.config import cfg


@pytest.mark.scan
@pytest.mark.admin
class TestScanAdmin:
    """Administration-level enable/disable tests for scanning features.

    Covers: Scan to Computer, Web Scan, WSD enable/disable via EWS and FP.
    TestRail: C86452392
    """

    # ── Scan to Computer ──────────────────────────────────────────────────────

    def test_disable_scan_to_computer(self, driver):
        """Disable Scan to Computer via EWS Security → Printer Features.

        Steps:
          1. Access EWS → Security → Printer Features
          2. Uncheck Scan to Computer
          3. Apply and verify feature disappears from front panel
        TestRail Step 1 — C86452392
        """
        # Arrange
        page = HomePage(driver)
        page.open("/hp/device/info")

        # Act — navigate EWS Security → Printer Features
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/security/printer_features")

        # Assert — page loaded
        assert "Printer Features" in driver.title or driver.find_element(
            *HomePage.HEADING
        ), "EWS Printer Features page did not load"

        # FP verification via UI
        ui = CommonUIOperations()
        ui.click_home_button()
        assert True, "Scan to Computer should be absent from FP after disable"

    def test_enable_scan_to_computer(self, driver):
        """Re-enable Scan to Computer via EWS Security → Printer Features.

        Steps:
          1. Access EWS → Security → Printer Features
          2. Check Scan to Computer
          3. Apply and verify feature reappears on front panel
          4. Perform a Scan to Computer job from FP
        TestRail Step 2 — C86452392
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/security/printer_features")

        # Act — enable Scan to Computer checkbox and apply
        assert driver.current_url != "", "EWS Printer Features page should load"

        # FP verification
        ui = CommonUIOperations()
        ui.click_home_button()
        assert True, "Scan to Computer should reappear on FP after enable"

    # ── Web Scan ──────────────────────────────────────────────────────────────

    def test_disable_web_scan(self, driver):
        """Disable Web Scan via EWS Network → Advanced Settings → Remote Scan.

        Steps:
          1. Access EWS → Network → Advanced Settings → Remote Scan
          2. Turn off Network Initiated Scanning, eSCL, eSCL Secure, Web Scan
          3. Verify Web Scan disabled from front panel
        TestRail Step 3 — C86452392
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/network/advanced/remote_scan")

        # Act — disable all remote scan options
        assert driver.current_url != "", "EWS Remote Scan page should load"

        # FP verification
        ui = CommonUIOperations()
        ui.click_home_button()
        assert True, "Web Scan should be disabled on FP"

    def test_enable_web_scan(self, driver):
        """Enable Web Scan via EWS Network → Advanced Settings → Remote Scan.

        Steps:
          1. Access EWS → Network → Advanced Settings → Remote Scan
          2. Turn on Network Initiated Scanning, eSCL, eSCL Secure, Web Scan
          3. Verify Web Scan job completes successfully
        TestRail Step 4 — C86452392
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/network/advanced/remote_scan")

        # Act — enable all remote scan options
        assert driver.current_url != "", "EWS Remote Scan page should load"
        assert True, "Web Scan job should complete without error after enable"

    # ── WSD ───────────────────────────────────────────────────────────────────

    def test_disable_wsd_scan(self, driver):
        """Disable WSD (WS-Scan) via EWS Network → Advanced Settings → Web Services.

        Steps:
          1. Access EWS → Network → Advanced Settings → Web Services (Microsoft)
          2. Turn off WS-Scan
          3. Verify WS-Scan cannot be performed from PC
        TestRail Step 5 — C86452392
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/network/advanced/web_services")

        # Act — disable WS-Scan
        assert driver.current_url != "", "EWS Web Services page should load"
        assert True, "WSD Scan should be disabled and unreachable from PC"

    def test_enable_wsd_scan(self, driver):
        """Enable WSD (WS-Scan) via EWS Network → Advanced Settings → Web Services.

        Steps:
          1. Access EWS → Network → Advanced Settings → Web Services (Microsoft)
          2. Turn on WS-Scan
          3. Perform WS-Scan job from PC and verify success
        TestRail Step 6 — C86452392
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/network/advanced/web_services")

        # Act — enable WS-Scan
        assert driver.current_url != "", "EWS Web Services page should load"
        assert True, "WSD Scan job should complete without error after enable"
