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

QUERIES_BY_ORIENTATION = {
    "Landscape": [
        "group of friends laughing outdoor picnic",
        "friends road trip vacation adventure",
        "friends party toast celebration",
        "friends dinner table restaurant laughing",
        "friends camping bonfire outdoors"
    ],
    "Portrait": [
        "best friends portrait smiling",
        "friends laughing candid vertical outdoor",
        "two female friends smiling happy",
        "group of friends vertical portrait",
        "friends hugging portrait lifestyle"
    ],
    "Square": [
        "friends selfie group square",
        "happy friends smiling portrait close up",
        "friends cafe coffee conversation square",
        "friends lifestyle aesthetic square"
    ]
}

print("="*70)
print("ENVATO ELEMENTS: MULTI-QUERY MASTER PHOTO HARVESTER — 'FRIENDS'")
print("Target: 20 Landscape, 20 Portrait, 20 Square (60 Total Full-Res Photos)")
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

    for orientation, target in TARGETS.items():
        have = count_orientation(orientation)
        print(f"\n>>> Orientation: {orientation} (Currently have {have}/{target})")
        if have >= target:
            print(f"✓ Target already reached for {orientation}.")
            continue

        for q in QUERIES_BY_ORIENTATION[orientation]:
            if have >= target:
                break
            print(f"\n  -> Searching: '{q}'")
            try:
                page.goto("https://app.envato.com/", timeout=30000)
                time.sleep(2)
                
                # Dismiss popups
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

                # Scroll down 3 times per query
                for _ in range(4):
                    if have >= target:
                        break
                    btns = page.locator("button[data-cy='item-action-download']").all()
                    for btn in btns:
                        if have >= target:
                            break
                        try:
                            btn.scroll_into_view_if_needed(timeout=1000)
                            with page.expect_download(timeout=8000) as dl_info:
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
                                    mb = os.path.getsize(save_path) / (1024 * 1024)

                                have += 1
                                print(f"    [{have:02d}/{target}] ✓ {sugg_name} ({w}x{h} px, {mb:.1f} MB)")
                                time.sleep(0.4)
                        except Exception:
                            pass

                    page.keyboard.press("PageDown")
                    page.evaluate("window.scrollBy(0, 1500)")
                    time.sleep(1.5)

            except Exception as e:
                print("Query step note:", e)

        print(f"✓ Completed {orientation}: {have}/{target} photos.")

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)

# Audit
all_files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
total_mb = sum(os.path.getsize(os.path.join(TARGET_DIR, f)) for f in all_files) / (1024 * 1024)

print("\n" + "="*70)
print(f"FINAL AUDIT: {len(all_files)} Full-Resolution Friends Photos ({total_mb:.1f} MB Total)")
print("="*70)
for idx, f in enumerate(sorted(all_files), 1):
    fp = os.path.join(TARGET_DIR, f)
    with Image.open(fp) as im:
        mb = os.path.getsize(fp) / (1024 * 1024)
        print(f" {idx:02d}. {f:<65} | {im.size[0]}x{im.size[1]} px | {mb:.1f} MB")
print("="*70)
