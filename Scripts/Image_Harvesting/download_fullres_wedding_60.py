#!/usr/bin/env python3
import os
import sys
import time
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Wedding"
ALT_TARGET = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(ALT_TARGET, exist_ok=True)

# Clean out old preview files
for f in os.listdir(TARGET_DIR):
    fp = os.path.join(TARGET_DIR, f)
    if os.path.isfile(fp):
        os.remove(fp)

for f in os.listdir(ALT_TARGET):
    fp = os.path.join(ALT_TARGET, f)
    if os.path.isfile(fp):
        os.remove(fp)

# Copy the first test download we already verified
test_file = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/test_dl/couple-celebrate-wedding-on-rocky-shoreline-at-sun-2026-03-17-00-03-13-utc.jpg"
if os.path.exists(test_file):
    shutil.copy2(test_file, os.path.join(TARGET_DIR, os.path.basename(test_file)))
    shutil.copy2(test_file, os.path.join(ALT_TARGET, os.path.basename(test_file)))

TARGET_PER_ORIENTATION = {
    "Landscape": 20,
    "Portrait": 20,
    "Square": 20
}

print("="*70)
print("ENVATO ELEMENTS: FULL-RESOLUTION UNCOMPRESSED PHOTO HARVESTER")
print("Target: 60 Full-Res Master Photos (20 Landscape, 20 Portrait, 20 Square)")
print("="*70)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=TARGET_DIR,
        accept_downloads=True
    )
    page = context.new_page()

    for orientation, target in TARGET_PER_ORIENTATION.items():
        current_in_orient = 0
        # Check current count of this orientation
        for f in os.listdir(TARGET_DIR):
            if f.endswith(('.jpg', '.jpeg', '.png')):
                try:
                    with Image.open(os.path.join(TARGET_DIR, f)) as im:
                        w, h = im.size
                        r = w / float(h)
                        if orientation == "Square" and 0.92 <= r <= 1.08:
                            current_in_orient += 1
                        elif orientation == "Portrait" and r < 0.92:
                            current_in_orient += 1
                        elif orientation == "Landscape" and r > 1.08:
                            current_in_orient += 1
                except Exception:
                    pass

        print(f"\n>>> Harvesting Full-Res Orientation: {orientation} (Have {current_in_orient}/{target})")
        if current_in_orient >= target:
            print(f"✓ Already have {current_in_orient} for {orientation}. Skipping.")
            continue

        page.goto("https://app.envato.com/", timeout=40000)
        time.sleep(2)

        # Close any popups
        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=1500)
        except Exception:
            pass

        # Search wedding
        inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
        inp.fill("wedding")
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
        clicked_ids = set()

        while current_in_orient < target and scroll_attempts < 30:
            scroll_attempts += 1
            
            # Find all download buttons
            dl_buttons = page.locator("button[data-cy='item-action-download']").all()
            
            for btn in dl_buttons:
                if current_in_orient >= target:
                    break
                try:
                    item_id = btn.get_attribute("data-analytics-item_id")
                    item_title = btn.get_attribute("data-analytics-item_title") or "wedding_photo"
                    if item_id in clicked_ids:
                        continue
                    clicked_ids.add(item_id)

                    # Scroll button into view
                    btn.scroll_into_view_if_needed(timeout=2000)
                    time.sleep(0.5)

                    # Trigger download
                    try:
                        with page.expect_download(timeout=15000) as download_info:
                            btn.click(timeout=3000)
                        download = download_info.value
                        suggested_name = download.suggested_filename
                        save_path = os.path.join(TARGET_DIR, suggested_name)
                        download.save_as(save_path)

                        # Sync copy to ALT_TARGET
                        shutil.copy2(save_path, os.path.join(ALT_TARGET, suggested_name))

                        # Check dimensions with PIL
                        with Image.open(save_path) as im:
                            w, h = im.size
                            file_size_mb = os.path.getsize(save_path) / (1024 * 1024)

                        current_in_orient += 1
                        print(f"  [{current_in_orient}/{target}] ✓ {suggested_name} ({w}x{h} px, {file_size_mb:.1f} MB)")
                        time.sleep(1)
                    except Exception as err:
                        # Sometimes clicking opens a modal or requires another click
                        pass
                except Exception:
                    pass

            page.evaluate("window.scrollBy(0, 1500)")
            time.sleep(2)

        print(f"✓ Completed {orientation}: {current_in_orient} full-res master photos.")

    context.close()

# Final summary
all_files = [f for f in os.listdir(TARGET_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
total_mb = sum(os.path.getsize(os.path.join(TARGET_DIR, f)) for f in all_files) / (1024 * 1024)

print("\n" + "="*70)
print(f"FINAL AUDIT: {len(all_files)} Full-Resolution Photos Downloaded ({total_mb:.1f} MB Total)")
print("="*70)
for idx, f in enumerate(sorted(all_files), 1):
    fp = os.path.join(TARGET_DIR, f)
    with Image.open(fp) as im:
        mb = os.path.getsize(fp) / (1024 * 1024)
        print(f" {idx:02d}. {f:<65} | {im.size[0]}x{im.size[1]} px | {mb:.1f} MB")
print("="*70)
