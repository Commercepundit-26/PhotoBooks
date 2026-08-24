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
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Baby"
TEMP_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(TEMP_DL, exist_ok=True)

TARGETS = {
    "Square": 20,
    "Portrait": 25,
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

SEARCH_QUERIES = [
    # Portrait
    ("Portrait", "cute baby portrait"),
    ("Portrait", "newborn baby sleeping"),
    ("Portrait", "happy baby laughing"),
    ("Portrait", "mother holding newborn baby"),
    ("Portrait", "father holding baby laughing"),
    ("Portrait", "toddler standing cute smile"),
    ("Portrait", "baby in knitted sweater"),
    ("Portrait", "baby crawling nursery"),
    ("Portrait", "baby playing with teddy bear"),
    ("Portrait", "baby smiling bright eyes"),
    
    # Square
    ("Square", "cute baby smiling square"),
    ("Square", "newborn baby cozy blanket"),
    ("Square", "baby laughing nursery"),
    ("Square", "baby close up eyes cute"),
    ("Square", "toddler playing toys"),
    ("Square", "tiny baby toes feet tender"),
    ("Square", "baby eating fruits messy"),
    ("Square", "baby wearing animal hat"),
    
    # Landscape
    ("Landscape", "cute baby crawling garden"),
    ("Landscape", "baby family nursery cozy"),
    ("Landscape", "newborn baby sleeping wicker basket"),
    ("Landscape", "baby playing with parents bed"),
    ("Landscape", "baby first steps nursery"),
    ("Landscape", "baby exploring sunny grass lawn"),
    ("Landscape", "baby siblings hugging joyful")
]

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swimwear', 'underwear', 'lingerie', 'office', 'laptop',
    'computer', 'classroom', 'meeting', 'intersection', 'crowd',
    'isolated-on-white', 'cut-out', 'sick', 'hospital', 'doctor', 'syringe', 'crying'
]

print("="*70)
print(f"STARTING DIRECT FAST BABY HARVEST (Target: 65 Master Photos)")
print(f"Current: Square={count_orientation('Square')}/20, Portrait={count_orientation('Portrait')}/25, Landscape={count_orientation('Landscape')}/20")
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

    for desired_orient, query in SEARCH_QUERIES:
        cur_total = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if cur_total >= 65 and count_orientation(desired_orient) >= TARGETS[desired_orient]:
            continue

        q_enc = urllib.parse.quote_plus(query)
        url = f"https://app.envato.com/elements/photos?q={q_enc}"
        print(f"\n-> [{desired_orient}] Navigating to query: '{query}'")
        
        try:
            page.goto(url, timeout=30000)
            time.sleep(2.5)
        except Exception:
            continue

        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=800)
        except Exception:
            pass

        seen_ids = set()
        for scroll_i in range(5):
            cur_total = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            if cur_total >= 65:
                break
            
            btns = page.locator("button[data-cy='item-action-download']").all()
            for btn in btns:
                cur_total = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                if cur_total >= 65:
                    break
                try:
                    item_id = btn.get_attribute("data-analytics-item_id")
                    if not item_id or item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)

                    btn.scroll_into_view_if_needed(timeout=800)
                    time.sleep(0.1)

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
                            act_orient = "Square" if 0.90 <= r <= 1.10 else ("Portrait" if r < 0.90 else "Landscape")
                            mb = os.path.getsize(sp) / (1024 * 1024)

                        cur_total = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                        print(f"  [{cur_total:02d}/65] ✓ [{act_orient}] {sugg} ({w}x{h} px, {mb:.1f} MB)")
                        time.sleep(0.15)
                except Exception:
                    pass

            page.evaluate("window.scrollBy(0, 1200)")
            time.sleep(1.5)

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
cur_total = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
print(f"\n=======================================================")
print(f"DONE! Total Baby Photos in Image_Library/Baby: {cur_total}/65")
print(f"Square: {count_orientation('Square')}, Portrait: {count_orientation('Portrait')}, Landscape: {count_orientation('Landscape')}")
print(f"=======================================================")
