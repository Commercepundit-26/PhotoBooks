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
                    if orient == "Square" and 0.92 <= r <= 1.08:
                        cnt += 1
                    elif orient == "Portrait" and r < 0.92:
                        cnt += 1
                    elif orient == "Landscape" and r > 1.08:
                        cnt += 1
            except Exception:
                pass
    return cnt

print("="*70)
print("ENVATO ELEMENTS: FULL-RES 60 MASTER PHOTO HARVESTER — 'FRIENDS'")
print("Target: 20 Landscape, 20 Portrait, 20 Square (60 Total Full-Res Photos)")
print("="*70)

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
        print(f"\n>>> Processing Orientation: {orientation} (Currently have {have}/{target})")
        if have >= target:
            print(f"✓ Already have {have} for {orientation}. Skipping.")
            continue

        page.goto("https://app.envato.com/", timeout=40000)
        time.sleep(2)

        # Dismiss popups
        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=1500)
        except Exception:
            pass

        # Search friends
        inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
        inp.fill("friends")
        inp.press("Enter")
        time.sleep(3)

        # Click + more under Photos
        try:
            more_btn = page.locator("text=+ more").first
            if more_btn.is_visible():
                more_btn.click()
                time.sleep(3)
        except Exception:
            pass

        # Apply orientation filter
        try:
            orient_btn = page.locator("button:has-text('Orientation')").first
            if orient_btn.is_visible():
                orient_btn.click()
                time.sleep(1)
                opt = page.locator(f"button:has-text('{orientation}'), label:has-text('{orientation}'), [role='option']:has-text('{orientation}')").first
                if opt.is_visible():
                    opt.click()
                    print(f"Applied {orientation} filter.")
                    time.sleep(3)
        except Exception as e:
            print("Orientation filter note:", e)

        scroll_attempts = 0
        seen_ids = set()

        while have < target and scroll_attempts < 40:
            scroll_attempts += 1
            
            # Find all download buttons
            dl_buttons = page.locator("button[data-cy='item-action-download']").all()
            
            for btn in dl_buttons:
                if have >= target:
                    break
                try:
                    item_id = btn.get_attribute("data-analytics-item_id")
                    if not item_id or item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)

                    btn.scroll_into_view_if_needed(timeout=2000)
                    time.sleep(0.2)

                    try:
                        with page.expect_download(timeout=15000) as download_info:
                            btn.click(timeout=3000)
                        download = download_info.value
                        sugg_name = download.suggested_filename
                        save_path = os.path.join(TARGET_DIR, sugg_name)
                        download.save_as(save_path)
                        shutil.copy2(save_path, os.path.join(ALT_TARGET, sugg_name))

                        with Image.open(save_path) as im:
                            w, h = im.size
                            mb = os.path.getsize(save_path) / (1024 * 1024)

                        have += 1
                        print(f"  [{have:02d}/{target}] ✓ {sugg_name} ({w}x{h} px, {mb:.1f} MB)")
                        time.sleep(0.6)
                    except Exception:
                        pass
                except Exception:
                    pass

            # Multi-scroll technique
            page.keyboard.press("PageDown")
            page.evaluate("window.scrollBy(0, 2000)")
            time.sleep(2)

        print(f"✓ Completed {orientation}: {have} master photos.")

    context.close()

# Cleanup temp downloads folder
shutil.rmtree(TEMP_DL, ignore_errors=True)

# Final audit
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
