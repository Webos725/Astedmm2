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

def wait_for_download(directory, timeout=60):
    log("ダウンロード完了待機中…")
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = os.listdir(directory)
        if not any(f.endswith(".crdownload") for f in files) and files:
            latest_file = max([os.path.join(directory, f) for f in files], key=os.path.getctime)
            return latest_file
        time.sleep(1)
    return None

try:
    # ---- 1. ログインページ ----
    log("Step 1: ログインページにアクセス")
    driver.get("https://aternos.org/go/")
    time.sleep(3)

    # ---- 2. ユーザー名・パスワード入力 ----
    log("Step 2: ユーザー名・パスワード入力")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    username_input = next(inp for inp in inputs if "username" in inp.get_attribute("class"))
    password_input = next(inp for inp in inputs if "password" in inp.get_attribute("class"))
    username_input.send_keys(USERNAME)
    log("ユーザー名送信完了")
    password_input.send_keys(PASSWORD)
    log("パスワード送信完了")

    # ---- 3. ログインボタンクリック ----
    log("Step 3: ログインボタンクリック")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    login_btn = next(btn for btn in buttons if btn.get_attribute("title") == "ログイン")
    login_btn.click()
    log("ログインボタンクリック完了")
    time.sleep(5)

    # ---- 4. Google Driveからダウンロード ----
    log("Step 4: Google Driveからファイルダウンロード")
    driver.get(DRIVE_URL)
    latest_file = wait_for_download(DOWNLOAD_DIR, timeout=60)
    if latest_file:
        log(f"ダウンロード完了: {latest_file}")
    else:
        log("ダウンロード失敗またはタイムアウト")

    # ---- 5. packs ページ移動 ----
    log("Step 5: packs ページに移動")
    driver.get("https://aternos.org/files/packs/")
    time.sleep(5)

    # ---- 6. アップロード input 探索・送信 ----
    log("Step 6: アップロード input 探索・送信開始")
    file_inputs = [inp for inp in driver.find_elements(By.TAG_NAME, "input") if "file" in inp.get_attribute("type")]
    log(f"アップロード候補 input 数: {len(file_inputs)}")

    if latest_file:
        for i, inp in enumerate(file_inputs):
            try:
                inp.send_keys(latest_file)
                log(f"input[{i}] にファイル送信成功")
            except Exception as e:
                log(f"input[{i}] 送信失敗: {e}")

    log("=== 処理完了 ===")

except Exception as main_e:
    log(f"エラー発生: {main_e}")

finally:
    driver.quit()
    log("ブラウザ終了")
