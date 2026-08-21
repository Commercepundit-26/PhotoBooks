#!/usr/bin/env python3
import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TEST_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/test_dl"
os.makedirs(TEST_DL, exist_ok=True)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=TEST_DL,
        accept_downloads=True
    )
    page = context.new_page()
    page.goto("https://app.envato.com/", timeout=30000)
    time.sleep(2)
    
    inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
    inp.fill("wedding")
    inp.press("Enter")
    time.sleep(3)
    
    more_btn = page.query_selector("text=+ more")
    if more_btn:
        more_btn.click()
        time.sleep(3)
        
    dl_buttons = page.locator("button[data-cy='item-action-download']").all()
    print(f"Found {len(dl_buttons)} download buttons!")
    
    if dl_buttons:
        print("Clicking first download button...")
        try:
            with page.expect_download(timeout=15000) as download_info:
                dl_buttons[0].click()
            dl = download_info.value
            target_path = os.path.join(TEST_DL, dl.suggested_filename)
            dl.save_as(target_path)
            print(f"✓ DIRECT DOWNLOAD SUCCESS: {target_path} ({os.path.getsize(target_path)} bytes)")
        except Exception as e:
            print("Download event:", e)
            time.sleep(2)
            # Check what popped up
            page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/after_download_click.png")
            print("Saved after_download_click.png")
            # Check for project dialog buttons
            dialog_btns = page.locator("button").all()
            for b in dialog_btns:
                if b.is_visible():
                    print("Visible button:", repr(b.inner_text().strip()))
                    
    context.close()
