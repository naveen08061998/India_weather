import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--no-sandbox")
options.binary_location = r"C:\Users\ReddyA41\AppData\Local\Google\Chrome\Application\chrome.exe"
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.page_load_strategy = "eager"
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(30)
driver.maximize_window()

try:
    driver.get("https://15.77.36.63")
except Exception:
    pass
time.sleep(5)
WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "launcherButton"))).click()
time.sleep(3)

# Find mat-list-item elements inside the notification panel
items = driver.find_elements(By.XPATH, "//mat-list-item | //hp-patterns-list-item | //*[contains(@class,'list-item')]")
print("mat-list-item / list-item elements:", len(items))
for i, el in enumerate(items):
    print(f"  [{i}] tag={el.tag_name} text={repr(el.text.strip()[:100])}")

# Also try direct: accordion items using mat-expansion-panel
exp = driver.find_elements(By.XPATH, "//mat-expansion-panel")
print("mat-expansion-panel elements:", len(exp))
for i, el in enumerate(exp):
    print(f"  [{i}] text={repr(el.text.strip()[:100])}")

driver.quit()
