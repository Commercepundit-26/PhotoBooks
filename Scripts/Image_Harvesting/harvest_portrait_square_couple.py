#!/usr/bin/env python3
import os
import sys
import time
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Couple"
TEMP_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(TEMP_DL, exist_ok=True)

TARGET_TOTAL = 65

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swim', 'swimwear', 'bath', 'towel', 'bed', 'bedroom',
    'lingerie', 'underwear', 'boudoir', 'naked', 'nude', 'shirtless',
    'office', 'laptop', 'computer', 'classroom', 'student', 'meeting',
    'intersection', 'crowd', 'isolated-on-white', 'cut-out'
]

QUERIES_PLAN = [
    # Portrait
    ("romantic couple laughing outdoor", "Portrait"),
    ("young couple hugging park autumn", "Portrait"),
    ("couple smiling coffee shop", "Portrait"),
    ("couple travel sightseeing city", "Portrait"),
    ("couple holding hands walking street", "Portrait"),

    # Square
    ("romantic couple smiling square", "Square"),
    ("young couple laughing selfie square", "Square"),
    ("couple coffee date cafe table square", "Square"),
    ("couple holding hands coffee cozy square", "Square"),
    ("couple enjoying park picnic square", "Square"),
    ("couple road trip car smiling square", "Square")
]

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

    for q, orient in QUERIES_PLAN:
        cur_count = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if cur_count >= TARGET_TOTAL:
            break

        print(f"\n[Status: {cur_count:02d}/{TARGET_TOTAL}] -> '{q}' ({orient})")
        page.goto("https://app.envato.com/", timeout=35000)
        time.sleep(1.5)

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=600)
        except Exception:
            pass

        try:
            inp = page.wait_for_selector("input[placeholder*='Search']", timeout=6000)
            inp.fill(q)
            page.keyboard.press("Enter")
            time.sleep(3.0)
        except Exception:
            continue

        try:
            more_btn = page.locator("text=+ more").first
            if more_btn.is_visible():
                more_btn.click()
                time.sleep(1.0)
        except Exception:
            pass

        try:
            orient_btn = page.locator("button:has-text('Orientation')").first
            if orient_btn.is_visible():
                orient_btn.click()
                time.sleep(0.8)
                opt = page.locator(f"button:has-text('{orient}'), label:has-text('{orient}'), [role='option']:has-text('{orient}')").first
                if opt.is_visible():
                    opt.click()
                    time.sleep(1.5)
        except Exception:
            pass

        got_in_q = 0
        btns = page.locator("button[data-cy='item-action-download']").all()
        for btn in btns:
            cur_count = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            if cur_count >= TARGET_TOTAL or got_in_q >= 5:
                break

            try:
                btn.scroll_into_view_if_needed(timeout=600)
                time.sleep(0.1)

                with page.expect_download(timeout=5000) as dl_info:
                    btn.click(timeout=1200)
                dl = dl_info.value
                sugg = dl.suggested_filename

                fl = sugg.lower()
                if any(kw in fl for kw in FORBIDDEN_KEYWORDS):
                    continue

                if sugg not in seen_files and sugg.lower().endswith(('.jpg', '.jpeg', '.png')):
                    sp = os.path.join(TARGET_DIR, sugg)
                    dl.save_as(sp)
                    seen_files.add(sugg)

                    with Image.open(sp) as im:
                        w, h = im.size
                        r = w / float(h)
                        this_orient = "Square" if 0.90 <= r <= 1.10 else ("Portrait" if r < 0.90 else "Landscape")
                        mb = os.path.getsize(sp) / (1024 * 1024)

                    cur_count = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                    print(f"  [{cur_count:02d}/{TARGET_TOTAL}] ✓ [{this_orient}] {sugg} ({w}x{h} px, {mb:.1f} MB)")
                    got_in_q += 1
                    time.sleep(0.2)
            except Exception:
                pass

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
