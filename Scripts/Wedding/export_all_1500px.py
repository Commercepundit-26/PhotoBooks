#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from PIL import Image

sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test"
PREVIEWS_DIR = os.path.join(BASE_DIR, "Previews")
BG_DIR = os.path.join(BASE_DIR, "Backgorunds")

bg_files = sorted([os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR) if f.endswith(".jpg")])
bg_names = [os.path.basename(f).split("_")[1] for f in bg_files]

SIZES = [
    {
        "key": "Square_10x10",
        "name": "Square (10x10 in)",
        "ai_file": os.path.join(BASE_DIR, "Wedding_Square_10x10.ai"),
        "resolution": 150,
        "px_size": (1500, 1500)
    },
    {
        "key": "Landscape_12x8",
        "name": "Landscape (12x8 in)",
        "ai_file": os.path.join(BASE_DIR, "Wedding_Landscape_12x8.ai"),
        "resolution": 125,
        "px_size": (1500, 1000)
    },
    {
        "key": "Portrait_8x12",
        "name": "Portrait (8x12 in)",
        "ai_file": os.path.join(BASE_DIR, "Wedding_Portrait_8x12.ai"),
        "resolution": 125,
        "px_size": (1000, 1500)
    }
]

print("="*80)
print("RE-EXPORTING ALL PREVIEW IMAGES AT 1500PX MAX DIMENSION")
print("="*80)

for s in SIZES:
    key = s["key"]
    name = s["name"]
    ai_file = s["ai_file"]
    res_dpi = s["resolution"]
    target_px = s["px_size"]

    print(f"\nProcessing {name} (Target: {target_px[0]}x{target_px[1]} px)...")

    size_folder = os.path.join(PREVIEWS_DIR, key)
    blank_dir = os.path.join(size_folder, "Blank")
    pop_dir = os.path.join(size_folder, "Populated")
    raw_dir = os.path.join(size_folder, "Raw_1500")

    shutil.rmtree(size_folder, ignore_errors=True)
    os.makedirs(blank_dir, exist_ok=True)
    os.makedirs(pop_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    jsx_script = f"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.open(new File("{ai_file}"));

var rawFolder = new Folder("{raw_dir}");
var capOpts = new ImageCaptureOptions();
capOpts.resolution = {res_dpi};
capOpts.antiAliasing = true;
capOpts.transparency = false;

var layoutLayer = doc.layers.getByName("Layout_Shapes");

// 1. Capture 22 Blank Artboards (Photos Hidden, Layout Shapes Visible)
for (var i = 0; i < layoutLayer.groupItems.length; i++) {{
    var grp = layoutLayer.groupItems[i];
    if (grp.name.indexOf("Photos_Page") !== -1) {{
        grp.hidden = true;
    }} else if (grp.name.indexOf("Layout_P") !== -1) {{
        grp.hidden = false;
    }}
}}
app.redraw();

for (var i = 0; i < doc.artboards.length; i++) {{
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/blank_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}}

// 2. Capture 22 Populated Artboards (Photos Visible, Layout Shapes Hidden)
for (var i = 0; i < layoutLayer.groupItems.length; i++) {{
    var grp = layoutLayer.groupItems[i];
    if (grp.name.indexOf("Photos_Page") !== -1) {{
        grp.hidden = false;
    }} else if (grp.name.indexOf("Layout_P") !== -1) {{
        grp.hidden = true;
    }}
}}
app.redraw();

for (var i = 0; i < doc.artboards.length; i++) {{
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/pop_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}}

// Restore visibility and close
for (var i = 0; i < layoutLayer.groupItems.length; i++) {{
    layoutLayer.groupItems[i].hidden = false;
}}
doc.close(SaveOptions.DONOTSAVECHANGES);
"""
    jsx_file = os.path.join(BASE_DIR, "Scripts", f"export_1500_{key}.jsx")
    with open(jsx_file, "w") as f:
        f.write(jsx_script)

    as_script = f'''with timeout of 1800 seconds
    tell application "Adobe Illustrator"
        do javascript file "{jsx_file}"
    end tell
end timeout'''
    
    print(f"  Capturing 44 artboards from {os.path.basename(ai_file)} in Illustrator...")
    res = subprocess.run(["osascript", "-e", as_script], capture_output=True, text=True)

    if res.returncode != 0:
        print(f"  Error: {res.stderr}")
        continue

    # Resize blank captures to exact 1500px
    print(f"  Saving 22 Blank Previews ({target_px[0]}x{target_px[1]} px)...")
    for a in range(1, 23):
        raw_p = os.path.join(raw_dir, f"blank_ab{a:02d}.png")
        if not os.path.exists(raw_p):
            continue
        bg_code = bg_names[a - 1]
        out_name = f"Blank_P{a:02d}_{key}_{bg_code}.jpg"
        out_p = os.path.join(blank_dir, out_name)

        with Image.open(raw_p) as im:
            im_rgb = im.convert("RGB")
            im_resized = im_rgb.resize(target_px, Image.Resampling.LANCZOS)
            im_resized.save(out_p, quality=93)
            print(f"    [Blank {a:02d}/22] ✓ {out_name}")

    # Resize populated captures to exact 1500px
    print(f"  Saving 22 Populated Previews ({target_px[0]}x{target_px[1]} px)...")
    for a in range(1, 23):
        raw_p = os.path.join(raw_dir, f"pop_ab{a:02d}.png")
        if not os.path.exists(raw_p):
            continue
        bg_code = bg_names[a - 1]
        out_name = f"Populated_P{a:02d}_{key}_{bg_code}.jpg"
        out_p = os.path.join(pop_dir, out_name)

        with Image.open(raw_p) as im:
            im_rgb = im.convert("RGB")
            im_resized = im_rgb.resize(target_px, Image.Resampling.LANCZOS)
            im_resized.save(out_p, quality=93)
            print(f"    [Pop {a:02d}/22] ✓ {out_name}")

    shutil.rmtree(raw_dir, ignore_errors=True)
    print(f"✓ Completed {name}")

# Update HTML Gallery
print("\n" + "="*80)
print("UPDATING INTERACTIVE HTML GALLERY FOR 1500PX...")
print("="*80)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wedding Photobook Previews (1500px High-Res) — 22 Pages & 3 Sizes</title>
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
    <h1>Wedding Photobook Previews (1500px High-Res)</h1>
    <p>All 22 Master Backgrounds ($5400\times5400\text{ px}$) across 3 separate Adobe Illustrator documents (Square 10x10, Landscape 12x8, Portrait 8x12) exported at max dimension of 1500px.</p>
    
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
      <div class="badge">1500px High-Res</div>
    </div>
    
    <div class="size-grid">
      <!-- Square 10x10 -->
      <div class="size-item">
        <div class="size-label">
          <span>Square (10x10 in)</span>
          <span class="size-tag">1500 &times; 1500 px</span>
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
          <span class="size-tag">1500 &times; 1000 px</span>
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
          <span class="size-tag">1000 &times; 1500 px</span>
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

print(f"✓ Interactive HTML Gallery updated at: {gallery_path}")
print("\n" + "="*80)
print("ALL 132 PREVIEW IMAGES EXPORTED AT 1500PX SUCCESSFULLY!")
print("="*80)
