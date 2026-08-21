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

# Target breakdown for 65 photos
TARGETS = {
    "Landscape": 22,
    "Portrait": 22,
    "Square": 21
}

# Strict negative keywords to avoid wedding, swimwear, work, or inappropriate content
FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swim', 'swimwear', 'bath', 'towel', 'bed', 'bedroom',
    'lingerie', 'underwear', 'boudoir', 'naked', 'nude', 'shirtless',
    'office', 'laptop', 'computer', 'classroom', 'student', 'meeting',
    'intersection', 'crowd', 'isolated-on-white', 'cut-out'
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
    "Landscape": [
        "romantic couple autumn park walking holding hands golden hour",
        "couple cooking kitchen laughing dinner date together",
        "young couple picnic park casual clothes smiling",
        "couple road trip scenic viewpoint laughing sunset",
        "couple laughing piggyback outdoor city street casual"
    ],
    "Portrait": [
        "romantic couple smiling hug outdoor casual vertical",
        "young couple laughing forehead touch love vertical",
        "couple travel city sightseeing holding hands vertical",
        "couple cozy coffee shop sweater autumn vertical",
        "couple walking autumn forest casual clothes vertical"
    ],
    "Square": [
        "romantic couple laughing candid square",
        "young couple selfie smiling casual clothes square",
        "couple coffee date cafe smiling table square",
        "couple holding hands coffee table cozy square",
        "couple smiling laughing outdoor park square"
    ]
}

print("="*75)
print("ENVATO ELEMENTS: 65 MASTER FULL-RES CAMERA PHOTOS — 'COUPLE / LOVE'")
print("Targets: 22 Landscape, 22 Portrait, 21 Square (65 Total Master Photos)")
print("Rule: 100% Non-Wedding, 100% Modest (No Swimwear/Bed), Authentic Romance")
print("="*75)

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
        print(f"\n>>> Orientation: {orientation} (Currently have {have}/{target})")
        if have >= target:
            print(f"✓ Target already met for {orientation}.")
            continue

        for q in QUERIES[orientation]:
            if have >= target or len(os.listdir(TARGET_DIR)) >= 65:
                break
            print(f"\n  -> Searching: '{q}' ({orientation})")
            page.goto("https://app.envato.com/", timeout=35000)
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
            for scroll_idx in range(6):
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

                        btn.scroll_into_view_if_needed(timeout=1000)
                        time.sleep(0.2)

                        with page.expect_download(timeout=6000) as dl_info:
                            btn.click(timeout=1500)
                        download = dl_info.value
                        sugg_name = download.suggested_filename

                        # Check filename against forbidden keywords
                        fl = sugg_name.lower()
                        if any(kw in fl for kw in FORBIDDEN_KEYWORDS):
                            continue

                        if sugg_name not in seen_files and sugg_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                            save_path = os.path.join(TARGET_DIR, sugg_name)
                            download.save_as(save_path)
                            seen_files.add(sugg_name)

                            with Image.open(save_path) as im:
                                w, h = im.size
                                r = w / float(h)
                                mb = os.path.getsize(save_path) / (1024 * 1024)

                            # Validate orientation
                            valid = False
                            if orientation == "Square" and 0.88 <= r <= 1.12:
                                valid = True
                            elif orientation == "Portrait" and r < 0.90:
                                valid = True
                            elif orientation == "Landscape" and r > 1.10:
                                valid = True

                            if valid:
                                have += 1
                                print(f"    [{have:02d}/{target}] ✓ [{orientation}] {sugg_name} ({w}x{h} px, {mb:.1f} MB)")
                            else:
                                # Keep it as general if it's high quality
                                pass
                            time.sleep(0.4)
                    except Exception:
                        pass

                page.keyboard.press("PageDown")
                page.evaluate("window.scrollBy(0, 1800)")
                time.sleep(1.5)

        print(f"✓ Completed {orientation}: {have}/{target} photos.")

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)

# Final audit
all_files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
total_mb = sum(os.path.getsize(os.path.join(TARGET_DIR, f)) for f in all_files) / (1024 * 1024)

print("\n" + "="*75)
print(f"FINAL AUDIT: {len(all_files)} Master Photos in 'Couple' ({total_mb:.1f} MB Total)")
print("="*75)
