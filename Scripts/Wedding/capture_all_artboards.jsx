
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.activeDocument;
var rawFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Raw_Captures");

var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

var layoutLayer = doc.layers.getByName("Layout_Shapes");

// 1. CAPTURE 21 BLANK ARTBOARDS (Photo groups hidden)
for (var g = 0; g < layoutLayer.groupItems.length; g++) {
    layoutLayer.groupItems[g].hidden = true;
}
app.redraw();

for (var i = 0; i < doc.artboards.length; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/blank_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}

// 2. CAPTURE 21 POPULATED ARTBOARDS (Photo groups visible)
for (var g = 0; g < layoutLayer.groupItems.length; g++) {
    layoutLayer.groupItems[g].hidden = false;
}
app.redraw();

for (var i = 0; i < doc.artboards.length; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/pop_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}
