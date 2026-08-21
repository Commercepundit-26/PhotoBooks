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

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swim', 'swimwear', 'bath', 'towel', 'bed', 'bedroom',
    'lingerie', 'underwear', 'boudoir', 'naked', 'nude', 'shirtless',
    'office', 'laptop', 'computer', 'classroom', 'student', 'meeting',
    'intersection', 'crowd'
]

def get_counts():
    land, port, sq = 0, 0, 0
    for f in os.listdir(TARGET_DIR):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            fp = os.path.join(TARGET_DIR, f)
            try:
                with Image.open(fp) as im:
                    w, h = im.size
                    r = w / float(h)
                    if 0.90 <= r <= 1.10:
                        sq += 1
                    elif r < 0.90:
                        port += 1
                    else:
                        land += 1
            except Exception:
                pass
    return land, port, sq

QUERIES_PLAN = [
    # Portrait
    ("romantic couple laughing outdoor vertical portrait", "Portrait", 10),
    ("young couple hug sweater autumn vertical portrait", "Portrait", 10),
    ("couple city travel sightseeing vertical portrait", "Portrait", 10),

    # Square
    ("romantic couple laughing outdoor square", "Square", 10),
    ("young couple selfie casual clothes square", "Square", 10),
    ("couple coffee date cafe smiling table square", "Square", 10),
    ("couple enjoying park picnic smiling square", "Square", 10)
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

    for q, orient, limit in QUERIES_PLAN:
        land, port, sq = get_counts()
        total = land + port + sq
        if total >= 65 and port >= 20 and sq >= 20:
            break

        print(f"\n[Status: {total}/65 | L:{land}/22, P:{port}/22, S:{sq}/21] -> '{q}' ({orient})")
        page.goto("https://app.envato.com/", timeout=30000)
        time.sleep(1.5)

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=600)
        except Exception:
            pass

        try:
            inp = page.wait_for_selector("input[placeholder*='Search']", timeout=6000)
            inp.fill(q)
            inp.press("Enter")
            time.sleep(2.5)
        except Exception:
            continue

        try:
            more_btn = page.locator("text=+ more").first
            if more_btn.is_visible():
                more_btn.click()
                time.sleep(1.5)
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

        got = 0
        seen_ids = set()
        for scroll_round in range(5):
            if got >= limit or len(os.listdir(TARGET_DIR)) >= 65:
                break

            btns = page.locator("button[data-cy='item-action-download']").all()
            for btn in btns:
                if got >= limit or len(os.listdir(TARGET_DIR)) >= 65:
                    break
                try:
                    item_id = btn.get_attribute("data-analytics-item_id")
                    if not item_id or item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)

                    btn.scroll_into_view_if_needed(timeout=800)
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

                        cur_total = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                        print(f"  [{cur_total:02d}/65] ✓ [{this_orient}] {sugg} ({w}x{h} px, {mb:.1f} MB)")
                        got += 1
                        time.sleep(0.25)
                except Exception:
                    pass

            page.keyboard.press("PageDown")
            page.evaluate("window.scrollBy(0, 1800)")
            time.sleep(1.2)

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
