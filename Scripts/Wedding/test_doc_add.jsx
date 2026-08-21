#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720);
doc.artboards[0].name = "P01_Square_10x10";
for (var i = 1; i < 7; i++) {
    var l = i * (720 + 50);
    var ab = doc.artboards.add([l, 0, l + 720, -720]);
    ab.name = "P0" + (i + 1) + "_Square_10x10";
}
var log = "Created doc with " + doc.artboards.length + " artboards!";
var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_out.txt");
f.open("w");
f.write(log);
f.close();
