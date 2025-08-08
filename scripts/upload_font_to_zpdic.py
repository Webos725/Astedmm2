import os
import time
import imageio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image

USER_ID = os.environ.get("USER_ID")
PASS = os.environ.get("PASS")
FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

print("[CLEAR] Chrome 起動準備")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,800")
chrome_options.binary_location = "/usr/bin/chromium-browser"

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://zpdic.ziphil.com/login")

frames = []  # スクリーンショットフレーム格納

def capture_frame():
    png = driver.get_screenshot_as_png()
    img = Image.open(bytearray(png))
    frames.append(img)

print("[CLEAR] ログイン開始")
try:
    # 1つ目の入力欄
    driver.find_elements(By.TAG_NAME, "input")[0].send_keys(USER_ID)
    capture_frame()
    time.sleep(1)

    # 2つ目の入力欄
    driver.find_elements(By.TAG_NAME, "input")[1].send_keys(PASS)
    capture_frame()
    time.sleep(1)

    # ログインボタン押下（部分一致検索）
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if "ログイン" in btn.text:
            btn.click()
            break
    capture_frame()

    time.sleep(6)  # ページ遷移待ち
    capture_frame()
    print("[CLEAR] ログイン完了")

    # 設定ページへ
    driver.get("https://zpdic.ziphil.com/dictionary/2283/settings")
    time.sleep(3)
    capture_frame()

    print("[CLEAR] アップロード試行")

    file_inputs = driver.find_elements(By.TAG_NAME, "input")
    found_upload = False
    for f in file_inputs:
        try:
            if f.get_attribute("type") == "file":
                f.send_keys(FONT_PATH)
                found_upload = True
                break
        except Exception as e:
            print("[FAIL] file入力でエラー:", e)

    if not found_upload:
        print("[FAIL] ファイルアップロードボタンが見つかりません")
    else:
        time.sleep(2)
        capture_frame()

        # 「変更」ボタンを探してクリック
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "変更" in btn.text:
                btn.click()
                break
        print("[CLEAR] アップロード完了")
        time.sleep(3)
        capture_frame()

except Exception as e:
    print("[FAIL] 処理中にエラー:", e)

finally:
    driver.quit()

# GIF生成
if frames:
    frames[0].save(
        "result.gif",
        save_all=True,
        append_images=frames[1:],
        duration=1000,
        loop=0
    )
    print("[CLEAR] GIF生成完了: result.gif")
else:
    print("[FAIL] スクリーンショットがありません")
