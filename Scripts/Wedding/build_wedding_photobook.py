#!/usr/bin/env python3
import os
import sys
import time
import shutil
import subprocess
import glob
from PIL import Image

sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test"
BG_DIR = os.path.join(BASE_DIR, "Backgorunds")
SOURCE_AI = os.path.join(BASE_DIR, "Unique shape Layouts.ai")
TARGET_AI = os.path.join(BASE_DIR, "Wedding_Photobook_3Sizes.ai")
WEDDING_PHOTOS_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding"

PREVIEWS_DIR = os.path.join(BASE_DIR, "Previews")
BLANK_DIR = os.path.join(PREVIEWS_DIR, "Blank_Layouts")
POPULATED_DIR = os.path.join(PREVIEWS_DIR, "Populated_Layouts")
RAW_BLANK_DIR = os.path.join(PREVIEWS_DIR, "Raw_Blank")
RAW_POP_DIR = os.path.join(PREVIEWS_DIR, "Raw_Populated")

os.makedirs(BLANK_DIR, exist_ok=True)
os.makedirs(POPULATED_DIR, exist_ok=True)
os.makedirs(RAW_BLANK_DIR, exist_ok=True)
os.makedirs(RAW_POP_DIR, exist_ok=True)

# 7 Background files
bg_files = sorted([os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR) if f.endswith(".jpg")])
print(f"Loaded {len(bg_files)} master backgrounds:")
for b in bg_files:
    print(f"  - {os.path.basename(b)}")

# 75 Wedding photos
wedding_photos = sorted([os.path.join(WEDDING_PHOTOS_DIR, f) for f in os.listdir(WEDDING_PHOTOS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

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

print(f"\nLoaded {len(wedding_photos)} master wedding photos:")
print(f"  - Landscape: {len(land_photos)}, Portrait: {len(port_photos)}, Square: {len(sq_photos)}")

# Create ExtendScript to build the document, artboards, backgrounds, layouts, and exports
jsx_script = f"""#target illustrator

app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

// 1. Open Source Layouts AI to read layout templates
var sourceFile = new File("{SOURCE_AI}");
var srcDoc = app.open(sourceFile);

// 2. Create Target Master Photobook Document
var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720, 1, DocumentArtboardLayout.GridByRow, 40, 7);
doc.name = "Wedding_Photobook_3Sizes";

// Define 21 Artboards (7 Square 720x720, 7 Landscape 864x576, 7 Portrait 576x864)
// Row 1: Square (10x10) - 7 pages
// Row 2: Landscape (12x8) - 7 pages
// Row 3: Portrait (8x12) - 7 pages

var startX = 0;
var startY = 0;
var spacing = 50;

// Update Artboard 0
doc.artboards[0].artboardRect = [0, 0, 720, -720];
doc.artboards[0].name = "P01_Square_10x10";

// Add remaining 6 Square artboards
for (var i = 1; i < 7; i++) {{
    var l = i * (720 + spacing);
    var ab = doc.artboards.add([l, 0, l + 720, -720]);
    ab.name = "P0" + (i + 1) + "_Square_10x10";
}}

// Add 7 Landscape artboards (Row 2, Y = -800)
var row2Y = -800;
for (var i = 0; i < 7; i++) {{
    var l = i * (864 + spacing);
    var ab = doc.artboards.add([l, row2Y, l + 864, row2Y - 576]);
    ab.name = "P0" + (i + 1) + "_Landscape_12x8";
}}

// Add 7 Portrait artboards (Row 3, Y = -1450)
var row3Y = -1450;
for (var i = 0; i < 7; i++) {{
    var l = i * (576 + spacing);
    var ab = doc.artboards.add([l, row3Y, l + 576, row3Y - 864]);
    ab.name = "P0" + (i + 1) + "_Portrait_8x12";
}}

// Setup Layers
var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";

var photoLayer = doc.layers.add();
photoLayer.name = "Photos_Masked";

var layoutLayer = doc.layers[0];
layoutLayer.name = "Layout_Shapes";

bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

// Master Background files list
var bgFilePaths = [
    "{bg_files[0]}",
    "{bg_files[1]}",
    "{bg_files[2]}",
    "{bg_files[3]}",
    "{bg_files[4]}",
    "{bg_files[5]}",
    "{bg_files[6]}"
];

// Place backgrounds on all 21 artboards
for (var i = 0; i < 21; i++) {{
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];
    var abW = abRight - abLeft;
    var abH = abTop - abBottom;

    var bgIdx = i % 7;
    var bgFile = new File(bgFilePaths[bgIdx]);

    var clipGroup = bgLayer.groupItems.add();

    var placed = clipGroup.placedItems.add();
    placed.file = bgFile;

    var side = Math.max(abW, abH);
    placed.width = side;
    placed.height = side;
    placed.left = abLeft + (abW - side) / 2;
    placed.top = abTop - (abH - side) / 2;

    var clipRect = clipGroup.pathItems.rectangle(abTop, abLeft, abW, abH);
    clipRect.filled = false;
    clipRect.stroked = false;
    clipRect.clipping = true;

    clipGroup.clipped = true;
}}

// Representative layout pairings from Unique shape Layouts.ai for the 7 pages:
// Page 1: Hero Cover / Minimal Statement
// Page 2: 2-Photo Duo
// Page 3: 3-Photo Classic Story
// Page 4: 4-Photo Quad
// Page 5: Arch / Unique Shape Layout
// Page 6: Multi-Photo Collage / Storyboard
// Page 7: Panoramic / Full Statement

var srcSquareAB = [0, 5, 7, 8, 16, 21, 23]; // AB indices in srcDoc for Square
var srcLandAB   = [42, 43, 46, 50, 51, 55, 47]; // AB indices in srcDoc for Landscape
var srcPortAB   = [25, 28, 29, 30, 35, 37, 39]; // AB indices in srcDoc for Portrait

function copyLayout(srcABIdx, targetABIdx) {{
    var sAB = srcDoc.artboards[srcABIdx];
    var sR = sAB.artboardRect;
    var sW = sR[2] - sR[0];
    var sH = sR[1] - sR[3];

    var tAB = doc.artboards[targetABIdx];
    var tR = tAB.artboardRect;
    var tLeft = tR[0];
    var tTop = tR[1];
    var tW = tR[2] - tR[0];
    var tH = tR[1] - tR[3];

    // Find items in srcDoc on sAB
    for (var l = 0; l < srcDoc.layers.length; l++) {{
        var lyr = srcDoc.layers[l];
        for (var k = 0; k < lyr.pageItems.length; k++) {{
            var item = lyr.pageItems[k];
            var ib = item.geometricBounds;
            var cx = (ib[0] + ib[2]) / 2;
            var cy = (ib[1] + ib[3]) / 2;

            if (cx >= sR[0] && cx <= sR[2] && cy <= sR[1] && cy >= sR[3]) {{
                // Calculate relative position
                var relX = (ib[0] - sR[0]) / sW;
                var relY = (sR[1] - ib[1]) / sH;
                var itemW = (ib[2] - ib[0]);
                var itemH = (ib[1] - ib[3]);

                var dup = item.duplicate(layoutLayer, ElementPlacement.PLACEATBEGINNING);
                dup.left = tLeft + (ib[0] - sR[0]);
                dup.top = tTop - (sR[1] - ib[1]);
            }}
        }}
    }}
}}

// Copy layouts for all 21 artboards
for (var p = 0; p < 7; p++) {{
    copyLayout(srcSquareAB[p], p);         // Square (0-6)
    copyLayout(srcLandAB[p], 7 + p);       // Landscape (7-13)
    copyLayout(srcPortAB[p], 14 + p);      // Portrait (14-20)
}}

// Save Target Master AI File
var targetFile = new File("{TARGET_AI}");
doc.saveAs(targetFile);

// Export Step A: Blank Layout Previews (Backgrounds + Layout Gray Boxes)
var rawBlankFolder = new Folder("{RAW_BLANK_DIR}");
var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 90;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;

var blankBase = new File(rawBlankFolder.fsName + "/blank.jpg");
doc.exportFile(blankBase, ExportType.JPEG, exportOpts);

// Step B: Mask Photos into Layout Containers
var landPhotos = {str(land_photos).replace("'", '"')};
var portPhotos = {str(port_photos).replace("'", '"')};
var sqPhotos = {str(sq_photos).replace("'", '"')};
var allPhotos = {str(wedding_photos).replace("'", '"')};

var landIdx = 0, portIdx = 0, sqIdx = 0, allIdx = 0;

for (var i = 0; i < doc.artboards.length; i++) {{
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];

    for (var k = 0; k < layoutLayer.pathItems.length; k++) {{
        var pi = layoutLayer.pathItems[k];
        if (pi.guides || pi.clipping) continue;

        var gb = pi.geometricBounds;
        var cx = (gb[0] + gb[2]) / 2;
        var cy = (gb[1] + gb[3]) / 2;

        if (cx >= abLeft && cx <= abRight && cy <= abTop && cy >= abBottom) {{
            var pw = gb[2] - gb[0];
            var ph = gb[1] - gb[3];

            if (pw > 25 && ph > 25) {{
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
            }}
        }}
    }}
}}

// Save populated document
doc.save();

// Export Step B: Populated Previews (Backgrounds + Masked Photos + Layout Frames)
var rawPopFolder = new Folder("{RAW_POP_DIR}");
var popBase = new File(rawPopFolder.fsName + "/pop.jpg");
doc.exportFile(popBase, ExportType.JPEG, exportOpts);

// Close source doc
srcDoc.close(SaveOptions.DONOTSAVECHANGES);
"""

jsx_path = os.path.join(BASE_DIR, "generate_photobook_system.jsx")
with open(jsx_path, "w") as f:
    f.write(jsx_script)

print("\nExecuting Master Photobook generation in Adobe Illustrator...")
cmd = f'osascript -e \'tell application "Adobe Illustrator" to do javascript file "{jsx_path}"\''
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if res.returncode != 0:
    print(f"Error: {res.stderr}")
    sys.exit(1)

print("✓ Illustrator file created and populated successfully!")

# Resize and organize Blank Previews to max 1000px
print("\nProcessing Blank Layout Previews (Max 1000px)...")
raw_blank_files = sorted(glob.glob(os.path.join(RAW_BLANK_DIR, "*.jpg")))

bg_names = ["wed_p01", "wed_p06", "wed_p12", "wed_p15", "wed_p16", "wed_p17", "wed_p18"]

blank_preview_paths = []
for idx, rf in enumerate(raw_blank_files):
    if idx >= 21: break
    page_num = (idx % 7) + 1
    bg_name = bg_names[idx % 7]
    
    if idx < 7:
        size_label = "Square_10x10"
        target_size = (1000, 1000)
    elif idx < 14:
        size_label = "Landscape_12x8"
        target_size = (1000, 667)
    else:
        size_label = "Portrait_8x12"
        target_size = (667, 1000)

    with Image.open(rf) as im:
        im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
        out_filename = f"Blank_P{page_num:02d}_{size_label}_{bg_name}.jpg"
        out_path = os.path.join(BLANK_DIR, out_filename)
        im_resized.save(out_path, quality=92)
        blank_preview_paths.append(out_path)
        print(f"  [{idx+1:02d}/21] ✓ {out_filename} ({target_size[0]}x{target_size[1]} px)")

# Resize and organize Populated Previews to max 1000px
print("\nProcessing Populated Layout Previews (Max 1000px)...")
raw_pop_files = sorted(glob.glob(os.path.join(RAW_POP_DIR, "*.jpg")))

pop_preview_paths = []
for idx, rf in enumerate(raw_pop_files):
    if idx >= 21: break
    page_num = (idx % 7) + 1
    bg_name = bg_names[idx % 7]

    if idx < 7:
        size_label = "Square_10x10"
        target_size = (1000, 1000)
    elif idx < 14:
        size_label = "Landscape_12x8"
        target_size = (1000, 667)
    else:
        size_label = "Portrait_8x12"
        target_size = (667, 1000)

    with Image.open(rf) as im:
        im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
        out_filename = f"Populated_P{page_num:02d}_{size_label}_{bg_name}.jpg"
        out_path = os.path.join(POPULATED_DIR, out_filename)
        im_resized.save(out_path, quality=92)
        pop_preview_paths.append(out_path)
        print(f"  [{idx+1:02d}/21] ✓ {out_filename} ({target_size[0]}x{target_size[1]} px)")

# Cleanup raw temp export directories
shutil.rmtree(RAW_BLANK_DIR, ignore_errors=True)
shutil.rmtree(RAW_POP_DIR, ignore_errors=True)

# Build Interactive HTML Review Gallery
print("\nGenerating Interactive Review Gallery HTML...")
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wedding Photobook Previews — 3 Sizes & 7 Master Backgrounds</title>
<style>
  :root {
    --bg-dark: #0f172a;
    --card-bg: #1e293b;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #38bdf8;
    --border: #334155;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-main);
    margin: 0;
    padding: 30px;
  }
  .header {
    text-align: center;
    margin-bottom: 40px;
  }
  .header h1 {
    font-size: 2.2rem;
    margin-bottom: 10px;
    color: var(--text-main);
  }
  .header p {
    color: var(--text-muted);
    font-size: 1.1rem;
    max-width: 800px;
    margin: 0 auto;
  }
  .tabs {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin: 30px 0;
  }
  .tab-btn {
    background: var(--card-bg);
    border: 1px solid var(--border);
    color: var(--text-main);
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .tab-btn.active {
    background: var(--accent);
    color: #0f172a;
    border-color: var(--accent);
  }
  .page-section {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 40px;
  }
  .page-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
  }
  .size-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 25px;
  }
  .size-card {
    background: #0f172a;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 15px;
    text-align: center;
  }
  .size-card h3 {
    font-size: 1rem;
    color: var(--text-muted);
    margin-top: 0;
    margin-bottom: 12px;
  }
  .preview-img {
    width: 100%;
    height: auto;
    border-radius: 6px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    transition: transform 0.2s;
  }
  .preview-img:hover {
    transform: scale(1.02);
  }
  .badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    background: rgba(56, 189, 248, 0.15);
    color: var(--accent);
  }
</style>
<script>
  function switchView(view) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(view + '-btn').classList.add('active');
    
    document.querySelectorAll('.img-blank').forEach(el => el.style.display = (view === 'blank' ? 'block' : 'none'));
    document.querySelectorAll('.img-pop').forEach(el => el.style.display = (view === 'pop' ? 'block' : 'none'));
  }
</script>
</head>
<body>

<div class="header">
  <h1>Wedding Photobook Multi-Size Preview System</h1>
  <p>7 Master Backgrounds ($5400\times5400\text{px}$) applied across all 3 Photobook Formats (Square 10x10, Landscape 12x8, Portrait 8x12) in a single unified Adobe Illustrator file.</p>
  
  <div class="tabs">
    <button id="pop-btn" class="tab-btn active" onclick="switchView('pop')">Populated Previews (Masked Wedding Photos)</button>
    <button id="blank-btn" class="tab-btn" onclick="switchView('blank')">Blank Layout Previews (Backgrounds + Layout Boxes)</button>
  </div>
</div>
"""

for p in range(1, 8):
    bg_name = bg_names[p - 1]
    
    sq_blank = f"Blank_Layouts/Blank_P{p:02d}_Square_10x10_{bg_name}.jpg"
    sq_pop   = f"Populated_Layouts/Populated_P{p:02d}_Square_10x10_{bg_name}.jpg"
    
    ls_blank = f"Blank_Layouts/Blank_P{p:02d}_Landscape_12x8_{bg_name}.jpg"
    ls_pop   = f"Populated_Layouts/Populated_P{p:02d}_Landscape_12x8_{bg_name}.jpg"
    
    pt_blank = f"Blank_Layouts/Blank_P{p:02d}_Portrait_8x12_{bg_name}.jpg"
    pt_pop   = f"Populated_Layouts/Populated_P{p:02d}_Portrait_8x12_{bg_name}.jpg"

    html_content += f"""
<div class="page-section">
  <div class="page-title">
    <span>Page {p:02d} — Background: <code>{bg_name}</code></span>
    <span class="badge">Identical Theme Across 3 Sizes</span>
  </div>
  
  <div class="size-grid">
    <!-- Square 10x10 -->
    <div class="size-card">
      <h3>Square (10x10 in) — 1000x1000 px</h3>
      <img class="preview-img img-pop" src="{sq_pop}" alt="Square Populated">
      <img class="preview-img img-blank" src="{sq_blank}" alt="Square Blank" style="display:none;">
    </div>
    
    <!-- Landscape 12x8 -->
    <div class="size-card">
      <h3>Landscape (12x8 in) — 1000x667 px</h3>
      <img class="preview-img img-pop" src="{ls_pop}" alt="Landscape Populated">
      <img class="preview-img img-blank" src="{ls_blank}" alt="Landscape Blank" style="display:none;">
    </div>
    
    <!-- Portrait 8x12 -->
    <div class="size-card">
      <h3>Portrait (8x12 in) — 667x1000 px</h3>
      <img class="preview-img img-pop" src="{pt_pop}" alt="Portrait Populated">
      <img class="preview-img img-blank" src="{pt_blank}" alt="Portrait Blank" style="display:none;">
    </div>
  </div>
</div>
"""

html_content += """
</body>
</html>
"""

gallery_path = os.path.join(PREVIEWS_DIR, "review_gallery.html")
with open(gallery_path, "w") as f:
    f.write(html_content)

print(f"✓ Interactive HTML Gallery created at: {gallery_path}")
print("\n" + "="*80)
print("ALL 21 PHOTOBOOK PAGES & PREVIEWS GENERATED SUCCESSFULLY!")
print("="*80)
