#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var sourceFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai");
var srcDoc = app.open(sourceFile);

var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720);

var sAB = srcDoc.artboards[0];
var sR = sAB.artboardRect;

var count = 0;
for (var l = 0; l < srcDoc.layers.length; l++) {
    var lyr = srcDoc.layers[l];
    for (var k = 0; k < lyr.pageItems.length; k++) {
        var item = lyr.pageItems[k];
        var ib = item.geometricBounds;
        var cx = (ib[0] + ib[2]) / 2;
        var cy = (ib[1] + ib[3]) / 2;
        if (cx >= sR[0] && cx <= sR[2] && cy <= sR[1] && cy >= sR[3]) {
            var dup = item.duplicate(doc.layers[0], ElementPlacement.PLACEATBEGINNING);
            dup.left = ib[0] - sR[0];
            dup.top = ib[1] - sR[1];
            count++;
        }
    }
}

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_copy_out.txt");
f.open("w");
f.write("Copied " + count + " items successfully!");
f.close();
