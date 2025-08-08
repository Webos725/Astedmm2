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
    log("WARN", f"Font file not found at {FONT_PATH} — the workflow shell will skip running this script if so.")

# ---------- Chrome 起動設定 ----------
log("CLEAR", "Starting Chrome (headless)")
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1366,768")
# Don't hard-fail if binary location differs; let webdriver find it.
try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    log("FAIL", f"Failed to start Chrome webdriver: {e}")
    # try fallback to explicit binary location
    try:
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome(options=chrome_options)
        log("OK", "Started Chrome with explicit binary_location")
    except Exception as e2:
        log("FAIL", f"Second attempt to start Chrome failed: {e2}")
        raise SystemExit(1)

wait = WebDriverWait(driver, 12)

# ---------- 実行本体（すべて safe_action で包む） ----------
try:
    # 1) ログインページへ
    safe_action(driver, "Open login page", lambda: driver.get("https://zpdic.ziphil.com/login"))

    # 2) 要素待ち & スクショ
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    except:
        log("WARN", "Login inputs not detected within wait timeout")
    save_shot(driver, "login_page_loaded")

    # 3) ID/PASS 入力（複数パターン試す）
    def fill_credentials():
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) >= 2:
            inputs[0].clear()
            inputs[0].send_keys(USER_ID or "")
            inputs[1].clear()
            inputs[1].send_keys(PASS or "")
            return
        # 別名で探す
        try:
            uid = driver.find_element(By.NAME, "userId")
            pwd = driver.find_element(By.NAME, "password")
            uid.clear(); uid.send_keys(USER_ID or "")
            pwd.clear(); pwd.send_keys(PASS or "")
            return
        except:
            pass
        # 他の候補
        names = ["username", "login", "email"]
        for n in names:
            try:
                e = driver.find_element(By.NAME, n)
                e.clear(); e.send_keys(USER_ID or "")
                break
            except:
                continue
    safe_action(driver, "Fill credentials", fill_credentials)

    # 4) ログインボタンを押す（多数候補）
    def click_login():
        # common patterns
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
        # 最後に buttons のテキスト走査
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "ログイン" in (b.text or "") or "Login" in (b.text or ""):
                b.click()
                return
        # try pressing enter on second input if present
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if len(inputs) >= 2:
                inputs[1].send_keys("\n")
        except:
            pass
    safe_action(driver, "Click login button", click_login)

    # wait a bit for navigation
    time.sleep(6)
    save_shot(driver, "after_login")

    # 5) 設定ページへ移動
    settings_url = "https://zpdic.ziphil.com/dictionary/2283/settings"
    safe_action(driver, f"Open settings page {settings_url}", lambda: driver.get(settings_url))
    time.sleep(3)
    save_shot(driver, "settings_page_loaded")

    # 6) 「フォントをアップロード」ラジオを探して選択（label経由など複数手段）
    def select_font_upload_radio():
        # try label text matching first
        try:
            labels = driver.find_elements(By.TAG_NAME, "label")
            for lab in labels:
                txt = (lab.text or "").strip()
                if "フォントをアップロード" in txt:
                    # click the label if it's clickable
                    try:
                        lab.click()
                        return True
                    except:
                        pass
                    # else click associated input via for attr
                    fid = lab.get_attribute("for")
                    if fid:
                        try:
                            r = driver.find_element(By.ID, fid)
                            r.click()
                            return True
                        except:
                            pass
        except:
            pass
        # next: search radio inputs and check their associated labels
        try:
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            for r in radios:
                try:
                    rid = r.get_attribute("id")
                    if rid:
                        try:
                            lab = driver.find_element(By.XPATH, f"//label[@for='{rid}']")
                            if "フォントをアップロード" in (lab.text or ""):
                                r.click()
                                return True
                        except:
                            pass
                except:
                    pass
        except:
            pass
        # fallback: try any radio with a nearby text containing 'アップロード' in parent
        try:
            elems = driver.find_elements(By.XPATH, "//*[contains(text(),'アップロード') or contains(text(),'フォント')]")
            for e in elems:
                # attempt to find a radio input within same ancestor
                try:
                    parent = e.find_element(By.XPATH, "./ancestor::div[1]")
                    try:
                        candidate = parent.find_element(By.XPATH, ".//input[@type='radio']")
                        candidate.click()
                        return True
                    except:
                        pass
                except:
                    pass
        except:
            pass
        return False

    safe_action(driver, "Select 'フォントをアップロード' radio", select_font_upload_radio)

    time.sleep(1)
    save_shot(driver, "after_select_radio")

    # 7) ファイル入力欄を探して送信（多様な selector を試す）
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
                # try to make visible if hidden
                try:
                    driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", el)
                except:
                    pass
                try:
                    el.send_keys(FONT_PATH)
                    found = True
                    log("CLEAR", f"Sent file to element {sel}")
                    break
                except Exception as e:
                    log("WARN", f"send_keys failed on {sel}: {e}")
            except Exception:
                continue
        # As fallback, search inputs and filter by type attribute presence
        if not found:
            try:
                for inp in driver.find_elements(By.TAG_NAME, "input"):
                    try:
                        t = (inp.get_attribute("type") or "").lower()
                        if t == "file" or (inp.get_attribute("accept") and ".ttf" in (inp.get_attribute("accept") or "")):
                            try:
                                driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", inp)
                            except:
                                pass
                            try:
                                inp.send_keys(FONT_PATH)
                                found = True
                                break
                            except:
                                pass
                    except:
                        pass
            except:
                pass
        if not found:
            log("WARN", "No file input accepted the font path")
        return found

    safe_action(driver, "Upload font file via file input", upload_file)
    time.sleep(2)
    save_shot(driver, "after_file_upload")

    # 8) 「変更」または「保存」ボタンを探してクリック（複数候補）
    def click_change_button():
        candidates = [
            "//button[contains(text(),'変更')]",
            "//button[contains(text(),'保存')]",
            "//input[@type='submit' and (contains(@value,'変更') or contains(@value,'保存'))]",
            "//button[contains(translate(., 'CHANGE', 'change'),'change')]"
        ]
        for c in candidates:
            try:
                el = driver.find_element(By.XPATH, c)
                el.click()
                log("CLEAR", f"Clicked change/save button via {c}")
                return True
            except:
                continue
        # fallback: find buttons and check text
        for b in driver.find_elements(By.TAG_NAME, "button"):
            try:
                txt = (b.text or "").strip()
                if "変更" in txt or "保存" in txt:
                    b.click()
                    return True
            except:
                pass
        # no button found
        log("WARN", "No change/save button found to click")
        return False

    safe_action(driver, "Click change/save button", click_change_button)
    time.sleep(3)
    save_shot(driver, "after_click_change")

    # 9) UI 総当たり（ラジオ・チェック・select の触診） — 破壊的操作はしないが触る
    def touch_all_ui():
        try:
            # radios & checkboxes
            for inp in driver.find_elements(By.TAG_NAME, "input"):
                try:
                    t = (inp.get_attribute("type") or "").lower()
                    if t in ("radio", "checkbox"):
                        try:
                            inp.click()
                        except:
                            pass
                except:
                    pass
            # selects: iterate options
            for sel in driver.find_elements(By.TAG_NAME, "select"):
                try:
                    opts = sel.find_elements(By.TAG_NAME, "option")
                    for o in opts[:3]:  # 最初の数個だけ
                        try:
                            o.click()
                            time.sleep(0.2)
                        except:
                            pass
                except:
                    pass
        except:
            pass

    safe_action(driver, "Touch all UI elements (non-destructive)", touch_all_ui)
    save_shot(driver, "after_touch_ui")

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
