#!/usr/bin/env python3
import os
import time
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FONT_URL = "https://fontstruct.com/fontstructions/download/2728972"
DOWNLOAD_DIR = os.path.abspath("downloads")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Chromeオプション
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=chrome_options)
driver.get(FONT_URL)

wait = WebDriverWait(driver, 40)  # 最大40秒待機

# チェックボックスON
checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
for cb in checkboxes:
    driver.execute_script("arguments[0].checked = true;", cb)

# TrueTypeボタンを柔軟に検索
all_buttons = driver.find_elements(By.XPATH, "//*[contains(text(),'TrueType')]")
print("Found buttons:")
for b in all_buttons:
    print(" - tag:", b.tag_name, "text:", b.text)

tt_button = wait.until(
    EC.element_to_be_clickable((
        By.XPATH,
        "//button[contains(text(),'TrueType')] | //a[contains(text(),'TrueType')]"
    ))
)
tt_button.click()

# ダウンロード完了待ち
zip_path = None
for _ in range(60):
    files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith(".zip")]
    if files:
        zip_path = os.path.join(DOWNLOAD_DIR, files[0])
        break
    time.sleep(1)

driver.quit()

if not zip_path or not os.path.exists(zip_path):
    raise FileNotFoundError("Font zip file was not downloaded.")

# zip解凍
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(DOWNLOAD_DIR)

# .ttfファイルを検索
ttf_files = []
for root, _, files in os.walk(DOWNLOAD_DIR):
    for f in files:
        if f.lower().endswith(".ttf"):
            ttf_files.append(os.path.join(root, f))

if not ttf_files:
    raise FileNotFoundError("No TTF file found inside the zip.")

print("Found TTF files:")
for ttf in ttf_files:
    print(" -", ttf)
