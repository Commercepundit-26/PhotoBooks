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
    page.goto("https://elements.envato.com/account/downloads", timeout=40000)
    time.sleep(3)
    
    # Check the first item
    first_btn = page.locator("button:has-text('Download')").nth(1)
    print("Clicking first download button:", first_btn.text_content())
    
    first_btn.click()
    time.sleep(2)
    page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/after_download_click.png")
    
    # Check if a modal opened or download started
    modals = page.locator("[role='dialog'], [class*='modal'], [class*='dialog'], [class*='popup'], [class*='dropdown']").all()
    print(f"Modals/dialogs found: {len(modals)}")
    for m in modals:
        print("Modal text:", m.text_content()[:200])
        
    context.close()
