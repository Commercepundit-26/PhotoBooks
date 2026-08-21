#!/usr/bin/env python3
import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.expanduser("~/.photobook_chrome_profile")
os.makedirs(PROFILE_DIR, exist_ok=True)

print("="*70)
print("PHOTOBOOK IMAGE SOURCING: ONE-TIME LOGIN HELPER")
print("="*70)
print(f"Using persistent profile directory: {PROFILE_DIR}")
print("\nA Google Chrome window will now open.")
print("1. Log in to your Freepik Premium account.")
print("2. Log in to your Envato Elements account.")
print("="*70)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        channel="chrome",
        args=["--start-maximized", "--no-first-run", "--no-default-browser-check"]
    )
    
    page1 = context.pages[0] if context.pages else context.new_page()
    page1.goto("https://www.freepik.com/log-in", wait_until="domcontentloaded")
    
    page2 = context.new_page()
    page2.goto("https://elements.envato.com/sign-in", wait_until="domcontentloaded")
    
    print("\nWaiting for you to log in in the opened Chrome browser window...")
    print("When you're done, you can close the browser window or press Ctrl+C in terminal.")
    
    # Keep checking until user closes all pages or interrupts
    try:
        while len(context.pages) > 0:
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Browser window closed or interrupted.")
        
    print("\nSaving session cookies and profile...")
    try:
        context.close()
    except Exception:
        pass
    print("✓ Session successfully saved! You can now run automated batch downloads.")
