
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var doc = app.open(new File("/Users/cp/Ronak/CC/Photobooks/Layout/Final Layouts.ai"));
var targetDoc = app.documents.add(DocumentColorSpace.RGB, 720, 720, 1);
var tR = targetDoc.artboards[0].artboardRect;

// Test Artboard 23 (P09) & Artboard 20 (P11)
var srcAb = doc.artboards[23];
var sR = srcAb.artboardRect;

var typeLayer = targetDoc.layers.add();
for (var t = 0; t < doc.textFrames.length; t++) {
    var tf = doc.textFrames[t];
    var tb = tf.geometricBounds;
    var cx = (tb[0] + tb[2]) / 2;
    var cy = (tb[1] + tb[3]) / 2;
    if (cx >= sR[0] && cx <= sR[2] && cy <= sR[1] && cy >= sR[3]) {
        var dupTF = tf.duplicate(typeLayer, ElementPlacement.PLACEATEND);
        dupTF.left = tR[0] + (tf.left - sR[0]);
        dupTF.top = tR[1] + (tf.top - sR[1]);

        var isScript = tf.contents.indexOf("Heading ") !== -1 && tf.contents.indexOf("too") === -1;
        if (isScript) {
            dupTF.contents = "Our Forever Story";
            dupTF.textRange.characterAttributes.textFont = app.textFonts.getByName("GreatVibes-Regular");
            dupTF.textRange.characterAttributes.size = 52;
        } else {
            dupTF.contents = "THE CELEBRATION OF LOVE";
            dupTF.textRange.characterAttributes.textFont = app.textFonts.getByName("Poppins-Medium");
            dupTF.textRange.characterAttributes.size = 28;
        }

        // Enforce 1-inch safe margin clamping
        var b = dupTF.geometricBounds;
        var relBottom = b[3] - tR[1];
        var relTop = b[1] - tR[1];
        
        while (relBottom < -648 && dupTF.textRange.characterAttributes.size > 20) {
            dupTF.textRange.characterAttributes.size -= 2;
            b = dupTF.geometricBounds;
            relBottom = b[3] - tR[1];
        }
        
        // If still bottom-overflowing, shift upward
        if (relBottom < -648) {
            dupTF.top += (-648 - relBottom);
        }
        // If top-overflowing past -72, shift downward
        b = dupTF.geometricBounds;
        relTop = b[1] - tR[1];
        if (relTop > -72) {
            dupTF.top -= (relTop - (-72));
        }
    }
}

doc.close(SaveOptions.DONOTSAVECHANGES);
targetDoc.close(SaveOptions.DONOTSAVECHANGES);
