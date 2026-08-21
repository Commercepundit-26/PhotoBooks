app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720);
var bgFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p01_5400x5400.jpg");

var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";

var clipGroup = bgLayer.groupItems.add();

var placed = clipGroup.placedItems.add();
placed.file = bgFile;
placed.width = 720;
placed.height = 720;
placed.left = 0;
placed.top = 0;

var clipRect = clipGroup.pathItems.rectangle(0, 0, 720, 720);
clipRect.filled = false;
clipRect.stroked = false;
clipRect.clipping = true;

clipGroup.clipped = true;

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_bg_out.txt");
f.open("w");
f.write("Placed background successfully!");
f.close();
