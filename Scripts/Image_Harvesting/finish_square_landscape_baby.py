#!/usr/bin/env python3
import os
import sys
import time
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Baby"
TEMP_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(TEMP_DL, exist_ok=True)

SEARCH_QUERIES = [
    "cute baby smiling square",
    "newborn baby sleeping cozy blanket square",
    "baby laughing nursery square",
    "baby close up eyes square",
    "toddler playing wooden toys square",
    "baby eating fruits messy square",
    "cute baby crawling garden landscape",
    "baby family nursery cozy landscape",
    "baby first steps nursery landscape",
    "baby exploring outdoors sunny grass landscape"
]

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swimwear', 'underwear', 'lingerie', 'office', 'laptop',
    'computer', 'classroom', 'meeting', 'intersection', 'crowd',
    'isolated-on-white', 'cut-out', 'sick', 'hospital', 'doctor', 'syringe', 'crying'
]

print("="*70)
print("FINISHING REMAINING SQUARE & LANDSCAPE BABY PHOTOS TO REACH 65+")
print("="*70)

# Kill any existing chrome profile processes
os.system("ps aux | grep photobook_chrome_profile | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true")
time.sleep(1)

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

    for q in SEARCH_QUERIES:
        total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if total_now >= 65:
            break

        print(f"\n>>> Query: '{q}' (Current Total: {total_now}/65)")
        page.goto("https://app.envato.com/", timeout=30000)
        time.sleep(2.0)

        # Close any popups/modals
        try:
            page.locator("button[aria-label='Close'], button:has-text('✕'), button:has-text('×')").first.click(timeout=600)
        except Exception:
            pass

        try:
            inp = page.locator("input[placeholder*='Search']").first
            inp.click(timeout=2000)
            inp.fill(q)
            inp.press("Enter")
            time.sleep(3.0)
        except Exception as e:
            continue

        try:
            page.locator("button[aria-label='Close'], button:has-text('✕'), button:has-text('×')").first.click(timeout=600)
        except Exception:
            pass

        got_in_query = 0
        seen_ids = set()
        for scroll_i in range(3):
            if got_in_query >= 4:
                break
            total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            if total_now >= 65:
                break

            btns = page.locator("button[data-cy='item-action-download']").all()
            for btn in btns:
                if got_in_query >= 4:
                    break
                total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                if total_now >= 65:
                    break
                try:
                    item_id = btn.get_attribute("data-analytics-item_id")
                    if not item_id or item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)

                    with page.expect_download(timeout=5000) as dl_info:
                        btn.click(timeout=800, force=True)
                    dl = dl_info.value
                    sugg = dl.suggested_filename

                    fl = sugg.lower()
                    if any(kw in fl for kw in FORBIDDEN_KEYWORDS):
                        continue

                    if sugg not in seen_files and fl.endswith(('.jpg', '.jpeg', '.png')):
                        sp = os.path.join(TARGET_DIR, sugg)
                        dl.save_as(sp)
                        seen_files.add(sugg)

                        with Image.open(sp) as im:
                            w, h = im.size
                            r = w / float(h)
                            act_orient = "Square" if 0.88 <= r <= 1.12 else ("Portrait" if r < 0.90 else "Landscape")
                            mb = os.path.getsize(sp) / (1024 * 1024)

                        total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                        got_in_query += 1
                        print(f"    [{total_now:02d}/65] ✓ [{act_orient}] {sugg} ({w}x{h} px, {mb:.1f} MB)")
                        time.sleep(0.15)
                except Exception:
                    pass

            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(1.0)

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
total_final = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
print(f"\n=======================================================")
print(f"HARVEST FINISHED! Total Baby Photos: {total_final}/65")
print(f"=======================================================")
