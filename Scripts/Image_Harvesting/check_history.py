import os, sys, time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome"
    )
    page = context.new_page()
    
    print("Navigating to https://app.envato.com/account/downloads ...")
    page.goto("https://app.envato.com/account/downloads", timeout=40000)
    time.sleep(4)
    print("Current URL:", page.url)
    print("Page Title:", page.title())
    
    # Take screenshot of the downloads page
    page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/my_downloads_page.png", full_page=True)
    print("Screenshot saved to my_downloads_page.png")
    
    # Check for downloaded items
    items = page.locator("a, button, div, span").all_text_contents()
    print("Page text snippet:", [t.strip() for t in items if len(t.strip()) > 5][:30])
    
    context.close()
