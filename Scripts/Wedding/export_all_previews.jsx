app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var aiFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Photobook_3Sizes.ai");
var doc = null;
for (var d = 0; d < app.documents.length; d++) {
    if (app.documents[d].name.indexOf("Wedding_Photobook_3Sizes") !== -1) {
        doc = app.documents[d];
        break;
    }
}
if (!doc) {
    doc = app.open(aiFile);
}

var rawBlankFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Raw_Blank");
if (!rawBlankFolder.exists) rawBlankFolder.create();

var rawPopFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Raw_Populated");
if (!rawPopFolder.exists) rawPopFolder.create();

var photoLayer = null;
try {
    photoLayer = doc.layers.getByName("Photos_Masked");
} catch(e) {}

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 88;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;

// 1. Export Blank Layout Previews (Hide Photos)
if (photoLayer) photoLayer.visible = false;

for (var a = 0; a < doc.artboards.length; a++) {
    doc.artboards.setActiveArtboardIndex(a);
    exportOpts.artboardRange = (a + 1).toString();
    var abFile = new File(rawBlankFolder.fsName + "/blank_ab" + (a + 1 < 10 ? "0" : "") + (a + 1) + ".jpg");
    doc.exportFile(abFile, ExportType.JPEG, exportOpts);
}

// 2. Export Populated Previews (Show Photos)
if (photoLayer) photoLayer.visible = true;

for (var a = 0; a < doc.artboards.length; a++) {
    doc.artboards.setActiveArtboardIndex(a);
    exportOpts.artboardRange = (a + 1).toString();
    var popFile = new File(rawPopFolder.fsName + "/pop_ab" + (a + 1 < 10 ? "0" : "") + (a + 1) + ".jpg");
    doc.exportFile(popFile, ExportType.JPEG, exportOpts);
}

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/export_status.txt");
f.open("w");
f.write("Exported all " + doc.artboards.length + " blank and populated artboards successfully!");
f.close();
