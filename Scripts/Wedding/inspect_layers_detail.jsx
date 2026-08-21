var doc = app.activeDocument;
var log = [];
for (var i = 0; i < doc.layers.length; i++) {
    var l = doc.layers[i];
    log.push("Layer: " + l.name + " (pageItems: " + l.pageItems.length + ", groupItems: " + l.groupItems.length + ", pathItems: " + l.pathItems.length + ")");
}
var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/layers_detail.txt");
f.open("w");
f.write(log.join("\n"));
f.close();
