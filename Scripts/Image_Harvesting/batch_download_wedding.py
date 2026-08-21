#!/usr/bin/env python3
import os
import sys
import time
import urllib.request
import ssl
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
ssl_ctx = ssl._create_unverified_context()

BASE_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/01_Wedding"
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")

TARGET_COUNTS = {
    "Landscape": 50,
    "Portrait": 50,
    "Square": 50
}

FOLDERS = {
    "Landscape": os.path.join(BASE_DIR, "Landscape_Horizontal"),
    "Portrait": os.path.join(BASE_DIR, "Portrait_Vertical"),
    "Square": os.path.join(BASE_DIR, "Square")
}

for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

print("="*65)
print("ENVATO ELEMENTS: AUTOMATED WEDDING PHOTO HARVESTER")
print("Target: 50 Landscape, 50 Portrait, 50 Square (150 Total)")
print("="*65)

def download_img(url, dest_path, headers):
    try:
        req = urllib.request.Request(url, headers=headers)
        data = urllib.request.urlopen(req, context=ssl_ctx, timeout=15).read()
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  [!] Download error: {e}")
        return False

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome"
    )
    page = context.new_page()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://app.envato.com/"
    }

    for orientation in ["Portrait", "Square", "Landscape"]:
        folder = FOLDERS[orientation]
        target = TARGET_COUNTS[orientation]
        current_count = len([f for f in os.listdir(folder) if f.endswith(('.jpg', '.jpeg', '.png'))])
        print(f"\n>>> Processing Orientation: {orientation} (Currently have {current_count}/{target})")
        
        if current_count >= target:
            print(f"✓ Already have {current_count} photos for {orientation}. Skipping.")
            continue
            
        page.goto("https://app.envato.com/", timeout=40000)
        time.sleep(3)
        
        # Close any onboarding tooltip / popup
        try:
            page.locator("button:has-text('✕'), button:has-text('×'), [aria-label*='close' i], [aria-label*='dismiss' i]").first.click(timeout=1500)
        except Exception:
            pass
            
        # Search wedding
        inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
        inp.fill("wedding")
        inp.press("Enter")
        time.sleep(4)
        
        # Click + more to get full gallery
        try:
            more_loc = page.locator("text=+ more").first
            if more_loc.is_visible():
                more_loc.click()
                time.sleep(3)
        except Exception:
            pass
            
        # Open Orientation filter
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
            print("Filter selection note:", e)
                
        # Scroll and collect images
        downloaded = current_count
        seen_urls = set()
        scroll_attempts = 0
        
        while downloaded < target and scroll_attempts < 40:
            scroll_attempts += 1
            imgs = page.locator("img[src^='https://']").all()
            
            for img in imgs:
                if downloaded >= target:
                    break
                try:
                    src = img.get_attribute("src")
                    if not src or src in seen_urls or "envato" not in src:
                        continue
                    seen_urls.add(src)
                    
                    filename = f"wedding_{orientation.lower()}_{downloaded+1:03d}.jpg"
                    dest_path = os.path.join(folder, filename)
                    
                    if download_img(src, dest_path, headers):
                        try:
                            with Image.open(dest_path) as im:
                                w, h = im.size
                            print(f"  [{downloaded+1}/{target}] Saved {filename} ({w}x{h})")
                            downloaded += 1
                        except Exception:
                            if os.path.exists(dest_path):
                                os.remove(dest_path)
                except Exception:
                    pass
                    
            page.evaluate("window.scrollBy(0, 1500)")
            time.sleep(2)
            
        print(f"✓ Finished {orientation}: {downloaded} photos saved in {folder}")

    context.close()

print("\n" + "="*65)
print("FINAL HARVEST SUMMARY:")
for orient, folder in FOLDERS.items():
    cnt = len([f for f in os.listdir(folder) if f.endswith(('.jpg', '.jpeg', '.png'))])
    print(f"  • {orient:<12}: {cnt} / {TARGET_COUNTS[orient]} photos")
print("="*65)
