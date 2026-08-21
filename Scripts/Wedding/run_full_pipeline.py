#!/usr/bin/env python3
import os
import sys
import time
import shutil
import subprocess
import glob
from PIL import Image

sys.stdout.reconfigure(line_buffering=True)

AI_FILE = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai"
BG_DIR = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds"
WEDDING_PHOTOS_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding"

PREVIEWS_DIR = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews"
BLANK_DIR = os.path.join(PREVIEWS_DIR, "Blank_Layouts")
POPULATED_DIR = os.path.join(PREVIEWS_DIR, "Populated_Layouts")
RAW_EXPORT_DIR = os.path.join(PREVIEWS_DIR, "Temp_Raw_Export")

os.makedirs(BLANK_DIR, exist_ok=True)
os.makedirs(POPULATED_DIR, exist_ok=True)
os.makedirs(RAW_EXPORT_DIR, exist_ok=True)

def run_jsx_code(jsx_code, script_name="temp.jsx"):
    jsx_path = f"/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/{script_name}"
    with open(jsx_path, "w") as f:
        f.write(jsx_code)
    cmd = f'osascript -e \'tell application "Adobe Illustrator" to do javascript file "{jsx_path}"\''
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error executing {script_name}: {res.stderr}")
        return False
    return True

print("="*80)
print("STARTING PHOTOBOOK LAYOUT & PREVIEW AUTOMATION PIPELINE")
print("="*80)

# STEP 1: OPEN FILE AND APPLY BACKGROUNDS TO ALL 63 ARTBOARDS
print("\n[Step 1] Opening Illustrator file & applying 5400x5400px Master Backgrounds...")

jsx_step1 = f"""
// Close any open documents
while (app.documents.length > 0) {{
    app.documents[0].close(SaveOptions.DONOTSAVECHANGES);
}}

var fileRef = new File("{AI_FILE}");
var doc = app.open(fileRef);

// Remove existing Backgrounds layer if present
try {{
    var oldBg = doc.layers.getByName("Backgrounds");
    oldBg.remove();
}} catch(e) {{}}

var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";
bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

var bgFolder = new Folder("{BG_DIR}");
var bgFiles = bgFolder.getFiles("*.jpg");
bgFiles.sort(function(a, b) {{ return a.name.localeCompare(b.name); }});

for (var i = 0; i < doc.artboards.length; i++) {{
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];
    var abW = abRight - abLeft;
    var abH = abTop - abBottom;

    var bgFile = bgFiles[i % bgFiles.length];

    var clipGroup = bgLayer.groupItems.add();

    // Place background image
    var placed = clipGroup.placedItems.add();
    placed.file = bgFile;

    var side = Math.max(abW, abH);
    placed.width = side;
    placed.height = side;
    placed.left = abLeft + (abW - side) / 2;
    placed.top = abTop - (abH - side) / 2;

    // Mask with artboard bounds
    var clipRect = clipGroup.pathItems.rectangle(abTop, abLeft, abW, abH);
    clipRect.filled = false;
    clipRect.stroked = false;
    clipRect.clipping = true;

    clipGroup.clipped = true;
}}

doc.save();
"""

if not run_jsx_code(jsx_step1, "step1_backgrounds.jsx"):
    sys.exit(1)
print("✓ Backgrounds successfully placed and masked on all 63 artboards!")

# STEP 2: EXPORT BLANK LAYOUT PREVIEWS
print("\n[Step 2] Exporting Blank Layout Previews (Backgrounds + Layout Gray Boxes)...")

for f in glob.glob(os.path.join(RAW_EXPORT_DIR, "*")):
    os.remove(f)

jsx_step2 = f"""
var doc = app.activeDocument;
var outFolder = new Folder("{RAW_EXPORT_DIR}");

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 90;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;

var baseFile = new File(outFolder.fsName + "/blank.jpg");
doc.exportFile(baseFile, ExportType.JPEG, exportOpts);
"""

run_jsx_code(jsx_step2, "step2_export_blank.jsx")
time.sleep(4)

raw_files = sorted(glob.glob(os.path.join(RAW_EXPORT_DIR, "*.jpg")))
print(f"  Exported {len(raw_files)} raw artboard images. Resizing to max 1000px...")

for idx, rf in enumerate(raw_files):
    with Image.open(rf) as im:
        w, h = im.size
        if w == h or abs(w - h) < 5:
            book_type = "Square_10x10"
            target_size = (1000, 1000)
        elif w > h:
            book_type = "Landscape_12x8"
            target_size = (1000, int(round(1000 * (h / float(w)))))
        else:
            book_type = "Portrait_8x12"
            target_size = (int(round(1000 * (w / float(h)))), 1000)
        
        im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
        out_name = f"Blank_AB{idx+1:02d}_{book_type}.jpg"
        out_path = os.path.join(BLANK_DIR, out_name)
        im_resized.save(out_path, quality=92)
        print(f"  [{idx+1:02d}/63] ✓ {out_name} -> {target_size[0]}x{target_size[1]} px")

print(f"✓ All {len(raw_files)} Blank Layout Previews exported into: {BLANK_DIR}")

# STEP 3: MASK DOWNLOADED WEDDING MASTER PHOTOS INTO ALL GRAY BOXES
print("\n[Step 3] Placing downloaded master Wedding photos into layout containers...")

wedding_photos = sorted([os.path.join(WEDDING_PHOTOS_DIR, f) for f in os.listdir(WEDDING_PHOTOS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
print(f"  Found {len(wedding_photos)} master wedding photos in Image_Library/Wedding.")

land_photos = []
port_photos = []
sq_photos = []

for wp in wedding_photos:
    with Image.open(wp) as im:
        w, h = im.size
        r = w / float(h)
        if 0.90 <= r <= 1.10:
            sq_photos.append(wp)
        elif r < 0.90:
            port_photos.append(wp)
        else:
            land_photos.append(wp)

print(f"  Photo breakdown: {len(land_photos)} Landscape, {len(port_photos)} Portrait, {len(sq_photos)} Square")

# Escape photo paths for JSX array
land_photos_json = str(land_photos).replace("'", '"')
port_photos_json = str(port_photos).replace("'", '"')
sq_photos_json = str(sq_photos).replace("'", '"')
all_photos_json = str(wedding_photos).replace("'", '"')

jsx_step3 = f"""
var doc = app.activeDocument;

// Create or reset Photos layer
var photoLayer;
try {{
    photoLayer = doc.layers.getByName("Photos_Masked");
    photoLayer.remove();
}} catch(e) {{}}

photoLayer = doc.layers.add();
photoLayer.name = "Photos_Masked";

// Ensure layer order: Layout on top, Photos_Masked in middle, Backgrounds on bottom
var bgLayer = doc.layers.getByName("Backgrounds");
photoLayer.move(bgLayer, ElementPlacement.PLACEBEFORE);

var landPhotos = {land_photos_json};
var portPhotos = {port_photos_json};
var sqPhotos = {sq_photos_json};
var allPhotos = {all_photos_json};

var landIdx = 0;
var portIdx = 0;
var sqIdx = 0;
var allIdx = 0;

var placedCount = 0;

for (var i = 0; i < doc.artboards.length; i++) {{
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];

    for (var j = 0; j < doc.layers.length; j++) {{
        var lyr = doc.layers[j];
        if (lyr.name == "Backgrounds" || lyr.name == "Photos_Masked") continue;

        for (var k = 0; k < lyr.pathItems.length; k++) {{
            var pi = lyr.pathItems[k];
            if (pi.guides || pi.clipping) continue;

            var gb = pi.geometricBounds;
            var cx = (gb[0] + gb[2]) / 2;
            var cy = (gb[1] + gb[3]) / 2;

            if (cx >= abLeft && cx <= abRight && cy <= abTop && cy >= abBottom) {{
                var pw = gb[2] - gb[0];
                var ph = gb[1] - gb[3];

                if (pw > 30 && ph > 30) {{
                    var ratio = pw / ph;
                    var chosenFile;
                    if (ratio >= 1.15 && landPhotos.length > 0) {{
                        chosenFile = landPhotos[landIdx % landPhotos.length];
                        landIdx++;
                    }} else if (ratio <= 0.85 && portPhotos.length > 0) {{
                        chosenFile = portPhotos[portIdx % portPhotos.length];
                        portIdx++;
                    }} else if (sqPhotos.length > 0) {{
                        chosenFile = sqPhotos[sqIdx % sqPhotos.length];
                        sqIdx++;
                    }} else {{
                        chosenFile = allPhotos[allIdx % allPhotos.length];
                        allIdx++;
                    }}

                    var pGroup = photoLayer.groupItems.add();

                    var pPlaced = pGroup.placedItems.add();
                    pPlaced.file = new File(chosenFile);

                    var scaleFactor = Math.max(pw / pPlaced.width, ph / pPlaced.height);
                    var newW = pPlaced.width * scaleFactor;
                    var newH = pPlaced.height * scaleFactor;
                    pPlaced.width = newW;
                    pPlaced.height = newH;
                    pPlaced.left = gb[0] + (pw - newW) / 2;
                    pPlaced.top = gb[1] - (ph - newH) / 2;

                    var maskPath = pi.duplicate(pGroup, ElementPlacement.PLACEATBEGINNING);
                    maskPath.filled = false;
                    maskPath.stroked = false;
                    maskPath.clipping = true;

                    pGroup.clipped = true;
                    placedCount++;
                }}
            }}
        }}
    }}
}}

doc.save();
"""

if not run_jsx_code(jsx_step3, "step3_mask_photos.jsx"):
    sys.exit(1)
print("✓ Master photos successfully placed and clipped to all layout boxes!")

# STEP 4: EXPORT POPULATED LAYOUT PREVIEWS
print("\n[Step 4] Exporting Populated Photobook Previews (Background + Photos + Layouts)...")

for f in glob.glob(os.path.join(RAW_EXPORT_DIR, "*")):
    os.remove(f)

jsx_step4 = f"""
var doc = app.activeDocument;
var outFolder = new Folder("{RAW_EXPORT_DIR}");

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 90;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;

var baseFile = new File(outFolder.fsName + "/pop.jpg");
doc.exportFile(baseFile, ExportType.JPEG, exportOpts);
"""

run_jsx_code(jsx_step4, "step4_export_pop.jsx")
time.sleep(4)

raw_pop_files = sorted(glob.glob(os.path.join(RAW_EXPORT_DIR, "*.jpg")))
print(f"  Exported {len(raw_pop_files)} raw populated images. Resizing to max 1000px...")

for idx, rf in enumerate(raw_pop_files):
    with Image.open(rf) as im:
        w, h = im.size
        if w == h or abs(w - h) < 5:
            book_type = "Square_10x10"
            target_size = (1000, 1000)
        elif w > h:
            book_type = "Landscape_12x8"
            target_size = (1000, int(round(1000 * (h / float(w)))))
        else:
            book_type = "Portrait_8x12"
            target_size = (int(round(1000 * (w / float(h)))), 1000)
        
        im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
        out_name = f"Populated_AB{idx+1:02d}_{book_type}.jpg"
        out_path = os.path.join(POPULATED_DIR, out_name)
        im_resized.save(out_path, quality=92)
        print(f"  [{idx+1:02d}/63] ✓ {out_name} -> {target_size[0]}x{target_size[1]} px")

shutil.rmtree(RAW_EXPORT_DIR, ignore_errors=True)

print("\n" + "="*80)
print("PHOTOBOOK AUTOMATION COMPLETE!")
print(f"Blank Layout Previews    : {len(raw_files)} files in {BLANK_DIR}")
print(f"Populated Layout Previews: {len(raw_pop_files)} files in {POPULATED_DIR}")
print("="*80)
