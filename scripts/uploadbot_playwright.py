#!/usr/bin/env python3
import os
import time
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------- 設定 ----------
SCREENSHOT_DIR = Path("screenshots4")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)

def save_shot(page, name):
    try:
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)[:120]
        path = SCREENSHOT_DIR / f"{int(time.time())}_{safe_name}.png"
        page.screenshot(path=str(path), full_page=True)
        log("SHOT", f"Saved screenshot: {path}")
    except Exception as e:
        log("WARN", f"Failed to save screenshot: {e}")

def safe_action(desc, fn, take_shot=True, page=None):
    try:
        log("RUN", desc)
        fn()
        log("OK", desc)
    except Exception as e:
        log("WARN", f"{desc} failed: {e}")
        traceback.print_exc()
    finally:
        if take_shot and page:
            try:
                save_shot(page, desc)
            except:
                pass

# ---------- 環境確認 ----------
USER_ID = os.environ.get("USER_ID")
PASS = os.environ.get("PASS")
FONT_PATH = Path("downloads/font.ttf")

if not USER_ID:
    log("WARN", "USER_ID not set in environment")
if not PASS:
    log("WARN", "PASS not set in environment")
if not FONT_PATH.exists():
    log("WARN", f"Font file not found at {FONT_PATH}")

# ---------- Playwright 起動 ----------
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent=USER_AGENT
    )
    page = context.new_page()

    try:
        # ---------- ログインページ ----------
        safe_action("Open login page", lambda: page.goto("https://zpdic.ziphil.com/login"), page=page)
        try:
            page.wait_for_selector("input", timeout=12000)
        except PWTimeout:
            log("WARN", "Login inputs not detected within wait timeout")
        save_shot(page, "login_page_loaded")

        # ---------- クレデンシャル入力 ----------
        def fill_credentials():
            inputs = page.query_selector_all("input")
            if len(inputs) >= 2:
                inputs[0].fill(USER_ID or "")
                inputs[1].fill(PASS or "")
                return
            for name in ["userId", "password", "username", "login", "email"]:
                try:
                    inp = page.query_selector(f"input[name='{name}']")
                    if inp:
                        inp.fill(USER_ID or "")
                        break
                except:
                    continue

        safe_action("Fill credentials", fill_credentials, page=page)

        # ---------- ログインボタン ----------
        def click_login():
            xpaths = [
                "//button[contains(text(),'ログイン')]",
                "//button[contains(text(),'ログ in')]",
                "//input[@type='submit' and (contains(@value,'ログイン') or contains(@value,'Login'))]",
                "//button[contains(translate(., 'LOGIN', 'login'), 'login')]"
            ]
            for xp in xpaths:
                btn = page.query_selector(xp)
                if btn:
                    btn.click()
                    return
            # フォールバック: text検索
            for b in page.query_selector_all("button"):
                if "ログイン" in (b.inner_text() or "") or "Login" in (b.inner_text() or ""):
                    b.click()
                    return
            # Enter送信
            inputs = page.query_selector_all("input[type='password'], input[type='text']")
            if len(inputs) >= 2:
                inputs[1].press("Enter")

        safe_action("Click login button", click_login, page=page)

        page.wait_for_timeout(6000)
        save_shot(page, "after_login")

        # ---------- 設定ページ ----------
        settings_url = "https://zpdic.ziphil.com/dictionary/2283/settings"
        safe_action(f"Open settings page {settings_url}", lambda: page.goto(settings_url), page=page)
        page.wait_for_timeout(3000)
        save_shot(page, "settings_page_loaded")

        # ---------- フォントアップロードラジオ選択 ----------
        def select_font_upload_radio():
            try:
                labels = page.query_selector_all("label")
                candidates = [l for l in labels if "フォントをアップロード" in (l.inner_text() or "")]
                if candidates:
                    candidates[-1].click()
                    return True
            except:
                pass
            # フォールバック
            radios = page.query_selector_all("input[type='radio']")
            for r in radios[::-1]:
                try:
                    rid = r.get_attribute("id")
                    if rid:
                        lab = page.query_selector(f"label[for='{rid}']")
                        if lab and "フォントをアップロード" in (lab.inner_text() or ""):
                            r.check()
                            return True
                except:
                    pass
            return False

        safe_action("Select 'フォントをアップロード' radio", select_font_upload_radio, page=page)
        page.wait_for_timeout(3000)
        save_shot(page, "after_select_radio")

        # ---------- フォントアップロード ----------
        def upload_file():
            found = False
            for inp in page.query_selector_all("input[type='file']"):
                try:
                    inp.set_input_files(str(FONT_PATH))
                    log("CLEAR", "Font uploaded via set_input_files")
                    found = True
                    break
                except:
                    continue

        safe_action("Upload font file via file input", upload_file, page=page)
        page.wait_for_timeout(12000)
        save_shot(page, "after_file_upload")

        # ---------- 変更/保存ボタン ----------
        def click_change_button():
            clicked_any = False
            xpaths = [
                "//button[contains(text(),'変更')]",
                "//button[contains(text(),'保存')]",
                "//input[@type='submit' and (contains(@value,'変更') or contains(@value,'保存'))]",
                "//button[contains(translate(., 'CHANGE', 'change'),'change')]"
            ]
            for xp in xpaths:
                for el in page.query_selector_all(xp):
                    try:
                        el.click()
                        clicked_any = True
                        log("CLEAR", f"Clicked change/save button via {xp}")
                    except Exception as e:
                        log("WARN", f"Failed clicking element {xp}: {e}")

            if not clicked_any:
                log("WARN", "No change/save button clicked")
            return clicked_any

        safe_action("Click all change/save buttons", click_change_button, page=page)
        page.wait_for_timeout(3000)
        save_shot(page, "after_click_change")

        # ---------- UI要素タッチ ----------
        def touch_all_ui():
            try:
                for inp in page.query_selector_all("input"):
                    t = (inp.get_attribute("type") or "").lower()
                    if t in ("radio", "checkbox"):
                        try:
                            inp.check() if not inp.is_checked() else None
                        except:
                            pass
                for sel in page.query_selector_all("select"):
                    opts = sel.query_selector_all("option")
                    for o in opts[:3]:
                        try:
                            o.select_option(o.get_attribute("value"))
                            time.sleep(0.2)
                        except:
                            pass
            except:
                pass

        safe_action("Touch all UI elements (non-destructive)", touch_all_ui, page=page)
        save_shot(page, "after_touch_ui")

        log("CLEAR", "Script completed main steps (errors were logged but not fatal)")

    except Exception as e:
        log("FAIL", f"Unexpected top-level error: {e}")
        traceback.print_exc()
        try:
            save_shot(page, "fatal_error")
        except:
            pass
    finally:
        context.close()
        browser.close()
        log("CLEAR", "Browser closed, script exit")
