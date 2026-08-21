var doc = app.activeDocument;
var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 90;
exportOpts.artboardClipping = true;

var destFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Blank_Layouts_Raw/preview.jpg");
doc.exportFile(destFile, ExportType.JPEG, exportOpts);
