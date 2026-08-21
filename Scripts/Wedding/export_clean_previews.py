#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import glob
from PIL import Image

sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test"
PREVIEWS_DIR = os.path.join(BASE_DIR, "Previews")
RAW_DIR = os.path.join(PREVIEWS_DIR, "Raw_Captures")
BLANK_DIR = os.path.join(PREVIEWS_DIR, "Blank_Layouts")
POPULATED_DIR = os.path.join(PREVIEWS_DIR, "Populated_Layouts")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(BLANK_DIR, exist_ok=True)
os.makedirs(POPULATED_DIR, exist_ok=True)

bg_names = ["wed_p01", "wed_p06", "wed_p12", "wed_p15", "wed_p16", "wed_p17", "wed_p18"]

# Clean old files
for d in [BLANK_DIR, POPULATED_DIR, RAW_DIR]:
    for f in glob.glob(os.path.join(d, "*")):
        if os.path.isfile(f):
            os.remove(f)

jsx_export = f"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var aiFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Photobook_3Sizes.ai");
var doc = null;
for (var d = 0; d < app.documents.length; d++) {{
    if (app.documents[d].name.indexOf("Wedding_Photobook_3Sizes") !== -1) {{
        doc = app.documents[d];
        break;
    }}
}}
if (!doc) {{
    doc = app.open(aiFile);
}}

var rawFolder = new Folder("{RAW_DIR}");

var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

var photoLayer = null;
try {{
    photoLayer = doc.layers.getByName("Photos_Masked");
}} catch(e) {{}}

// 1. Export 21 Blank Artboards (Hide Photos)
if (photoLayer) photoLayer.visible = false;

for (var i = 0; i < doc.artboards.length; i++) {{
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/blank_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}}

// 2. Export 21 Populated Artboards (Show Photos)
if (photoLayer) photoLayer.visible = true;

for (var i = 0; i < doc.artboards.length; i++) {{
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/pop_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}}
"""

jsx_path = os.path.join(BASE_DIR, "capture_artboards.jsx")
with open(jsx_path, "w") as f:
    f.write(jsx_export)

print("Capturing 21 individual artboards from Adobe Illustrator...")
cmd = f'osascript -e \'tell application "Adobe Illustrator" to do javascript file "{jsx_path}"\''
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if res.returncode != 0:
    print(f"Error: {res.stderr}")
    sys.exit(1)

print("✓ All 42 artboard captures (21 blank + 21 populated) generated!")

# Resize and organize Blank Previews
print("\nOrganizing Blank Layout Previews (Max 1000px)...")
for a in range(1, 22):
    raw_path = os.path.join(RAW_DIR, f"blank_ab{a:02d}.png")
    if not os.path.exists(raw_path):
        print(f"Missing {raw_path}")
        continue
    
    p_num = ((a - 1) % 7) + 1
    bg_name = bg_names[(a - 1) % 7]

    if a <= 7:
        size_label = "Square_10x10"
        target_size = (1000, 1000)
    elif a <= 14:
        size_label = "Landscape_12x8"
        target_size = (1000, 667)
    else:
        size_label = "Portrait_8x12"
        target_size = (667, 1000)

    with Image.open(raw_path) as im:
        im_rgb = im.convert("RGB")
        im_resized = im_rgb.resize(target_size, Image.Resampling.LANCZOS)
        out_name = f"Blank_P{p_num:02d}_{size_label}_{bg_name}.jpg"
        out_path = os.path.join(BLANK_DIR, out_name)
        im_resized.save(out_path, quality=93)
        print(f"  [Blank {a:02d}/21] ✓ {out_name} -> {target_size[0]}x{target_size[1]} px")

# Resize and organize Populated Previews
print("\nOrganizing Populated Layout Previews (Max 1000px)...")
for a in range(1, 22):
    raw_path = os.path.join(RAW_DIR, f"pop_ab{a:02d}.png")
    if not os.path.exists(raw_path):
        print(f"Missing {raw_path}")
        continue

    p_num = ((a - 1) % 7) + 1
    bg_name = bg_names[(a - 1) % 7]

    if a <= 7:
        size_label = "Square_10x10"
        target_size = (1000, 1000)
    elif a <= 14:
        size_label = "Landscape_12x8"
        target_size = (1000, 667)
    else:
        size_label = "Portrait_8x12"
        target_size = (667, 1000)

    with Image.open(raw_path) as im:
        im_rgb = im.convert("RGB")
        im_resized = im_rgb.resize(target_size, Image.Resampling.LANCZOS)
        out_name = f"Populated_P{p_num:02d}_{size_label}_{bg_name}.jpg"
        out_path = os.path.join(POPULATED_DIR, out_name)
        im_resized.save(out_path, quality=93)
        print(f"  [Pop {a:02d}/21] ✓ {out_name} -> {target_size[0]}x{target_size[1]} px")

# Clean raw folder
shutil.rmtree(RAW_DIR, ignore_errors=True)

# Generate HTML Review Gallery
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wedding Photobook Multi-Size Preview System</title>
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
    max-width: 780px;
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
    <p>7 Master Background Textures ($5400\times5400\text{ px}$) unified across 3 Book Formats (Square 10x10, Landscape 12x8, Portrait 8x12) in 1 Illustrator file.</p>
    
    <div class="tabs">
      <button id="pop-btn" class="tab-btn active" onclick="switchTab('pop')">Populated Previews (Masked Wedding Photos)</button>
      <button id="blank-btn" class="tab-btn" onclick="switchTab('blank')">Blank Layout Previews (Backgrounds + Layout Boxes)</button>
    </div>
  </div>
"""

layout_descriptions = [
    "Cover / Hero Title Spread (1 Statement Frame)",
    "2-Photo Clean Duo Spread (2 Balanced Frames)",
    "3-Photo Classic Story Spread (1 Focal + 2 Story Frames)",
    "4-Photo Rhythmic Quad Spread (4 Balanced Frames)",
    "Arch & Unique Shapes Spread (Artistic Masking Frames)",
    "Multi-Photo Collage / Storyboard Spread (Gallery Frames)",
    "Panoramic Showcase Spread (Full-Width Statement Frame)"
]

for p in range(1, 8):
    bg_name = bg_names[p - 1]
    desc = layout_descriptions[p - 1]
    
    sq_blank = f"Blank_Layouts/Blank_P{p:02d}_Square_10x10_{bg_name}.jpg"
    sq_pop   = f"Populated_Layouts/Populated_P{p:02d}_Square_10x10_{bg_name}.jpg"
    
    ls_blank = f"Blank_Layouts/Blank_P{p:02d}_Landscape_12x8_{bg_name}.jpg"
    ls_pop   = f"Populated_Layouts/Populated_P{p:02d}_Landscape_12x8_{bg_name}.jpg"
    
    pt_blank = f"Blank_Layouts/Blank_P{p:02d}_Portrait_8x12_{bg_name}.jpg"
    pt_pop   = f"Populated_Layouts/Populated_P{p:02d}_Portrait_8x12_{bg_name}.jpg"

    html_content += f"""
  <div class="page-card">
    <div class="page-header">
      <div class="page-title">Page {p:02d}: {desc} &nbsp;•&nbsp; <code>{bg_name}</code></div>
      <div class="badge">Universal 5.4K Texture</div>
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

print(f"\n✓ Interactive HTML Review Gallery updated at: {gallery_path}")
print("✓ ALL INDIVIDUAL ARTBOARDS EXPORTED CLEANLY!")
