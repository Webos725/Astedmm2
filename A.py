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

def log(msg):
    print(f"[LOG] {msg}")

try:
    # ---- 1. ログインページ ----
    log("Step 1: ログインページにアクセス")
    driver.get("https://aternos.org/go/")
    time.sleep(3)

    # ---- 2. ユーザー名・パスワード入力 ----
    log("Step 2: ユーザー名・パスワード入力開始")

    # iframe探索＋表示 input のみ取得
    def get_visible_inputs(driver):
        driver.switch_to.default_content()
        all_inputs = []
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            all_inputs.extend([inp for inp in driver.find_elements(By.TAG_NAME, "input") if inp.is_displayed()])
            driver.switch_to.default_content()
        # ページ直下の input も追加
        all_inputs.extend([inp for inp in driver.find_elements(By.TAG_NAME, "input") if inp.is_displayed()])
        return all_inputs

    visible_inputs = get_visible_inputs(driver)
    username_sent = False
    password_sent = False

    for i, inp in enumerate(visible_inputs):
        try:
            type_attr = inp.get_attribute("type")
            if not username_sent and type_attr in ["text", "email"]:
                inp.click()
                inp.send_keys(USERNAME)
                username_sent = True
                log(f"input[{i}] にユーザー名送信")
            elif not password_sent and type_attr == "password":
                inp.click()
                inp.send_keys(PASSWORD)
                password_sent = True
                log(f"input[{i}] にパスワード送信")
            if username_sent and password_sent:
                break
        except Exception as e:
            log(f"input[{i}] 送信失敗: {e}")

    # ---- 3. ログインボタンクリック ----
    log("Step 3: ログインボタンを探してクリック")
    driver.switch_to.default_content()
    buttons = driver.find_elements(By.TAG_NAME, "button")
    login_clicked = False
    for i, btn in enumerate(buttons):
        try:
            if "ログイン" in btn.text:
                btn.click()
                login_clicked = True
                log(f"button[{i}] ログインボタンクリック")
                break
        except Exception as e:
            log(f"button[{i}] クリック失敗: {e}")
    if not login_clicked:
        log("ログインボタンが見つかりませんでした")

    time.sleep(5)

    # ---- 4. Google Driveからダウンロード ----
    log("Step 4: Google Driveからファイルダウンロード")
    driver.get(DRIVE_URL)
    time.sleep(10)
    downloaded_files = os.listdir(DOWNLOAD_DIR)
    latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
    log(f"ダウンロード完了: {latest_file}")

    # ---- 5. packs ページ移動 ----
    log("Step 5: packs ページに移動")
    driver.get("https://aternos.org/files/packs/")
    time.sleep(5)

    # ---- 6. アップロード input 探索・送信 ----
    log("Step 6: アップロード input 探索・送信開始")

    def find_upload_inputs(driver):
        driver.switch_to.default_content()
        inputs_found = []
        # iframe 内も探索
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            labels = driver.find_elements(By.TAG_NAME, "label")
            for label in labels:
                if "アップロード" in label.text:
                    html_for = label.get_attribute("for")
                    if html_for:
                        try:
                            inp = driver.find_element(By.ID, html_for)
                            if inp.is_displayed():
                                inputs_found.append(inp)
                        except:
                            continue
            driver.switch_to.default_content()
        # ページ直下も探索
        labels = driver.find_elements(By.TAG_NAME, "label")
        for label in labels:
            if "アップロード" in label.text:
                html_for = label.get_attribute("for")
                if html_for:
                    try:
                        inp = driver.find_element(By.ID, html_for)
                        if inp.is_displayed():
                            inputs_found.append(inp)
                    except:
                        continue
        return inputs_found

    upload_inputs = find_upload_inputs(driver)
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
