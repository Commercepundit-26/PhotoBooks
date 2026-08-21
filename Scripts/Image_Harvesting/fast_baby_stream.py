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

TARGET_TOTAL = 65

REQUIRED_KEYWORDS = ['baby', 'infant', 'newborn', 'toddler', 'child', 'kid', 'nursery', 'son', 'daughter', 'mother-and-baby', 'father-and-baby', 'parents', 'cute', 'little-boy', 'little-girl', 'feet', 'toes', 'hands']

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swimwear', 'underwear', 'lingerie', 'office', 'laptop',
    'computer', 'classroom', 'meeting', 'intersection', 'crowd',
    'isolated-on-white', 'cut-out', 'sick', 'hospital', 'doctor', 'syringe', 'crying'
]

SEARCH_TERMS = [
    "newborn baby sleeping peacefully cozy blanket",
    "happy baby playing with wooden toys nursery",
    "loving mother holding newborn baby tender",
    "father holding cute baby laughing outdoors",
    "baby first steps walking nursery smiling",
    "adorable baby crawling on blanket smiling",
    "baby portrait smiling beautiful eyes vertical",
    "cute baby outdoors garden picnic smiling",
    "tiny baby feet hands close up tender macro",
    "happy baby sitting on grass laughing",
    "baby in cozy knitted sweater smiling",
    "mother and baby laughing together nursery",
    "cute toddler playing outdoor autumn leaves",
    "adorable baby eating fruits smiling messy",
    "cute newborn baby in wicker basket cozy",
    "baby laughing with parents in bedroom cozy",
    "cute baby wearing animal bear hat smiling",
    "baby playing with soap bubbles laughing",
    "baby sitting with teddy bear smiling nursery",
    "cute smiling baby in wooden crib nursery",
    "mother kissing baby cheek smiling tenderly",
    "father carrying cute toddler on shoulders laughing",
    "baby exploring garden flowers smiling sunny",
    "newborn baby yawn stretch cozy blanket"
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
        time.sleep(1.6)

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=400)
        except Exception:
            pass

        try:
            inp = page.wait_for_selector("input[placeholder*='Search']", timeout=5000)
            inp.fill(term)
            page.keyboard.press("Enter")
            time.sleep(3.0)
        except Exception:
            continue

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=400)
        except Exception:
            pass

        btns = page.locator("button[data-cy='item-action-download']").all()

        got_in_term = 0
        seen_ids = set()
        for btn in btns:
            cur_count = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            if cur_count >= TARGET_TOTAL or got_in_term >= 3:
                break

            try:
                item_id = btn.get_attribute("data-analytics-item_id")
                if item_id and item_id in seen_ids:
                    continue
                if item_id:
                    seen_ids.add(item_id)

                if not btn.is_visible():
                    continue

                with page.expect_download(timeout=2000) as dl_info:
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
                    time.sleep(0.1)
            except Exception:
                pass

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
