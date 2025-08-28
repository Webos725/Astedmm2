from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# ---- 設定 ----
USERNAME = "komugishomin"   # ←自分のAternosユーザー名
PASSWORD = "A1B2c!d?"       # ←自分のAternosパスワード
DRIVE_URL = "https://drive.google.com/uc?export=download&id=1-kutpyH8lIg_8aXXhAnosghVHVvqhsdI"

# 保存先（Chromeの自動ダウンロードフォルダ）
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

# ---- Chromeオプション ----
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": DOWNLOAD_DIR,  # ダウンロード先
    "download.prompt_for_download": False,       # ダイアログ禁止
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

# Chromeオプション
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

# ドライバ起動
service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # ---- 1. Aternosログイン ----
    driver.get("https://aternos.org/go/")
    time.sleep(3)

    # ログインフォームに入力
    driver.find_element(By.NAME, "user").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)
    time.sleep(5)

    # ---- 2. Google Driveからファイルダウンロード ----
    driver.get(DRIVE_URL)
    time.sleep(10)  # ダウンロード完了待機（ネット速度で調整）

    # ダウンロードされたファイル名を確認
    downloaded_files = os.listdir(DOWNLOAD_DIR)
    latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)

    print(f"Downloaded: {latest_file}")

    # ---- 3. Aternos packs ページへ移動 ----
    driver.get("https://aternos.org/files/packs/")
    time.sleep(5)

    # ---- 4. アップロード input にファイル送信 ----
    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(latest_file)

    print("アップロード完了")

    # ---- 終了 ----
    time.sleep(10)
finally:
    driver.quit()
