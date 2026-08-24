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

SPECIFIC_QUERIES = {
    "Square": [
        "baby smiling square",
        "newborn baby sleeping square",
        "baby laughing nursery square",
        "baby eyes portrait square",
        "toddler playing toys square",
        "baby toes feet tender square",
        "baby eating messy square",
        "baby wearing cute hat square"
    ],
    "Portrait": [
        "cute baby portrait vertical",
        "newborn baby vertical",
        "baby smiling vertical",
        "mother holding baby vertical",
        "father holding baby vertical",
        "baby crawling nursery vertical",
        "toddler standing vertical",
        "baby in sweater vertical",
        "baby playing teddy bear vertical",
        "baby bath splash vertical"
    ],
    "Landscape": [
        "cute baby crawling landscape",
        "baby family nursery landscape",
        "newborn baby sleeping basket landscape",
        "baby playing with parents landscape",
        "baby first steps landscape",
        "baby exploring sunny grass landscape",
        "baby siblings hugging landscape"
    ]
}

FORBIDDEN_KEYWORDS = [
    'wedding', 'bride', 'groom', 'veil', 'tuxedo', 'gown', 'altar',
    'bikini', 'swimwear', 'underwear', 'lingerie', 'office', 'laptop',
    'computer', 'classroom', 'meeting', 'intersection', 'crowd',
    'isolated-on-white', 'cut-out', 'sick', 'hospital', 'doctor', 'syringe', 'crying'
]

print("="*70)
print("COMPLETING 65 FULL-RES MASTER PHOTOS — 'BABY'")
print("="*70)

seen_files = set(os.listdir(TARGET_DIR))

# Kill any existing chrome profile processes first
os.system("ps aux | grep photobook_chrome_profile | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true")
time.sleep(1)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=TEMP_DL,
        accept_downloads=True
    )
    page = context.new_page()

    for orientation in ["Portrait", "Square", "Landscape"]:
        target = TARGETS[orientation]
        have = count_orientation(orientation)
        print(f"\n>>> Orientation: {orientation} (Currently have {have}/{target})")
        if have >= target:
            print(f"✓ Already reached target for {orientation}.")
            continue

        for q in SPECIFIC_QUERIES[orientation]:
            have = count_orientation(orientation)
            if have >= target:
                break
            print(f"\n  -> Searching: '{q}' ({orientation} | Current: {have}/{target})")
            page.goto("https://app.envato.com/", timeout=30000)
            time.sleep(2)

            try:
                page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=1000)
            except Exception:
                pass

            try:
                inp = page.wait_for_selector("input[placeholder*='Search']", timeout=8000)
                inp.fill(q)
                inp.press("Enter")
                time.sleep(3)
            except Exception:
                continue

            try:
                more_btn = page.locator("text=+ more").first
                if more_btn.is_visible():
                    more_btn.click()
                    time.sleep(1.5)
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
                have = count_orientation(orientation)
                if have >= target:
                    break
                btns = page.locator("button[data-cy='item-action-download']").all()
                for btn in btns:
                    have = count_orientation(orientation)
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

                        fl = sugg_name.lower()
                        if any(kw in fl for kw in FORBIDDEN_KEYWORDS):
                            continue

                        if sugg_name not in seen_files and fl.endswith(('.jpg', '.jpeg', '.png')):
                            save_path = os.path.join(TARGET_DIR, sugg_name)
                            download.save_as(save_path)
                            seen_files.add(sugg_name)

                            with Image.open(save_path) as im:
                                w, h = im.size
                                r = w / float(h)
                                mb = os.path.getsize(save_path) / (1024 * 1024)

                            valid = False
                            if orientation == "Square" and 0.88 <= r <= 1.12:
                                valid = True
                            elif orientation == "Portrait" and r < 0.90:
                                valid = True
                            elif orientation == "Landscape" and r > 1.10:
                                valid = True

                            if valid:
                                have += 1
                                total_all = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                                print(f"    [{total_all:02d}/65] ✓ [{orientation}] {sugg_name} ({w}x{h} px, {mb:.1f} MB) -> {orientation} count: {have}/{target}")
                            time.sleep(0.3)
                    except Exception:
                        pass

                page.keyboard.press("PageDown")
                page.evaluate("window.scrollBy(0, 1500)")
                time.sleep(1.5)

        print(f"✓ Completed {orientation}: {have}/{target} photos.")

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
total_final = len([f for f in os.listdir(TARGET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
print(f"\n=======================================================")
print(f"HARVEST COMPLETE! Total Baby Master Photos: {total_final}/65")
print(f"Square: {count_orientation('Square')}, Portrait: {count_orientation('Portrait')}, Landscape: {count_orientation('Landscape')}")
print(f"=======================================================")
