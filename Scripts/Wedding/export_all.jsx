var doc = app.activeDocument;
var outFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Blank_Layouts_All");
if (!outFolder.exists) outFolder.create();

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 85;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;

var destFile = new File(outFolder.fsName + "/layout.jpg");
doc.exportFile(destFile, ExportType.JPEG, exportOpts);
