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
    
    # Search wedding in Photos
    search_input = page.wait_for_selector("input", timeout=10000)
    search_input.fill("wedding")
    search_input.press("Enter")
    time.sleep(4)
    
    # Click '+ more'
    more_link = page.query_selector("text=+ more")
    if more_link:
        more_link.click()
        time.sleep(3)
        
    # Find all download buttons or photo cards
    print("Looking for download buttons...")
    # Hover over the first photo to reveal buttons
    cards = page.query_selector_all("img, [role='img'], [data-test-selector='item-card']")
    print(f"Found {len(cards)} image cards")
    
    if len(cards) > 2:
        card = cards[1]
        card.hover()
        time.sleep(1)
        
        # Look for download button / icon
        dl_buttons = page.query_selector_all("button:has-text('Download'), button[aria-label*='Download'], button:has(svg), [data-test-selector*='download']")
        print(f"Found {len(dl_buttons)} potential download buttons")
        
        page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/hover_view.png")
        print("Hover screenshot saved.")
        
    context.close()
