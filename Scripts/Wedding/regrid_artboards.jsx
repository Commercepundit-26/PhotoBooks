
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

// 1. Close extra untitled / duplicate documents
for (var d = app.documents.length - 1; d >= 0; d--) {
    var docItem = app.documents[d];
    if (docItem.name.indexOf("Untitled") !== -1) {
        docItem.close(SaveOptions.DONOTSAVECHANGES);
    }
}

var targetFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Photobook_3Sizes.ai");
var doc = null;
for (var d = 0; d < app.documents.length; d++) {
    if (app.documents[d].name.indexOf("Wedding_Photobook_3Sizes") !== -1) {
        doc = app.documents[d];
        break;
    }
}
if (!doc) {
    doc = app.open(targetFile);
}

// 2. Arrange 21 artboards in 7 Page Columns:
// Column Width: 950 pt, Column Spacing: 120 pt
// Top Row (Square): Y = 0 to -720
// Middle Row (Landscape): Y = -820 to -1396
// Bottom Row (Portrait): Y = -1496 to -2360

var colWidth = 950;
var colSpacing = 120;
var totalColStep = colWidth + colSpacing;

var bgNames = ["wed_p01", "wed_p06", "wed_p12", "wed_p15", "wed_p16", "wed_p17", "wed_p18"];

// Helper to move all items inside an old artboard rect to a new artboard rect
function moveItemsOnArtboard(oldRect, newRect) {
    var dx = newRect[0] - oldRect[0];
    var dy = newRect[1] - oldRect[1];

    for (var l = 0; l < doc.layers.length; l++) {
        var lyr = doc.layers[l];
        for (var k = 0; k < lyr.pageItems.length; k++) {
            var item = lyr.pageItems[k];
            var ib = item.geometricBounds;
            var cx = (ib[0] + ib[2]) / 2;
            var cy = (ib[1] + ib[3]) / 2;

            if (cx >= oldRect[0] && cx <= oldRect[2] && cy <= oldRect[1] && cy >= oldRect[3]) {
                item.left += dx;
                item.top += dy;
            }
        }
    }
}

// Position each page column
for (var p = 0; p < 7; p++) {
    var colX = p * totalColStep;
    var bgName = bgNames[p];

    // 1. Square Artboard (Index p)
    var abSq = doc.artboards[p];
    var oldSq = [abSq.artboardRect[0], abSq.artboardRect[1], abSq.artboardRect[2], abSq.artboardRect[3]];
    var sqLeft = colX + (colWidth - 720) / 2;
    var sqTop = 0;
    var newSq = [sqLeft, sqTop, sqLeft + 720, sqTop - 720];
    moveItemsOnArtboard(oldSq, newSq);
    abSq.artboardRect = newSq;
    abSq.name = "P0" + (p + 1) + "_Square_10x10_" + bgName;

    // 2. Landscape Artboard (Index 7 + p)
    var abLs = doc.artboards[7 + p];
    var oldLs = [abLs.artboardRect[0], abLs.artboardRect[1], abLs.artboardRect[2], abLs.artboardRect[3]];
    var lsLeft = colX + (colWidth - 864) / 2;
    var lsTop = -820;
    var newLs = [lsLeft, lsTop, lsLeft + 864, lsTop - 576];
    moveItemsOnArtboard(oldLs, newLs);
    abLs.artboardRect = newLs;
    abLs.name = "P0" + (p + 1) + "_Landscape_12x8_" + bgName;

    // 3. Portrait Artboard (Index 14 + p)
    var abPt = doc.artboards[14 + p];
    var oldPt = [abPt.artboardRect[0], abPt.artboardRect[1], abPt.artboardRect[2], abPt.artboardRect[3]];
    var ptLeft = colX + (colWidth - 576) / 2;
    var ptTop = -1496;
    var newPt = [ptLeft, ptTop, ptLeft + 576, ptTop - 864];
    moveItemsOnArtboard(oldPt, newPt);
    abPt.artboardRect = newPt;
    abPt.name = "P0" + (p + 1) + "_Portrait_8x12_" + bgName;
}

doc.save();
