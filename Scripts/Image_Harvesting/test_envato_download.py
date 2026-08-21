#!/usr/bin/env python3
import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
DOWNLOAD_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/01_Wedding/All_Raw"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

print("Starting Envato Photo Downloader Test...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=DOWNLOAD_DIR,
        accept_downloads=True
    )
    
    page = context.new_page()
    print("Navigating to https://app.envato.com/ ...")
    page.goto("https://app.envato.com/", timeout=60000)
    time.sleep(2)
    
    # Check if signed in
    print("Page URL:", page.url)
    
    # Fill wedding into search
    print("Searching for 'wedding'...")
    search_input = page.wait_for_selector("input", timeout=10000)
    search_input.fill("wedding")
    search_input.press("Enter")
    time.sleep(4)
    
    # Filter to Photos
    print("Checking Photos section...")
    # Look for photos container or heading
    more_link = page.query_selector("text=+ more")
    if more_link:
        print("Clicking '+ more' under photos...")
        more_link.click()
        time.sleep(3)
        
    page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/download_test_view.png")
    print("Screenshot saved to download_test_view.png")
    
    context.close()
    print("Done test.")
