app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.activeDocument;
var photoLayer = doc.layers.getByName("Photos_Masked");
photoLayer.visible = false;
app.redraw();

var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

var r0 = doc.artboards[0].artboardRect;
var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_export/test_blank_p01.png");
doc.imageCapture(f, r0, capOpts);

photoLayer.visible = true;
app.redraw();
