
var doc = app.activeDocument;
var res = "Doc: " + doc.name + ", Artboards: " + doc.artboards.length;
var f = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/test_res.txt");
f.open("w");
f.write(res);
f.close();
