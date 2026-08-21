
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var logFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/photobook_build_log.txt");
logFile.open("w");
function log(msg) {
    logFile.writeln(msg);
}

log("STEP 1: Opening Source Document...");
var sourceFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Unique shape Layouts.ai");
var srcDoc = null;
for (var d = 0; d < app.documents.length; d++) {
    if (app.documents[d].name.indexOf("Unique shape Layouts") !== -1) {
        srcDoc = app.documents[d];
        break;
    }
}
if (!srcDoc) {
    srcDoc = app.open(sourceFile);
}

log("STEP 2: Indexing Layout Elements in Source Document...");
var itemsByAB = [];
for (var a = 0; a < srcDoc.artboards.length; a++) {
    itemsByAB.push([]);
}

for (var k = 0; k < srcDoc.pageItems.length; k++) {
    var item = srcDoc.pageItems[k];
    if (item.guides || item.clipping) continue;
    var ib = item.geometricBounds;
    var cx = (ib[0] + ib[2]) / 2;
    var cy = (ib[1] + ib[3]) / 2;

    for (var a = 0; a < srcDoc.artboards.length; a++) {
        var ar = srcDoc.artboards[a].artboardRect;
        if (cx >= ar[0] && cx <= ar[2] && cy <= ar[1] && cy >= ar[3]) {
            itemsByAB[a].push(item);
            break;
        }
    }
}
log("Source indexing complete!");

log("STEP 3: Creating Master Document with 21 Artboards...");
var doc = app.documents.add(DocumentColorSpace.RGB, 720, 720);
doc.artboards[0].artboardRect = [0, 0, 720, -720];
doc.artboards[0].name = "P01_Square_10x10";

var spacing = 60;

// Add 6 Square artboards (Row 1, Y = 0)
for (var i = 1; i < 7; i++) {
    var l = i * (720 + spacing);
    var ab = doc.artboards.add([l, 0, l + 720, -720]);
    ab.name = "P0" + (i + 1) + "_Square_10x10";
}

// Add 7 Landscape artboards (Row 2, Y = -850)
var row2Y = -850;
for (var i = 0; i < 7; i++) {
    var l = i * (864 + spacing);
    var ab = doc.artboards.add([l, row2Y, l + 864, row2Y - 576]);
    ab.name = "P0" + (i + 1) + "_Landscape_12x8";
}

// Add 7 Portrait artboards (Row 3, Y = -1550)
var row3Y = -1550;
for (var i = 0; i < 7; i++) {
    var l = i * (576 + spacing);
    var ab = doc.artboards.add([l, row3Y, l + 576, row3Y - 864]);
    ab.name = "P0" + (i + 1) + "_Portrait_8x12";
}

// Layers Setup
var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";

var photoLayer = doc.layers.add();
photoLayer.name = "Photos_Masked";

var layoutLayer = doc.layers[0];
layoutLayer.name = "Layout_Shapes";

bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

log("STEP 4: Placing 7 Master Backgrounds across 21 Artboards...");
var bgFilePaths = [
    "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p01_5400x5400.jpg",
    "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p06_5400x5400.jpg",
    "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p12_5400x5400.jpg",
    "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p15_5400x5400.jpg",
    "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p16_5400x5400.jpg",
    "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p17_5400x5400.jpg",
    "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p18_5400x5400.jpg"
];

for (var i = 0; i < 21; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];
    var abW = abRight - abLeft;
    var abH = abTop - abBottom;

    var bgIdx = i % 7;
    var bgFile = new File(bgFilePaths[bgIdx]);

    var clipGroup = bgLayer.groupItems.add();

    var placed = clipGroup.placedItems.add();
    placed.file = bgFile;

    var side = Math.max(abW, abH);
    placed.width = side;
    placed.height = side;
    placed.left = abLeft + (abW - side) / 2;
    placed.top = abTop - (abH - side) / 2;

    var clipRect = clipGroup.pathItems.rectangle(abTop, abLeft, abW, abH);
    clipRect.filled = false;
    clipRect.stroked = false;
    clipRect.clipping = true;

    clipGroup.clipped = true;
}
log("Backgrounds placed successfully!");

log("STEP 5: Copying Selected Layout Shapes...");
var srcSquareAB = [0, 5, 7, 8, 16, 21, 23];
var srcLandAB   = [42, 43, 46, 50, 51, 55, 47];
var srcPortAB   = [25, 28, 29, 30, 35, 37, 39];

function copyFastLayout(sABIdx, tABIdx) {
    var sR = srcDoc.artboards[sABIdx].artboardRect;
    var tR = doc.artboards[tABIdx].artboardRect;
    var items = itemsByAB[sABIdx];

    for (var m = 0; m < items.length; m++) {
        var itm = items[m];
        var dup = itm.duplicate(layoutLayer, ElementPlacement.PLACEATBEGINNING);
        dup.left = tR[0] + (itm.left - sR[0]);
        dup.top = tR[1] + (itm.top - sR[1]);
    }
}

for (var p = 0; p < 7; p++) {
    copyFastLayout(srcSquareAB[p], p);         // Square (0..6)
    copyFastLayout(srcLandAB[p], 7 + p);       // Landscape (7..13)
    copyFastLayout(srcPortAB[p], 14 + p);      // Portrait (14..20)
}
log("Layout shapes copied for all 21 artboards!");

log("STEP 6: Saving Master AI Document...");
var targetFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Photobook_3Sizes.ai");
doc.saveAs(targetFile);
log("Saved master AI document.");

log("STEP 7: Exporting Blank Layout Previews...");
var rawBlankFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Raw_Blank");
var exportOpts = new ExportOptionsJPEG();
exportOpts.antiAliasing = true;
exportOpts.qualitySetting = 90;
exportOpts.artboardClipping = true;
exportOpts.saveMultipleArtboards = true;

var blankBase = new File(rawBlankFolder.fsName + "/blank.jpg");
doc.exportFile(blankBase, ExportType.JPEG, exportOpts);
log("Blank previews exported!");

log("STEP 8: Placing & Masking Master Wedding Photos...");
var landPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-couple-in-love-a-guy-and-a-girl-on-a-walk-in-the-2026-01-07-00-24-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-couple-kissing-each-other-in-park-2026-01-09-09-26-30-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-celebrating-their-wedding-day-tog-2026-01-11-09-56-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-wedding-bouquet-held-by-a-loving-couple-2026-01-07-07-32-44-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-celebrate-with-wedding-guests-outd-2026-01-09-11-10-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-exchange-rings-at-wedding-ceremony-2026-01-07-07-32-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-hands-walking-in-woods-2026-03-10-01-03-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hug-while-on-a-walk-in-the-park-2026-03-24-23-46-52-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-on-wedding-day-with-guests-2026-03-26-04-28-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walking-through-beautiful-garden-t-2026-01-08-06-25-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bridesmaid-helping-bride-with-her-wedding-dress-2026-03-10-04-45-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bunch-of-fresh-flowers-at-the-garden-2026-01-07-23-43-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-bride-and-groom-holding-hands-at-a-wed-2026-01-09-10-40-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-vibrant-pink-red-and-white-flowers-2026-03-26-03-30-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-portrait-of-the-bride-and-groom-the-brid-2026-03-10-01-07-58-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-celebrate-wedding-on-rocky-shoreline-at-sun-2026-03-17-00-03-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-bride-and-groom-holding-hands-at-wedding-2026-01-08-05-33-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-celebrate-wedding-in-a-lush-garden-2026-03-19-22-09-00-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-at-outdoor-wedding-ceremony-2026-01-09-10-01-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-surrounded-by-beautiful-nat-2026-01-09-10-57-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-wedding-bouquet-held-by-couple-close-up-2026-03-24-01-19-06-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-posing-in-the-autumn-forest-2026-03-10-22-41-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-smiling-on-wedding-day-2026-01-11-09-56-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-wedding-day-couple-posing-outdoors-together-2026-03-26-03-49-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/ill-stand-by-your-side-in-the-good-and-the-bad-2026-03-25-04-38-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/intimate-wedding-moment-with-rings-2026-01-08-00-29-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-holding-hands-and-looking-at-e-2026-01-05-23-53-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-on-a-green-forest-2026-01-06-11-09-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-celebrate-wedding-day-in-natural-set-2026-01-09-09-21-40-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-holding-hands-at-wedding-ceremony-2026-01-08-06-58-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-walking-in-amazing-blossoming-flowers-fi-2026-03-09-04-36-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embrace-on-wedding-day-in-nature-2026-01-08-23-53-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-flowers-on-wedding-day-2026-03-19-09-26-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-hands-at-wedding-reception-2026-01-07-23-20-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/shot-of-a-bride-and-bridegroom-holding-hands-walki-2026-01-08-00-25-39-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/silhouette-of-couple-embracing-near-water-at-sunse-2026-01-08-06-31-21-utc.jpg"];
var portPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-happy-young-couple-in-walk-in-a-garden-a-man-in-2026-01-05-04-57-23-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-young-couple-kissing-outdoors-on-thei-2026-01-07-06-23-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-and-groom-embrace-at-night-2026-03-16-22-55-01-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-with-groom-embracing-her-2026-01-11-09-55-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-bouquet-on-wedding-day-2026-03-09-05-39-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-holding-bouquet-in-their-hands-in-2026-01-11-08-15-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-posing-and-hugging-in-hotel-room-2026-01-09-00-45-27-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walk-together-in-the-park-pretty-2026-03-19-22-04-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-with-her-groom-on-wedding-day-2026-01-05-01-07-39-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-a-woman-fastening-the-back-of-a-lace-w-2026-08-05-20-36-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-walking-hand-in-hand-after-lakeside-wedding-2026-01-06-10-44-10-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/gorgeous-bride-and-stylish-groom-gently-hugging-on-2026-01-09-00-50-56-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-01-07-00-04-47-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-03-26-09-43-25-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/lovely-bride-reading-vows-to-her-husband-2026-01-09-12-03-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-holding-hands-with-a-floral-bouquet-2026-03-25-22-58-38-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embracing-on-their-wedding-day-2026-01-08-08-07-47-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-moment-between-a-groom-and-bride-2026-01-09-11-05-56-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-ceremony-of-couple-exchanging-rin-2026-01-08-06-20-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-and-groom-are-walking-in-the-park-along-2026-01-11-10-58-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-in-an-elegant-wedding-dress-holds-a-beau-2026-01-05-06-07-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-bouquet-held-by-woman-in-white-dress-2026-01-09-06-33-05-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-holding-hands-on-wedding-day-2026-01-05-05-40-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-rings-and-elegant-white-flower-bouquet-2026-03-25-09-55-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-in-white-wedding-dress-holding-bouquet-2026-03-26-03-59-20-utc.jpg"];
var sqPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-holding-hands-on-wedding-day-2026-01-11-08-12-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-in-wedding-dress-and-suit-2026-03-26-09-10-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/cheerful-married-couple-near-old-building-2026-01-09-08-42-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/hands-of-bride-and-groom-holding-flowers-2026-01-07-07-20-33-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-embracing-under-green-leaves-2026-01-09-07-31-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-hugging-on-rock-on-the-background-of-2026-03-24-09-11-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-kiss-between-couple-in-sunlight-2026-01-09-09-43-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/smiling-bride-and-groom-pose-outdoors-on-wedding-d-2026-03-25-02-19-07-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/walk-just-married-on-the-background-of-the-old-cas-2026-01-09-13-09-03-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-happy-bride-and-groom-in-a-summer-2026-03-25-23-44-54-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-a-summer-park-2026-01-09-14-26-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-formal-wear-embracing-outdoors-2026-01-11-08-14-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-day-stroll-on-a-grassy-summer-lawn-2026-01-07-00-35-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-holding-roses-bouquet-in-wedding-dress-2026-03-18-10-59-35-utc.jpg"];
var allPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-couple-in-love-a-guy-and-a-girl-on-a-walk-in-the-2026-01-07-00-24-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-happy-young-couple-in-walk-in-a-garden-a-man-in-2026-01-05-04-57-23-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-couple-kissing-each-other-in-park-2026-01-09-09-26-30-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-young-couple-kissing-outdoors-on-thei-2026-01-07-06-23-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-and-groom-embrace-at-night-2026-03-16-22-55-01-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-with-groom-embracing-her-2026-01-11-09-55-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-celebrating-their-wedding-day-tog-2026-01-11-09-56-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-holding-hands-on-wedding-day-2026-01-11-08-12-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-wedding-bouquet-held-by-a-loving-couple-2026-01-07-07-32-44-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-celebrate-with-wedding-guests-outd-2026-01-09-11-10-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-exchange-rings-at-wedding-ceremony-2026-01-07-07-32-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-bouquet-on-wedding-day-2026-03-09-05-39-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-hands-walking-in-woods-2026-03-10-01-03-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-holding-bouquet-in-their-hands-in-2026-01-11-08-15-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hug-while-on-a-walk-in-the-park-2026-03-24-23-46-52-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-in-wedding-dress-and-suit-2026-03-26-09-10-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-on-wedding-day-with-guests-2026-03-26-04-28-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-posing-and-hugging-in-hotel-room-2026-01-09-00-45-27-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walk-together-in-the-park-pretty-2026-03-19-22-04-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walking-through-beautiful-garden-t-2026-01-08-06-25-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-with-her-groom-on-wedding-day-2026-01-05-01-07-39-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bridesmaid-helping-bride-with-her-wedding-dress-2026-03-10-04-45-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bunch-of-fresh-flowers-at-the-garden-2026-01-07-23-43-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/cheerful-married-couple-near-old-building-2026-01-09-08-42-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-a-woman-fastening-the-back-of-a-lace-w-2026-08-05-20-36-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-bride-and-groom-holding-hands-at-a-wed-2026-01-09-10-40-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-vibrant-pink-red-and-white-flowers-2026-03-26-03-30-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-portrait-of-the-bride-and-groom-the-brid-2026-03-10-01-07-58-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-celebrate-wedding-on-rocky-shoreline-at-sun-2026-03-17-00-03-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-walking-hand-in-hand-after-lakeside-wedding-2026-01-06-10-44-10-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-bride-and-groom-holding-hands-at-wedding-2026-01-08-05-33-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-celebrate-wedding-in-a-lush-garden-2026-03-19-22-09-00-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-at-outdoor-wedding-ceremony-2026-01-09-10-01-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-surrounded-by-beautiful-nat-2026-01-09-10-57-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-wedding-bouquet-held-by-couple-close-up-2026-03-24-01-19-06-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/gorgeous-bride-and-stylish-groom-gently-hugging-on-2026-01-09-00-50-56-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/hands-of-bride-and-groom-holding-flowers-2026-01-07-07-20-33-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-01-07-00-04-47-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-03-26-09-43-25-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-posing-in-the-autumn-forest-2026-03-10-22-41-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-smiling-on-wedding-day-2026-01-11-09-56-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-embracing-under-green-leaves-2026-01-09-07-31-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-hugging-on-rock-on-the-background-of-2026-03-24-09-11-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-wedding-day-couple-posing-outdoors-together-2026-03-26-03-49-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/ill-stand-by-your-side-in-the-good-and-the-bad-2026-03-25-04-38-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/intimate-wedding-moment-with-rings-2026-01-08-00-29-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-holding-hands-and-looking-at-e-2026-01-05-23-53-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-on-a-green-forest-2026-01-06-11-09-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/lovely-bride-reading-vows-to-her-husband-2026-01-09-12-03-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-celebrate-wedding-day-in-natural-set-2026-01-09-09-21-40-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-holding-hands-at-wedding-ceremony-2026-01-08-06-58-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-holding-hands-with-a-floral-bouquet-2026-03-25-22-58-38-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-walking-in-amazing-blossoming-flowers-fi-2026-03-09-04-36-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embrace-on-wedding-day-in-nature-2026-01-08-23-53-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embracing-on-their-wedding-day-2026-01-08-08-07-47-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-flowers-on-wedding-day-2026-03-19-09-26-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-hands-at-wedding-reception-2026-01-07-23-20-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-moment-between-a-groom-and-bride-2026-01-09-11-05-56-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-ceremony-of-couple-exchanging-rin-2026-01-08-06-20-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-kiss-between-couple-in-sunlight-2026-01-09-09-43-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/shot-of-a-bride-and-bridegroom-holding-hands-walki-2026-01-08-00-25-39-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/silhouette-of-couple-embracing-near-water-at-sunse-2026-01-08-06-31-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/smiling-bride-and-groom-pose-outdoors-on-wedding-d-2026-03-25-02-19-07-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-and-groom-are-walking-in-the-park-along-2026-01-11-10-58-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-in-an-elegant-wedding-dress-holds-a-beau-2026-01-05-06-07-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/walk-just-married-on-the-background-of-the-old-cas-2026-01-09-13-09-03-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-bouquet-held-by-woman-in-white-dress-2026-01-09-06-33-05-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-happy-bride-and-groom-in-a-summer-2026-03-25-23-44-54-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-holding-hands-on-wedding-day-2026-01-05-05-40-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-a-summer-park-2026-01-09-14-26-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-formal-wear-embracing-outdoors-2026-01-11-08-14-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-day-stroll-on-a-grassy-summer-lawn-2026-01-07-00-35-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-rings-and-elegant-white-flower-bouquet-2026-03-25-09-55-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-holding-roses-bouquet-in-wedding-dress-2026-03-18-10-59-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-in-white-wedding-dress-holding-bouquet-2026-03-26-03-59-20-utc.jpg"];

var landIdx = 0, portIdx = 0, sqIdx = 0, allIdx = 0;
var maskedCount = 0;

for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];

    for (var k = 0; k < layoutLayer.pathItems.length; k++) {
        var pi = layoutLayer.pathItems[k];
        if (pi.guides || pi.clipping) continue;

        var gb = pi.geometricBounds;
        var cx = (gb[0] + gb[2]) / 2;
        var cy = (gb[1] + gb[3]) / 2;

        if (cx >= abLeft && cx <= abRight && cy <= abTop && cy >= abBottom) {
            var pw = gb[2] - gb[0];
            var ph = gb[1] - gb[3];

            if (pw > 25 && ph > 25) {
                var ratio = pw / ph;
                var chosenFile;
                if (ratio >= 1.15 && landPhotos.length > 0) {
                    chosenFile = landPhotos[landIdx % landPhotos.length];
                    landIdx++;
                } else if (ratio <= 0.85 && portPhotos.length > 0) {
                    chosenFile = portPhotos[portIdx % portPhotos.length];
                    portIdx++;
                } else if (sqPhotos.length > 0) {
                    chosenFile = sqPhotos[sqIdx % sqPhotos.length];
                    sqIdx++;
                } else {
                    chosenFile = allPhotos[allIdx % allPhotos.length];
                    allIdx++;
                }

                var pGroup = photoLayer.groupItems.add();

                var pPlaced = pGroup.placedItems.add();
                pPlaced.file = new File(chosenFile);

                var scaleFactor = Math.max(pw / pPlaced.width, ph / pPlaced.height);
                var newW = pPlaced.width * scaleFactor;
                var newH = pPlaced.height * scaleFactor;
                pPlaced.width = newW;
                pPlaced.height = newH;
                pPlaced.left = gb[0] + (pw - newW) / 2;
                pPlaced.top = gb[1] - (ph - newH) / 2;

                var maskPath = pi.duplicate(pGroup, ElementPlacement.PLACEATBEGINNING);
                maskPath.filled = false;
                maskPath.stroked = false;
                maskPath.clipping = true;

                pGroup.clipped = true;
                maskedCount++;
            }
        }
    }
}
log("Placed and masked " + maskedCount + " photos!");

doc.save();
log("Saved master document with masked photos.");

log("STEP 9: Exporting Populated Previews...");
var rawPopFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Raw_Populated");
var popBase = new File(rawPopFolder.fsName + "/pop.jpg");
doc.exportFile(popBase, ExportType.JPEG, exportOpts);
log("Populated previews exported!");

log("ALL DONE!");
logFile.close();
