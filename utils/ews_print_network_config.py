"""
EWS automation: navigate to Support Tools -> Reports and Pages,
enter PIN 12345678, and print the Network Configuration Page.
Single-run, no retries — uses only confirmed-working selectors.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EWS_IP = "15.77.36.63"
EWS_URL = f"https://{EWS_IP}"
PIN = "12345678"

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--allow-insecure-localhost")
    options.binary_location = r"C:\Users\ReddyA41\AppData\Local\Google\Chrome\Application\chrome.exe"
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.page_load_strategy = "eager"
    # Selenium 4.6+ uses built-in selenium-manager — no service argument needed
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    driver.maximize_window()
    return driver


def wait_ready(driver, timeout=20):
    """Wait until document.readyState is complete."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def main():
    driver = get_driver()
    wait = WebDriverWait(driver, 25)

    try:
        # ── Step 1: Open EWS ─────────────────────────────────────────────────
        print(f"[1] Opening EWS at {EWS_URL} ...")
        try:
            driver.get(EWS_URL)
        except Exception:
            pass  # SSL noise — page still loads
        time.sleep(5)
        print(f"    URL: {driver.current_url}  |  Title: {driver.title}")

        # ── Step 2: Click "Support Tools" ────────────────────────────────────
        print("[2] Clicking 'Support Tools' ...")
        support_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//span[contains(translate(text(),"
            "'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SUPPORT')]"
        )))
        support_btn.click()
        time.sleep(2)
        print("    Clicked.")

        # ── Step 3: Click "Reports and Pages" ────────────────────────────────
        print("[3] Clicking 'Reports and Pages' ...")
        reports_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Reports and Pages")))
        reports_link.click()
        time.sleep(2)
        print(f"    URL: {driver.current_url}")

        # ── Step 4: Enter PIN ────────────────────────────────────────────────
        print(f"[4] Entering PIN ...")
        pin_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
        pin_field.clear()
        pin_field.send_keys(PIN)
        print("    PIN entered.")

        # ── Step 5: Submit PIN ───────────────────────────────────────────────
        print("[5] Submitting PIN ...")
        pin_field.send_keys(Keys.RETURN)

        # Wait for redirect to reports page
        WebDriverWait(driver, 25).until(
            lambda d: "supportTools" in d.current_url or "reports" in d.current_url
        )
        print(f"    URL: {driver.current_url}")

        # Give Angular time to render the page content
        time.sleep(6)

        # ── Step 6: Check "Network Configuration Report" checkbox ───────────
        print("[6] Selecting 'Network Configuration Report' checkbox ...")

        # Scroll the report into view and click its checkbox via JS
        result = driver.execute_script("""
            // Find the label/span with exact text 'Network Configuration Report'
            var allEls = Array.from(document.querySelectorAll('*'));
            var labelEl = null;
            for (var i = 0; i < allEls.length; i++) {
                var txt = allEls[i].textContent.trim();
                if (txt === 'Network Configuration Report') {
                    labelEl = allEls[i];
                    break;
                }
            }
            if (!labelEl) return 'label_not_found';

            // Scroll into view
            labelEl.scrollIntoView({block: 'center'});

            // Walk up to find mat-checkbox or input[type=checkbox]
            var container = labelEl;
            for (var i = 0; i < 8; i++) {
                if (!container) break;
                var cb = container.querySelector('input[type="checkbox"]');
                if (cb) { cb.click(); return 'checkbox_clicked'; }
                // mat-checkbox click (Angular Material)
                if (container.tagName && container.tagName.toLowerCase() === 'mat-checkbox') {
                    container.click(); return 'mat-checkbox_clicked';
                }
                var mc = container.querySelector('mat-checkbox');
                if (mc) { mc.click(); return 'mat-checkbox_clicked'; }
                container = container.parentElement;
            }
            return 'checkbox_not_found';
        """)
        print(f"    Checkbox result: {result}")

        if result == "label_not_found":
            # Fallback: use Selenium to find by link text / partial text
            try:
                cb_label = wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    "//*[normalize-space(text())='Network Configuration Report']"
                    "/ancestor::mat-list-item | "
                    "//*[normalize-space(text())='Network Configuration Report']"
                    "/ancestor::*[contains(@class,'mat-list-item') or contains(@class,'list-item')][1]"
                )))
                cb_label.click()
                print("    Clicked via Selenium ancestor selector")
            except Exception as e:
                print(f"    Selenium fallback failed: {e}")

        time.sleep(1)

        # ── Step 7: Click the now-enabled footer Print button ────────────────
        print("[7] Clicking the Print button ...")
        try:
            print_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "reports-print-footer"))
            )
            print_btn.click()
            print("    Print button clicked (id=reports-print-footer)")
        except Exception:
            # If still disabled, force-click via JS
            driver.execute_script(
                "document.getElementById('reports-print-footer').click();"
            )
            print("    Print button force-clicked via JS")

        time.sleep(3)
        print(f"\n[Done] Final URL: {driver.current_url}  |  Title: {driver.title}")
        print("Browser stays open 30 s — verify on screen.")
        time.sleep(30)

    except Exception as e:
        import traceback
        print(f"[ERROR] {e}")
        traceback.print_exc()
        time.sleep(15)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
