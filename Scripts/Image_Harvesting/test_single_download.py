#!/usr/bin/env python3
import os
import sys
import time
import glob
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
DOWNLOAD_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/01_Wedding/All_Raw"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=DOWNLOAD_DIR,
        accept_downloads=True
    )
    
    page = context.new_page()
    page.goto("https://app.envato.com/", timeout=30000)
    time.sleep(2)
    
    # Search wedding
    inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
    inp.fill("wedding")
    inp.press("Enter")
    time.sleep(3)
    
    more_btn = page.query_selector("text=+ more")
    if more_btn:
        more_btn.click()
        time.sleep(3)
        
    # Hover over the first photo
    cards = page.locator("img").all()
    print(f"Found {len(cards)} image elements")
    
    if len(cards) > 1:
        # Hover over the first photo to reveal download button
        cards[0].hover()
        time.sleep(1)
        
        # Find download button in that card
        # In Envato App, the download button is a button with a download svg icon
        dl_btn = page.locator("button[aria-label*='download' i], button:has(svg path[d*='M12'])").first
        
        # Let's also look for all visible buttons on the card
        card_buttons = page.locator("button").all()
        print(f"Total buttons found on page: {len(card_buttons)}")
        
        # Click the download button and wait for download event
        try:
            with page.expect_download(timeout=15000) as download_info:
                # Click the card's download button or trigger download
                for b in card_buttons:
                    if b.is_visible():
                        # check if it has download icon
                        html = b.inner_html()
                        if 'download' in html.lower() or 'm19' in html.lower() or 'm12' in html.lower() or 'arrow' in html.lower():
                            print("Found download button, clicking...")
                            b.click()
                            break
                            
            download = download_info.value
            save_path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            download.save_as(save_path)
            print(f"✓ Downloaded successfully: {save_path} ({os.path.getsize(save_path)} bytes)")
        except Exception as e:
            print("Download trigger test note:", e)
            
    context.close()
