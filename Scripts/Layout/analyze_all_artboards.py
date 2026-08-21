import subprocess
import json

jsx = """
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

function analyzeDoc(filePath) {
    var doc = app.open(new File(filePath));
    var res = {
        name: doc.name,
        path: filePath,
        artboards: []
    };

    for (var a = 0; a < doc.artboards.length; a++) {
        var ab = doc.artboards[a];
        var ar = ab.artboardRect;
        var w = Math.round(ar[2] - ar[0]);
        var h = Math.round(ar[1] - ar[3]);
        var orientation = "Square";
        if (w > h) orientation = "Landscape";
        else if (h > w) orientation = "Portrait";

        var itemCount = 0;
        var pathCount = 0;
        var groupCount = 0;

        for (var k = 0; k < doc.pageItems.length; k++) {
            var item = doc.pageItems[k];
            if (item.guides || item.clipping) continue;
            var ib = item.geometricBounds;
            var cx = (ib[0] + ib[2]) / 2;
            var cy = (ib[1] + ib[3]) / 2;
            if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {
                itemCount++;
                if (item.typename === "PathItem") pathCount++;
                else if (item.typename === "GroupItem") groupCount++;
            }
        }

        res.artboards.push({
            index: a,
            name: ab.name,
            rect: [Math.round(ar[0]), Math.round(ar[1]), Math.round(ar[2]), Math.round(ar[3])],
            width: w,
            height: h,
            orientation: orientation,
            itemCount: itemCount,
            pathCount: pathCount,
            groupCount: groupCount
        });
    }
    doc.close(SaveOptions.DONOTSAVECHANGES);
    return res;
}

var data = [
    analyzeDoc("/Users/cp/Ronak/CC/Photobooks/Layout/Layouts.ai"),
    analyzeDoc("/Users/cp/Ronak/CC/Photobooks/Layout/Unique shape Layouts.ai")
];

var f = new File("/Users/cp/Ronak/CC/Photobooks/Layout/analysis_data.json");
f.open("w");
// custom json stringify for extendscript
function toJson(obj) {
    if (typeof obj === "string") return '"' + obj.replace(/\\\\/g, '\\\\\\\\').replace(/"/g, '\\\\"') + '"';
    if (typeof obj === "number" || typeof obj === "boolean") return String(obj);
    if (obj instanceof Array) {
        var arrStr = [];
        for (var i = 0; i < obj.length; i++) arrStr.push(toJson(obj[i]));
        return "[" + arrStr.join(",") + "]";
    }
    var objStr = [];
    for (var k in obj) {
        if (obj.hasOwnProperty(k)) {
            objStr.push('"' + k + '":' + toJson(obj[k]));
        }
    }
    return "{" + objStr.join(",") + "}";
}
f.write(toJson(data));
f.close();
"""

with open("/Users/cp/Ronak/CC/Photobooks/Layout/analyze.jsx", "w") as f:
    f.write(jsx)

subprocess.run(['osascript', '-e', 'tell application "Adobe Illustrator" to do javascript file "/Users/cp/Ronak/CC/Photobooks/Layout/analyze.jsx"'])

with open("/Users/cp/Ronak/CC/Photobooks/Layout/analysis_data.json") as f:
    data = json.load(f)

for doc in data:
    print("="*60)
    print(f"DOCUMENT: {doc['name']} (Total Artboards: {len(doc['artboards'])})")
    print("="*60)
    sq = [ab for ab in doc['artboards'] if ab['orientation'] == 'Square']
    land = [ab for ab in doc['artboards'] if ab['orientation'] == 'Landscape']
    port = [ab for ab in doc['artboards'] if ab['orientation'] == 'Portrait']
    print(f"  Square Artboards:    {len(sq)}")
    print(f"  Landscape Artboards: {len(land)}")
    print(f"  Portrait Artboards:  {len(port)}")
    empty = [ab for ab in doc['artboards'] if ab['itemCount'] == 0]
    if empty:
        print(f"  Empty Artboards ({len(empty)}): {[ab['index'] for ab in empty]}")
    else:
        print("  All artboards have items.")
