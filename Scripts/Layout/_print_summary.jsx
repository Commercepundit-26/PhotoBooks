
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var doc = app.open(new File("/Users/cp/Ronak/CC/Photobooks/extra/Wedding-V2/Wedding_Square_10x10.ai"));

var str = "";
for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0], abTop = r[1], abRight = r[2], abBottom = r[3];

    str += "=== PAGE " + (i + 1 < 10 ? "0" : "") + (i + 1) + " (" + ab.name + ") ===\n";
    var count = 0;
    for (var t = 0; t < doc.textFrames.length; t++) {
        var tf = doc.textFrames[t];
        var tb = tf.geometricBounds;
        var cx = (tb[0] + tb[2]) / 2;
        var cy = (tb[1] + tb[3]) / 2;
        if (cx >= abLeft && cx <= abRight && cy <= abTop && cy >= abBottom) {
            count++;
            var fontName = tf.textRange.characterAttributes.textFont.name;
            var fontSize = tf.textRange.characterAttributes.size;
            var cleanText = tf.contents.replace(/\r/g, " [LINE BREAK] ");
            var relL = (tb[0] - abLeft).toFixed(1);
            var relT = (abTop - tb[1]).toFixed(1);
            var relR = (tb[2] - abLeft).toFixed(1);
            var relB = (abTop - tb[3]).toFixed(1);
            str += "  [" + count + "] Font: " + fontName + " (" + fontSize + "pt) | Bounds: [L:" + relL + ", T:" + relT + ", R:" + relR + ", B:" + relB + "pt]\n";
            str += "      Text: \"" + cleanText + "\"\n";
        }
    }
    if (count === 0) {
        str += "  [Pure Photo Layout - No Text]\n";
    }
    str += "\n";
}

doc.close(SaveOptions.DONOTSAVECHANGES);

var f = new File("/Users/cp/Ronak/CC/Photobooks/Scripts/Layout/full_22_page_report.txt");
f.open("w");
f.write(str);
f.close();
