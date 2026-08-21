app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.activeDocument;
var testFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_export");

var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

// Test Artboard 0 (Square)
var r0 = doc.artboards[0].artboardRect;
var f0 = new File(testFolder.fsName + "/test_sq.png");
doc.imageCapture(f0, r0, capOpts);

// Test Artboard 7 (Landscape)
var r7 = doc.artboards[7].artboardRect;
var f7 = new File(testFolder.fsName + "/test_ls.png");
doc.imageCapture(f7, r7, capOpts);

// Test Artboard 14 (Portrait)
var r14 = doc.artboards[14].artboardRect;
var f14 = new File(testFolder.fsName + "/test_pt.png");
doc.imageCapture(f14, r14, capOpts);
