import os, sys, time, shutil
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)
PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
TARGET_DIR = "/Users/cp/Ronak/CC/Photobooks/Wedding"
ALT_TARGET = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding"
TEMP_DL = "/Users/cp/Ronak/CC/Photobooks/Image_Library/scripts/temp_downloads"
os.makedirs(TEMP_DL, exist_ok=True)

# 1. Remove the badly cropped photos flagged by the user
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
                print(f"🗑️ Removed flagged awkwardly cropped file: {f}")
                try:
                    os.remove(fp)
                except Exception as e:
                    print("Error removing:", e)

# 2. Harvest all items from the User's My Downloads history
print("\n" + "="*70)
print("HARVESTING USER DOWNLOAD HISTORY FROM ENVATO ELEMENTS")
print("="*70)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=True,
        channel="chrome",
        downloads_path=TEMP_DL,
        accept_downloads=True
    )
    page = context.new_page()
    page.goto("https://elements.envato.com/account/downloads", timeout=40000)
    time.sleep(4)
    
    # Scroll to load all items if pagination/infinite scroll exists
    for _ in range(5):
        page.keyboard.press("PageDown")
        time.sleep(1)
        
    dl_buttons = page.locator("button:has-text('Download')").all()
    print(f"Found {len(dl_buttons)} download buttons in My Downloads.")
    
    downloaded_count = 0
    for idx, btn in enumerate(dl_buttons):
        try:
            btn.scroll_into_view_if_needed(timeout=2000)
            time.sleep(0.3)
            
            with page.expect_download(timeout=15000) as dl_info:
                btn.click(timeout=3000)
            download = dl_info.value
            sugg_name = download.suggested_filename
            print(f"Triggered download: {sugg_name}")
            
            # Check if it's an image or zip
            temp_save = os.path.join(TEMP_DL, sugg_name)
            download.save_as(temp_save)
            
            if sugg_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                target_file = os.path.join(TARGET_DIR, sugg_name)
                shutil.copy2(temp_save, target_file)
                shutil.copy2(temp_save, os.path.join(ALT_TARGET, sugg_name))
                with Image.open(target_file) as im:
                    sz_mb = os.path.getsize(target_file)/(1024*1024)
                    print(f"  ✓ Saved Photo: {sugg_name} ({im.size[0]}x{im.size[1]} px, {sz_mb:.1f} MB)")
                    downloaded_count += 1
            elif sugg_name.lower().endswith('.zip'):
                # Extract if it contains photos
                import zipfile
                with zipfile.ZipFile(temp_save, 'r') as z:
                    for zf in z.namelist():
                        if zf.lower().endswith(('.jpg', '.jpeg', '.png')) and not zf.startswith('__MACOSX'):
                            extracted_path = z.extract(zf, TEMP_DL)
                            base_name = os.path.basename(extracted_path)
                            target_file = os.path.join(TARGET_DIR, base_name)
                            shutil.copy2(extracted_path, target_file)
                            shutil.copy2(extracted_path, os.path.join(ALT_TARGET, base_name))
                            with Image.open(target_file) as im:
                                sz_mb = os.path.getsize(target_file)/(1024*1024)
                                print(f"  ✓ Extracted from ZIP: {base_name} ({im.size[0]}x{im.size[1]} px, {sz_mb:.1f} MB)")
                                downloaded_count += 1
            time.sleep(1)
        except Exception as e:
            # print("Download error:", e)
            pass

    context.close()

shutil.rmtree(TEMP_DL, ignore_errors=True)
print(f"\n✓ Finished harvesting {downloaded_count} items from User Download History.")
