from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time

# ---- 設定 ----
USERNAME = "komugishomin"
PASSWORD = "A1B2c!d?"
DRIVE_URL = "https://drive.google.com/uc?export=download&id=1-kutpyH8lIg_8aXXhAnosghVHVvqhsdI"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---- Chromeオプション ----
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

def log(msg):
    print(f"[LOG] {msg}")

try:
    # ---- 1. ログインページ ----
    log("Step 1: ログインページにアクセス")
    driver.get("https://aternos.org/go/")
    time.sleep(3)

    # ---- 2. ユーザー名・パスワード入力 ----
    log("Step 2: ユーザー名・パスワード入力")
    username_input = driver.find_element(By.CSS_SELECTOR, "input.username")
    password_input = driver.find_element(By.CSS_SELECTOR, "input.password")

    username_input.send_keys(USERNAME)
    log("ユーザー名送信完了")
    password_input.send_keys(PASSWORD)
    log("パスワード送信完了")

    # ---- 3. ログインボタンクリック ----
    log("Step 3: ログインボタンクリック")
    login_btn = driver.find_element(By.CSS_SELECTOR, "button[title='ログイン']")
    login_btn.click()
    log("ログインボタンクリック完了")
    time.sleep(5)

    # ---- 4. Google Driveからダウンロード ----
    log("Step 4: Google Driveからファイルダウンロード")
    driver.get(DRIVE_URL)
    time.sleep(10)  # ダウンロード待機
    downloaded_files = os.listdir(DOWNLOAD_DIR)
    if downloaded_files:
        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
        log(f"ダウンロード完了: {latest_file}")
    else:
        log("ダウンロードファイルが見つかりません")

    # ---- 5. packs ページ移動 ----
    log("Step 5: packs ページに移動")
    driver.get("https://aternos.org/files/packs/")
    time.sleep(5)

    # ---- 6. アップロード input 探索・送信 ----
    log("Step 6: アップロード input 探索・送信開始")
    upload_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
    log(f"アップロード候補 input 数: {len(upload_inputs)}")

    for i, inp in enumerate(upload_inputs):
        try:
            inp.send_keys(latest_file)
            log(f"input[{i}] にファイル送信成功")
        except Exception as e:
            log(f"input[{i}] 送信失敗: {e}")

    log("=== 完了 ===")
    time.sleep(10)

finally:
    driver.quit()
        try:
            inp.send_keys(latest_file)
            log(f"input[{i}] にファイル送信成功")
        except Exception as e:
            log(f"input[{i}] 送信失敗: {e}")

    log("=== 完了 ===")
    time.sleep(10)

finally:
    driver.quit()
