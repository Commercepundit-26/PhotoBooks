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
    ("Portrait", "cute baby portrait smiling"),
    ("Portrait", "adorable newborn baby sleeping"),
    ("Portrait", "happy baby laughing nursery"),
    ("Portrait", "mother holding newborn baby tender"),
    ("Portrait", "father holding baby laughing outdoors"),
    ("Portrait", "baby crawling on blanket smiling"),
    ("Portrait", "toddler standing cute smiling"),
    ("Portrait", "baby in cozy knitted sweater"),
    ("Portrait", "baby playing with teddy bear nursery"),
    ("Portrait", "baby bath time splashing water"),
    
    # Square
    ("Square", "cute baby smiling square"),
    ("Square", "newborn baby cozy blanket square"),
    ("Square", "baby laughing nursery square"),
    ("Square", "baby close up eyes cute square"),
    ("Square", "toddler playing wooden toys square"),
    ("Square", "tiny baby toes feet tender square"),
    ("Square", "baby eating fruits messy square"),
    ("Square", "baby wearing animal hat square"),
    
    # Landscape
    ("Landscape", "cute baby crawling garden lawn"),
    ("Landscape", "baby family nursery cozy living room"),
    ("Landscape", "newborn baby sleeping wicker basket"),
    ("Landscape", "baby playing with parents on bed"),
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
print("STARTING ROBUST BABY HARVEST TO REACH 65 MASTER PHOTOS")
print(f"Current: Square={count_orientation('Square')}/20, Portrait={count_orientation('Portrait')}/25, Landscape={count_orientation('Landscape')}/20 | Total: {len(os.listdir(TARGET_DIR))}")
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

        print(f"\n>>> [{target_orient}] Searching: '{q}' (Have {have}/{TARGETS[target_orient]} | Total: {total_now}/65)")
        page.goto("https://app.envato.com/", timeout=35000)
        time.sleep(2.5)

        # Close any popups/modals
        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=800)
        except Exception:
            pass

        try:
            inp = page.locator("input[placeholder*='Search']").first
            inp.click()
            inp.fill(q)
            page.keyboard.press("Enter")
            time.sleep(3.5)
        except Exception as e:
            print(f"  [!] Search error: {e}")
            continue

        # Close popup if re-appeared
        try:
            page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=800)
        except Exception:
            pass

        seen_ids = set()
        for scroll_i in range(5):
            total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            if total_now >= 65 and count_orientation(target_orient) >= TARGETS[target_orient]:
                break

            btns = page.locator("button[data-cy='item-action-download']").all()
            if scroll_i == 0:
                print(f"  Found {len(btns)} items on page.")

            for btn in btns:
                total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                if total_now >= 65 and count_orientation(target_orient) >= TARGETS[target_orient]:
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
                            act_orient = "Square" if 0.88 <= r <= 1.12 else ("Portrait" if r < 0.90 else "Landscape")
                            mb = os.path.getsize(sp) / (1024 * 1024)

                        total_now = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                        print(f"    [{total_now:02d}/65] ✓ [{act_orient}] {sugg} ({w}x{h} px, {mb:.1f} MB)")
                        time.sleep(0.2)
                except Exception:
                    pass

            page.evaluate("window.scrollBy(0, 1200)")
            time.sleep(1.5)

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
total_final = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
print(f"\n=======================================================")
print(f"HARVEST FINISHED! Total Baby Photos: {total_final}/65")
print(f"Square: {count_orientation('Square')}, Portrait: {count_orientation('Portrait')}, Landscape: {count_orientation('Landscape')}")
print(f"=======================================================")
