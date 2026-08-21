app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var sourceFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai");
var srcDoc = app.open(sourceFile);

var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720);
var layoutLayer = doc.layers[0];
var pGroup = layoutLayer.groupItems.add();

var itm = srcDoc.pageItems[0];
var dup = itm.duplicate(layoutLayer, ElementPlacement.PLACEATBEGINNING);
dup.move(pGroup, ElementPlacement.PLACEATBEGINNING);

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_move_out.txt");
f.open("w");
f.write("Success with dup.move(pGroup, ElementPlacement.PLACEATBEGINNING)!");
f.close();
