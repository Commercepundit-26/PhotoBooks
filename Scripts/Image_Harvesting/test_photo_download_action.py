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

print("Starting Envato Photo Download Action Test...")
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
    
    # Close any onboarding tooltip / popup
    try:
        page.locator("button:has-text('✕'), button:has-text('×'), [aria-label*='close' i], [aria-label*='dismiss' i]").first.click(timeout=2000)
        print("Closed onboarding popup")
    except Exception:
        pass
        
    # Click search input, fill wedding, press enter
    inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
    inp.fill("wedding")
    inp.press("Enter")
    time.sleep(3)
    
    # Click '+ more' next to Photos section
    more_btn = page.query_selector("text=+ more")
    if more_btn:
        print("Clicking '+ more' for Photos...")
        more_btn.click()
        time.sleep(3)
        
    # Take screenshot of the photo gallery
    page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/wedding_gallery_ready.png")
    print("Gallery screenshot saved!")
    
    # Find all download buttons on cards
    # On each card, the download icon is a button or link with svg
    print("Finding download buttons on photo cards...")
    # Listen for download event
    download_triggers = page.locator("button").all()
    print(f"Total buttons found: {len(download_triggers)}")
    
    context.close()
    print("Done inspection.")
