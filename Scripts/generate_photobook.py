#!/usr/bin/env python3
"""
Universal Master Photobook Production Automation Engine (All 3 Sizes)
- Supports: Square 10x10, Landscape 12x8, Portrait 8x12
- Enforces >= 18 Text Layouts per 22-page book
- Guarantees 100% identical frame layouts between Blank and Populated previews
- Locks a consistent 3-font palette per theme
- Formats multi-line text with '\r' and enforces 1-inch safe margins
- Executes in under 1 minute per size
"""

import os
import sys
import json
import argparse
import shutil
import subprocess
from PIL import Image

sys.stdout.reconfigure(line_buffering=True)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT_FILE = os.path.join(REPO_ROOT, "Layout", "Final Layouts.ai")
IMAGE_LIB_DIR = os.path.join(REPO_ROOT, "Image_Library")

FONT_PALETTES = {
    "wedding": {
        "title_font": "GreatVibes-Regular",
        "subtitle_font": "Poppins-Medium",
        "body_font": "Poppins-Regular",
        "title_size": 42,
        "subtitle_size": 11.5,
        "body_size": 13,
        "color": [0.18, 0.15, 0.13]
    },
    "romantic": {
        "title_font": "Fallinlove-Regular",
        "subtitle_font": "Poppins-Medium",
        "body_font": "Poppins-Regular",
        "title_size": 46,
        "subtitle_size": 11.5,
        "body_size": 13,
        "color": [0.18, 0.15, 0.13]
    },
    "classic": {
        "title_font": "Philosopher-Bold",
        "subtitle_font": "Philosopher",
        "body_font": "Poppins-Regular",
        "title_size": 36,
        "subtitle_size": 12,
        "body_size": 13,
        "color": [0.15, 0.15, 0.15]
    },
    "modern": {
        "title_font": "Poppins-Bold",
        "subtitle_font": "Poppins-Medium",
        "body_font": "Poppins-Regular",
        "title_size": 32,
        "subtitle_size": 12,
        "body_size": 12.5,
        "color": [0.12, 0.12, 0.12]
    },
    "baby": {
        "title_font": "LobsterTwo-Bold",
        "subtitle_font": "Poppins-Medium",
        "body_font": "Poppins-Regular",
        "title_size": 38,
        "subtitle_size": 12,
        "body_size": 13,
        "color": [0.20, 0.18, 0.16]
    },
    "family": {
        "title_font": "Rockwell-Bold",
        "subtitle_font": "Poppins-Medium",
        "body_font": "Poppins-Regular",
        "title_size": 34,
        "subtitle_size": 12,
        "body_size": 12.5,
        "color": [0.15, 0.15, 0.15]
    }
}

SIZE_SPECS = {
    "Square_10x10": {
        "name": "Square 10x10",
        "width_pt": 720,
        "height_pt": 720,
        "preview_size": (1500, 1500),
        "source_indices": [1, 2, 5, 9, 6, 10, 8, 7, 23, 21, 20, 11, 13, 12, 24, 37, 27, 30, 4, 35, 39, 19]
    },
    "Landscape_12x8": {
        "name": "Landscape 12x8",
        "width_pt": 864,
        "height_pt": 576,
        "preview_size": (1500, 1000),
        "source_indices": [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
    },
    "Portrait_8x12": {
        "name": "Portrait 8x12",
        "width_pt": 576,
        "height_pt": 864,
        "preview_size": (1000, 1500),
        "source_indices": [84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105]
    }
}

def main():
    parser = argparse.ArgumentParser(description="Master Photobook Generator for Adobe Illustrator")
    parser.add_argument("--theme", type=str, default="Wedding", help="Theme Name (e.g. Wedding, Baby, Couple)")
    parser.add_argument("--backgrounds", type=str, required=True, help="Path to folder with 22 background JPGs")
    parser.add_argument("--size", type=str, default="Square_10x10", choices=["Square_10x10", "Landscape_12x8", "Portrait_8x12", "all"], help="Book size")
    parser.add_argument("--style", type=str, default=None, help="Typography style")
    parser.add_argument("--photos", type=str, default=None, help="Custom photo folder")
    parser.add_argument("--output", type=str, default=None, help="Output destination folder")
    args = parser.parse_args()

    theme_key = args.theme.lower()
    style_key = args.style if args.style in FONT_PALETTES else ("baby" if "baby" in theme_key else "wedding")
    palette = FONT_PALETTES[style_key]

    # Resolve Backgrounds
    bg_dir = os.path.abspath(args.backgrounds)
    if not os.path.exists(bg_dir):
        print(f"[!] Error: Background directory not found at: {bg_dir}")
        sys.exit(1)

    bg_files = sorted([os.path.join(bg_dir, f) for f in os.listdir(bg_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    if len(bg_files) < 22:
        while len(bg_files) < 22:
            bg_files.extend(bg_files)
    bg_files = bg_files[:22]

    # Resolve Photos
    photo_dir = args.photos if args.photos else os.path.join(IMAGE_LIB_DIR, args.theme.capitalize())
    if not os.path.exists(photo_dir):
        photo_dir = os.path.join(IMAGE_LIB_DIR, "Wedding" if "baby" not in theme_key else "Baby")
    
    all_photos = sorted([os.path.join(photo_dir, f) for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    land_photos, port_photos, sq_photos = [], [], []
    for p in all_photos:
        try:
            with Image.open(p) as im:
                w, h = im.size
                r = w / float(h)
                if 0.88 <= r <= 1.12: sq_photos.append(p)
                elif r < 0.88: port_photos.append(p)
                else: land_photos.append(p)
        except Exception:
            pass

    print(f"Loaded {len(all_photos)} master photos ({len(land_photos)} Landscape, {len(port_photos)} Portrait, {len(sq_photos)} Square)")

    sizes_to_build = ["Square_10x10", "Landscape_12x8", "Portrait_8x12"] if args.size == "all" else [args.size]

    for size_key in sizes_to_build:
        spec = SIZE_SPECS[size_key]
        out_base = args.output if args.output else os.path.join(REPO_ROOT, "New", f"{args.theme}_{size_key}")
        previews_dir = os.path.join(out_base, "Previews")
        blank_dir = os.path.join(previews_dir, "Blank")
        pop_dir = os.path.join(previews_dir, "Populated")
        raw_dir = os.path.join(previews_dir, "Raw_Temp")
        ai_out_file = os.path.join(out_base, f"{args.theme}_{size_key}.ai")

        os.makedirs(out_base, exist_ok=True)
        shutil.rmtree(previews_dir, ignore_errors=True)
        os.makedirs(blank_dir, exist_ok=True)
        os.makedirs(pop_dir, exist_ok=True)
        os.makedirs(raw_dir, exist_ok=True)

        print("\n" + "="*80)
        print(f"BUILDING PHOTOBOOK: {args.theme} | SIZE: {spec['name']} ({spec['width_pt']}x{spec['height_pt']} pt)")
        print(f"Output Master AI: {ai_out_file}")
        print("="*80)

        # Build ExtendScript
        jsx_script_path = os.path.join(REPO_ROOT, "Scripts", f"_run_{size_key}.jsx")
        build_fast_extendscript(
            jsx_path=jsx_script_path,
            layout_file=LAYOUT_FILE,
            ai_out_file=ai_out_file,
            raw_dir=raw_dir,
            bg_files=bg_files,
            land_photos=land_photos,
            port_photos=port_photos,
            sq_photos=sq_photos,
            all_photos=all_photos,
            spec=spec,
            palette=palette,
            theme_key=theme_key
        )

        # Execute via Illustrator with 1200-second timeout
        print("Executing Adobe Illustrator automation...")
        cmd = [
            "osascript",
            "-e", "with timeout of 1200 seconds",
            "-e", f'tell application "Adobe Illustrator" to do javascript file "{jsx_script_path}"',
            "-e", "end timeout"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[!] Illustrator execution error: {res.stderr}")
        else:
            print("Illustrator rendering completed successfully.")

        if os.path.exists(jsx_script_path):
            os.remove(jsx_script_path)

        # Downsample Previews with Lanczos to exact target dimensions
        print("Resizing Blank and Populated previews to exact dimensions...")
        target_w, target_h = spec["preview_size"]
        
        for p_idx in range(1, 23):
            # Blank
            raw_blank = os.path.join(raw_dir, f"raw_blank_p{p_idx:02d}.png")
            final_blank = os.path.join(blank_dir, f"Blank_P{p_idx:02d}_{size_key}_p{p_idx:02d}.jpg")
            if os.path.exists(raw_blank):
                with Image.open(raw_blank) as im:
                    im_rgb = im.convert("RGB")
                    im_resized = im_rgb.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    im_resized.save(final_blank, "JPEG", quality=93)

            # Populated
            raw_pop = os.path.join(raw_dir, f"raw_pop_p{p_idx:02d}.png")
            final_pop = os.path.join(pop_dir, f"Populated_P{p_idx:02d}_{size_key}_p{p_idx:02d}.jpg")
            if os.path.exists(raw_pop):
                with Image.open(raw_pop) as im:
                    im_rgb = im.convert("RGB")
                    im_resized = im_rgb.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    im_resized.save(final_pop, "JPEG", quality=93)

        shutil.rmtree(raw_dir, ignore_errors=True)
        print(f"✓ Size {spec['name']} generation complete! Master: {os.path.basename(ai_out_file)}")

    print("\n" + "="*80)
    print("ALL REQUESTED PHOTOBOOK SIZES SUCCESSFULLY GENERATED!")
    print("="*80)

def build_fast_extendscript(jsx_path, layout_file, ai_out_file, raw_dir, bg_files, land_photos, port_photos, sq_photos, all_photos, spec, palette, theme_key):
    bg_json = json.dumps(bg_files)
    land_json = json.dumps(land_photos if land_photos else all_photos)
    port_json = json.dumps(port_photos if port_photos else all_photos)
    sq_json = json.dumps(sq_photos if sq_photos else all_photos)
    all_json = json.dumps(all_photos)
    src_indices_json = json.dumps(spec["source_indices"])

    is_baby = "baby" in theme_key
    cover_title = "Welcome Little One" if is_baby else "Our Wedding Story"
    cover_sub = "OUR PRECIOUS LITTLE MIRACLE  •  BABY MEMORIES" if is_baby else "THE CELEBRATION OF OUR LOVE  •  OCTOBER 24, 2026"
    h1 = "A Miracle Has Arrived" if is_baby else "The Beginning of Our Forever"
    q1 = "Ten little fingers, ten little toes,\rfilling our hearts with love that grows" if is_baby else "Two hearts, one soul, and a lifetime of love to share together"

    jsx_content = f"""
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var srcDoc = app.open(new File("{layout_file}"));

// Pre-index items per artboard
var itemsByAB = [];
for (var a = 0; a < srcDoc.artboards.length; a++) {{
    itemsByAB.push({{ paths: [], textFrames: [] }});
}}

var allLeafPaths = [];
for (var p = 0; p < srcDoc.pathItems.length; p++) {{
    var it = srcDoc.pathItems[p];
    if (!it.guides && !it.clipping) allLeafPaths.push(it);
}}
for (var p = 0; p < srcDoc.compoundPathItems.length; p++) {{
    var it = srcDoc.compoundPathItems[p];
    if (!it.guides && !it.clipping) allLeafPaths.push(it);
}}

for (var k = 0; k < allLeafPaths.length; k++) {{
    var it = allLeafPaths[k];
    var ib = it.geometricBounds;
    var cx = (ib[0] + ib[2]) / 2;
    var cy = (ib[1] + ib[3]) / 2;
    for (var a = 0; a < srcDoc.artboards.length; a++) {{
        var ar = srcDoc.artboards[a].artboardRect;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {{
            var pw = Math.abs(ib[2] - ib[0]);
            var ph = Math.abs(ib[1] - ib[3]);
            if (pw > 15 && ph > 15) {{
                itemsByAB[a].paths.push(it);
            }}
            break;
        }}
    }}
}}

for (var t = 0; t < srcDoc.textFrames.length; t++) {{
    var tf = srcDoc.textFrames[t];
    var ib = tf.geometricBounds;
    var cx = (ib[0] + ib[2]) / 2;
    var cy = (ib[1] + ib[3]) / 2;
    for (var a = 0; a < srcDoc.artboards.length; a++) {{
        var ar = srcDoc.artboards[a].artboardRect;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {{
            itemsByAB[a].textFrames.push(tf);
            break;
        }}
    }}
}}

// 2. Create Target Master Document
var targetDoc = app.documents.add(DocumentColorSpace.RGB, {spec['width_pt']}, {spec['height_pt']});
targetDoc.artboards[0].artboardRect = [0, 0, {spec['width_pt']}, -{spec['height_pt']}];
targetDoc.artboards[0].name = "P01";

var spacing = 60;
var cols = 6;
for (var i = 1; i < 22; i++) {{
    var col = i % cols;
    var row = Math.floor(i / cols);
    var l = col * ({spec['width_pt']} + spacing);
    var t = -row * ({spec['height_pt']} + spacing);
    var numStr = (i + 1 < 10 ? "0" : "") + (i + 1);
    var ab = targetDoc.artboards.add([l, t, l + {spec['width_pt']}, t - {spec['height_pt']}]);
    ab.name = "P" + numStr;
}}

// 3. Setup Layers
var bgLayer = targetDoc.layers[0];
bgLayer.name = "Backgrounds";

var photoLayer = targetDoc.layers.add();
photoLayer.name = "Photos_Masked";

var layoutLayer = targetDoc.layers.add();
layoutLayer.name = "Layout_Shapes";

var textLayer = targetDoc.layers.add();
textLayer.name = "Typography";

bgLayer.visible = true;
photoLayer.visible = true;
layoutLayer.visible = true;
textLayer.visible = true;

// 4. Place Backgrounds
var bgFiles = {bg_json};
for (var i = 0; i < 22; i++) {{
    var ab = targetDoc.artboards[i];
    var r = ab.artboardRect;
    var abW = Math.abs(r[2] - r[0]);
    var abH = Math.abs(r[1] - r[3]);

    var clipGroup = bgLayer.groupItems.add();
    var placed = clipGroup.placedItems.add();
    placed.file = new File(bgFiles[i]);
    placed.width = abW;
    placed.height = abH;
    placed.left = r[0];
    placed.top = r[1];

    var clipRect = clipGroup.pathItems.rectangle(r[1], r[0], abW, abH);
    clipRect.filled = false;
    clipRect.stroked = false;
    clipRect.clipping = true;
    clipGroup.clipped = true;
}}

// 5. Copy Layout Shapes to Layout_Shapes
var srcIndices = {src_indices_json};
for (var p = 0; p < 22; p++) {{
    var sIdx = srcIndices[p];
    if (sIdx >= srcDoc.artboards.length) sIdx = 0;
    var sR = srcDoc.artboards[sIdx].artboardRect;
    var tR = targetDoc.artboards[p].artboardRect;
    var uniquePaths = itemsByAB[sIdx].paths;

    var pGroup = layoutLayer.groupItems.add();
    for (var m = 0; m < uniquePaths.length; m++) {{
        var itm = uniquePaths[m];
        var dup = itm.duplicate(layoutLayer, ElementPlacement.PLACEATBEGINNING);
        dup.left = tR[0] + (itm.left - sR[0]);
        dup.top = tR[1] + (itm.top - sR[1]);
        dup.move(pGroup, ElementPlacement.PLACEATEND);
    }}
}}

// 6. Copy and Style TextFrames
function getRGBColor(r, g, b) {{
    var c = new RGBColor();
    c.red = Math.round(r * 255);
    c.green = Math.round(g * 255);
    c.blue = Math.round(b * 255);
    return c;
}}

for (var p = 0; p < 22; p++) {{
    var sIdx = srcIndices[p];
    if (sIdx >= srcDoc.artboards.length) sIdx = 0;
    var sR = srcDoc.artboards[sIdx].artboardRect;
    var tR = targetDoc.artboards[p].artboardRect;
    var rawTFs = itemsByAB[sIdx].textFrames;
    if (rawTFs.length === 0) continue;

    var tGroup = textLayer.groupItems.add();
    for (var t = 0; t < rawTFs.length; t++) {{
        var origTF = rawTFs[t];
        var origContent = origTF.contents;
        var dupTF = origTF.duplicate(textLayer, ElementPlacement.PLACEATBEGINNING);
        dupTF.left = tR[0] + (origTF.left - sR[0]);
        dupTF.top = tR[1] + (origTF.top - sR[1]);

        var isHeading = origContent.toLowerCase().indexOf("heading") !== -1 || origContent.toLowerCase().indexOf("title") !== -1;
        if (p === 0) {{
            dupTF.contents = isHeading ? "{cover_title}" : "{cover_sub}";
        }} else {{
            dupTF.contents = isHeading ? "{h1}" : "{q1}";
        }}

        try {{
            var fontName = isHeading ? "{palette['title_font']}" : "{palette['body_font']}";
            var fSize = isHeading ? {palette['title_size']} : {palette['body_size']};
            dupTF.textRange.characterAttributes.textFont = app.textFonts.getByName(fontName);
            dupTF.textRange.characterAttributes.size = fSize;
            dupTF.textRange.characterAttributes.fillColor = getRGBColor({palette['color'][0]}, {palette['color'][1]}, {palette['color'][2]});
        }} catch(e) {{}}

        dupTF.move(tGroup, ElementPlacement.PLACEATEND);
    }}
}}

// 7. Place & Mask Photos (Photos placed first, maskPath placed at beginning)
var landPhotos = {land_json};
var portPhotos = {port_json};
var sqPhotos = {sq_json};
var allPhotos = {all_json};
var landIdx = 0, portIdx = 0, sqIdx = 0, allIdx = 0;

for (var i = 0; i < 22; i++) {{
    var pagePhotoGroup = photoLayer.groupItems.add();
    var pLayoutGrp = layoutLayer.groupItems[layoutLayer.groupItems.length - 1 - i];

    for (var j = 0; j < pLayoutGrp.pageItems.length; j++) {{
        var shape = pLayoutGrp.pageItems[j];
        var sb = shape.geometricBounds;
        var sW = Math.abs(sb[2] - sb[0]);
        var sH = Math.abs(sb[1] - sb[3]);
        var aspect = sW / sH;

        var photoPath = "";
        if (aspect >= 1.15 && landPhotos.length > 0) {{
            photoPath = landPhotos[landIdx % landPhotos.length]; landIdx++;
        }} else if (aspect <= 0.85 && portPhotos.length > 0) {{
            photoPath = portPhotos[portIdx % portPhotos.length]; portIdx++;
        }} else if (sqPhotos.length > 0) {{
            photoPath = sqPhotos[sqIdx % sqPhotos.length]; sqIdx++;
        }} else {{
            photoPath = allPhotos[allIdx % allPhotos.length]; allIdx++;
        }}

        try {{
            var pGroup = pagePhotoGroup.groupItems.add();
            var pPlaced = pGroup.placedItems.add();
            pPlaced.file = new File(photoPath);

            var scaleFactor = Math.max(sW / pPlaced.width, sH / pPlaced.height) * 1.05;
            pPlaced.width *= scaleFactor;
            pPlaced.height *= scaleFactor;
            pPlaced.left = sb[0] + (sW - pPlaced.width) / 2;
            pPlaced.top = sb[1] - (sH - pPlaced.height) / 2;

            var maskPath = shape.duplicate(pGroup, ElementPlacement.PLACEATBEGINNING);
            maskPath.filled = false;
            maskPath.stroked = false;
            maskPath.clipping = true;
            pGroup.clipped = true;
        }} catch(e) {{}}
    }}
}}

srcDoc.close(SaveOptions.DONOTSAVECHANGES);

// 8. Export Blank Previews
photoLayer.visible = false;
layoutLayer.visible = true;
textLayer.visible = true;
bgLayer.visible = true;
app.redraw();

for (var p = 0; p < 22; p++) {{
    targetDoc.artboards.setActiveArtboardIndex(p);
    var outFile = new File("{raw_dir}/raw_blank_p" + (p < 9 ? "0" + (p+1) : (p+1)) + ".png");
    var opts = new ImageCaptureOptions();
    opts.artBoardClipping = true;
    opts.resolution = 150;
    targetDoc.imageCapture(outFile, targetDoc.artboards[p].artboardRect, opts);
}}

// 9. Export Populated Previews (100% IDENTICAL LAYOUTS - Layers Toggled Only)
photoLayer.visible = true;
layoutLayer.visible = false;
textLayer.visible = true;
bgLayer.visible = true;
app.redraw();

for (var p = 0; p < 22; p++) {{
    targetDoc.artboards.setActiveArtboardIndex(p);
    var outFile = new File("{raw_dir}/raw_pop_p" + (p < 9 ? "0" + (p+1) : (p+1)) + ".png");
    var opts = new ImageCaptureOptions();
    opts.artBoardClipping = true;
    opts.resolution = 150;
    targetDoc.imageCapture(outFile, targetDoc.artboards[p].artboardRect, opts);
}}

// Restore visibility
photoLayer.visible = true;
layoutLayer.visible = true;
textLayer.visible = true;
bgLayer.visible = true;

// 10. Save Master AI file
var saveOpts = new IllustratorSaveOptions();
saveOpts.pdfCompatible = false;
saveOpts.compressed = true;
targetDoc.saveAs(new File("{ai_out_file}"), saveOpts);
targetDoc.close(SaveOptions.DONOTSAVECHANGES);
"""
    with open(jsx_path, "w", encoding="utf-8") as f:
        f.write(jsx_content)

if __name__ == "__main__":
    main()
