app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var aiFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Photobook_3Sizes.ai");
var doc = app.open(aiFile);

var testFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_export");
if (!testFolder.exists) testFolder.create();

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 90;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;
exportOpts.artboardRange = "1";

var testFile = new File(testFolder.fsName + "/page1.jpg");
doc.exportFile(testFile, ExportType.JPEG, exportOpts);
