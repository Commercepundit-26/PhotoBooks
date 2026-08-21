var doc = app.activeDocument;
var names = [];
for (var i = 0; i < doc.layers.length; i++) {
    names.push(doc.layers[i].name);
}
var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/layer_names.txt");
f.open("w");
f.write(names.join(", "));
f.close();
