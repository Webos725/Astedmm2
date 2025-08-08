from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import sys

def log_clear(msg):
    print(f"[CLEAR] {msg}")

def log_fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

# --- Secrets 読み込み ---
print("[INFO] GitHub Secrets から認証情報を読み込み中...")
user_id = os.environ.get("USER_ID")
password = os.environ.get("PASS")

if not user_id or not password:
    log_fail("USER_ID または PASS が設定されていません。")

# --- アップロードファイル確認 ---
upload_file_path = os.path.abspath("downloads/Conlangg.ttf")
if not os.path.exists(upload_file_path):
    log_fail(f"アップロードファイルが存在しません: {upload_file_path}")
log_clear(f"アップロードファイルを確認: {upload_file_path}")

# --- Chrome設定 ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 1. ログインページへ
    print("[INFO] ログインページへアクセス中...")
    driver.get("https://zpdic.ziphil.com/login")
    time.sleep(3)
    log_clear("ログインページにアクセス成功")

    # 2. ID とパスワード入力
    print("[INFO] ユーザーIDとパスワードを入力中...")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    if len(inputs) < 2:
        log_fail("ログインページで入力欄が見つかりません。")
    inputs[0].send_keys(user_id)
    inputs[1].send_keys(password)
    log_clear("ログイン情報入力完了")

    # 3. 「ログイン」ボタン押下
    print("[INFO] ログインボタンを押下中...")
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
    login_button.click()
    time.sleep(6)
    log_clear("ログイン成功")

    # 4. 辞書設定ページへ移動
    print("[INFO] 辞書設定ページへ移動中...")
    driver.get("https://zpdic.ziphil.com/dictionary/2283/settings")
    time.sleep(3)
    log_clear("辞書設定ページにアクセス成功")

    # 5. ファイルアップロード
    print("[INFO] ファイルアップロード欄を探しています...")
    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    if not file_inputs:
        log_fail("ファイルアップロード欄が見つかりません。")
    file_inputs[0].send_keys(upload_file_path)
    log_clear("ファイル選択完了")

    # 6. 「変更」ボタン押下
    print("[INFO] 変更ボタンを押下中...")
    change_button = driver.find_element(By.XPATH, "//button[contains(text(), '変更')]")
    change_button.click()
    time.sleep(4)
    log_clear("変更完了 - アップロード成功")

except Exception as e:
    log_fail(f"エラー発生: {e}")

finally:
    driver.quit()
