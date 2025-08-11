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
SCREENSHOT_DIR = os.path.abspath("scripts/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

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
            try:
                save_shot(driver, desc)
            except:
                pass

# ---------- 環境確認 ----------
USER_ID = os.environ.get("USER_ID")
PASS = os.environ.get("PASS")
FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not USER_ID:
    log("WARN", "USER_ID not set in environment")
if not PASS:
    log("WARN", "PASS not set in environment")
if not os.path.exists(FONT_PATH):
    log("WARN", f"Font file not found at {FONT_PATH}")

# ---------- Chrome 起動設定 ----------
log("CLEAR", "Starting Chrome (headless)")
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1366,768")
try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    log("FAIL", f"Failed to start Chrome webdriver: {e}")
    try:
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome(options=chrome_options)
        log("OK", "Started Chrome with explicit binary_location")
    except Exception as e2:
        log("FAIL", f"Second attempt to start Chrome failed: {e2}")
        raise SystemExit(1)

wait = WebDriverWait(driver, 15)

# ---------- 実行本体 ----------
try:
    safe_action(driver, "Open login page", lambda: driver.get("https://zpdic.ziphil.com/login"))
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    save_shot(driver, "login_page_loaded")

    def fill_credentials():
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) >= 2:
            inputs[0].clear()
            inputs[0].send_keys(USER_ID or "")
            inputs[1].clear()
            inputs[1].send_keys(PASS or "")
            return
        try:
            uid = driver.find_element(By.NAME, "userId")
            pwd = driver.find_element(By.NAME, "password")
            uid.clear(); uid.send_keys(USER_ID or "")
            pwd.clear(); pwd.send_keys(PASS or "")
            return
        except:
            pass
        names = ["username", "login", "email"]
        for n in names:
            try:
                e = driver.find_element(By.NAME, n)
                e.clear(); e.send_keys(USER_ID or "")
                break
            except:
                continue
    safe_action(driver, "Fill credentials", fill_credentials)

    def click_login():
        candidates = [
            "//button[contains(text(),'ログイン')]",
            "//button[contains(text(),'ログ in')]",
            "//input[@type='submit' and (contains(@value,'ログイン') or contains(@value,'Login'))]",
            "//button[contains(translate(., 'LOGIN', 'login'), 'login')]"
        ]
        for c in candidates:
            try:
                el = driver.find_element(By.XPATH, c)
                el.click()
                return
            except:
                continue
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

    settings_url = "https://zpdic.ziphil.com/dictionary/2283/settings"
    safe_action(driver, f"Open settings page {settings_url}", lambda: driver.get(settings_url))
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "label")))
    save_shot(driver, "settings_page_loaded")

    def select_font_upload_radio():
        radios_to_click = []
        labels = driver.find_elements(By.TAG_NAME, "label")
        for lab in labels:
            if "フォントをアップロード" in (lab.text or ""):
                radios_to_click.append(lab)
        if radios_to_click:
            radios_to_click[-1].click()
            return True
        return False
    safe_action(driver, "Select 'フォントをアップロード' radio", select_font_upload_radio)
    save_shot(driver, "after_select_radio")

    def upload_file():
        candidates = [
            "//input[@type='file']",
            "//input[contains(@accept,'.ttf')]",
            "//input[contains(@name,'font')]",
            "//input[contains(@class,'file')]",
            "//input"
        ]
        found = False
        for sel in candidates:
            try:
                el = driver.find_element(By.XPATH, sel)
                driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", el)
                el.send_keys(FONT_PATH)
                found = True
                log("CLEAR", f"Sent file to element {sel}")
                break
            except:
                continue
        if found:
            log("CLEAR", "Upload complete, waiting for preview/acknowledgement...")
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'font-preview')]")))
            except:
                log("WARN", "Font preview not detected, continuing anyway")
        return found
    safe_action(driver, "Upload font file via file input", upload_file)
    save_shot(driver, "after_file_upload")

    def click_change_button():
        try:
            # フォントアップロードのラジオボタン近くの保存ボタンを優先
            radio = driver.find_element(By.XPATH, "//input[@type='radio' and @checked or @type='radio' and @selected]")
            btn = radio.find_element(By.XPATH, "./ancestor::div[1]//button[contains(text(),'変更') or contains(text(),'保存')]")
            btn.click()
            log("CLEAR", "Clicked targeted save button")
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'保存しました') or contains(text(),'変更しました')]")))
            log("OK", "Save confirmed on page")
            return True
        except Exception as e:
            log("WARN", f"Save button click failed: {e}")
            return False
    safe_action(driver, "Click save button", click_change_button)
    save_shot(driver, "after_click_change")

    log("CLEAR", "Script completed main steps")
except Exception as e:
    log("FAIL", f"Unexpected error: {e}")
    traceback.print_exc()
    try:
        save_shot(driver, "fatal_error")
    except:
        pass
finally:
    try:
        driver.quit()
    except:
        pass
    log("CLEAR", "Driver quit, script exit")
