var doc = app.activeDocument;
var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 90;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;
exportOpts.artboardRange = "1";

var destFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/test_ab1.jpg");
doc.exportFile(destFile, ExportType.JPEG, exportOpts);
