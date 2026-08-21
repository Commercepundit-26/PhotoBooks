
// Close any open documents
while (app.documents.length > 0) {
    app.documents[0].close(SaveOptions.DONOTSAVECHANGES);
}

var fileRef = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai");
var doc = app.open(fileRef);

// Remove existing Backgrounds layer if present
try {
    var oldBg = doc.layers.getByName("Backgrounds");
    oldBg.remove();
} catch(e) {}

var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";
bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

var bgFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds");
var bgFiles = bgFolder.getFiles("*.jpg");
bgFiles.sort(function(a, b) { return a.name.localeCompare(b.name); });

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

    // Place background image
    var placed = clipGroup.placedItems.add();
    placed.file = bgFile;

    var side = Math.max(abW, abH);
    placed.width = side;
    placed.height = side;
    placed.left = abLeft + (abW - side) / 2;
    placed.top = abTop - (abH - side) / 2;

    // Mask with artboard bounds
    var clipRect = clipGroup.pathItems.rectangle(abTop, abLeft, abW, abH);
    clipRect.filled = false;
    clipRect.stroked = false;
    clipRect.clipping = true;

    clipGroup.clipped = true;
}

doc.save();
