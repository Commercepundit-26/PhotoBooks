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
                    if orient == "Square" and 0.88 <= r <= 1.12:
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
    ("Portrait", "cute baby vertical"),
    ("Portrait", "newborn baby vertical"),
    ("Portrait", "happy baby laughing vertical"),
    ("Portrait", "mother holding newborn baby vertical"),
    ("Portrait", "father holding baby laughing vertical"),
    ("Portrait", "baby crawling blanket vertical"),
    ("Portrait", "toddler standing smiling vertical"),
    ("Portrait", "baby knitted sweater vertical"),
    ("Portrait", "baby teddy bear vertical"),
    ("Portrait", "baby bath splash vertical"),
    
    # Square
    ("Square", "cute baby smiling square"),
    ("Square", "newborn baby cozy blanket square"),
    ("Square", "baby laughing nursery square"),
    ("Square", "baby eyes cute square"),
    ("Square", "toddler playing wooden toys square"),
    ("Square", "baby toes feet tender square"),
    ("Square", "baby eating fruits messy square"),
    ("Square", "baby wearing animal hat square"),
    
    # Landscape
    ("Landscape", "cute baby crawling garden lawn"),
    ("Landscape", "baby family nursery cozy living room"),
    ("Landscape", "newborn baby sleeping wicker basket"),
    ("Landscape", "baby playing with parents bed"),
    ("Landscape", "baby first steps nursery room"),
    ("Landscape", "baby exploring outdoors sunny grass"),
    ("Landscape", "cute baby siblings hugging joyful")
]

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swimwear', 'underwear', 'lingerie', 'office', 'laptop',
    'computer', 'classroom', 'meeting', 'intersection', 'crowd',
    'isolated-on-white', 'cut-out', 'sick', 'hospital', 'doctor', 'syringe', 'crying'
]

print("="*70)
print("STARTING DIRECT BABY HARVEST TO 65")
print(f"Current: Square={count_orientation('Square')}/20, Portrait={count_orientation('Portrait')}/25, Landscape={count_orientation('Landscape')}/20 | Total: {len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])}")
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

    for target_orient, q in SEARCH_QUERIES:
        total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        have = count_orientation(target_orient)
        if total_now >= 65 and have >= TARGETS[target_orient]:
            continue

        print(f"\n>>> [{target_orient}] Query: '{q}' (Have {have}/{TARGETS[target_orient]} | Total: {total_now}/65)")
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
            if total_now >= 65 and count_orientation(target_orient) >= TARGETS[target_orient]:
                break

            btns = page.locator("button[data-cy='item-action-download']").all()
            for btn in btns:
                if got_in_query >= 4:
                    break
                total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                if total_now >= 65 and count_orientation(target_orient) >= TARGETS[target_orient]:
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
print(f"Square: {count_orientation('Square')}, Portrait: {count_orientation('Portrait')}, Landscape: {count_orientation('Landscape')}")
print(f"=======================================================")
