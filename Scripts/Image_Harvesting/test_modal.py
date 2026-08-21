#!/usr/bin/env python3
import os
import sys
import time
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
    page.goto("https://app.envato.com/", timeout=60000)
    time.sleep(2)
    
    search_input = page.wait_for_selector("input", timeout=10000)
    search_input.fill("wedding")
    search_input.press("Enter")
    time.sleep(3)
    
    more_link = page.query_selector("text=+ more")
    if more_link:
        more_link.click()
        time.sleep(3)
        
    # Click right in the center of the first image
    imgs = page.locator("img").all()
    print(f"Found {len(imgs)} img tags")
    if len(imgs) > 2:
        print("Clicking img 1...")
        imgs[1].click()
        time.sleep(3)
        page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/modal_opened.png")
        print("Screenshot saved to modal_opened.png")
        
        # Check buttons in the opened modal / drawer
        buttons = page.locator("button").all()
        print(f"Found {len(buttons)} buttons")
        for b in buttons:
            txt = b.inner_text().strip()
            if txt:
                print("Button:", repr(txt))
                
    context.close()
