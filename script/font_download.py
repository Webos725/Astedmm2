from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import time
import os
import shutil

# 保存先ディレクトリ
download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

# Chromeオプション
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

# ダウンロード設定
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# ドライバ起動
service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.pentacom.jp/pentacom/bitfontmaker2/gallery/?id=18845") 
    # 18818 18845
    time.sleep(4)

    # DOWNLOADボタン押下
    download_button = driver.find_element(By.XPATH, "//a[text()='DOWNLOAD']")
    download_button.click()

    # アラートOK
    time.sleep(2)
    alert = Alert(driver)
    alert.accept()

    # ダウンロード待機（拡張子チェック）
    timeout = 20
    ttf_file_path = None
    for _ in range(timeout):
        time.sleep(1)
        files = [f for f in os.listdir(download_dir) if f.lower().endswith(".ttf")]
        if files:
            ttf_file_path = os.path.join(download_dir, files[0])
            break

    if ttf_file_path:
        fixed_path = os.path.join(download_dir, "yeerial.ttf")
        shutil.move(ttf_file_path, fixed_path)
        print(f"ダウンロード完了: {fixed_path}")
    else:
        print("TTFファイルが見つかりませんでした。")

finally:
    driver.quit()
