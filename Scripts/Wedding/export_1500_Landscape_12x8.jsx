
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.open(new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Landscape_12x8.ai"));

var rawFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Landscape_12x8/Raw_1500");
var capOpts = new ImageCaptureOptions();
capOpts.resolution = 125;
capOpts.antiAliasing = true;
capOpts.transparency = false;

var layoutLayer = doc.layers.getByName("Layout_Shapes");

// 1. Capture 22 Blank Artboards (Photos Hidden, Layout Shapes Visible)
for (var i = 0; i < layoutLayer.groupItems.length; i++) {
    var grp = layoutLayer.groupItems[i];
    if (grp.name.indexOf("Photos_Page") !== -1) {
        grp.hidden = true;
    } else if (grp.name.indexOf("Layout_P") !== -1) {
        grp.hidden = false;
    }
}
app.redraw();

for (var i = 0; i < doc.artboards.length; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/blank_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}

// 2. Capture 22 Populated Artboards (Photos Visible, Layout Shapes Hidden)
for (var i = 0; i < layoutLayer.groupItems.length; i++) {
    var grp = layoutLayer.groupItems[i];
    if (grp.name.indexOf("Photos_Page") !== -1) {
        grp.hidden = false;
    } else if (grp.name.indexOf("Layout_P") !== -1) {
        grp.hidden = true;
    }
}
app.redraw();

for (var i = 0; i < doc.artboards.length; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/pop_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}

// Restore visibility and close
for (var i = 0; i < layoutLayer.groupItems.length; i++) {
    layoutLayer.groupItems[i].hidden = false;
}
doc.close(SaveOptions.DONOTSAVECHANGES);
