import os
import time
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome"
    )
    page = context.new_page()
    page.goto("https://app.envato.com/", timeout=30000)
    time.sleep(3)
    page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Scripts/Image_Harvesting/envato_state.png")
    print("Screenshot saved to envato_state.png")
    context.close()
