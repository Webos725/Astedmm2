#!/usr/bin/env python3
import os
import time
import traceback
import base64
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
FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")  # TTF

if not USER_ID:
    log("WARN", "USER_ID not set in environment")
if not PASS:
    log("WARN", "PASS not set in environment")
if not os.path.exists(FONT_PATH):
    log("WARN", f"Font file not found at {FONT_PATH} — the workflow shell will skip running this script if so.")

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

wait = WebDriverWait(driver, 12)

# ---------- 実行本体 ----------
try:
    safe_action(driver, "Open login page", lambda: driver.get("https://zpdic.ziphil.com/login"))

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    except:
        log("WARN", "Login inputs not detected within wait timeout")
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
    time.sleep(3)
    save_shot(driver, "settings_page_loaded")

    def select_font_upload_radio():
        radios_to_click = []
        try:
            labels = driver.find_elements(By.TAG_NAME, "label")
            for lab in labels:
                txt = (lab.text or "").strip()
                if "フォントをアップロード" in txt:
                    radios_to_click.append(lab)
            if radios_to_click:
                radios_to_click[-1].click()
                return True
        except:
            pass

        try:
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            matching_radios = []
            for r in radios:
                try:
                    rid = r.get_attribute("id")
                    if rid:
                        lab = driver.find_element(By.XPATH, f"//label[@for='{rid}']")
                        if "フォントをアップロード" in (lab.text or ""):
                            matching_radios.append(r)
                except:
                    pass
            if matching_radios:
                matching_radios[-1].click()
                return True
        except:
            pass

        try:
            elems = driver.find_elements(By.XPATH, "//*[contains(text(),'アップロード') or contains(text(),'フォント')]")
            candidate_radios = []
            for e in elems:
                try:
                    parent = e.find_element(By.XPATH, "./ancestor::div[1]")
                    candidate = parent.find_element(By.XPATH, ".//input[@type='radio']")
                    candidate_radios.append(candidate)
                except:
                    pass
            if candidate_radios:
                candidate_radios[-1].click()
                return True
        except:
            pass

        return False

    safe_action(driver, "Select 'フォントをアップロード' radio", select_font_upload_radio)

    time.sleep(1)
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
        file_input = None

        # ---- send_keys をまず試す ----
        for sel in candidates:
            try:
                el = driver.find_element(By.XPATH, sel)
                driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", el)
                el.send_keys(FONT_PATH)
                file_input = el
                found = True
                log("CLEAR", f"Sent file via send_keys to {sel}")
                break
            except Exception as e:
                log("WARN", f"send_keys failed on {sel}: {e}")

        time.sleep(3)  # send_keys後の待機

        # ---- JSで直接Fileオブジェクトを注入 ----
        try:
            if file_input is None:
                file_input = driver.find_element(By.CSS_SELECTOR, "input[type=file]")
            with open(FONT_PATH, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")
            js = """
            var b64 = arguments[0];
            var filename = arguments[1];
            var content = atob(b64);
            var array = new Uint8Array(content.length);
            for (var i = 0; i < content.length; i++) {
                array[i] = content.charCodeAt(i);
            }
            var blob = new Blob([array], {type: "font/ttf"});
            var file = new File([blob], filename, {type: "font/ttf"});
            var dt = new DataTransfer();
            dt.items.add(file);
            arguments[2].files = dt.files;
            arguments[2].dispatchEvent(new Event('change', { bubbles: true }));
            """
            driver.execute_script(js, b64_data, os.path.basename(FONT_PATH), file_input)
            found = True
            log("CLEAR", "Injected File via JS")
        except Exception as e:
            log("WARN", f"JS injection failed: {e}")

        # ---- ファイル名確認 ----
        if found:
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'.ttf') or contains(text(),'Conlangg')]")))
                log("OK", "Font file name appeared after upload")
            except:
                log("WARN", "Font file name not detected in DOM")
        else:
            log("WARN", "No file input accepted the font path")

        return found

    def click_change_button():
        clicked_any = False
        candidates = [
            "//button[contains(text(),'変更')]",
            "//button[contains(text(),'保存')]",
            "//input[@type='submit' and (contains(@value,'変更') or contains(@value,'保存'))]",
            "//button[contains(translate(., 'CHANGE', 'change'),'change')]"
        ]
        for c in candidates:
            try:
                elements = driver.find_elements(By.XPATH, c)
                for el in elements:
                    try:
                        el.click()
                        log("CLEAR", f"Clicked change/save button via {c}")
                        clicked_any = True
                    except Exception as e:
                        log("WARN", f"Failed clicking element {c}: {e}")
            except Exception as e:
                log("WARN", f"Failed finding elements by xpath {c}: {e}")
        return clicked_any

    def upload_file_and_confirm():
        if not upload_file():
            return False
        # 再度ラジオを選択
        select_font_upload_radio()
        time.sleep(1)
        # 保存ボタン押下
        click_change_button()
        # 反映待ち
        time.sleep(20)
        return True

    safe_action(driver, "Upload font file and confirm", upload_file_and_confirm)
    save_shot(driver, "after_upload_and_confirm")

    log("CLEAR", "Script completed main steps (errors were logged but not fatal)")

except Exception as e:
    log("FAIL", f"Unexpected top-level error: {e}")
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
