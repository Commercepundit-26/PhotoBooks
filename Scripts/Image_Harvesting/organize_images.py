#!/usr/bin/env python3
import os
import glob
import shutil
from PIL import Image

BASE_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/01_Wedding"
RAW_DIR = os.path.join(BASE_DIR, "All_Raw")
SQUARE_DIR = os.path.join(BASE_DIR, "Square")
PORTRAIT_DIR = os.path.join(BASE_DIR, "Portrait_Vertical")
LANDSCAPE_DIR = os.path.join(BASE_DIR, "Landscape_Horizontal")

os.makedirs(SQUARE_DIR, exist_ok=True)
os.makedirs(PORTRAIT_DIR, exist_ok=True)
os.makedirs(LANDSCAPE_DIR, exist_ok=True)

extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.JPEG", "*.PNG"]
all_files = []
for ext in extensions:
    all_files.extend(glob.glob(os.path.join(RAW_DIR, ext)))

print(f"Found {len(all_files)} raw images in {RAW_DIR}")

for idx, file_path in enumerate(all_files, 1):
    try:
        with Image.open(file_path) as img:
            w, h = img.size
            ratio = w / float(h)
            
            # Categorize
            if 0.92 <= ratio <= 1.08:
                target_folder = SQUARE_DIR
                cat = "Square"
            elif ratio < 0.92:
                target_folder = PORTRAIT_DIR
                cat = "Portrait"
            else:
                target_folder = LANDSCAPE_DIR
                cat = "Landscape"
                
            dest = os.path.join(target_folder, os.path.basename(file_path))
            if not os.path.exists(dest):
                shutil.copy2(file_path, dest)
                print(f"[{idx}/{len(all_files)}] {os.path.basename(file_path)} ({w}x{h}, {ratio:.2f}) -> {cat}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Summary counts
sq_count = len(glob.glob(os.path.join(SQUARE_DIR, "*.*")))
port_count = len(glob.glob(os.path.join(PORTRAIT_DIR, "*.*")))
land_count = len(glob.glob(os.path.join(LANDSCAPE_DIR, "*.*")))

print("\n" + "="*50)
print("IMAGE LIBRARY STATUS: 01_Wedding")
print("="*50)
print(f"  • Square (1:1):            {sq_count} / 50")
print(f"  • Portrait Vertical:       {port_count} / 50")
print(f"  • Landscape Horizontal:    {land_count} / 50")
print("="*50)
