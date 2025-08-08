import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def log(status, message):
    print(f"[{status}] {message}", flush=True)

USER_ID = os.environ.get("USER_ID")
PASS = os.environ.get("PASS")
FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not USER_ID or not PASS:
    log("FAIL", "USER_ID または PASS が設定されていません")
    exit(1)

if not os.path.exists(FONT_PATH):
    log("FAIL", f"フォントファイルが見つかりません: {FONT_PATH}")
    exit(1)

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

log("CLEAR", "Chrome 起動準備")
driver = webdriver.Chrome(options=chrome_options)

try:
    log("CLEAR", "ログインページにアクセス")
    driver.get("https://zpdic.ziphil.com/login")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "input"))
    )
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(USER_ID)
    inputs[1].send_keys(PASS)

    log("CLEAR", "ログインボタンをクリック")
    driver.find_element(By.XPATH, "//button[contains(text(),'ログイン')]").click()
    time.sleep(6)

    settings_url = "https://zpdic.ziphil.com/dictionary/2283/settings"
    log("CLEAR", f"設定ページにアクセス: {settings_url}")
    driver.get(settings_url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )

    log("CLEAR", "フォントアップロードのラジオボタンを選択")

    radio_xpaths = [
        "//input[@type='radio' and following-sibling::*[contains(text(),'フォントをアップロード')]]",
        "//input[@type='radio' and contains(@value,'UPLOAD')]",
        "//label[contains(.,'フォントをアップロード')]/input[@type='radio']"
    ]

    upload_radio = None
    for xp in radio_xpaths:
        try:
            upload_radio = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            break
        except:
            continue

    if not upload_radio:
        driver.save_screenshot("radio_not_found.png")
        log("FAIL", "フォントアップロードのラジオボタンが見つかりません（radio_not_found.pngを確認）")
        driver.quit()
        exit(1)

    upload_radio.click()

    log("CLEAR", "アップロードフィールドを探す")
    try:
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
    except:
        driver.save_screenshot("file_input_not_found.png")
        log("FAIL", "ファイル入力欄が見つかりません（file_input_not_found.pngを確認）")
        driver.quit()
        exit(1)

    log("CLEAR", f"フォントファイルを選択: {FONT_PATH}")
    file_input.send_keys(FONT_PATH)

    log("CLEAR", "変更ボタンを探す")
    try:
        change_button = driver.find_element(By.XPATH, "//button[contains(text(),'変更')]")
    except:
        change_button = None
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            if "変更" in btn.text:
                change_button = btn
                break

    if not change_button:
        driver.save_screenshot("change_button_not_found.png")
        log("FAIL", "変更ボタンが見つかりません（change_button_not_found.pngを確認）")
        driver.quit()
        exit(1)

    change_button.click()

    log("CLEAR", "アップロード処理完了")
    time.sleep(3)

except Exception as e:
    driver.save_screenshot("unexpected_error.png")
    log("FAIL", f"エラー発生: {e}（unexpected_error.pngを確認）")
    driver.quit()
    exit(1)

driver.quit()
log("CLEAR", "処理全体が正常終了")
