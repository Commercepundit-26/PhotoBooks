
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

var rawFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Raw_Captures");

var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

var photoLayer = null;
try {
    photoLayer = doc.layers.getByName("Photos_Masked");
} catch(e) {}

// 1. Export 21 Blank Artboards (Hide Photos)
if (photoLayer) photoLayer.visible = false;

for (var i = 0; i < doc.artboards.length; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/blank_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}

// 2. Export 21 Populated Artboards (Show Photos)
if (photoLayer) photoLayer.visible = true;

for (var i = 0; i < doc.artboards.length; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/pop_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}
