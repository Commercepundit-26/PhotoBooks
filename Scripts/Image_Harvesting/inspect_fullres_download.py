#!/usr/bin/env python3
import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TEST_DL_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/test_dl"
os.makedirs(TEST_DL_DIR, exist_ok=True)

print("Testing full-resolution download click on Envato Elements...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False, # Launch visible so we can observe the exact download modal/action
        channel="chrome",
        downloads_path=TEST_DL_DIR,
        accept_downloads=True
    )
    page = context.new_page()
    page.goto("https://app.envato.com/", timeout=40000)
    time.sleep(3)
    
    # Close any onboarding
    try:
        page.locator("button:has-text('✕'), button:has-text('×')").first.click(timeout=2000)
    except:
        pass
        
    # Search wedding
    inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
    inp.fill("wedding")
    inp.press("Enter")
    time.sleep(3)
    
    # Click '+ more' under Photos
    try:
        page.locator("text=+ more").first.click(timeout=3000)
        time.sleep(3)
    except:
        pass
        
    print("Looking for photo cards...")
    # Find the first photo container
    cards = page.locator("div:has(> img[src*='envato'])").all()
    print(f"Found {len(cards)} cards")
    
    if cards:
        print("Hovering card 0...")
        cards[0].hover()
        time.sleep(1)
        
        # Click the download button on the card
        dl_btn = cards[0].locator("button:has(svg)").last
        print("Clicking download button on card...")
        
        try:
            with page.expect_download(timeout=15000) as download_info:
                dl_btn.click()
            download = download_info.value
            save_path = os.path.join(TEST_DL_DIR, download.suggested_filename)
            download.save_as(save_path)
            print(f"✓ FULL RES DOWNLOAD SUCCESS: {save_path} ({os.path.getsize(save_path)} bytes)")
        except Exception as e:
            print("Download event wait:", e)
            time.sleep(3)
            # Check if a modal popped up (e.g. 'Add to project' or 'Download without project')
            buttons = page.locator("button").all()
            print("Visible buttons after click:")
            for b in buttons:
                if b.is_visible():
                    print(" -", repr(b.inner_text().strip()))
            page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/after_dl_click.png")
            
    context.close()
