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
    
    urls_to_test = [
        "https://elements.envato.com/account/downloads",
        "https://elements.envato.com/user/downloads",
        "https://elements.envato.com/downloads",
        "https://app.envato.com/"
    ]
    
    for u in urls_to_test:
        print(f"\nTesting: {u}")
        page.goto(u, timeout=30000)
        time.sleep(3)
        print("Final URL:", page.url)
        print("Title:", page.title())
        page.screenshot(path=f"/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/page_{page.url.replace('https://', '').replace('/', '_')[:30]}.png")
        
        # Look for 'Downloads' link or My Downloads
        links = page.locator("a:has-text('Download'), a:has-text('History'), a:has-text('My account')").all()
        for l in links:
            try:
                print("Found link:", l.text_content().strip(), "href:", l.get_attribute("href"))
            except:
                pass
                
    context.close()
