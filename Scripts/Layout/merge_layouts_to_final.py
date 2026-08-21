#!/usr/bin/env python3
import os
import sys
import json
import subprocess

sys.stdout.reconfigure(line_buffering=True)

LAYOUTS_DIR = "/Users/cp/Ronak/CC/Photobooks/Layout"
FILE_LAYOUTS = os.path.join(LAYOUTS_DIR, "Layouts.ai")
FILE_UNIQUE = os.path.join(LAYOUTS_DIR, "Unique shape Layouts.ai")
FILE_TARGET = os.path.join(LAYOUTS_DIR, "Final Layouts.ai")

print("="*80)
print("MERGING LAYOUTS.AI AND UNIQUE SHAPE LAYOUTS.AI INTO FINAL LAYOUTS.AI")
print("="*80)

if os.path.exists(FILE_TARGET):
    os.remove(FILE_TARGET)

# Define source artboards to include in each category
square_sources = [
    # 25 from Layouts.ai
    [FILE_LAYOUTS, 0], [FILE_LAYOUTS, 3], [FILE_LAYOUTS, 4], [FILE_LAYOUTS, 5], [FILE_LAYOUTS, 6],
    [FILE_LAYOUTS, 7], [FILE_LAYOUTS, 8], [FILE_LAYOUTS, 9], [FILE_LAYOUTS, 10], [FILE_LAYOUTS, 11],
    [FILE_LAYOUTS, 12], [FILE_LAYOUTS, 13], [FILE_LAYOUTS, 14], [FILE_LAYOUTS, 15], [FILE_LAYOUTS, 16],
    [FILE_LAYOUTS, 17], [FILE_LAYOUTS, 18], [FILE_LAYOUTS, 19], [FILE_LAYOUTS, 20], [FILE_LAYOUTS, 21],
    [FILE_LAYOUTS, 22], [FILE_LAYOUTS, 23], [FILE_LAYOUTS, 24], [FILE_LAYOUTS, 47], [FILE_LAYOUTS, 48],
    # 26 from Unique shape Layouts.ai
    [FILE_UNIQUE, 0], [FILE_UNIQUE, 1], [FILE_UNIQUE, 2], [FILE_UNIQUE, 3], [FILE_UNIQUE, 4],
    [FILE_UNIQUE, 5], [FILE_UNIQUE, 6], [FILE_UNIQUE, 7], [FILE_UNIQUE, 8], [FILE_UNIQUE, 9],
    [FILE_UNIQUE, 10], [FILE_UNIQUE, 11], [FILE_UNIQUE, 12], [FILE_UNIQUE, 13], [FILE_UNIQUE, 14],
    [FILE_UNIQUE, 15], [FILE_UNIQUE, 16], [FILE_UNIQUE, 17], [FILE_UNIQUE, 18], [FILE_UNIQUE, 19],
    [FILE_UNIQUE, 20], [FILE_UNIQUE, 21], [FILE_UNIQUE, 22], [FILE_UNIQUE, 23], [FILE_UNIQUE, 24],
    [FILE_UNIQUE, 57]
]

landscape_sources = [
    # 25 from Layouts.ai
    [FILE_LAYOUTS, 2], [FILE_LAYOUTS, 51], [FILE_LAYOUTS, 52], [FILE_LAYOUTS, 53], [FILE_LAYOUTS, 54],
    [FILE_LAYOUTS, 55], [FILE_LAYOUTS, 56], [FILE_LAYOUTS, 57], [FILE_LAYOUTS, 58], [FILE_LAYOUTS, 59],
    [FILE_LAYOUTS, 60], [FILE_LAYOUTS, 61], [FILE_LAYOUTS, 62], [FILE_LAYOUTS, 63], [FILE_LAYOUTS, 64],
    [FILE_LAYOUTS, 65], [FILE_LAYOUTS, 66], [FILE_LAYOUTS, 67], [FILE_LAYOUTS, 68], [FILE_LAYOUTS, 69],
    [FILE_LAYOUTS, 70], [FILE_LAYOUTS, 71], [FILE_LAYOUTS, 72], [FILE_LAYOUTS, 73], [FILE_LAYOUTS, 74],
    # 21 from Unique shape Layouts.ai
    [FILE_UNIQUE, 26], [FILE_UNIQUE, 27], [FILE_UNIQUE, 41], [FILE_UNIQUE, 42], [FILE_UNIQUE, 43],
    [FILE_UNIQUE, 44], [FILE_UNIQUE, 45], [FILE_UNIQUE, 46], [FILE_UNIQUE, 47], [FILE_UNIQUE, 48],
    [FILE_UNIQUE, 49], [FILE_UNIQUE, 50], [FILE_UNIQUE, 51], [FILE_UNIQUE, 52], [FILE_UNIQUE, 53],
    [FILE_UNIQUE, 54], [FILE_UNIQUE, 55], [FILE_UNIQUE, 56], [FILE_UNIQUE, 59], [FILE_UNIQUE, 61],
    [FILE_UNIQUE, 62]
]

portrait_sources = [
    # 25 from Layouts.ai
    [FILE_LAYOUTS, 1], [FILE_LAYOUTS, 25], [FILE_LAYOUTS, 26], [FILE_LAYOUTS, 27], [FILE_LAYOUTS, 28],
    [FILE_LAYOUTS, 29], [FILE_LAYOUTS, 30], [FILE_LAYOUTS, 31], [FILE_LAYOUTS, 32], [FILE_LAYOUTS, 33],
    [FILE_LAYOUTS, 34], [FILE_LAYOUTS, 35], [FILE_LAYOUTS, 36], [FILE_LAYOUTS, 37], [FILE_LAYOUTS, 38],
    [FILE_LAYOUTS, 39], [FILE_LAYOUTS, 40], [FILE_LAYOUTS, 41], [FILE_LAYOUTS, 42], [FILE_LAYOUTS, 43],
    [FILE_LAYOUTS, 44], [FILE_LAYOUTS, 45], [FILE_LAYOUTS, 46], [FILE_LAYOUTS, 49], [FILE_LAYOUTS, 50],
    # 16 from Unique shape Layouts.ai
    [FILE_UNIQUE, 25], [FILE_UNIQUE, 28], [FILE_UNIQUE, 29], [FILE_UNIQUE, 30], [FILE_UNIQUE, 31],
    [FILE_UNIQUE, 32], [FILE_UNIQUE, 33], [FILE_UNIQUE, 34], [FILE_UNIQUE, 35], [FILE_UNIQUE, 36],
    [FILE_UNIQUE, 37], [FILE_UNIQUE, 38], [FILE_UNIQUE, 39], [FILE_UNIQUE, 40], [FILE_UNIQUE, 58],
    [FILE_UNIQUE, 60]
]

print(f"Total Square Layouts:    {len(square_sources)}")
print(f"Total Landscape Layouts: {len(landscape_sources)}")
print(f"Total Portrait Layouts:  {len(portrait_sources)}")
print(f"Grand Total:             {len(square_sources) + len(landscape_sources) + len(portrait_sources)} Artboards")

sq_json = json.dumps(square_sources)
ls_json = json.dumps(landscape_sources)
pt_json = json.dumps(portrait_sources)

jsx_code = f"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

// 1. Open Both Source Documents
var docLayouts = app.open(new File("{FILE_LAYOUTS}"));
var docUnique  = app.open(new File("{FILE_UNIQUE}"));

// Index items for docLayouts
var itemsByAB_Layouts = [];
for (var a = 0; a < docLayouts.artboards.length; a++) itemsByAB_Layouts.push([]);
for (var k = 0; k < docLayouts.pageItems.length; k++) {{
    var it = docLayouts.pageItems[k];
    if (it.guides || it.clipping) continue;
    var ib = it.geometricBounds;
    var cx = (ib[0] + ib[2]) / 2;
    var cy = (ib[1] + ib[3]) / 2;
    for (var a = 0; a < docLayouts.artboards.length; a++) {{
        var ar = docLayouts.artboards[a].artboardRect;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {{
            itemsByAB_Layouts[a].push(it);
            break;
        }}
    }}
}}

// Index items for docUnique
var itemsByAB_Unique = [];
for (var a = 0; a < docUnique.artboards.length; a++) itemsByAB_Unique.push([]);
for (var k = 0; k < docUnique.pageItems.length; k++) {{
    var it = docUnique.pageItems[k];
    if (it.guides || it.clipping) continue;
    var ib = it.geometricBounds;
    var cx = (ib[0] + ib[2]) / 2;
    var cy = (ib[1] + ib[3]) / 2;
    for (var a = 0; a < docUnique.artboards.length; a++) {{
        var ar = docUnique.artboards[a].artboardRect;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {{
            itemsByAB_Unique[a].push(it);
            break;
        }}
    }}
}}

// 2. Create Target Master Document
var targetDoc = app.documents.add(DocumentColorSpace.RGB, 720, 720);

// Setup 3 Layers
var layerSquare = targetDoc.layers[0];
layerSquare.name = "Square_10x10_Layouts";

var layerLandscape = targetDoc.layers.add();
layerLandscape.name = "Landscape_12x8_Layouts";

var layerPortrait = targetDoc.layers.add();
layerPortrait.name = "Portrait_8x12_Layouts";

// Spacing definitions
var spacing = 50;
var sectionGap = 250;
var cols = 6;
var topStart = 3800;

// Helper to copy artboard items
function copyArtboardContent(srcDocPath, srcABIdx, targetABIdx, targetLayer, groupName, targetW, targetH) {{
    var isLayouts = (srcDocPath.indexOf("Layouts.ai") !== -1 && srcDocPath.indexOf("Unique") === -1);
    var srcDoc = isLayouts ? docLayouts : docUnique;
    var items = isLayouts ? itemsByAB_Layouts[srcABIdx] : itemsByAB_Unique[srcABIdx];
    var sR = srcDoc.artboards[srcABIdx].artboardRect;
    var tR = targetDoc.artboards[targetABIdx].artboardRect;

    var sW = sR[2] - sR[0];
    var sH = sR[1] - sR[3];

    var scaleX = targetW / sW;
    var scaleY = targetH / sH;

    var pGroup = targetLayer.groupItems.add();
    pGroup.name = groupName;

    for (var m = 0; m < items.length; m++) {{
        var itm = items[m];
        var dup = itm.duplicate(targetLayer, ElementPlacement.PLACEATBEGINNING);
        
        if (Math.abs(sW - targetW) < 1 && Math.abs(sH - targetH) < 1) {{
            dup.left = tR[0] + (itm.left - sR[0]);
            dup.top = tR[1] + (itm.top - sR[1]);
        }} else {{
            dup.left = tR[0] + (itm.left - sR[0]) * scaleX;
            dup.top = tR[1] + (itm.top - sR[1]) * scaleY;
            dup.width = itm.width * scaleX;
            dup.height = itm.height * scaleY;
        }}
        dup.move(pGroup, ElementPlacement.PLACEATBEGINNING);
    }}
}}

// ==========================================
// SECTION 1: SQUARE LAYOUTS (720x720 pt)
// X: -6500 to -1930
// ==========================================
var sqW = 720;
var sqH = 720;
var sqSources = {sq_json};
var sqLeftStart = -6500;

for (var i = 0; i < sqSources.length; i++) {{
    var col = i % cols;
    var row = Math.floor(i / cols);
    var l = sqLeftStart + col * (sqW + spacing);
    var t = topStart - row * (sqH + spacing);

    var numStr = (i + 1 < 10 ? "0" : "") + (i + 1);
    var abName = "Square_Layout_" + numStr;

    if (i === 0) {{
        targetDoc.artboards[0].artboardRect = [l, t, l + sqW, t - sqH];
        targetDoc.artboards[0].name = abName;
    }} else {{
        var ab = targetDoc.artboards.add([l, t, l + sqW, t - sqH]);
        ab.name = abName;
    }}

    copyArtboardContent(sqSources[i][0], sqSources[i][1], i, layerSquare, "Square_P" + numStr, sqW, sqH);
}}

var sqSectionWidth = cols * sqW + (cols - 1) * spacing;

// ==========================================
// SECTION 2: LANDSCAPE LAYOUTS (864x576 pt)
// X: -1680 to 3804
// ==========================================
var lsW = 864;
var lsH = 576;
var lsSources = {ls_json};
var lsLeftOffset = sqLeftStart + sqSectionWidth + sectionGap;
var lsStartABIndex = sqSources.length;

for (var i = 0; i < lsSources.length; i++) {{
    var col = i % cols;
    var row = Math.floor(i / cols);
    var l = lsLeftOffset + col * (lsW + spacing);
    var t = topStart - row * (lsH + spacing);

    var numStr = (i + 1 < 10 ? "0" : "") + (i + 1);
    var abName = "Landscape_Layout_" + numStr;

    var targetABIdx = lsStartABIndex + i;
    var ab = targetDoc.artboards.add([l, t, l + lsW, t - lsH]);
    ab.name = abName;

    copyArtboardContent(lsSources[i][0], lsSources[i][1], targetABIdx, layerLandscape, "Landscape_P" + numStr, lsW, lsH);
}}

var lsSectionWidth = cols * lsW + (cols - 1) * spacing;

// ==========================================
// SECTION 3: PORTRAIT LAYOUTS (576x864 pt)
// X: 4054 to 7760
// ==========================================
var ptW = 576;
var ptH = 864;
var ptSources = {pt_json};
var ptLeftOffset = lsLeftOffset + lsSectionWidth + sectionGap;
var ptStartABIndex = sqSources.length + lsSources.length;

for (var i = 0; i < ptSources.length; i++) {{
    var col = i % cols;
    var row = Math.floor(i / cols);
    var l = ptLeftOffset + col * (ptW + spacing);
    var t = topStart - row * (ptH + spacing);

    var numStr = (i + 1 < 10 ? "0" : "") + (i + 1);
    var abName = "Portrait_Layout_" + numStr;

    var targetABIdx = ptStartABIndex + i;
    var ab = targetDoc.artboards.add([l, t, l + ptW, t - ptH]);
    ab.name = abName;

    copyArtboardContent(ptSources[i][0], ptSources[i][1], targetABIdx, layerPortrait, "Portrait_P" + numStr, ptW, ptH);
}}

// 4. Save Final Master Document
var targetFile = new File("{FILE_TARGET}");
var saveOpts = new IllustratorSaveOptions();
saveOpts.pdfCompatible = false;
saveOpts.compressed = true;
targetDoc.saveAs(targetFile, saveOpts);

// Close all documents
targetDoc.close(SaveOptions.DONOTSAVECHANGES);
docLayouts.close(SaveOptions.DONOTSAVECHANGES);
docUnique.close(SaveOptions.DONOTSAVECHANGES);
"""

jsx_file = os.path.join(LAYOUTS_DIR, "execute_merge.jsx")
with open(jsx_file, "w") as f:
    f.write(jsx_code)

print("Executing merge in Adobe Illustrator...")
as_cmd = f'''with timeout of 1800 seconds
    tell application "Adobe Illustrator"
        do javascript file "{jsx_file}"
    end tell
end timeout'''

res = subprocess.run(["osascript", "-e", as_cmd], capture_output=True, text=True)

if res.returncode != 0:
    print(f"Error: {res.stderr}")
    sys.exit(1)

print(f"✓ Saved Final Master Layouts Document: {FILE_TARGET}")
