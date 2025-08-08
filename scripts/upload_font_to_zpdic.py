from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

# GitHub Actions の secrets から取得
user_id = os.environ.get("USER_ID")
password = os.environ.get("PASS")

if not user_id or not password:
    raise ValueError("USER_ID または PASS が環境変数に設定されていません。")

# アップロードするファイル
upload_file_path = os.path.abspath("downloads/Conlangg.ttf")
if not os.path.exists(upload_file_path):
    raise FileNotFoundError(f"{upload_file_path} が存在しません。")

# Chrome設定
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 1. ログインページへ
    driver.get("https://zpdic.ziphil.com/login")
    time.sleep(3)

    # 2. ID と パスワードを入力
    inputs = driver.find_elements(By.TAG_NAME, "input")
    if len(inputs) < 2:
        raise RuntimeError("ログインページでテキスト入力欄が見つかりません。")

    inputs[0].send_keys(user_id)
    inputs[1].send_keys(password)

    # 3. 「ログイン」と部分一致するボタンをクリック
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
    login_button.click()

    # 4. ページ遷移待機
    time.sleep(6)

    # 5. 辞書設定ページへ移動
    driver.get("https://zpdic.ziphil.com/dictionary/2283/settings")
    time.sleep(3)

    # 6. ファイルアップロード欄を探して送信
    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    if not file_inputs:
        raise RuntimeError("ファイルアップロード欄が見つかりません。")

    file_inputs[0].send_keys(upload_file_path)

    # 7. 「変更」と部分一致するボタンをクリック
    change_button = driver.find_element(By.XPATH, "//button[contains(text(), '変更')]")
    change_button.click()

    time.sleep(4)
    print("アップロード完了")

finally:
    driver.quit()
