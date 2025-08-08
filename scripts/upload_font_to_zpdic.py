import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USER_ID = os.getenv("USER_ID")
PASS = os.getenv("PASS")
TTF_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not USER_ID or not PASS:
    print("[FAIL] USER_ID / PASS が設定されていません")
    exit(1)

if not os.path.exists(TTF_PATH):
    print(f"[FAIL] TTF ファイルが存在しません: {TTF_PATH}")
    exit(1)

print("[CLEAR] Chrome 起動準備")
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

try:
    print("[CLEAR] ログインページへ移動")
    driver.get("https://zpdic.ziphil.com/login")

    # ログインフォーム入力
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(USER_ID)
    inputs[1].send_keys(PASS)

    driver.find_element(By.XPATH, "//button[contains(text(),'ログイン')]").click()
    time.sleep(6)  # ログイン処理待ち

    print("[CLEAR] 辞書設定ページへ移動")
    driver.get("https://zpdic.ziphil.com/dictionary/2283/settings")
    time.sleep(3)

    # ファイル入力欄を探す
    selectors = [
        "input[type='file']",
        "//input[@type='file']",
        "//form//input[@type='file']",
    ]

    file_input = None
    for sel in selectors:
        try:
            if sel.startswith("//"):
                file_input = driver.find_element(By.XPATH, sel)
            else:
                file_input = driver.find_element(By.CSS_SELECTOR, sel)
            print(f"[CLEAR] file input 発見: {sel}")
            break
        except:
            print(f"[INFO] file input 未発見: {sel}")
            continue

    if not file_input:
        print("[FAIL] ファイルアップロード欄が見つかりません")
        exit(1)

    # hidden 対策
    driver.execute_script("arguments[0].style.display = 'block';", file_input)
    file_input.send_keys(TTF_PATH)
    print("[CLEAR] TTF ファイルをセットしました")

    # 「変更」ボタンを押す
    change_btn = driver.find_element(By.XPATH, "//button[contains(text(),'変更')]")
    change_btn.click()
    print("[CLEAR] アップロード完了")
    
except Exception as e:
    print(f"[FAIL] エラー発生: {e}")
    exit(1)
finally:
    driver.quit()
