import os
import subprocess
import json

jsx = '''
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.open(new File("/Users/cp/Ronak/CC/Photobooks/extra/Wedding-V2/Wedding_Square_10x10.ai"));

var issues = [];
var summary = [];

for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0], abTop = r[1], abRight = r[2], abBottom = r[3];

    var safeLeft = abLeft + 70;
    var safeTop = abTop - 70;
    var safeRight = abRight - 70;
    var safeBottom = abBottom + 70;

    var pageTFs = [];
    for (var t = 0; t < doc.textFrames.length; t++) {
        var tf = doc.textFrames[t];
        var tb = tf.geometricBounds;
        var cx = (tb[0] + tb[2]) / 2;
        var cy = (tb[1] + tb[3]) / 2;
        if (cx >= abLeft && cx <= abRight && cy <= abTop && cy >= abBottom) {
            pageTFs.push(tf);
            
            var tL = tb[0], tT = tb[1], tR_pos = tb[2], tB = tb[3];
            var clipLeft = tL < safeLeft;
            var clipTop = tT > safeTop;
            var clipRight = tR_pos > safeRight;
            var clipBottom = tB < safeBottom;

            if (clipLeft || clipTop || clipRight || clipBottom) {
                var desc = "";
                if (clipLeft) desc += "Left (" + (tL - abLeft).toFixed(1) + "pt < 72pt) ";
                if (clipTop) desc += "Top (" + (abTop - tT).toFixed(1) + "pt < 72pt) ";
                if (clipRight) desc += "Right (" + (abRight - tR_pos).toFixed(1) + "pt < 72pt) ";
                if (clipBottom) desc += "Bottom (" + (tB - abBottom).toFixed(1) + "pt < 72pt) ";
                issues.push("Page " + (i + 1) + ": " + tf.contents.replace(/\\r/g, " ") + " -> " + desc);
            }
        }
    }
}

doc.close(SaveOptions.DONOTSAVECHANGES);

var f = new File("/Users/cp/Ronak/CC/Photobooks/Scripts/Layout/audit_results.txt");
f.open("w");
f.write(issues.join("\\n"));
f.close();
'''

with open("/Users/cp/Ronak/CC/Photobooks/Scripts/Layout/_audit_all.jsx", "w") as f:
    f.write(jsx)

subprocess.run(["osascript", "-e", 'tell application "Adobe Illustrator" to do javascript file "/Users/cp/Ronak/CC/Photobooks/Scripts/Layout/_audit_all.jsx"'])
