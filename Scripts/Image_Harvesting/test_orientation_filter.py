#!/usr/bin/env python3
import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
DOWNLOAD_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/01_Wedding/All_Raw"

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
        
    # Click Orientation dropdown
    orient_btn = page.locator("button:has-text('Orientation')").first
    if orient_btn:
        orient_btn.click()
        time.sleep(1)
        print("Clicked Orientation dropdown")
        
        # Check items in dropdown menu
        menu_items = page.locator("[role='menuitem'], [role='option'], label, button").all()
        for item in menu_items:
            t = item.inner_text().strip()
            if any(k in t.lower() for k in ['square', 'horizontal', 'vertical', 'landscape', 'portrait', 'orientation']):
                print(" - Filter Option:", repr(t))
                
        page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/orientation_dropdown.png")
        print("Dropdown screenshot saved!")
        
    context.close()
