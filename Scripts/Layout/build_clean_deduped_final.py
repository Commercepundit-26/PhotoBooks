#!/usr/bin/env python3
import os
import sys
import subprocess

sys.stdout.reconfigure(line_buffering=True)

LAYOUT_DIR = "/Users/cp/Ronak/CC/Photobooks/Layout"
FILE_INPUT = os.path.join(LAYOUT_DIR, "Final Layouts.ai")
FILE_TARGET = os.path.join(LAYOUT_DIR, "Final Layouts.ai")

print("="*80)
print("COMPREHENSIVE DE-DUPLICATION & CLEANUP OF FINAL LAYOUTS.AI")
print("="*80)

jsx_code = f"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

// 1. Open Source Document
var srcDoc = app.open(new File("{FILE_INPUT}"));

// Recursive helper to extract all leaf paths & compound paths
function getAllLeafPaths(container, out) {{
    for (var i = 0; i < container.pathItems.length; i++) {{
        var pi = container.pathItems[i];
        if (!pi.guides && !pi.clipping) out.push(pi);
    }}
    for (var i = 0; i < container.compoundPathItems.length; i++) {{
        var cpi = container.compoundPathItems[i];
        if (!cpi.guides && !cpi.clipping) out.push(cpi);
    }}
    for (var g = 0; g < container.groupItems.length; g++) {{
        getAllLeafPaths(container.groupItems[g], out);
    }}
}}

var allDocPaths = [];
getAllLeafPaths(srcDoc, allDocPaths);

// 2. Identify Non-Empty Artboards and Extract UNIQUE Paths only
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

    var abPaths = [];
    for (var k = 0; k < allDocPaths.length; k++) {{
        var it = allDocPaths[k];
        var ib = it.geometricBounds;
        var cx = (ib[0] + ib[2]) / 2;
        var cy = (ib[1] + ib[3]) / 2;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {{
            var pw = Math.abs(ib[2] - ib[0]);
            var ph = Math.abs(ib[1] - ib[3]);
            if (pw > 15 && ph > 15) {{
                abPaths.push(it);
            }}
        }}
    }}

    // De-duplicate paths strictly by geometric bounds (tolerance 0.5pt)
    var uniquePaths = [];
    for (var i = 0; i < abPaths.length; i++) {{
        var pi = abPaths[i];
        var pb = pi.geometricBounds;
        var isDup = false;
        for (var u = 0; u < uniquePaths.length; u++) {{
            var ub = uniquePaths[u].geometricBounds;
            if (Math.abs(pb[0] - ub[0]) < 0.5 &&
                Math.abs(pb[1] - ub[1]) < 0.5 &&
                Math.abs(pb[2] - ub[2]) < 0.5 &&
                Math.abs(pb[3] - ub[3]) < 0.5) {{
                isDup = true;
                break;
            }}
        }}
        if (!isDup) {{
            uniquePaths.push(pi);
        }}
    }}

    if (uniquePaths.length > 0) {{
        var entry = {{
            origIndex: a,
            origName: ab.name,
            rect: ar,
            width: w,
            height: h,
            paths: uniquePaths
        }};
        if (orientation === "Square") validSquare.push(entry);
        else if (orientation === "Landscape") validLandscape.push(entry);
        else validPortrait.push(entry);
    }}
}}

// 3. Create Fresh Target Master Document
var targetDoc = app.documents.add(DocumentColorSpace.RGB, 720, 720);

// Setup 3 Clean Layers
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

// Helper to duplicate ONLY unique paths into target group
function copyUniquePaths(entry, targetABIdx, targetLayer, groupName, targetW, targetH) {{
    var paths = entry.paths;
    var sR = entry.rect;
    var tR = targetDoc.artboards[targetABIdx].artboardRect;

    var sW = sR[2] - sR[0];
    var sH = sR[1] - sR[3];

    var scaleX = targetW / sW;
    var scaleY = targetH / sH;

    var pGroup = targetLayer.groupItems.add();
    pGroup.name = groupName;

    for (var m = 0; m < paths.length; m++) {{
        var itm = paths[m];
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
        dup.move(pGroup, ElementPlacement.PLACEATEND);
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

    copyUniquePaths(validSquare[i], i, layerSquare, "Square_P" + numStr, sqW, sqH);
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

    copyUniquePaths(validLandscape[i], targetABIdx, layerLandscape, "Landscape_P" + numStr, lsW, lsH);
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

    copyUniquePaths(validPortrait[i], targetABIdx, layerPortrait, "Portrait_P" + numStr, ptW, ptH);
}}

// 4. Save Final Master Document over original
var targetFile = new File("{FILE_TARGET}");
var saveOpts = new IllustratorSaveOptions();
saveOpts.pdfCompatible = false;
saveOpts.compressed = true;
targetDoc.saveAs(targetFile, saveOpts);

// Close documents
targetDoc.close(SaveOptions.DONOTSAVECHANGES);
srcDoc.close(SaveOptions.DONOTSAVECHANGES);
"""

jsx_file = os.path.join(LAYOUT_DIR, "execute_dedup.jsx")
with open(jsx_file, "w") as f:
    f.write(jsx_code)

print("Executing comprehensive de-duplication in Adobe Illustrator...")
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
print(f"✓ Successfully saved de-duplicated Final Master Layouts Document: {FILE_TARGET}")
