from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import time
import os

download_dir = os.path.abspath("downloads")

chrome_options = Options()
chrome_options.add_argument("--headless")  # GUIなしで実行
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.pentacom.jp/pentacom/bitfontmaker2/gallery/?id=16077")
    time.sleep(7)

    download_button = driver.find_element(By.XPATH, "//a[text()='DOWNLOAD']")
    download_button.click()

    time.sleep(1)
    alert = Alert(driver)
    alert.accept()

    time.sleep(5)
finally:
    driver.quit()

print(f"ダウンロード完了: {download_dir}")
