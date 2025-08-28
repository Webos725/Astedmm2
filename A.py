#!/usr/bin/env python3
import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- 設定 ----------
USERNAME = "komugishomin"
PASSWORD = "A1B2c!d?"

SCREENSHOT_DIR = os.path.abspath("scripts/screenshots_aternos")
DOWNLOAD_DIR = os.path.abspath("downloads")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DRIVE_URL = "https://drive.google.com/uc?export=download&id=1-kutpyH8lIg_8aXXhAnosghVHVvqhsdI"

def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)

def save_shot(driver, name):
    try:
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)[:120]
        path = os.path.join(SCREENSHOT_DIR, f"{int(time.time())}_{safe_name}.png")
        driver.save_screenshot(path)
        log("SHOT", f"Saved screenshot: {path}")
    except Exception as e:
        log("WARN", f"Failed to save screenshot: {e}")

def safe_action(driver, desc, fn, take_shot=True):
    try:
        log("RUN", desc)
        fn()
        log("OK", desc)
    except Exception as e:
        log("WARN", f"{desc} failed: {e}")
        traceback.print_exc()
    finally:
        if take_shot:
            try: save_shot(driver, desc)
            except: pass

def wait_for_download(directory, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        files = os.listdir(directory)
        if files and not any(f.endswith(".crdownload") for f in files):
            return max([os.path.join(directory, f) for f in files], key=os.path.getctime)
        time.sleep(1)
    return None

def force_send_keys(driver, el, file_path):
    try:
        driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", el)
    except:
        pass
    el.send_keys(file_path)

# ---------- Chrome 起動 ----------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"--window-size=1366,768")
prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

# ---------- 実行 ----------
try:
    # ログイン
    safe_action(driver, "Open login page", lambda: driver.get("https://aternos.org/go/"))

    def fill_credentials():
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) >= 2:
            inputs[0].send_keys(USERNAME)
            inputs[1].send_keys(PASSWORD)
    safe_action(driver, "Fill credentials", fill_credentials)

    def click_login():
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "ログイン" in (b.text or "") or "Login" in (b.text or ""):
                b.click()
                return
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if len(inputs) >= 2:
                inputs[1].send_keys("\n")
        except:
            pass
    safe_action(driver, "Click login button", click_login)

    time.sleep(6)
    save_shot(driver, "after_login")

    # Google Drive からファイル取得
    safe_action(driver, "Open Google Drive link", lambda: driver.get(DRIVE_URL))
    latest_file = wait_for_download(DOWNLOAD_DIR, 60)
    if not latest_file:
        log("FAIL", "File download failed")
        raise SystemExit(1)
    log("CLEAR", f"Downloaded file: {latest_file}")
    save_shot(driver, "after_download")

    # packs ページへ
    safe_action(driver, "Open packs page", lambda: driver.get("https://aternos.org/files/packs/"))
    time.sleep(5)
    save_shot(driver, "packs_page")

    # アップロード
    def upload_file():
        candidates = [
            "//input[@type='file']",
            "//input[contains(@name,'upload')]",
            "//input[contains(@class,'upload')]",
            "//input[contains(@accept,'.zip')]",
            "//input[contains(@accept,'pack')]",
            "//input",
        ]
        for sel in candidates:
            try:
                el = driver.find_element(By.XPATH, sel)
                force_send_keys(driver, el, latest_file)
                log("CLEAR", f"Sent file to {sel}")
                return True
            except Exception as e:
                log("WARN", f"{sel} failed: {e}")
        for inp in driver.find_elements(By.TAG_NAME, "input")[:7]:
            try:
                if (inp.get_attribute("type") or "").lower() == "file":
                    force_send_keys(driver, inp, latest_file)
                    log("CLEAR", "Sent file to fallback input")
                    return True
            except Exception as e:
                log("WARN", f"fallback failed: {e}")
        return False
    safe_action(driver, "Upload file", upload_file)

    time.sleep(15)
    save_shot(driver, "after_upload")
    log("CLEAR", "Script finished successfully")

except Exception as e:
    log("FAIL", f"Top level error: {e}")
    traceback.print_exc()
    try: save_shot(driver, "fatal_error")
    except: pass
finally:
    driver.quit()
    log("CLEAR", "Driver quit, exit")
