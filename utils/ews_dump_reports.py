"""
Dump the full DOM structure of the Reports and Pages page after PIN auth.
Saves a screenshot to reports/ews_reports_page.png for inspection.
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EWS_URL = "https://15.77.36.63"
PIN = "12345678"

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
wait = WebDriverWait(driver, 25)

try:
    # Navigate to EWS
    try:
        driver.get(EWS_URL)
    except Exception:
        pass
    time.sleep(8)
    driver.save_screenshot("reports/ews_home.png")
    print("Home screenshot saved. Title:", driver.title, "URL:", driver.current_url)

    # Click Support Tools — wait up to 20s for Angular to render nav
    support = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((
        By.XPATH,
        "//span[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SUPPORT')]"
    )))
    support.click()
    time.sleep(2)

    # Click Reports and Pages
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Reports and Pages"))).click()
    time.sleep(2)

    # Enter PIN
    pin_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
    pin_field.clear()
    pin_field.send_keys(PIN)
    pin_field.send_keys(Keys.RETURN)

    # Wait for reports page
    WebDriverWait(driver, 25).until(
        lambda d: "supportTools" in d.current_url or "reports" in d.current_url
    )
    time.sleep(6)

    print("URL:", driver.current_url)
    print("Title:", driver.title)

    # Save screenshot
    driver.save_screenshot("reports/ews_reports_page.png")
    print("Screenshot saved to reports/ews_reports_page.png")

    # Dump ALL buttons with their full outer HTML context
    print("\n=== ALL BUTTONS (outerHTML) ===")
    btns = driver.find_elements(By.TAG_NAME, "button")
    for i, b in enumerate(btns):
        print(f"\n--- Button {i} ---")
        print("  text:", repr(b.text.strip()))
        print("  aria-label:", b.get_attribute("aria-label"))
        print("  id:", b.get_attribute("id"))
        print("  class:", b.get_attribute("class"))
        try:
            print("  outerHTML:", b.get_attribute("outerHTML")[:300])
        except Exception:
            pass

    # Use JS to dump each button alongside its nearest text label
    print("\n=== BUTTONS WITH NEAREST LABEL (JS) ===")
    result = driver.execute_script("""
        var btns = Array.from(document.querySelectorAll('button'));
        return btns.map(function(btn) {
            var txt = btn.textContent.trim() || btn.getAttribute('aria-label') || '';
            // Walk up to find a sibling or nearby text
            var container = btn.parentElement;
            var nearby = '';
            for (var i = 0; i < 6; i++) {
                if (!container) break;
                var allText = container.textContent.trim();
                if (allText && allText !== txt) { nearby = allText.substring(0, 120); break; }
                container = container.parentElement;
            }
            return {btn: txt, nearby: nearby, id: btn.id, cls: btn.className.substring(0, 60)};
        });
    """)
    for r in result:
        print(r)

    # Also dump full page text to see all report names
    print("\n=== ALL LEAF TEXT NODES ===")
    texts = driver.execute_script("""
        var results = [];
        document.querySelectorAll('*').forEach(function(el) {
            if (el.children.length === 0) {
                var t = el.textContent.trim();
                if (t && t.length < 120) results.push(el.tagName + ': ' + t);
            }
        });
        return results;
    """)
    for t in texts:
        print(t)

    time.sleep(20)

finally:
    driver.quit()
