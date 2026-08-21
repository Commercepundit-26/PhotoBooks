var doc = app.activeDocument;
var info = [];
info.push("Document Name: " + doc.name);
info.push("Artboard Count: " + doc.artboards.length);
for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var w = Math.round(r[2] - r[0]);
    var h = Math.round(r[1] - r[3]);
    info.push("  Artboard " + (i + 1) + " ['" + ab.name + "']: " + w + " x " + h + " pt");
}
info.push("Layers (" + doc.layers.length + "):");
for (var j = 0; j < doc.layers.length; j++) {
    var l = doc.layers[j];
    info.push("  Layer " + (j + 1) + " ['" + l.name + "']: visible=" + l.visible + ", items=" + l.pageItems.length);
}
var outFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/doc_info.txt");
outFile.open("w");
outFile.write(info.join("\n"));
outFile.close();
