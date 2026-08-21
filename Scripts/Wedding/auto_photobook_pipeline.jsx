#target illustrator

app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var aiPath = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai";
var bgPath = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds";
var weddingPhotosPath = "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding";

var blankExportPath = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Blank_Layouts_Raw";
var popExportPath = "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Populated_Layouts_Raw";

var logFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/pipeline_log.txt");
logFile.open("w");
function log(msg) {
    logFile.writeln(msg);
}

log("Starting Photobook Automation Pipeline in Illustrator...");

// 1. Open AI Document
var fileRef = new File(aiPath);
var doc = app.open(fileRef);
log("Opened Document: " + doc.name + " (" + doc.artboards.length + " artboards)");

// 2. Setup Backgrounds
try {
    var oldBg = doc.layers.getByName("Backgrounds");
    oldBg.remove();
} catch(e) {}

var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";
bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

var bgFolder = new Folder(bgPath);
var bgFiles = bgFolder.getFiles("*.jpg");
bgFiles.sort(function(a, b) { return a.name.localeCompare(b.name); });

log("Applying 5400x5400px backgrounds across all " + doc.artboards.length + " artboards...");

for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];
    var abW = abRight - abLeft;
    var abH = abTop - abBottom;

    var bgFile = bgFiles[i % bgFiles.length];

    var clipGroup = bgLayer.groupItems.add();

    var placed = clipGroup.placedItems.add();
    placed.file = bgFile;

    var side = Math.max(abW, abH);
    placed.width = side;
    placed.height = side;
    placed.left = abLeft + (abW - side) / 2;
    placed.top = abTop - (abH - side) / 2;

    var clipRect = clipGroup.pathItems.rectangle(abTop, abLeft, abW, abH);
    clipRect.filled = false;
    clipRect.stroked = false;
    clipRect.clipping = true;

    clipGroup.clipped = true;
}
log("Backgrounds successfully applied!");

// 3. Export Blank Layout Previews
var rawBlankFolder = new Folder(blankExportPath);
if (!rawBlankFolder.exists) rawBlankFolder.create();

var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 88;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;

log("Exporting Blank Layout Previews...");
var blankBase = new File(rawBlankFolder.fsName + "/blank.jpg");
doc.exportFile(blankBase, ExportType.JPEG, exportOpts);
log("Blank Layout Previews exported!");

// 4. Place and Mask Wedding Photos
log("Placing and masking downloaded master wedding photos into layout boxes...");

try {
    var oldPhoto = doc.layers.getByName("Photos_Masked");
    oldPhoto.remove();
} catch(e) {}

var photoLayer = doc.layers.add();
photoLayer.name = "Photos_Masked";
photoLayer.move(bgLayer, ElementPlacement.PLACEBEFORE);

var photosFolder = new Folder(weddingPhotosPath);
var photoFiles = photosFolder.getFiles("*.jpg");

var landPhotos = [];
var portPhotos = [];
var sqPhotos = [];

for (var p = 0; p < photoFiles.length; p++) {
    var pf = photoFiles[p];
    var pfn = pf.name.toLowerCase();
    // Simple heuristic or rotation
    if (p % 3 == 0) portPhotos.push(pf);
    else if (p % 3 == 1) sqPhotos.push(pf);
    else landPhotos.push(pf);
}

var landIdx = 0, portIdx = 0, sqIdx = 0, allIdx = 0;
var placedBoxesCount = 0;

for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];

    for (var j = 0; j < doc.layers.length; j++) {
        var lyr = doc.layers[j];
        if (lyr.name == "Backgrounds" || lyr.name == "Photos_Masked") continue;

        for (var k = 0; k < lyr.pathItems.length; k++) {
            var pi = lyr.pathItems[k];
            if (pi.guides || pi.clipping) continue;

            var gb = pi.geometricBounds;
            var cx = (gb[0] + gb[2]) / 2;
            var cy = (gb[1] + gb[3]) / 2;

            if (cx >= abLeft && cx <= abRight && cy <= abTop && cy >= abBottom) {
                var pw = gb[2] - gb[0];
                var ph = gb[1] - gb[3];

                if (pw > 30 && ph > 30) {
                    var ratio = pw / ph;
                    var chosenFile;
                    if (ratio >= 1.15 && landPhotos.length > 0) {
                        chosenFile = landPhotos[landIdx % landPhotos.length];
                        landIdx++;
                    } else if (ratio <= 0.85 && portPhotos.length > 0) {
                        chosenFile = portPhotos[portIdx % portPhotos.length];
                        portIdx++;
                    } else if (sqPhotos.length > 0) {
                        chosenFile = sqPhotos[sqIdx % sqPhotos.length];
                        sqIdx++;
                    } else {
                        chosenFile = photoFiles[allIdx % photoFiles.length];
                        allIdx++;
                    }

                    var pGroup = photoLayer.groupItems.add();

                    var pPlaced = pGroup.placedItems.add();
                    pPlaced.file = chosenFile;

                    var scaleFactor = Math.max(pw / pPlaced.width, ph / pPlaced.height);
                    var newW = pPlaced.width * scaleFactor;
                    var newH = pPlaced.height * scaleFactor;
                    pPlaced.width = newW;
                    pPlaced.height = newH;
                    pPlaced.left = gb[0] + (pw - newW) / 2;
                    pPlaced.top = gb[1] - (ph - newH) / 2;

                    var maskPath = pi.duplicate(pGroup, ElementPlacement.PLACEATBEGINNING);
                    maskPath.filled = false;
                    maskPath.stroked = false;
                    maskPath.clipping = true;

                    pGroup.clipped = true;
                    placedBoxesCount++;
                }
            }
        }
    }
}

log("Masked photos placed in " + placedBoxesCount + " photo containers!");

// 5. Save Document
doc.save();
log("Master Document saved successfully!");

// 6. Export Populated Layout Previews
var rawPopFolder = new Folder(popExportPath);
if (!rawPopFolder.exists) rawPopFolder.create();

log("Exporting Populated Layout Previews...");
var popBase = new File(rawPopFolder.fsName + "/pop.jpg");
doc.exportFile(popBase, ExportType.JPEG, exportOpts);
log("Populated Layout Previews exported successfully!");

logFile.close();
