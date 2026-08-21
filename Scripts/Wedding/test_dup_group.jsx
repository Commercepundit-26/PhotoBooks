app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var sourceFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai");
var srcDoc = app.open(sourceFile);

var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720);
var layoutLayer = doc.layers[0];
var pGroup = layoutLayer.groupItems.add();

var itm = srcDoc.pageItems[0];
var dup = itm.duplicate(layoutLayer, ElementPlacement.PLACEATBEGINNING);
dup.moveToBeginning(pGroup);

var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_dup_out.txt");
f.open("w");
f.write("Success duplicating into layer then moving to group!");
f.close();
