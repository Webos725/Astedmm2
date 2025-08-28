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

print("=== GitHub Actions: Selenium Workflow Start ===")

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
    print("Step 1: ログインページに移動")
    driver.get("https://aternos.org/go/")
    time.sleep(3)

    # iframe探索＋表示 input のみ取得
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        driver.switch_to.frame(iframe)
        visible_inputs = [inp for inp in driver.find_elements(By.TAG_NAME, "input") if inp.is_displayed()]
        if visible_inputs:
            break
    else:
        driver.switch_to.default_content()
        visible_inputs = [inp for inp in driver.find_elements(By.TAG_NAME, "input") if inp.is_displayed()]

    username_sent = False
    password_sent = False

    print("Step 2: ユーザー名・パスワード入力")
    for i, inp in enumerate(visible_inputs):
        try:
            type_attr = inp.get_attribute("type")
            if not username_sent and type_attr in ["text", "email"]:
                inp.click()
                inp.send_keys(USERNAME)
                username_sent = True
                print(f"  input[{i}] にユーザー名送信")
            elif not password_sent and type_attr == "password":
                inp.click()
                inp.send_keys(PASSWORD + Keys.RETURN)
                password_sent = True
                print(f"  input[{i}] にパスワード送信")
            if username_sent and password_sent:
                break
        except Exception as e:
            print(f"  input[{i}] 送信失敗: {e}")

    driver.switch_to.default_content()
    time.sleep(5)

    # ---- 3. Google Driveからダウンロード ----
    print("Step 3: Google Driveからファイルダウンロード")
    driver.get(DRIVE_URL)
    time.sleep(10)

    downloaded_files = os.listdir(DOWNLOAD_DIR)
    latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
    print(f"  ダウンロード完了: {latest_file}")

    # ---- 4. packs ページへ移動 ----
    print("Step 4: packs ページに移動")
    driver.get("https://aternos.org/files/packs/")
    time.sleep(5)

    # iframe探索＋「アップロード」ラベルの親要素に input を探す
    print("Step 5: アップロード input 検索・送信")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        driver.switch_to.frame(iframe)
        labels = driver.find_elements(By.TAG_NAME, "label")
        upload_inputs = []
        for label in labels:
            if "アップロード" in label.text:
                try:
                    # labelが指す input を取得
                    html_for = label.get_attribute("for")
                    if html_for:
                        inp = driver.find_element(By.ID, html_for)
                        if inp.is_displayed():
                            upload_inputs.append(inp)
                except:
                    continue
        if upload_inputs:
            break
    else:
        driver.switch_to.default_content()
        upload_inputs = []
        labels = driver.find_elements(By.TAG_NAME, "label")
        for label in labels:
            if "アップロード" in label.text:
                html_for = label.get_attribute("for")
                if html_for:
                    try:
                        inp = driver.find_element(By.ID, html_for)
                        if inp.is_displayed():
                            upload_inputs.append(inp)
                    except:
                        continue

    if not upload_inputs:
        print("  アップロード用 input が見つかりませんでした")
    else:
        for i, inp in enumerate(upload_inputs):
            try:
                inp.send_keys(latest_file)
                print(f"  input[{i}] にファイル送信成功")
            except Exception as e:
                print(f"  input[{i}] 送信失敗: {e}")

    print("=== 完了 ===")
    time.sleep(10)

finally:
    driver.quit()
