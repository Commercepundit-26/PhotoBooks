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
    time.sleep(4)
    
    page.screenshot(path="/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/my_downloads_full.png", full_page=True)
    
    # Find all items and download buttons
    items = page.locator("div, li, tr").all()
    print("Page title:", page.title())
    
    # Look for download links/buttons on this page
    dl_links = page.locator("a:has-text('Download'), button:has-text('Download')").all()
    print(f"Total download buttons found: {len(dl_links)}")
    for idx, dl in enumerate(dl_links[:20]):
        try:
            print(f"  {idx+1}. text='{dl.text_content().strip()}' tag={dl.evaluate('el => el.tagName')} href={dl.get_attribute('href')}")
        except:
            pass

    # Look for titles
    titles = page.locator("h2, h3, h4, a[href*='elements.envato.com/']").all()
    print(f"\nTitles/Items found ({len(titles)}):")
    for idx, t in enumerate(titles[:30]):
        try:
            txt = t.text_content().strip()
            href = t.get_attribute("href")
            if txt and len(txt) > 3:
                print(f"  - {txt} (href: {href})")
        except:
            pass

    context.close()
