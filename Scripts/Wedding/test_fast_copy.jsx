app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var sourceFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai");
var srcDoc = app.open(sourceFile);

var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720);

// Pre-filter items by artboard in srcDoc
var itemsByAB = [];
for (var a = 0; a < srcDoc.artboards.length; a++) {
    itemsByAB.push([]);
}

for (var k = 0; k < srcDoc.pageItems.length; k++) {
    var item = srcDoc.pageItems[k];
    var ib = item.geometricBounds;
    var cx = (ib[0] + ib[2]) / 2;
    var cy = (ib[1] + ib[3]) / 2;

    for (var a = 0; a < srcDoc.artboards.length; a++) {
        var ar = srcDoc.artboards[a].artboardRect;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {
            itemsByAB[a].push(item);
            break;
        }
    }
}

// Copy items for artboard 0
var ab0Items = itemsByAB[0];
for (var i = 0; i < ab0Items.length; i++) {
    var sR = srcDoc.artboards[0].artboardRect;
    var dup = ab0Items[i].duplicate(doc.layers[0], ElementPlacement.PLACEATBEGINNING);
    dup.left = dup.left - sR[0];
    dup.top = dup.top - sR[1];
}

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/fast_copy_out.txt");
f.open("w");
f.write("Fast copy completed! " + ab0Items.length + " items copied.");
f.close();
