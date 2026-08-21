var doc = app.activeDocument;
var outFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Blank_Layouts");

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 88;
exportOpts.artboardClipping = true;

// Ensure Backgrounds layer exists and is populated
var bgLayer;
try {
    bgLayer = doc.layers.getByName("Backgrounds");
} catch(e) {
    bgLayer = doc.layers.add();
    bgLayer.name = "Backgrounds";
    bgLayer.zOrder(ZOrderMethod.SENDTOBACK);
}

for (var i = 0; i < doc.artboards.length; i++) {
    doc.artboards.setActiveArtboardIndex(i);
    var ab = doc.artboards[i];
    var abName = ab.name.replace(/[^a-zA-Z0-9_-]/g, "_");
    var rect = ab.artboardRect;
    var w = Math.round(rect[2] - rect[0]);
    var h = Math.round(rect[1] - rect[3]);
    var typeStr = (w == 720 && h == 720) ? "Square_10x10" : ((w == 864 && h == 576) ? "Landscape_12x8" : "Portrait_8x12");
    
    var padIdx = (i + 1 < 10) ? ("0" + (i + 1)) : ("" + (i + 1));
    var fName = "Layout_" + padIdx + "_" + typeStr + "_" + abName + ".jpg";
    var destFile = new File(outFolder.fsName + "/" + fName);
    doc.exportFile(destFile, ExportType.JPEG, exportOpts);
}
