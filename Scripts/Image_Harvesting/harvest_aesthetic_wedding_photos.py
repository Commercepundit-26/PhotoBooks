import os, sys, time, shutil
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Wedding"
ALT_TARGET = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding"
TEMP_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads"
os.makedirs(TEMP_DL, exist_ok=True)

# 1. Clean out the 3 flagged awkwardly cropped images
flagged_names = [
    "bride-in-white-dress-in-a-green-garden-2026-03-26-04-02-39-utc",
    "well-dressed-man-outdoors-in-stylish-suit-2026-01-07-02-15-04-utc",
    "wedding-couple-holding-hands-with-floral-bouquet-2026-01-09-12-16-14-utc"
]

for d in [TARGET_DIR, ALT_TARGET]:
    for f in os.listdir(d):
        for flag in flagged_names:
            if flag in f:
                fp = os.path.join(d, f)
                try:
                    os.remove(fp)
                    print(f"🗑️ Removed: {f}")
                except Exception:
                    pass

queries = [
    "guy and a girl newlyweds are walking in the forest",
    "Omelnickiy wedding",
    "wedding bride groom portrait smiling",
    "wedding couple outdoors romantic forest",
    "wedding couple kissing ceremony sunset"
]

print("="*70)
print("HARVESTING AESTHETIC WEDDING PHOTOS (Omelnickiy & User Download History)")
print("="*70)

seen_files = set(os.listdir(TARGET_DIR))

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=TEMP_DL,
        accept_downloads=True
    )
    page = context.new_page()

    for q in queries:
        print(f"\n>>> Searching: '{q}'")
        page.goto("https://app.envato.com/", timeout=40000)
        time.sleep(2)

        try:
            inp = page.wait_for_selector("input[placeholder*='Search']", timeout=10000)
            inp.fill(q)
            inp.press("Enter")
            time.sleep(3)
        except Exception as e:
            print("Search error:", e)
            continue

        try:
            more_btn = page.locator("text=+ more").first
            if more_btn.is_visible():
                more_btn.click()
                time.sleep(2)
        except Exception:
            pass

        for scroll_idx in range(4):
            dl_buttons = page.locator("button[data-cy='item-action-download']").all()
            for btn in dl_buttons:
                try:
                    item_id = btn.get_attribute("data-analytics-item_id")
                    btn.scroll_into_view_if_needed(timeout=1500)
                    time.sleep(0.2)

                    with page.expect_download(timeout=12000) as dl_info:
                        btn.click(timeout=2500)
                    download = dl_info.value
                    sugg_name = download.suggested_filename

                    if sugg_name not in seen_files and sugg_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        save_path = os.path.join(TARGET_DIR, sugg_name)
                        download.save_as(save_path)
                        shutil.copy2(save_path, os.path.join(ALT_TARGET, sugg_name))
                        seen_files.add(sugg_name)
                        
                        with Image.open(save_path) as im:
                            w, h = im.size
                            mb = os.path.getsize(save_path)/(1024*1024)
                            print(f"  ✓ Downloaded: {sugg_name} ({w}x{h} px, {mb:.1f} MB)")
                        time.sleep(0.5)
                except Exception:
                    pass

            page.keyboard.press("PageDown")
            page.evaluate("window.scrollBy(0, 1500)")
            time.sleep(1.5)

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
