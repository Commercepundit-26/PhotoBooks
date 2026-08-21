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
    "Square": 20,
    "Portrait": 20,
    "Landscape": 20
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

SPECIFIC_QUERIES = {
    "Square": [
        "friends selfie square",
        "friends cafe coffee square",
        "friends laughing lifestyle square",
        "friends group smiling square",
        "friends party drinks square"
    ],
    "Portrait": [
        "best friends portrait vertical",
        "friends laughing outdoors vertical"
    ],
    "Landscape": [
        "friends road trip vacation landscape",
        "friends barbecue party outdoor"
    ]
}

print("="*70)
print("COMPLETING 60 FULL-RES MASTER PHOTOS — 'FRIENDS'")
print("="*70)

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

    for orientation in ["Square", "Portrait", "Landscape"]:
        target = TARGETS[orientation]
        have = count_orientation(orientation)
        print(f"\n>>> Orientation: {orientation} (Currently have {have}/{target})")
        if have >= target:
            print(f"✓ Already reached target for {orientation}.")
            continue

        for q in SPECIFIC_QUERIES[orientation]:
            if have >= target:
                break
            print(f"\n  -> Searching: '{q}' ({orientation})")
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
            for scroll_idx in range(6):
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
                        time.sleep(0.2)

                        with page.expect_download(timeout=6000) as dl_info:
                            btn.click(timeout=1500)
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
                                print(f"    [{have:02d}/{target}] ✓ {sugg_name} ({w}x{h} px, {mb:.1f} MB)")
                            time.sleep(0.4)
                    except Exception:
                        pass

                page.keyboard.press("PageDown")
                page.evaluate("window.scrollBy(0, 1500)")
                time.sleep(1.5)

        print(f"✓ Completed {orientation}: {have}/{target} photos.")

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)

# Audit
all_files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
total_mb = sum(os.path.getsize(os.path.join(TARGET_DIR, f)) for f in all_files) / (1024 * 1024)

print("\n" + "="*70)
print(f"FINAL FRIENDS AUDIT: {len(all_files)} Full-Resolution Photos ({total_mb:.1f} MB Total)")
print("="*70)
for idx, f in enumerate(sorted(all_files), 1):
    fp = os.path.join(TARGET_DIR, f)
    with Image.open(fp) as im:
        mb = os.path.getsize(fp) / (1024 * 1024)
        print(f" {idx:02d}. {f:<65} | {im.size[0]}x{im.size[1]} px | {mb:.1f} MB")
print("="*70)
