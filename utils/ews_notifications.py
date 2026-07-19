"""
EWS automation: open https://15.77.36.63, click the notification bell,
and take a screenshot of each alert/notification.
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EWS_URL = "https://15.77.36.63"
SCREENSHOTS_DIR = "reports/notifications"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = r"C:\Users\ReddyA41\AppData\Local\Google\Chrome\Application\chrome.exe"
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    return driver


def main():
    driver = get_driver()
    wait = WebDriverWait(driver, 25)

    try:
        # ── Step 1: Open EWS ─────────────────────────────────────────────────
        print(f"[1] Opening EWS at {EWS_URL} ...")
        try:
            driver.get(EWS_URL)
        except Exception:
            pass  # SSL noise
        # Retry once if page didn't load
        time.sleep(8)
        if "15.77.36.63" not in driver.current_url:
            print("    Retrying navigation ...")
            try:
                driver.get(EWS_URL)
            except Exception:
                pass
            time.sleep(8)
        print(f"    URL: {driver.current_url}  |  Title: {driver.title}")

        # Screenshot of home page
        home_path = os.path.join(SCREENSHOTS_DIR, "00_home.png")
        driver.save_screenshot(home_path)
        print(f"    Saved: {home_path}")

        # ── Step 2: Click the notification bell ──────────────────────────────
        print("[2] Clicking notification bell (launcherButton) ...")
        bell_btn = wait.until(EC.element_to_be_clickable((By.ID, "launcherButton")))
        bell_btn.click()
        time.sleep(3)

        bell_path = os.path.join(SCREENSHOTS_DIR, "01_bell_open.png")
        driver.save_screenshot(bell_path)
        print(f"    Saved: {bell_path}")

        # ── Step 3: Find all alert/notification items ────────────────────────
        print("[3] Looking for alert items in the notification panel ...")

        # Wait for the panel to appear
        try:
            wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(@class,'notification') or contains(@class,'alert') "
                "or contains(@class,'launcher') or contains(@class,'cdm-launcher')]"
            )))
        except Exception:
            print("    Panel selector timeout — continuing with what is rendered")
        time.sleep(2)

        # Find individual notification/alert rows
        # Each notification is a mat-expansion-panel inside the bell panel
        alert_rows = driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'notification-list')]//mat-expansion-panel"
        )
        print(f"    Found {len(alert_rows)} notification row(s)")

        for i, row in enumerate(alert_rows):
            title = row.find_element(By.XPATH, ".//mat-panel-title | .//mat-list-item | .//*[self::span][normalize-space(text())]")
            txt = title.text.strip().split("\n")[0][:60] if title else f"alert_{i+1}"
            print(f"\n    [{i+1}] Notification: {repr(txt)}")

            # Screenshot collapsed state
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
            time.sleep(0.5)
            collapsed_path = os.path.join(SCREENSHOTS_DIR, f"alert_{i+1:02d}_collapsed.png")
            row.screenshot(collapsed_path)
            print(f"         Collapsed: {collapsed_path}")

            # Click header to expand
            try:
                header = row.find_element(By.XPATH, ".//mat-expansion-panel-header")
                header.click()
            except Exception:
                row.click()
            time.sleep(1.5)

            # Full viewport screenshot (expanded)
            exp_path = os.path.join(SCREENSHOTS_DIR, f"alert_{i+1:02d}_expanded.png")
            driver.save_screenshot(exp_path)
            print(f"         Expanded : {exp_path}")

            # Element crop of expanded panel
            try:
                elem_path = os.path.join(SCREENSHOTS_DIR, f"alert_{i+1:02d}_element.png")
                row.screenshot(elem_path)
                print(f"         Element  : {elem_path}")
            except Exception:
                pass

            # Collapse before next
            try:
                header = row.find_element(By.XPATH, ".//mat-expansion-panel-header")
                header.click()
                time.sleep(0.8)
            except Exception:
                pass

        # ── Step 4: Final full-page screenshot ───────────────────────────────
        final_path = os.path.join(SCREENSHOTS_DIR, "99_final.png")
        driver.save_screenshot(final_path)
        print(f"\n[Done] Final screenshot: {final_path}")
        print("Browser stays open 20 s — verify on screen.")
        time.sleep(20)

    except Exception as e:
        import traceback
        print(f"[ERROR] {e}")
        traceback.print_exc()
        err_path = os.path.join(SCREENSHOTS_DIR, "error.png")
        try:
            driver.save_screenshot(err_path)
            print(f"Error screenshot: {err_path}")
        except Exception:
            pass
        time.sleep(10)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
