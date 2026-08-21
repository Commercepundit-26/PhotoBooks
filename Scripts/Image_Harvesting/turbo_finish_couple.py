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

REQUIRED_KEYWORDS = ['couple', 'lover', 'romantic', 'boyfriend', 'girlfriend', 'dating', 'hug', 'kiss', 'man-and-woman', 'two-people', 'pair']

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swim', 'swimwear', 'bath', 'towel', 'bed', 'bedroom',
    'lingerie', 'underwear', 'boudoir', 'naked', 'nude', 'shirtless',
    'office', 'laptop', 'computer', 'classroom', 'student', 'meeting',
    'intersection', 'crowd', 'isolated-on-white', 'cut-out', 'lizard', 'escalator'
]

SEARCH_TERMS = [
    "young loving couple winter coats snow",
    "couple coffee date cafe smiling table",
    "happy couple dancing kitchen dinner home",
    "couple autumn park walking laughing holding hands",
    "couple road trip scenic car mountain viewpoint",
    "couple laughing selfie phone casual smiling",
    "loving couple forehead touch intimate sweet outdoor",
    "couple picnic park blanket laughing summer sunset"
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

    for term in SEARCH_TERMS:
        cur_count = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if cur_count >= TARGET_TOTAL:
            break

        print(f"\n[Status: {cur_count:02d}/{TARGET_TOTAL}] -> Searching: '{term}'")
        page.goto("https://app.envato.com/", timeout=35000)
        time.sleep(2.0)

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=500)
        except Exception:
            pass

        try:
            inp = page.wait_for_selector("input[placeholder*='Search']", timeout=6000)
            inp.fill(term)
            page.keyboard.press("Enter")
            time.sleep(3.5)
        except Exception:
            continue

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=500)
        except Exception:
            pass

        btns = page.locator("button[data-cy='item-action-download']").all()
        print(f"  Found {len(btns)} download buttons.")

        seen_ids = set()
        got_in_term = 0
        for btn in btns:
            cur_count = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            if cur_count >= TARGET_TOTAL or got_in_term >= 4:
                break

            try:
                item_id = btn.get_attribute("data-analytics-item_id")
                if item_id and item_id in seen_ids:
                    continue
                if item_id:
                    seen_ids.add(item_id)

                btn.scroll_into_view_if_needed(timeout=400)
                time.sleep(0.05)

                with page.expect_download(timeout=1800) as dl_info:
                    btn.click(timeout=600, force=True)
                dl = dl_info.value
                sugg = dl.suggested_filename

                fl = sugg.lower()
                if any(kw in fl for kw in FORBIDDEN_KEYWORDS):
                    continue

                if not any(req in fl for req in REQUIRED_KEYWORDS):
                    continue

                if sugg not in seen_files and fl.endswith(('.jpg', '.jpeg', '.png')):
                    sp = os.path.join(TARGET_DIR, sugg)
                    dl.save_as(sp)
                    seen_files.add(sugg)

                    with Image.open(sp) as im:
                        w, h = im.size
                        r = w / float(h)
                        orient = "Square" if 0.90 <= r <= 1.10 else ("Portrait" if r < 0.90 else "Landscape")
                        mb = os.path.getsize(sp) / (1024 * 1024)

                    cur_count = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                    print(f"  [{cur_count:02d}/{TARGET_TOTAL}] ✓ [{orient}] {sugg} ({w}x{h} px, {mb:.1f} MB)")
                    got_in_term += 1
                    time.sleep(0.15)
            except Exception:
                pass

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
