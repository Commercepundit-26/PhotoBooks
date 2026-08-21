#!/usr/bin/env python3
import os
import sys
import time
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Friends"
ALT_TARGET = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Friends"
TEMP_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(ALT_TARGET, exist_ok=True)
os.makedirs(TEMP_DL, exist_ok=True)

TARGETS = {
    "Landscape": 20,
    "Portrait": 20,
    "Square": 20
}

def count_orientation(orient):
    cnt = 0
    for f in os.listdir(TARGET_DIR):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            fp = os.path.join(TARGET_DIR, f)
            try:
                with Image.open(fp) as im:
                    w, h = im.size
                    r = w / float(h)
                    if orient == "Square" and 0.90 <= r <= 1.10:
                        cnt += 1
                    elif orient == "Portrait" and r < 0.90:
                        cnt += 1
                    elif orient == "Landscape" and r > 1.10:
                        cnt += 1
            except Exception:
                pass
    return cnt

QUERIES = {
    "Landscape": ["friends vacation summer beach sunset"],
    "Portrait": ["friends portrait smiling outdoor vertical"],
    "Square": ["friends coffee cafe conversation square"]
}

seen_files = set(os.listdir(TARGET_DIR))

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=TEMP_DL,
        accept_downloads=True
    )
    page = context.new_page()

    for orientation, target in TARGETS.items():
        have = count_orientation(orientation)
        if have >= target:
            print(f"✓ {orientation} already at {have}/{target}.")
            continue

        q = QUERIES[orientation][0]
        print(f"\n>>> Topping up {orientation}: ({have}/{target}) with '{q}'")
        page.goto("https://app.envato.com/", timeout=30000)
        time.sleep(2)

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=1000)
        except Exception:
            pass

        inp = page.wait_for_selector("input[placeholder*='Search']", timeout=8000)
        inp.fill(q)
        inp.press("Enter")
        time.sleep(3)

        try:
            more_btn = page.locator("text=+ more").first
            if more_btn.is_visible():
                more_btn.click()
                time.sleep(2)
        except Exception:
            pass

        try:
            orient_btn = page.locator("button:has-text('Orientation')").first
            if orient_btn.is_visible():
                orient_btn.click()
                time.sleep(1)
                opt = page.locator(f"button:has-text('{orientation}'), label:has-text('{orientation}'), [role='option']:has-text('{orientation}')").first
                if opt.is_visible():
                    opt.click()
                    time.sleep(2)
        except Exception:
            pass

        seen_ids = set()
        for _ in range(6):
            if have >= target:
                break
            btns = page.locator("button[data-cy='item-action-download']").all()
            for btn in btns:
                if have >= target:
                    break
                try:
                    item_id = btn.get_attribute("data-analytics-item_id")
                    if not item_id or item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)

                    btn.scroll_into_view_if_needed(timeout=1000)
                    time.sleep(0.15)

                    with page.expect_download(timeout=5000) as dl_info:
                        btn.click(timeout=1200)
                    download = dl_info.value
                    sugg_name = download.suggested_filename

                    if sugg_name not in seen_files and sugg_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        save_path = os.path.join(TARGET_DIR, sugg_name)
                        download.save_as(save_path)
                        shutil.copy2(save_path, os.path.join(ALT_TARGET, sugg_name))
                        seen_files.add(sugg_name)

                        with Image.open(save_path) as im:
                            w, h = im.size
                            r = w / float(h)
                            mb = os.path.getsize(save_path) / (1024 * 1024)

                        valid = False
                        if orientation == "Square" and 0.88 <= r <= 1.12:
                            valid = True
                        elif orientation == "Portrait" and r < 0.90:
                            valid = True
                        elif orientation == "Landscape" and r > 1.10:
                            valid = True

                        if valid:
                            have += 1
                            print(f"  [{have:02d}/{target}] ✓ {sugg_name} ({w}x{h} px, {mb:.1f} MB)")
                        time.sleep(0.3)
                except Exception:
                    pass

            page.keyboard.press("PageDown")
            page.evaluate("window.scrollBy(0, 1500)")
            time.sleep(1.5)

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
