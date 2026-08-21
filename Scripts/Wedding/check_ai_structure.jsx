app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.open(new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Square_10x10.ai"));
var info = [];
info.push("Doc: " + doc.name);
info.push("Artboards count: " + doc.artboards.length);
for (var i = 0; i < doc.layers.length; i++) {
    var l = doc.layers[i];
    info.push("Layer " + i + ": " + l.name + " (visible: " + l.visible + ", groupItems: " + l.groupItems.length + ", pageItems: " + l.pageItems.length + ")");
}

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Scripts/ai_structure_out.txt");
f.open("w");
f.write(info.join("\n"));
f.close();

doc.close(SaveOptions.DONOTSAVECHANGES);
