#!/usr/bin/env python3
import os
import sys
import time
import shutil
import urllib.parse
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Couple"
TEMP_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(TEMP_DL, exist_ok=True)

TARGETS = {
    "Landscape": 22,
    "Portrait": 22,
    "Square": 21
}

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swim', 'swimwear', 'bath', 'towel', 'bed', 'bedroom',
    'lingerie', 'underwear', 'boudoir', 'naked', 'nude', 'shirtless',
    'office', 'laptop', 'computer', 'classroom', 'student', 'meeting',
    'intersection', 'crowd'
]

def count_orientation(orient):
    cnt = 0
    for f in os.listdir(TARGET_DIR):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            fp = os.path.join(TARGET_DIR, f)
            try:
                with Image.open(fp) as im:
                    w, h = im.size
                    r = w / float(h)
                    if orient == "Square" and 0.88 <= r <= 1.12:
                        cnt += 1
                    elif orient == "Portrait" and r < 0.88:
                        cnt += 1
                    elif orient == "Landscape" and r > 1.12:
                        cnt += 1
            except Exception:
                pass
    return cnt

QUERIES_BY_ORIENT = {
    "Landscape": [
        "romantic couple autumn park walking holding hands",
        "couple cooking kitchen laughing dinner date",
        "young couple picnic park casual clothes smiling",
        "couple road trip scenic viewpoint laughing",
        "couple laughing piggyback outdoor city street"
    ],
    "Portrait": [
        "romantic couple smiling hug outdoor casual",
        "young couple laughing forehead touch love",
        "couple travel city sightseeing holding hands",
        "couple cozy coffee shop sweater autumn",
        "couple walking autumn forest casual clothes"
    ],
    "Square": [
        "romantic couple laughing candid square",
        "young couple selfie smiling casual clothes square",
        "couple coffee date cafe smiling table square",
        "couple holding hands coffee table cozy square",
        "couple smiling laughing outdoor park square"
    ]
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

    for orient, target in TARGETS.items():
        have = count_orientation(orient)
        print(f"\n>>> Orientation: {orient} (Currently have {have}/{target})")
        if have >= target:
            continue

        for q in QUERIES_BY_ORIENT[orient]:
            if have >= target or len(os.listdir(TARGET_DIR)) >= 65:
                break

            print(f"  -> Search: '{q}' ({orient})")
            page.goto("https://app.envato.com/", timeout=30000)
            time.sleep(1.5)

            try:
                page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=800)
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

            seen_ids = set()
            for scroll_idx in range(5):
                if have >= target or len(os.listdir(TARGET_DIR)) >= 65:
                    break

                btns = page.locator("button[data-cy='item-action-download']").all()
                for btn in btns:
                    if have >= target or len(os.listdir(TARGET_DIR)) >= 65:
                        break
                    try:
                        item_id = btn.get_attribute("data-analytics-item_id")
                        if not item_id or item_id in seen_ids:
                            continue
                        seen_ids.add(item_id)

                        btn.scroll_into_view_if_needed(timeout=800)
                        time.sleep(0.15)

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
                                mb = os.path.getsize(sp) / (1024 * 1024)

                            valid = False
                            if orient == "Square" and 0.88 <= r <= 1.12:
                                valid = True
                            elif orient == "Portrait" and r < 0.88:
                                valid = True
                            elif orient == "Landscape" and r > 1.12:
                                valid = True

                            if valid:
                                have += 1
                                print(f"    [{have:02d}/{target}] ✓ [{orient}] {sugg} ({w}x{h} px, {mb:.1f} MB)")
                            time.sleep(0.3)
                    except Exception:
                        pass

                page.keyboard.press("PageDown")
                page.evaluate("window.scrollBy(0, 1500)")
                time.sleep(1.2)

        print(f"✓ Completed {orient}: {have}/{target}")

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)

# Audit
all_files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
total_mb = sum(os.path.getsize(os.path.join(TARGET_DIR, f)) for f in all_files) / (1024 * 1024)
print("\n" + "="*75)
print(f"FINAL AUDIT: {len(all_files)} Master Photos in 'Couple' ({total_mb:.1f} MB Total)")
print("="*75)
