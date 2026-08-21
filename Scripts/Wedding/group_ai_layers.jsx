app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var aiFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Photobook_3Sizes.ai");
var doc = null;
for (var d = 0; d < app.documents.length; d++) {
    if (app.documents[d].name.indexOf("Wedding_Photobook_3Sizes") !== -1) {
        doc = app.documents[d];
        break;
    }
}
if (!doc) {
    doc = app.open(aiFile);
}

var layoutLayer = null;
try { layoutLayer = doc.layers.getByName("Layout_Shapes"); } catch(e) {}
var bgLayer = null;
try { bgLayer = doc.layers.getByName("Backgrounds"); } catch(e) {}

// Group elements by artboard
for (var a = 0; a < doc.artboards.length; a++) {
    var ab = doc.artboards[a];
    var abName = ab.name;
    var r = ab.artboardRect;

    // Group layout shapes for this artboard
    if (layoutLayer) {
        var abLayoutGroup = layoutLayer.groupItems.add();
        abLayoutGroup.name = "Layout_" + abName;

        for (var p = layoutLayer.pathItems.length - 1; p >= 0; p--) {
            var pi = layoutLayer.pathItems[p];
            if (pi.parent == abLayoutGroup) continue;
            var gb = pi.geometricBounds;
            var cx = (gb[0] + gb[2]) / 2;
            var cy = (gb[1] + gb[3]) / 2;
            if (cx >= r[0] && cx <= r[2] && cy <= r[1] && cy >= r[3]) {
                pi.moveToBeginning(abLayoutGroup);
            }
        }

        for (var g = layoutLayer.groupItems.length - 1; g >= 0; g--) {
            var grp = layoutLayer.groupItems[g];
            if (grp == abLayoutGroup || grp.parent == abLayoutGroup) continue;
            var gb = grp.geometricBounds;
            var cx = (gb[0] + gb[2]) / 2;
            var cy = (gb[1] + gb[3]) / 2;
            if (cx >= r[0] && cx <= r[2] && cy <= r[1] && cy >= r[3]) {
                grp.moveToBeginning(abLayoutGroup);
            }
        }
    }

    // Group background for this artboard
    if (bgLayer) {
        for (var g = 0; g < bgLayer.groupItems.length; g++) {
            var bgGrp = bgLayer.groupItems[g];
            var gb = bgGrp.geometricBounds;
            var cx = (gb[0] + gb[2]) / 2;
            var cy = (gb[1] + gb[3]) / 2;
            if (cx >= r[0] && cx <= r[2] && cy <= r[1] && cy >= r[3]) {
                bgGrp.name = "Background_" + abName;
            }
        }
    }
}

doc.saveAs(aiFile);
