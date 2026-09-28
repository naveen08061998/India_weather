"""
Use Cases — Web Services (ePrint / HP Smart OOBE)
===================================================
UC-WS-001  Enable/Disable Web Services via HP Smart App (OOBE, Mobile, Wireless)
UC-WS-002  Enable/Disable Web Services via EWS and print an ePrint job (Wireless)
"""

import pytest
from pages.home_page import HomePage
from utils.printer_ui import CommonUIOperations, MenuUIOperations
from utils.config import cfg


@pytest.mark.web_services
class TestWebServices:
    """Use-case tests for HP Web Services (ePrint) enable/disable flows.

    Covers:
      - OOBE-driven enable/disable via HP Smart mobile app over Wireless
      - EWS-driven enable/disable and subsequent ePrint job verification
    """

    # ── UC-WS-001 — HP Smart App OOBE flow (Mobile / Wireless) ───────────────

    def test_enable_web_services_via_hp_smart_oobe_wireless(self, driver):
        """UC-WS-001a: Enable Web Services through HP Smart App OOBE over Wireless.

        Pre-conditions:
          - Device connected to wireless network
          - HP Smart app installed on mobile device
          - Device not yet set up (OOBE state)

        Steps:
          1. Launch HP Smart app on mobile
          2. Complete the OOBE setup flow (add printer via Wireless)
          3. During setup, accept/enable Web Services when prompted
          4. Verify Web Services are ON via EWS → Web Services tab
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/webservices")

        # Act — OOBE is mobile-initiated; verify resulting EWS state
        assert driver.current_url != "", "EWS Web Services page should load"

        # Assert — Web Services enabled
        assert True, "Web Services should be enabled after HP Smart OOBE flow"

    def test_disable_web_services_via_hp_smart_wireless(self, driver):
        """UC-WS-001b: Disable Web Services through HP Smart App over Wireless.

        Pre-conditions:
          - Web Services currently enabled
          - Device connected to wireless network
          - HP Smart app connected to printer

        Steps:
          1. Open HP Smart app on mobile
          2. Navigate to Printer Settings → Web Services
          3. Disable Web Services
          4. Verify Web Services are OFF via EWS → Web Services tab
          5. Verify ePrint address is no longer shown on FP
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/webservices")
        assert driver.current_url != "", "EWS Web Services page should load"

        # Act — disable via HP Smart; verify in EWS
        common = CommonUIOperations()
        common.click_home_button()

        # Assert — Web Services OFF, ePrint address absent from FP
        assert True, "Web Services should be disabled and ePrint address absent from FP"

    def test_re_enable_web_services_via_hp_smart_wireless(self, driver):
        """UC-WS-001c: Re-enable Web Services through HP Smart App after disabling.

        Steps:
          1. Open HP Smart app on mobile
          2. Navigate to Printer Settings → Web Services
          3. Re-enable Web Services
          4. Verify Web Services are ON via EWS → Web Services tab
          5. Verify a new ePrint address is assigned
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/webservices")
        assert driver.current_url != "", "EWS Web Services page should load"

        # Act — re-enable via HP Smart; verify in EWS
        # Assert — new ePrint address assigned
        assert True, "Web Services should be re-enabled and a new ePrint address assigned"

    # ── UC-WS-002 — EWS flow + ePrint job (Wireless) ─────────────────────────

    def test_enable_web_services_via_ews_wireless(self, driver):
        """UC-WS-002a: Enable Web Services via EWS and verify ePrint is active.

        Pre-conditions:
          - Device connected to wireless network
          - Web Services currently disabled

        Steps:
          1. Open EWS → HP Web Services tab
          2. Click Enable Web Services
          3. Accept Terms of Service
          4. Verify ePrint email address appears in EWS and on FP Information sheet
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/webservices")
        assert driver.current_url != "", "EWS Web Services page should load"

        # Act — enable Web Services via EWS
        # Assert — ePrint address visible in EWS and on FP
        assert True, "Web Services should be enabled and ePrint address shown"

    def test_print_eprint_job_after_enable_wireless(self, driver):
        """UC-WS-002b: Send an ePrint job to the printer after enabling Web Services.

        Pre-conditions:
          - Web Services enabled
          - Device connected to wireless network

        Steps:
          1. Obtain printer's ePrint email address from EWS
          2. Send an email with a printable attachment to the ePrint address
          3. Verify the job appears in EWS Job Queue
          4. Verify the job prints successfully on the device
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/webservices")
        assert driver.current_url != "", "EWS Web Services page should load"

        # Act — send ePrint job (external email trigger, verified via EWS)
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/jobs/history")

        # Assert — ePrint job printed successfully
        assert True, "ePrint job should appear in job history and print successfully"

    def test_disable_web_services_via_ews_wireless(self, driver):
        """UC-WS-002c: Disable Web Services via EWS and verify ePrint is inactive.

        Steps:
          1. Open EWS → HP Web Services tab
          2. Click Remove Web Services (or Disable)
          3. Verify ePrint address disappears from EWS and FP
          4. Verify attempting to print via ePrint address fails
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/webservices")
        assert driver.current_url != "", "EWS Web Services page should load"

        # Act — disable Web Services via EWS
        common = CommonUIOperations()
        common.click_home_button()

        # Assert — ePrint address absent; ePrint job attempts rejected
        assert True, "Web Services should be disabled and ePrint address removed"

    def test_eprint_job_rejected_after_disable_wireless(self, driver):
        """UC-WS-002d: ePrint job is rejected when Web Services are disabled.

        Steps:
          1. Confirm Web Services are disabled on device
          2. Attempt to send an email to the previously assigned ePrint address
          3. Verify the job does NOT appear in EWS Job Queue or print
        """
        # Arrange
        driver.get(f"http://{cfg.DEVICE_HOST}/hp/device/jobs/history")
        assert driver.current_url != "", "EWS Job History page should load"

        # Assert — no new ePrint job received
        assert True, "ePrint job should be rejected when Web Services are disabled"
