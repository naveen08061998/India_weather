from selenium import webdriver
import time
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = r'C:\Users\ReddyA41\AppData\Local\Google\Chrome\Application\chrome.exe'
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.page_load_strategy = 'eager'

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(30)

try:
    driver.get('https://15.77.36.63')
except Exception as e:
    print('nav warning:', e)

# Wait for Angular to fully render - wait until app-root has children
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
try:
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script(
            "return document.querySelector('app-root') && document.querySelector('app-root').children.length > 0"
        )
    )
    print('Angular app-root rendered')
except Exception:
    print('Timeout waiting for Angular, continuing anyway')

time.sleep(3)
print('URL:', driver.current_url)
print('TITLE:', driver.title)

# Dump all visible text elements (buttons, anchors, mat-list-item, etc.)
all_clickable = driver.find_elements(By.XPATH,
    '//*[self::a or self::button or self::mat-list-item or '
    'contains(@class,"nav") or contains(@class,"menu") or contains(@class,"tab")]'
)
print('=== CLICKABLE/NAV ELEMENTS ===')
for el in all_clickable:
    txt = el.text.strip()
    if txt:
        print(el.tag_name, repr(txt[:80]), 'class=' + str(el.get_attribute('class'))[:60],
              'href=' + str(el.get_attribute('href')))

# Also dump all text nodes to find navigation labels
spans = driver.find_elements(By.XPATH, '//*[string-length(normalize-space(text())) > 0]')
print('\n=== ALL TEXT NODES (first 60) ===')
seen = set()
count = 0
for el in spans:
    txt = el.text.strip()
    if txt and txt not in seen and len(txt) < 100:
        seen.add(txt)
        print(el.tag_name, repr(txt))
        count += 1
        if count >= 60:
            break

driver.quit()
