#!/usr/bin/env python3
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import glob, shutil

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# ダウンロード先を作業ディレクトリに指定
prefs = {"download.default_directory": os.getcwd()}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)

try:
    # 1. ログインページ
    driver.get("https://zpdic.ziphil.com/login")
    time.sleep(2)

    # 2. 上から0番目と1番目のinputに入力
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(os.environ["USER_ID"])
    inputs[1].send_keys(os.environ["PASS"])

    # 3. ログイン
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)

    # 4. 設定ページ
    driver.get("https://zpdic.ziphil.com/dictionary/2283/settings/file")
    time.sleep(3)

    # 5. エクスポートボタン押下
    export_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'エクスポート')]")
    export_btn.click()
    time.sleep(2)

    # 6. ダウンロードボタン押下
    download_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'ダウンロード')]")
    download_btn.click()
    time.sleep(16)

    # 7. 最新JSONをa.jsonにリネーム
    files = sorted(glob.glob("*.json"), key=os.path.getmtime, reverse=True)
    if files:
        shutil.move(files[0], "a.json")

finally:
    driver.quit()
