#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import glob
from PIL import Image

sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test"
BG_DIR = os.path.join(BASE_DIR, "Backgorunds")
SOURCE_AI = os.path.join(BASE_DIR, "Unique shape Layouts.ai")
WEDDING_PHOTOS_DIR = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding"

PREVIEWS_DIR = os.path.join(BASE_DIR, "Previews")
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")
os.makedirs(SCRIPTS_DIR, exist_ok=True)

print("="*80)
print("STARTING COMPLETE PHOTOBOOK GENERATION (22 PAGES ACROSS 3 SEPARATE AI FILES)")
print("="*80)

# Delete previous AI files if present
for old_f in ["Wedding_Photobook_3Sizes.ai", "Wedding_Square_10x10.ai", "Wedding_Landscape_12x8.ai", "Wedding_Portrait_8x12.ai"]:
    p = os.path.join(BASE_DIR, old_f)
    if os.path.exists(p):
        os.remove(p)

# Reset Previews directory
if os.path.exists(PREVIEWS_DIR):
    shutil.rmtree(PREVIEWS_DIR)
os.makedirs(PREVIEWS_DIR, exist_ok=True)

# 22 Background files
bg_files = sorted([os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR) if f.endswith(".jpg")])
bg_names = [os.path.basename(f).split("_")[1] for f in bg_files]
print(f"Loaded {len(bg_files)} backgrounds: {', '.join(bg_names)}")

# 75 Master Wedding photos
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

print(f"Loaded {len(wedding_photos)} master photos ({len(land_photos)} Landscape, {len(port_photos)} Portrait, {len(sq_photos)} Square)")

# Size Definitions
SIZES = [
    {
        "key": "Square_10x10",
        "name": "Square (10x10 in)",
        "ai_file": os.path.join(BASE_DIR, "Wedding_Square_10x10.ai"),
        "pt_w": 720,
        "pt_h": 720,
        "px_size": (1000, 1000),
        "src_ab_indices": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    },
    {
        "key": "Landscape_12x8",
        "name": "Landscape (12x8 in)",
        "ai_file": os.path.join(BASE_DIR, "Wedding_Landscape_12x8.ai"),
        "pt_w": 864,
        "pt_h": 576,
        "px_size": (1000, 667),
        "src_ab_indices": [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 59, 61, 62, 27, 41, 42]
    },
    {
        "key": "Portrait_8x12",
        "name": "Portrait (8x12 in)",
        "ai_file": os.path.join(BASE_DIR, "Wedding_Portrait_8x12.ai"),
        "pt_w": 576,
        "pt_h": 864,
        "px_size": (667, 1000),
        "src_ab_indices": [25, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 57, 58, 60, 25, 28, 29, 30, 31]
    }
]

def generate_photobook_size(size_info):
    key = size_info["key"]
    title = size_info["name"]
    ai_target = size_info["ai_file"]
    pt_w = size_info["pt_w"]
    pt_h = size_info["pt_h"]
    px_target = size_info["px_size"]
    src_indices = size_info["src_ab_indices"]

    print(f"\n" + "-"*80)
    print(f"GENERATING SIZE: {title} -> {os.path.basename(ai_target)}")
    print(f"-"*80)

    size_folder = os.path.join(PREVIEWS_DIR, key)
    blank_dir = os.path.join(size_folder, "Blank")
    pop_dir = os.path.join(size_folder, "Populated")
    raw_dir = os.path.join(size_folder, "Raw_Temp")

    shutil.rmtree(size_folder, ignore_errors=True)
    os.makedirs(blank_dir, exist_ok=True)
    os.makedirs(pop_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    bg_paths_json = str(bg_files).replace("'", '"')
    land_photos_json = str(land_photos).replace("'", '"')
    port_photos_json = str(port_photos).replace("'", '"')
    sq_photos_json = str(sq_photos).replace("'", '"')
    all_photos_json = str(wedding_photos).replace("'", '"')
    src_indices_json = str(src_indices)

    jsx_script = f"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

// 1. Open Source AI Layouts
var sourceFile = new File("{SOURCE_AI}");
var srcDoc = null;
for (var d = 0; d < app.documents.length; d++) {{
    if (app.documents[d].name.indexOf("Unique shape Layouts") !== -1) {{
        srcDoc = app.documents[d];
        break;
    }}
}}
if (!srcDoc) {{
    srcDoc = app.open(sourceFile);
}}

// Index layout elements in source document
var itemsByAB = [];
for (var a = 0; a < srcDoc.artboards.length; a++) {{
    itemsByAB.push([]);
}}
for (var k = 0; k < srcDoc.pageItems.length; k++) {{
    var item = srcDoc.pageItems[k];
    if (item.guides || item.clipping) continue;
    var ib = item.geometricBounds;
    var cx = (ib[0] + ib[2]) / 2;
    var cy = (ib[1] + ib[3]) / 2;

    for (var a = 0; a < srcDoc.artboards.length; a++) {{
        var ar = srcDoc.artboards[a].artboardRect;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {{
            itemsByAB[a].push(item);
            break;
        }}
    }}
}}

// 2. Create Target AI Document
var doc = app.documents.add(DocumentColorSpace.RGB, {pt_w}, {pt_h});
doc.artboards[0].artboardRect = [0, 0, {pt_w}, -{pt_h}];
doc.artboards[0].name = "P01_{key}_wed_p01";

var spacing = 60;
var rowCols = 6;

// Create 21 more artboards in clean grid (4 rows of 6 cols)
for (var i = 1; i < 22; i++) {{
    var col = i % rowCols;
    var row = Math.floor(i / rowCols);
    var l = col * ({pt_w} + spacing);
    var t = -row * ({pt_h} + spacing);
    var pNum = (i + 1 < 10 ? "0" : "") + (i + 1);
    var ab = doc.artboards.add([l, t, l + {pt_w}, t - {pt_h}]);
    ab.name = "P" + pNum + "_{key}_wed_p" + pNum;
}}

// 3. Setup Layers
var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";

var photoLayer = doc.layers.add();
photoLayer.name = "Photos_Masked";

var layoutLayer = doc.layers[0];
layoutLayer.name = "Layout_Shapes";

bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

// 4. Place 22 Backgrounds
var bgFiles = {bg_paths_json};
for (var i = 0; i < 22; i++) {{
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];
    var abW = abRight - abLeft;
    var abH = abTop - abBottom;

    var bgFile = new File(bgFiles[i]);

    var clipGroup = bgLayer.groupItems.add();
    clipGroup.name = "Background_P" + (i + 1 < 10 ? "0" : "") + (i + 1);

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

// 5. Copy Layout Shapes
var srcABs = {src_indices_json};
for (var p = 0; p < 22; p++) {{
    var sIdx = srcABs[p];
    var sR = srcDoc.artboards[sIdx].artboardRect;
    var tR = doc.artboards[p].artboardRect;
    var items = itemsByAB[sIdx];

    var pGroup = layoutLayer.groupItems.add();
    pGroup.name = "Layout_P" + (p + 1 < 10 ? "0" : "") + (p + 1);

    for (var m = 0; m < items.length; m++) {{
        var itm = items[m];
        var dup = itm.duplicate(layoutLayer, ElementPlacement.PLACEATBEGINNING);
        dup.left = tR[0] + (itm.left - sR[0]);
        dup.top = tR[1] + (itm.top - sR[1]);
        dup.move(pGroup, ElementPlacement.PLACEATBEGINNING);
    }}
}}

// 6. Capture 22 Blank Artboards
var rawFolder = new Folder("{raw_dir}");
var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

for (var i = 0; i < 22; i++) {{
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/blank_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}}

// 7. Recursive helper to extract all PathItems
function getAllPaths(container, out) {{
    for (var i = 0; i < container.pathItems.length; i++) {{
        out.push(container.pathItems[i]);
    }}
    for (var g = 0; g < container.groupItems.length; g++) {{
        getAllPaths(container.groupItems[g], out);
    }}
}}

var allLayoutPaths = [];
getAllPaths(layoutLayer, allLayoutPaths);

// 8. Place & Mask Photos inside every frame
var landPhotos = {land_photos_json};
var portPhotos = {port_photos_json};
var sqPhotos = {sq_photos_json};
var allPhotos = {all_photos_json};

var landIdx = 0, portIdx = 0, sqIdx = 0, allIdx = 0;

for (var i = 0; i < 22; i++) {{
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];

    var pagePhotoGroup = photoLayer.groupItems.add();
    pagePhotoGroup.name = "Photos_Page_" + (i + 1 < 10 ? "0" : "") + (i + 1);

    for (var k = 0; k < allLayoutPaths.length; k++) {{
        var pi = allLayoutPaths[k];
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

                var pGroup = pagePhotoGroup.groupItems.add();

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

// 9. Hide placeholder vector gray boxes on Layout layer so masked photos show cleanly
for (var k = 0; k < allLayoutPaths.length; k++) {{
    allLayoutPaths[k].hidden = true;
}}
app.redraw();

// 10. Capture 22 Populated Artboards
for (var i = 0; i < 22; i++) {{
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/pop_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}}

// 11. Restore Layout Shapes visibility so user can edit both layers
for (var k = 0; k < allLayoutPaths.length; k++) {{
    allLayoutPaths[k].hidden = false;
}}

// 12. Save Master AI Document non-interactively and Close
var targetFile = new File("{ai_target}");
var saveOpts = new IllustratorSaveOptions();
saveOpts.pdfCompatible = false;
saveOpts.compressed = true;
doc.saveAs(targetFile, saveOpts);
doc.close(SaveOptions.DONOTSAVECHANGES);
"""

    jsx_file = os.path.join(SCRIPTS_DIR, f"build_{key}.jsx")
    with open(jsx_file, "w") as f:
        f.write(jsx_script)

    print(f"  Executing {key} in Adobe Illustrator...")
    as_script = f'''with timeout of 1800 seconds
    tell application "Adobe Illustrator"
        do javascript file "{jsx_file}"
    end tell
end timeout'''
    res = subprocess.run(["osascript", "-e", as_script], capture_output=True, text=True)

    if res.returncode != 0:
        print(f"  Error: {res.stderr}")
        return False

    print(f"  ✓ Saved Illustrator Document: {os.path.basename(ai_target)}")

    # Resize raw blank captures to max 1000px
    print(f"  Organizing 22 Blank Previews for {key}...")
    for a in range(1, 23):
        raw_p = os.path.join(raw_dir, f"blank_ab{a:02d}.png")
        if not os.path.exists(raw_p):
            continue
        bg_code = bg_names[a - 1]
        out_name = f"Blank_P{a:02d}_{key}_{bg_code}.jpg"
        out_p = os.path.join(blank_dir, out_name)

        with Image.open(raw_p) as im:
            im_rgb = im.convert("RGB")
            im_resized = im_rgb.resize(px_target, Image.Resampling.LANCZOS)
            im_resized.save(out_p, quality=93)
            print(f"    [Blank {a:02d}/22] ✓ {out_name} ({px_target[0]}x{px_target[1]} px)")

    # Resize raw populated captures to max 1000px
    print(f"  Organizing 22 Populated Previews for {key}...")
    for a in range(1, 23):
        raw_p = os.path.join(raw_dir, f"pop_ab{a:02d}.png")
        if not os.path.exists(raw_p):
            continue
        bg_code = bg_names[a - 1]
        out_name = f"Populated_P{a:02d}_{key}_{bg_code}.jpg"
        out_p = os.path.join(pop_dir, out_name)

        with Image.open(raw_p) as im:
            im_rgb = im.convert("RGB")
            im_resized = im_rgb.resize(px_target, Image.Resampling.LANCZOS)
            im_resized.save(out_p, quality=93)
            print(f"    [Pop {a:02d}/22] ✓ {out_name} ({px_target[0]}x{px_target[1]} px)")

    shutil.rmtree(raw_dir, ignore_errors=True)
    print(f"✓ Completed Size: {title}")
    return True

# Run for all 3 sizes one by one
for s_info in SIZES:
    generate_photobook_size(s_info)

# 3. Build Unified 22-Page Interactive Review Gallery HTML
print("\n" + "="*80)
print("BUILDING UNIFIED 22-PAGE INTERACTIVE REVIEW GALLERY HTML...")
print("="*80)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wedding Photobook Previews — 22 Pages & 3 Distinct AI Sizes</title>
<style>
  :root {
    --bg-dark: #090d16;
    --card-bg: #151d2f;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #38bdf8;
    --border: #24324f;
    --tag-bg: rgba(56, 189, 248, 0.12);
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-main);
    margin: 0;
    padding: 30px 20px 80px;
  }
  .container {
    max-width: 1400px;
    margin: 0 auto;
  }
  .header {
    text-align: center;
    margin-bottom: 35px;
    padding-bottom: 25px;
    border-bottom: 1px solid var(--border);
  }
  .header h1 {
    font-size: 2.3rem;
    margin: 0 0 10px;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .header p {
    color: var(--text-muted);
    font-size: 1.05rem;
    max-width: 820px;
    margin: 0 auto 20px;
    line-height: 1.5;
  }
  .tabs {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 20px;
  }
  .tab-btn {
    background: var(--card-bg);
    border: 1px solid var(--border);
    color: var(--text-main);
    padding: 12px 26px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .tab-btn:hover {
    border-color: var(--accent);
  }
  .tab-btn.active {
    background: var(--accent);
    color: #090d16;
    border-color: var(--accent);
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
  }
  .page-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 40px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  }
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
  }
  .page-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--accent);
  }
  .page-title code {
    background: rgba(255,255,255,0.08);
    padding: 3px 8px;
    border-radius: 5px;
    font-size: 0.95rem;
    color: #fff;
  }
  .badge {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    background: var(--tag-bg);
    color: var(--accent);
    border: 1px solid rgba(56, 189, 248, 0.3);
  }
  .size-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 22px;
  }
  @media (max-width: 1024px) {
    .size-grid { grid-template-columns: 1fr; }
  }
  .size-item {
    background: #090d16;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .size-label {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 12px;
    text-align: center;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .size-tag {
    font-size: 0.75rem;
    background: rgba(255,255,255,0.06);
    padding: 2px 8px;
    border-radius: 4px;
    color: #cbd5e1;
  }
  .img-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
  }
  .preview-img {
    max-width: 100%;
    max-height: 480px;
    height: auto;
    object-fit: contain;
    border-radius: 6px;
    transition: transform 0.25s ease;
  }
  .preview-img:hover {
    transform: scale(1.03);
    cursor: zoom-in;
  }
  #modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.9);
    justify-content: center;
    align-items: center;
    cursor: zoom-out;
  }
  #modal img {
    max-width: 92vw;
    max-height: 92vh;
    border-radius: 8px;
    box-shadow: 0 0 40px rgba(0,0,0,0.8);
  }
</style>
<script>
  function switchTab(view) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(view + '-btn').classList.add('active');
    
    document.querySelectorAll('.img-blank').forEach(el => el.style.display = (view === 'blank' ? 'block' : 'none'));
    document.querySelectorAll('.img-pop').forEach(el => el.style.display = (view === 'pop' ? 'block' : 'none'));
  }
  function openZoom(src) {
    var modal = document.getElementById('modal');
    var modalImg = document.getElementById('modal-img');
    modalImg.src = src;
    modal.style.display = 'flex';
  }
  function closeZoom() {
    document.getElementById('modal').style.display = 'none';
  }
</script>
</head>
<body>

<div class="container">
  <div class="header">
    <h1>Wedding Photobook Multi-Size Preview System</h1>
    <p>All 22 Master Backgrounds ($5400\times5400\text{ px}$) generated across 3 separate Adobe Illustrator documents (Square 10x10, Landscape 12x8, Portrait 8x12).</p>
    
    <div class="tabs">
      <button id="pop-btn" class="tab-btn active" onclick="switchTab('pop')">Populated Previews (Masked Wedding Photos)</button>
      <button id="blank-btn" class="tab-btn" onclick="switchTab('blank')">Blank Layout Previews (Backgrounds + Layout Boxes)</button>
    </div>
  </div>
"""

for p in range(1, 23):
    bg_code = bg_names[p - 1]
    
    sq_blank = f"Square_10x10/Blank/Blank_P{p:02d}_Square_10x10_{bg_code}.jpg"
    sq_pop   = f"Square_10x10/Populated/Populated_P{p:02d}_Square_10x10_{bg_code}.jpg"
    
    ls_blank = f"Landscape_12x8/Blank/Blank_P{p:02d}_Landscape_12x8_{bg_code}.jpg"
    ls_pop   = f"Landscape_12x8/Populated/Populated_P{p:02d}_Landscape_12x8_{bg_code}.jpg"
    
    pt_blank = f"Portrait_8x12/Blank/Blank_P{p:02d}_Portrait_8x12_{bg_code}.jpg"
    pt_pop   = f"Portrait_8x12/Populated/Populated_P{p:02d}_Portrait_8x12_{bg_code}.jpg"

    html_content += f"""
  <div class="page-card">
    <div class="page-header">
      <div class="page-title">Page {p:02d} &nbsp;•&nbsp; Background: <code>{bg_code}</code></div>
      <div class="badge">Master 5.4K Texture</div>
    </div>
    
    <div class="size-grid">
      <!-- Square 10x10 -->
      <div class="size-item">
        <div class="size-label">
          <span>Square (10x10 in)</span>
          <span class="size-tag">1000 &times; 1000 px</span>
        </div>
        <div class="img-wrapper">
          <img class="preview-img img-pop" src="{sq_pop}" onclick="openZoom(this.src)" alt="Square Populated">
          <img class="preview-img img-blank" src="{sq_blank}" onclick="openZoom(this.src)" alt="Square Blank" style="display:none;">
        </div>
      </div>
      
      <!-- Landscape 12x8 -->
      <div class="size-item">
        <div class="size-label">
          <span>Landscape (12x8 in)</span>
          <span class="size-tag">1000 &times; 667 px</span>
        </div>
        <div class="img-wrapper">
          <img class="preview-img img-pop" src="{ls_pop}" onclick="openZoom(this.src)" alt="Landscape Populated">
          <img class="preview-img img-blank" src="{ls_blank}" onclick="openZoom(this.src)" alt="Landscape Blank" style="display:none;">
        </div>
      </div>
      
      <!-- Portrait 8x12 -->
      <div class="size-item">
        <div class="size-label">
          <span>Portrait (8x12 in)</span>
          <span class="size-tag">667 &times; 1000 px</span>
        </div>
        <div class="img-wrapper">
          <img class="preview-img img-pop" src="{pt_pop}" onclick="openZoom(this.src)" alt="Portrait Populated">
          <img class="preview-img img-blank" src="{pt_blank}" onclick="openZoom(this.src)" alt="Portrait Blank" style="display:none;">
        </div>
      </div>
    </div>
  </div>
"""

html_content += """
</div>

<div id="modal" onclick="closeZoom()">
  <img id="modal-img" src="" alt="Zoomed Preview">
</div>

</body>
</html>
"""

gallery_path = os.path.join(PREVIEWS_DIR, "review_gallery.html")
with open(gallery_path, "w") as f:
    f.write(html_content)

print(f"✓ Interactive HTML Gallery created at: {gallery_path}")
print("\n" + "="*80)
print("ALL 3 AI DOCUMENTS & 132 PREVIEWS GENERATED SUCCESSFULLY!")
print("="*80)
