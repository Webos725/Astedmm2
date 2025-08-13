#!/usr/bin/env python3
import os
import time
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------- 設定 ----------
SCREENSHOT_DIR = Path("scripts/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
FONT_PATH = Path("downloads/font.ttf")
USER_ID = os.environ.get("USER_ID")
PASS = os.environ.get("PASS")

def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)

def save_shot(page, name):
    try:
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)[:120]
        path = SCREENSHOT_DIR / f"{int(time.time())}_{safe_name}.png"
        page.screenshot(path=str(path))
        log("SHOT", f"Saved screenshot: {path}")
    except Exception as e:
        log("WARN", f"Failed to save screenshot: {e}")

if not USER_ID:
    log("WARN", "USER_ID not set in environment")
if not PASS:
    log("WARN", "PASS not set in environment")
if not FONT_PATH.exists():
    log("WARN", f"Font file not found at {FONT_PATH}")

# ---------- 実行 ----------
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        # ログインページ
        log("RUN", "Open login page")
        page.goto("https://zpdic.ziphil.com/login")
        save_shot(page, "login_page_loaded")

        # 入力フォーム
        try:
            page.fill("input[name='userId'], input[name='username'], input[type='text']", USER_ID or "")
            page.fill("input[name='password'], input[type='password']", PASS or "")
            log("OK", "Filled credentials")
        except Exception as e:
            log("WARN", f"Failed to fill credentials: {e}")

        # ログインボタン
        try:
            page.click("button:has-text('ログイン'), button:has-text('Login'), input[type='submit']")
            log("OK", "Clicked login button")
        except:
            log("WARN", "Login button click fallback")
            page.keyboard.press("Enter")

        time.sleep(6)
        save_shot(page, "after_login")

        # 設定ページ
        settings_url = "https://zpdic.ziphil.com/dictionary/2283/settings"
        log("RUN", f"Open settings page {settings_url}")
        page.goto(settings_url)
        time.sleep(3)
        save_shot(page, "settings_page_loaded")

        # フォントアップロードラジオ選択
        try:
            radios = page.locator("label:has-text('フォントをアップロード')")
            if radios.count() > 0:
                radios.nth(radios.count()-1).click()
                log("OK", "Selected 'フォントをアップロード' radio")
            else:
                log("WARN", "No radio found for upload")
        except:
            log("WARN", "Failed selecting radio")

        time.sleep(3)
        save_shot(page, "after_select_radio")

        # ファイルアップロード（send_keys → 3秒後 JS fallback）
        uploaded = False
        try:
            file_inputs = page.locator("input[type='file']")
            if file_inputs.count() > 0:
                file_inputs.first.set_input_files(str(FONT_PATH))
                uploaded = True
                log("CLEAR", "Font uploaded via set_input_files")
        except Exception as e:
            log("WARN", f"set_input_files failed: {e}")

        if not uploaded:
            log("RUN", "Waiting 3s before JS fallback")
            time.sleep(3)
            try:
                page.evaluate(f"""
                let fileInput = document.querySelector("input[type=file]");
                let dt = new DataTransfer();
                dt.items.add(new File([''], '{FONT_PATH.name}'));
                fileInput.files = dt.files;
                fileInput.dispatchEvent(new Event('change', {{bubbles:true}}));
                """)
                uploaded = True
                log("CLEAR", "Font uploaded via JS fallback")
            except Exception as e:
                log("WARN", f"JS fallback failed: {e}")

        time.sleep(12)
        save_shot(page, "after_file_upload")

        # 変更/保存ボタンクリック
        try:
            page.click("button:has-text('変更'), button:has-text('保存'), input[type='submit']")
            log("CLEAR", "Clicked change/save button")
        except:
            log("WARN", "Change/save button not found or failed")

        time.sleep(3)
        save_shot(page, "after_click_change")

        # UI要素に軽く触れる（非破壊）
        try:
            for inp in page.locator("input[type='radio'], input[type='checkbox']").all():
                try:
                    inp.check()
                    time.sleep(0.2)
                except:
                    pass
            for sel in page.locator("select").all():
                options = sel.locator("option").all()[:3]
                for o in options:
                    try:
                        o.select_option(o.get_attribute("value"))
                        time.sleep(0.2)
                    except:
                        pass
        except:
            pass

        save_shot(page, "after_touch_ui")
        log("CLEAR", "Script completed main steps")

    except Exception as e:
        log("FAIL", f"Unexpected top-level error: {e}")
        traceback.print_exc()
        try:
            save_shot(page, "fatal_error")
        except:
            pass
    finally:
        browser.close()
        log("CLEAR", "Browser closed, script exit")
