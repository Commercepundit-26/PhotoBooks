var doc = app.activeDocument;
var out = [];

for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect; // [left, top, right, bottom]
    var w = Math.round(r[2] - r[0]);
    var h = Math.round(r[1] - r[3]);
    var sizeLabel = (w == 720 && h == 720) ? "Square (10x10)" : ((w == 576 && h == 864) ? "Portrait (8x12)" : ((w == 864 && h == 576) ? "Landscape (12x8)" : (w + "x" + h)));
    
    // Find items on this artboard
    var itemsOnAb = [];
    for (var j = 0; j < doc.pageItems.length; j++) {
        var item = doc.pageItems[j];
        var ib = item.geometricBounds; // [l, t, r, b]
        var cx = (ib[0] + ib[2]) / 2;
        var cy = (ib[1] + ib[3]) / 2;
        if (cx >= r[0] && cx <= r[2] && cy <= r[1] && cy >= r[3]) {
            itemsOnAb.push(item.typename + (item.typename == "PathItem" ? " [w=" + Math.round(ib[2]-ib[0]) + ", h=" + Math.round(ib[1]-ib[3]) + "]" : ""));
        }
    }
    out.push("Artboard " + (i + 1) + " (" + sizeLabel + ") -> " + itemsOnAb.length + " items: " + itemsOnAb.join(", "));
}

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/artboards_detail.txt");
f.open("w");
f.write(out.join("\n"));
f.close();
