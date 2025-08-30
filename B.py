#!/usr/bin/env python3
import os
import time
import traceback
from playwright.sync_api import sync_playwright

# ---------- 設定 ----------
USERNAME = "komugishomin"
PASSWORD = "A1B2c!d?"

SCREENSHOT_DIR = os.path.abspath("scripts/screenshots_playwright")
DOWNLOAD_DIR = os.path.abspath("downloads")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DRIVE_URL = "https://konnitiwa768.github.io/PVPVe/packs.mcaddon"

def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)

def save_shot(page, name):
    try:
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)[:120]
        path = os.path.join(SCREENSHOT_DIR, f"{int(time.time())}_{safe_name}.png")
        page.screenshot(path=path, full_page=True)
        log("SHOT", f"Saved screenshot: {path}")
    except Exception as e:
        log("WARN", f"Failed to save screenshot: {e}")

def wait_for_download(context, timeout=60):
    try:
        with context.expect_download(timeout=timeout * 1000) as download_info:
            download = download_info.value
            path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            download.save_as(path)
            return path
    except Exception:
        return None

# ---------- 実行 ----------
with sync_playwright() as p:
    browser = None
    try:
        # CI環境では headless=True が必須
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # ログインページ
        log("RUN", "Open login page")
        page.goto("https://aternos.org/go/")
        save_shot(page, "login_page")

        # ユーザー名 / パスワード入力
        log("RUN", "Fill credentials")
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            time.sleep(0.5)  # 人間っぽく
            inputs[1].fill(PASSWORD)
        save_shot(page, "filled_credentials")

        # ログインボタン押下
        log("RUN", "Click login button")
        btns = page.query_selector_all("button")
        clicked = False
        for b in btns:
            text = (b.inner_text() or "").strip()
            if "ログイン" in text or "Login" in text:
                b.click()
                clicked = True
                break
        if not clicked and len(inputs) >= 2:
            inputs[1].press("Enter")

        page.wait_for_timeout(6000)
        save_shot(page, "after_login")

        # Google Drive ダウンロード
        log("RUN", "Open Google Drive link")
        page.goto(DRIVE_URL)
        dl_path = wait_for_download(context, timeout=60)
        if not dl_path:
            log("FAIL", "File download failed")
            raise SystemExit(1)
        log("CLEAR", f"Downloaded file: {dl_path}")
        save_shot(page, "after_download")

        # packs ページへ
        log("RUN", "Open packs page")
        page.goto("https://aternos.org/files/packs/")
        page.wait_for_timeout(5000)
        save_shot(page, "packs_page")

        # アップロード
        log("RUN", "Upload file")
        uploaded = False
        for sel in [
            "input[type='file']",
            "input[name*='upload']",
            "input[class*='upload']",
            "input[accept*='pack']",
            "input"
        ]:
            try:
                inp = page.query_selector(sel)
                if inp:
                    inp.set_input_files(dl_path)
                    log("CLEAR", f"Sent file to {sel}")
                    uploaded = True
                    break
            except Exception as e:
                log("WARN", f"{sel} failed: {e}")
        if not uploaded:
            log("FAIL", "No file input found for upload")
        page.wait_for_timeout(15000)
        save_shot(page, "after_upload")

        log("CLEAR", "Script finished successfully")

    except Exception as e:
        log("FAIL", f"Top level error: {e}")
        traceback.print_exc()
        try:
            save_shot(page, "fatal_error")
        except:
            pass
    finally:
        if browser:
            browser.close()
        log("CLEAR", "Browser quit, exit")
