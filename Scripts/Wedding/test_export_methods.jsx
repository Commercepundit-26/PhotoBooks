app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.activeDocument;
var ab0 = doc.artboards[0];
var r = ab0.artboardRect;

// Method 1: doc.imageCapture
var f1 = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_export/method1_capture.png");
var capOpts = new ImageCaptureOptions();
capOpts.resolution = 72;
capOpts.antiAliasing = true;
capOpts.transparency = false;
doc.imageCapture(f1, r, capOpts);

// Method 2: ExportOptionsPNG24
var f2 = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_export/method2_png24.png");
var pngOpts = new ExportOptionsPNG24();
pngOpts.artBoardClipping = true;
pngOpts.antiAliasing = true;
pngOpts.saveMultipleArtboards = true;
pngOpts.artboardRange = "1";
doc.exportFile(f2, ExportType.PNG24, pngOpts);
