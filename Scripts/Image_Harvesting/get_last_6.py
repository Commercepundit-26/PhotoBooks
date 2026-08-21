#!/usr/bin/env python3
import os, sys, time, shutil
from PIL import Image
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.expanduser('~/.photobook_chrome_profile')
TARGET_DIR = '/Users/cp/Ronak/CC/Photobooks/Friends'
ALT_TARGET = '/Users/cp/Ronak/CC/Photobooks/Image_Library/Friends'
TEMP_DL = '/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads'
os.makedirs(TEMP_DL, exist_ok=True)

seen_files = set(os.listdir(TARGET_DIR))

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel='chrome',
        downloads_path=TEMP_DL,
        accept_downloads=True
    )
    page = context.new_page()

    page.goto('https://app.envato.com/photos/friends', timeout=30000)
    time.sleep(3)

    try:
        page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=1000)
    except:
        pass

    page.evaluate("window.scrollBy(0, 3000)")
    time.sleep(2)

    added = 0
    btns = page.locator("button[data-cy='item-action-download']").all()
    for btn in btns:
        if len(os.listdir(TARGET_DIR)) >= 60:
            break
        try:
            btn.scroll_into_view_if_needed(timeout=1000)
            time.sleep(0.2)
            with page.expect_download(timeout=6000) as dl_info:
                btn.click(timeout=1500)
            dl = dl_info.value
            sugg = dl.suggested_filename
            if sugg not in seen_files and sugg.lower().endswith(('.jpg', '.jpeg', '.png')):
                sp = os.path.join(TARGET_DIR, sugg)
                dl.save_as(sp)
                shutil.copy2(sp, os.path.join(ALT_TARGET, sugg))
                seen_files.add(sugg)
                added += 1
                with Image.open(sp) as im:
                    w, h = im.size
                    mb = os.path.getsize(sp)/(1024*1024)
                    print(f"  [{len(os.listdir(TARGET_DIR))}/60] ✓ {sugg} ({w}x{h} px, {mb:.1f} MB)")
                time.sleep(0.3)
        except Exception:
            pass

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
