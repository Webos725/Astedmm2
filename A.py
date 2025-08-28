from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# ---- 設定 ----
USERNAME = "komugishomin"
PASSWORD = "A1B2c!d?"
DRIVE_URL = "https://drive.google.com/uc?export=download&id=1-kutpyH8lIg_8aXXhAnosghVHVvqhsdI"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

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

try:
    # ---- 1. Aternosログイン ----
    driver.get("https://aternos.org/go/")
    time.sleep(3)

    # ページ内すべての input を取得
    login_inputs = driver.find_elements(By.TAG_NAME, "input")
    username_sent = False
    password_sent = False

    for i, inp in enumerate(login_inputs):
        try:
            # ユーザー名は type が text または email の input に送信
            type_attr = inp.get_attribute("type")
            if not username_sent and type_attr in ["text", "email"]:
                inp.send_keys(USERNAME)
                username_sent = True
                print(f"input[{i}] にユーザー名送信")
            # パスワードは type=password の input に送信
            elif not password_sent and type_attr == "password":
                inp.send_keys(PASSWORD + Keys.RETURN)
                password_sent = True
                print(f"input[{i}] にパスワード送信")
            if username_sent and password_sent:
                break
        except Exception as e:
            print(f"input[{i}] 送信失敗: {e}")

    time.sleep(5)

    # ---- 2. Google Driveからファイルダウンロード ----
    driver.get(DRIVE_URL)
    time.sleep(10)  # ダウンロード待機

    downloaded_files = os.listdir(DOWNLOAD_DIR)
    latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
    print(f"Downloaded: {latest_file}")

    # ---- 3. Aternos packs ページへ移動 ----
    driver.get("https://aternos.org/files/packs/")
    time.sleep(5)

    # ---- 4. packsページの input にファイル送信 ----
    pack_inputs = driver.find_elements(By.TAG_NAME, "input")
    for i, inp in enumerate(pack_inputs):
        try:
            inp.send_keys(latest_file)
            print(f"input[{i}] に送信成功")
        except Exception as e:
            print(f"input[{i}] 失敗: {e}")

    print("完了！")
    time.sleep(10)

finally:
    driver.quit()
