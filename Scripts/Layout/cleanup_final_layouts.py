#!/usr/bin/env python3
import os
import sys
import subprocess

sys.stdout.reconfigure(line_buffering=True)

LAYOUT_DIR = "/Users/cp/Ronak/CC/Photobooks/Layout"
FILE_INPUT = os.path.join(LAYOUT_DIR, "Final Layouts.ai")
FILE_BACKUP = os.path.join(LAYOUT_DIR, "Final Layouts_backup.ai")

print("="*80)
print("REMOVING EMPTY ARTBOARDS & REORGANIZING FINAL LAYOUTS.AI")
print("="*80)

jsx_code = f"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

// 1. Open User-Edited Final Layouts.ai
var srcDoc = app.open(new File("{FILE_INPUT}"));

// 2. Identify Non-Empty Artboards and their items
var validSquare = [];
var validLandscape = [];
var validPortrait = [];

for (var a = 0; a < srcDoc.artboards.length; a++) {{
    var ab = srcDoc.artboards[a];
    var ar = ab.artboardRect;
    var w = Math.round(ar[2] - ar[0]);
    var h = Math.round(ar[1] - ar[3]);
    var orientation = "Square";
    if (w > h) orientation = "Landscape";
    else if (h > w) orientation = "Portrait";

    var items = [];
    for (var k = 0; k < srcDoc.pageItems.length; k++) {{
        var it = srcDoc.pageItems[k];
        if (it.guides || it.clipping) continue;
        var ib = it.geometricBounds;
        var cx = (ib[0] + ib[2]) / 2;
        var cy = (ib[1] + ib[3]) / 2;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {{
            items.push(it);
        }}
    }}

    if (items.length > 0) {{
        var entry = {{
            origIndex: a,
            origName: ab.name,
            rect: ar,
            width: w,
            height: h,
            items: items
        }};
        if (orientation === "Square") validSquare.push(entry);
        else if (orientation === "Landscape") validLandscape.push(entry);
        else validPortrait.push(entry);
    }}
}}

// 3. Create Clean Master Target Document
var targetDoc = app.documents.add(DocumentColorSpace.RGB, 720, 720);

// Setup 3 Layers
var layerSquare = targetDoc.layers[0];
layerSquare.name = "Square_10x10_Layouts";

var layerLandscape = targetDoc.layers.add();
layerLandscape.name = "Landscape_12x8_Layouts";

var layerPortrait = targetDoc.layers.add();
layerPortrait.name = "Portrait_8x12_Layouts";

var spacing = 50;
var sectionGap = 250;
var cols = 6;
var topStart = 3800;

// Helper to copy content to target artboard
function copyItemsToTarget(entry, targetABIdx, targetLayer, groupName, targetW, targetH) {{
    var items = entry.items;
    var sR = entry.rect;
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
// ==========================================
var sqW = 720;
var sqH = 720;
var sqLeftStart = -6500;

for (var i = 0; i < validSquare.length; i++) {{
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

    copyItemsToTarget(validSquare[i], i, layerSquare, "Square_P" + numStr, sqW, sqH);
}}

var sqSectionWidth = cols * sqW + (cols - 1) * spacing;

// ==========================================
// SECTION 2: LANDSCAPE LAYOUTS (864x576 pt)
// ==========================================
var lsW = 864;
var lsH = 576;
var lsLeftOffset = sqLeftStart + sqSectionWidth + sectionGap;
var lsStartABIndex = validSquare.length;

for (var i = 0; i < validLandscape.length; i++) {{
    var col = i % cols;
    var row = Math.floor(i / cols);
    var l = lsLeftOffset + col * (lsW + spacing);
    var t = topStart - row * (lsH + spacing);

    var numStr = (i + 1 < 10 ? "0" : "") + (i + 1);
    var abName = "Landscape_Layout_" + numStr;

    var targetABIdx = lsStartABIndex + i;
    var ab = targetDoc.artboards.add([l, t, l + lsW, t - lsH]);
    ab.name = abName;

    copyItemsToTarget(validLandscape[i], targetABIdx, layerLandscape, "Landscape_P" + numStr, lsW, lsH);
}}

var lsSectionWidth = cols * lsW + (cols - 1) * spacing;

// ==========================================
// SECTION 3: PORTRAIT LAYOUTS (576x864 pt)
// ==========================================
var ptW = 576;
var ptH = 864;
var ptLeftOffset = lsLeftOffset + lsSectionWidth + sectionGap;
var ptStartABIndex = validSquare.length + validLandscape.length;

for (var i = 0; i < validPortrait.length; i++) {{
    var col = i % cols;
    var row = Math.floor(i / cols);
    var l = ptLeftOffset + col * (ptW + spacing);
    var t = topStart - row * (ptH + spacing);

    var numStr = (i + 1 < 10 ? "0" : "") + (i + 1);
    var abName = "Portrait_Layout_" + numStr;

    var targetABIdx = ptStartABIndex + i;
    var ab = targetDoc.artboards.add([l, t, l + ptW, t - ptH]);
    ab.name = abName;

    copyItemsToTarget(validPortrait[i], targetABIdx, layerPortrait, "Portrait_P" + numStr, ptW, ptH);
}}

// 4. Save Final Master Document over original
var targetFile = new File("{FILE_INPUT}");
var saveOpts = new IllustratorSaveOptions();
saveOpts.pdfCompatible = false;
saveOpts.compressed = true;
targetDoc.saveAs(targetFile, saveOpts);

// Close documents
targetDoc.close(SaveOptions.DONOTSAVECHANGES);
srcDoc.close(SaveOptions.DONOTSAVECHANGES);
"""

jsx_file = os.path.join(LAYOUT_DIR, "execute_cleanup.jsx")
with open(jsx_file, "w") as f:
    f.write(jsx_code)

print("Executing cleanup in Adobe Illustrator...")
as_cmd = f'''with timeout of 1800 seconds
    tell application "Adobe Illustrator"
        do javascript file "{jsx_file}"
    end tell
end timeout'''

res = subprocess.run(["osascript", "-e", as_cmd], capture_output=True, text=True)

if res.returncode != 0:
    print(f"Error: {res.stderr}")
    sys.exit(1)

os.remove(jsx_file)
if os.path.exists(FILE_BACKUP):
    os.remove(FILE_BACKUP)

print(f"✓ Cleaned and saved Final Master Layouts Document: {FILE_INPUT}")
