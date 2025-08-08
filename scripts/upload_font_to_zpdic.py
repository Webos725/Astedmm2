import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def log(status, message):
    print(f"[{status}] {message}", flush=True)

# --- 環境変数 ---
USER_ID = os.environ.get("USER_ID")
PASS = os.environ.get("PASS")
FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not USER_ID or not PASS:
    log("FAIL", "USER_ID または PASS が設定されていません")
    exit(1)
if not os.path.exists(FONT_PATH):
    log("FAIL", f"フォントファイルが見つかりません: {FONT_PATH}")
    exit(1)

# --- Chrome オプション設定 ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

log("CLEAR", "Chrome 起動準備")
driver = webdriver.Chrome(options=chrome_options)

try:
    # --- ログイン ---
    log("CLEAR", "ログインページにアクセス")
    driver.get("https://zpdic.ziphil.com/login")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "input"))
    )
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(USER_ID)
    inputs[1].send_keys(PASS)

    log("CLEAR", "ログインボタンをクリック")
    login_button = driver.find_element(By.XPATH, "//button[contains(text(),'ログイン')]")
    login_button.click()

    time.sleep(6)  # ページ遷移待機

    # --- 設定ページに移動 ---
    settings_url = "https://zpdic.ziphil.com/dictionary/2283/settings"
    log("CLEAR", f"設定ページにアクセス: {settings_url}")
    driver.get(settings_url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "input"))
    )

    # --- アップロード ---
    log("CLEAR", "アップロードフィールドを探す")

    # 「フォントファイル」のラベルを目印にinput[type='file']を探すXPath
    file_input = None
    try:
        # 例：ラベル「フォントファイル」のすぐ近くにあるinput[type=file]を特定
        file_input = driver.find_element(By.XPATH, "//label[contains(text(),'フォントファイル')]/following-sibling::input[@type='file']")
    except:
        # fallbackで単純にinput[type=file]を探す
        inputs_file = driver.find_elements(By.XPATH, "//input[@type='file']")
        if inputs_file:
            file_input = inputs_file[0]

    if not file_input:
        log("FAIL", "アップロードフィールドが見つかりません")
        driver.quit()
        exit(1)

    log("CLEAR", f"フォントファイルを選択: {FONT_PATH}")
    file_input.send_keys(FONT_PATH)

    # --- 変更ボタンをクリック ---
    log("CLEAR", "変更ボタンを探す")

    # 変更ボタンは画像にあるように「変更」のみテキストがあるボタン
    change_button = None
    try:
        change_button = driver.find_element(By.XPATH, "//button[contains(text(),'変更')]")
    except:
        # 万が一取れなければ、submitボタン系で探す
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "変更" in btn.text:
                change_button = btn
                break

    if not change_button:
        log("FAIL", "変更ボタンが見つかりません")
        driver.quit()
        exit(1)

    change_button.click()

    log("CLEAR", "アップロード処理完了")
    time.sleep(3)

except Exception as e:
    log("FAIL", f"エラー発生: {e}")
    driver.quit()
    exit(1)

driver.quit()
log("CLEAR", "処理全体が正常終了")
WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "input"))
    )
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(USER_ID)
    inputs[1].send_keys(PASS)

    log("CLEAR", "ログインボタンをクリック")
    login_button = driver.find_element(By.XPATH, "//button[contains(text(),'ログイン')]")
    login_button.click()

    time.sleep(6)  # ページ遷移待機

    # --- 設定ページに移動 ---
    settings_url = "https://zpdic.ziphil.com/dictionary/2283/settings"
    log("CLEAR", f"設定ページにアクセス: {settings_url}")
    driver.get(settings_url)

    #// WebDriverWait(driver, 10).until(
    # //    EC.presence_of_element_located((By.TAG_NAME, "input"))
    # )
    time.sleep(6)
    # --- アップロード ---
    log("CLEAR", "アップロードフィールドを探す")
    file_input = None
    selectors = [
        "//input[@type='file']",
        "//input[contains(@accept,'.ttf')]",
        "//input"
    ]
    for sel in selectors:
        try:
            file_input = driver.find_element(By.XPATH, sel)
            break
        except:
            pass

    if not file_input:
        log("FAIL", "アップロードフィールドが見つかりません")
        driver.quit()
        exit(1)

    log("CLEAR", f"フォントファイルを選択: {FONT_PATH}")
    file_input.send_keys(FONT_PATH)

    # --- 変更ボタンをクリック ---
    log("CLEAR", "変更ボタンを探す")
    change_button = driver.find_element(By.XPATH, "//button[contains(text(),'変更')]")
    change_button.click()

    log("CLEAR", "アップロード処理完了")
    time.sleep(3)

except Exception as e:
    log("FAIL", f"エラー発生: {e}")
    driver.quit()
    exit(1)

driver.quit()
log("CLEAR", "処理全体が正常終了")
