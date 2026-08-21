var doc = app.activeDocument;

// Find or create Backgrounds layer at the bottom
var bgLayer;
try {
    bgLayer = doc.layers.getByName("Backgrounds");
    bgLayer.remove();
} catch(e) {}

bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";
bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

var bgDir = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds");
var bgFiles = bgDir.getFiles("*.jpg");

bgFiles.sort(function(a, b) {
    return a.name.localeCompare(b.name);
});

for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var rect = ab.artboardRect;
    var abLeft = rect[0];
    var abTop = rect[1];
    var abRight = rect[2];
    var abBottom = rect[3];
    var abW = abRight - abLeft;
    var abH = abTop - abBottom;

    var bgFile = bgFiles[i % bgFiles.length];

    var clipGroup = bgLayer.groupItems.add();

    // Place image first (bottom of group)
    var placed = clipGroup.placedItems.add();
    placed.file = bgFile;

    var side = Math.max(abW, abH);
    placed.width = side;
    placed.height = side;
    placed.left = abLeft + (abW - side) / 2;
    placed.top = abTop - (abH - side) / 2;

    // Create mask path (top of group)
    var clipRect = clipGroup.pathItems.rectangle(abTop, abLeft, abW, abH);
    clipRect.filled = false;
    clipRect.stroked = false;
    clipRect.clipping = true;

    clipGroup.clipped = true;
}

// Export blank previews for each artboard
var outFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Blank_Layouts_Raw");
if (!outFolder.exists) outFolder.create();

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 92;
exportOpts.artboardClipping = true;

for (var i = 0; i < doc.artboards.length; i++) {
    doc.artboards.setActiveArtboardIndex(i);
    var ab = doc.artboards[i];
    var abName = ab.name.replace(/[^a-zA-Z0-9_-]/g, "_");
    var rect = ab.artboardRect;
    var w = Math.round(rect[2] - rect[0]);
    var h = Math.round(rect[1] - rect[3]);
    var typeStr = (w == 720 && h == 720) ? "Square" : ((w == 864 && h == 576) ? "Landscape" : "Portrait");
    
    var fName = "AB" + (i + 1 < 10 ? "0" + (i + 1) : (i + 1)) + "_" + typeStr + "_" + abName + ".jpg";
    var destFile = new File(outFolder.fsName + "/" + fName);
    doc.exportFile(destFile, ExportType.JPEG, exportOpts);
}
