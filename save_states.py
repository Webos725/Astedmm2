#!/usr/bin/env python3
import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.environ["ATER_USERNAME"]
PASSWORD = os.environ["ATER_PASSWORD"]
STATE_FILE = "aternos_state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # GUI 表示
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://aternos.org/go/")
    time.sleep(2)

    # ユーザー名 / パスワード入力
    inputs = page.query_selector_all("input")
    if len(inputs) >= 2:
        inputs[0].fill(USERNAME)
        inputs[1].fill(PASSWORD)

    # ログインボタン
    btns = page.query_selector_all("button")
    for b in btns:
        text = (b.inner_text() or "").strip()
        if "ログイン" in text or "Login" in text:
            b.click()
            break

    # 少し待つ
    time.sleep(8)

    # state.json 保存
    context.storage_state(path=STATE_FILE)
    print(f"[INFO] state saved to {STATE_FILE}")

    browser.close()
