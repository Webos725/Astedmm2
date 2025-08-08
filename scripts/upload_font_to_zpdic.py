import os
import time
import imageio
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USER_ID = os.environ.get("USER_ID")
PASS = os.environ.get("PASS")
FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

print("[CLEAR] Chrome 起動準備")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1280,800")
chrome_options.binary_location = "/usr/bin/chromium-browser"

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

frames = []

def screenshot_step():
    """現在のブラウザ画面をキャプチャしてframesに追加"""
    png = driver.get_screenshot_as_png()
    img = Image.open(bytearray(png)).convert("RGB")
    frames.append(img)

try:
    print("[CLEAR] ZpDIC ログインページへアクセス")
    driver.get("https://zpdic.ziphil.com/login")
    screenshot_step()

    # ログイン入力
    print("[CLEAR] ID/PASS 入力")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(USER_ID)
    inputs[1].send_keys(PASS)
    screenshot_step()

    # ログインボタン押下
    print("[CLEAR] ログインボタン押下")
    login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'ログイン')]")
    login_btn.click()
    time.sleep(6)
    screenshot_step()

    print("[CLEAR] ログイン完了")

    # 設定ページへ移動
    print("[CLEAR] 設定ページへ移動")
    driver.get("https://zpdic.ziphil.com/dictionary/2283/settings")
    time.sleep(3)
    screenshot_step()

    # ファイルアップロード要素探索
    print("[CLEAR] ファイルアップロードボタン探索")
    upload_elem = None
    candidates = [
        "//input[@type='file']",
        "//input[contains(@accept, '.ttf')]",
        "//input[contains(@name, 'font')]"
    ]
    for xpath in candidates:
        try:
            upload_elem = driver.find_element(By.XPATH, xpath)
            break
        except:
            pass

    if not upload_elem:
        raise Exception("アップロード要素が見つかりません")

    # ファイル送信
    print("[CLEAR] フォントファイル送信")
    upload_elem.send_keys(FONT_PATH)
    time.sleep(2)
    screenshot_step()

    # 保存ボタン押下
    print("[CLEAR] 保存ボタン押下")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if "変更" in btn.text:
            btn.click()
            break
    time.sleep(3)
    screenshot_step()

    print("[CLEAR] アップロード完了")

except Exception as e:
    print(f"[FAIL] {e}")

finally:
    driver.quit()
    if frames:
        output_path = "scripts/progress.gif"
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=1000,
            loop=0
        )
        print(f"[CLEAR] GIF保存完了: {output_path}")
    else:
        print("[FAIL] スクリーンショットがありません")
