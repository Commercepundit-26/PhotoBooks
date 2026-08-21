app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.activeDocument;
var layoutLayer = doc.layers.getByName("Layout_Shapes");

// Hide all photo groups
for (var g = 0; g < layoutLayer.groupItems.length; g++) {
    layoutLayer.groupItems[g].hidden = true;
}
app.redraw();

var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

var r0 = doc.artboards[0].artboardRect;
var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_export/test_blank_p01_fixed.png");
doc.imageCapture(f, r0, capOpts);

// Unhide photo groups
for (var g = 0; g < layoutLayer.groupItems.length; g++) {
    layoutLayer.groupItems[g].hidden = false;
}
app.redraw();
