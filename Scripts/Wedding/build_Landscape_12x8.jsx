
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

// 1. Open Source AI Layouts
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

// Index layout elements in source document
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

// 2. Create Target AI Document
var doc = app.documents.add(DocumentColorSpace.RGB, 864, 576);
doc.artboards[0].artboardRect = [0, 0, 864, -576];
doc.artboards[0].name = "P01_Landscape_12x8_wed_p01";

var spacing = 60;
var rowCols = 6;

// Create 21 more artboards in clean grid (4 rows of 6 cols)
for (var i = 1; i < 22; i++) {
    var col = i % rowCols;
    var row = Math.floor(i / rowCols);
    var l = col * (864 + spacing);
    var t = -row * (576 + spacing);
    var pNum = (i + 1 < 10 ? "0" : "") + (i + 1);
    var ab = doc.artboards.add([l, t, l + 864, t - 576]);
    ab.name = "P" + pNum + "_Landscape_12x8_wed_p" + pNum;
}

// 3. Setup Layers
var bgLayer = doc.layers.add();
bgLayer.name = "Backgrounds";

var photoLayer = doc.layers.add();
photoLayer.name = "Photos_Masked";

var layoutLayer = doc.layers[0];
layoutLayer.name = "Layout_Shapes";

bgLayer.zOrder(ZOrderMethod.SENDTOBACK);

// 4. Place 22 Backgrounds
var bgFiles = ["/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p01_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p02_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p03_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p04_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p05_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p06_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p07_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p08_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p09_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p10_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p11_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p12_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p13_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p14_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p15_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p16_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p17_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p18_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p19_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p20_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p21_5400x5400.jpg", "/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Backgorunds/wed_p22_5400x5400.jpg"];
for (var i = 0; i < 22; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];
    var abW = abRight - abLeft;
    var abH = abTop - abBottom;

    var bgFile = new File(bgFiles[i]);

    var clipGroup = bgLayer.groupItems.add();
    clipGroup.name = "Background_P" + (i + 1 < 10 ? "0" : "") + (i + 1);

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

// 5. Copy Layout Shapes
var srcABs = [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 59, 61, 62, 27, 41, 42];
for (var p = 0; p < 22; p++) {
    var sIdx = srcABs[p];
    var sR = srcDoc.artboards[sIdx].artboardRect;
    var tR = doc.artboards[p].artboardRect;
    var items = itemsByAB[sIdx];

    var pGroup = layoutLayer.groupItems.add();
    pGroup.name = "Layout_P" + (p + 1 < 10 ? "0" : "") + (p + 1);

    for (var m = 0; m < items.length; m++) {
        var itm = items[m];
        var dup = itm.duplicate(layoutLayer, ElementPlacement.PLACEATBEGINNING);
        dup.left = tR[0] + (itm.left - sR[0]);
        dup.top = tR[1] + (itm.top - sR[1]);
        dup.move(pGroup, ElementPlacement.PLACEATBEGINNING);
    }
}

// 6. Capture 22 Blank Artboards
var rawFolder = new Folder("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Previews/Landscape_12x8/Raw_Temp");
var capOpts = new ImageCaptureOptions();
capOpts.resolution = 100;
capOpts.antiAliasing = true;
capOpts.transparency = false;

for (var i = 0; i < 22; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/blank_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}

// 7. Recursive helper to extract all PathItems
function getAllPaths(container, out) {
    for (var i = 0; i < container.pathItems.length; i++) {
        out.push(container.pathItems[i]);
    }
    for (var g = 0; g < container.groupItems.length; g++) {
        getAllPaths(container.groupItems[g], out);
    }
}

var allLayoutPaths = [];
getAllPaths(layoutLayer, allLayoutPaths);

// 8. Place & Mask Photos inside every frame
var landPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-couple-in-love-a-guy-and-a-girl-on-a-walk-in-the-2026-01-07-00-24-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-couple-kissing-each-other-in-park-2026-01-09-09-26-30-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-celebrating-their-wedding-day-tog-2026-01-11-09-56-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-wedding-bouquet-held-by-a-loving-couple-2026-01-07-07-32-44-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-celebrate-with-wedding-guests-outd-2026-01-09-11-10-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-exchange-rings-at-wedding-ceremony-2026-01-07-07-32-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-hands-walking-in-woods-2026-03-10-01-03-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hug-while-on-a-walk-in-the-park-2026-03-24-23-46-52-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-on-wedding-day-with-guests-2026-03-26-04-28-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walking-through-beautiful-garden-t-2026-01-08-06-25-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bridesmaid-helping-bride-with-her-wedding-dress-2026-03-10-04-45-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bunch-of-fresh-flowers-at-the-garden-2026-01-07-23-43-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-bride-and-groom-holding-hands-at-a-wed-2026-01-09-10-40-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-vibrant-pink-red-and-white-flowers-2026-03-26-03-30-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-portrait-of-the-bride-and-groom-the-brid-2026-03-10-01-07-58-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-celebrate-wedding-on-rocky-shoreline-at-sun-2026-03-17-00-03-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-bride-and-groom-holding-hands-at-wedding-2026-01-08-05-33-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-celebrate-wedding-in-a-lush-garden-2026-03-19-22-09-00-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-at-outdoor-wedding-ceremony-2026-01-09-10-01-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-surrounded-by-beautiful-nat-2026-01-09-10-57-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-wedding-bouquet-held-by-couple-close-up-2026-03-24-01-19-06-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-posing-in-the-autumn-forest-2026-03-10-22-41-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-smiling-on-wedding-day-2026-01-11-09-56-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-wedding-day-couple-posing-outdoors-together-2026-03-26-03-49-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/ill-stand-by-your-side-in-the-good-and-the-bad-2026-03-25-04-38-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/intimate-wedding-moment-with-rings-2026-01-08-00-29-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-holding-hands-and-looking-at-e-2026-01-05-23-53-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-on-a-green-forest-2026-01-06-11-09-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-celebrate-wedding-day-in-natural-set-2026-01-09-09-21-40-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-holding-hands-at-wedding-ceremony-2026-01-08-06-58-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-walking-in-amazing-blossoming-flowers-fi-2026-03-09-04-36-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embrace-on-wedding-day-in-nature-2026-01-08-23-53-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-flowers-on-wedding-day-2026-03-19-09-26-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-hands-at-wedding-reception-2026-01-07-23-20-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/shot-of-a-bride-and-bridegroom-holding-hands-walki-2026-01-08-00-25-39-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/silhouette-of-couple-embracing-near-water-at-sunse-2026-01-08-06-31-21-utc.jpg"];
var portPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-happy-young-couple-in-walk-in-a-garden-a-man-in-2026-01-05-04-57-23-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-young-couple-kissing-outdoors-on-thei-2026-01-07-06-23-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-and-groom-embrace-at-night-2026-03-16-22-55-01-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-with-groom-embracing-her-2026-01-11-09-55-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-bouquet-on-wedding-day-2026-03-09-05-39-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-holding-bouquet-in-their-hands-in-2026-01-11-08-15-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-posing-and-hugging-in-hotel-room-2026-01-09-00-45-27-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walk-together-in-the-park-pretty-2026-03-19-22-04-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-with-her-groom-on-wedding-day-2026-01-05-01-07-39-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-a-woman-fastening-the-back-of-a-lace-w-2026-08-05-20-36-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-walking-hand-in-hand-after-lakeside-wedding-2026-01-06-10-44-10-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/gorgeous-bride-and-stylish-groom-gently-hugging-on-2026-01-09-00-50-56-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-01-07-00-04-47-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-03-26-09-43-25-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/lovely-bride-reading-vows-to-her-husband-2026-01-09-12-03-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-holding-hands-with-a-floral-bouquet-2026-03-25-22-58-38-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embracing-on-their-wedding-day-2026-01-08-08-07-47-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-moment-between-a-groom-and-bride-2026-01-09-11-05-56-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-ceremony-of-couple-exchanging-rin-2026-01-08-06-20-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-and-groom-are-walking-in-the-park-along-2026-01-11-10-58-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-in-an-elegant-wedding-dress-holds-a-beau-2026-01-05-06-07-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-bouquet-held-by-woman-in-white-dress-2026-01-09-06-33-05-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-holding-hands-on-wedding-day-2026-01-05-05-40-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-rings-and-elegant-white-flower-bouquet-2026-03-25-09-55-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-in-white-wedding-dress-holding-bouquet-2026-03-26-03-59-20-utc.jpg"];
var sqPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-holding-hands-on-wedding-day-2026-01-11-08-12-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-in-wedding-dress-and-suit-2026-03-26-09-10-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/cheerful-married-couple-near-old-building-2026-01-09-08-42-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/hands-of-bride-and-groom-holding-flowers-2026-01-07-07-20-33-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-embracing-under-green-leaves-2026-01-09-07-31-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-hugging-on-rock-on-the-background-of-2026-03-24-09-11-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-kiss-between-couple-in-sunlight-2026-01-09-09-43-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/smiling-bride-and-groom-pose-outdoors-on-wedding-d-2026-03-25-02-19-07-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/walk-just-married-on-the-background-of-the-old-cas-2026-01-09-13-09-03-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-happy-bride-and-groom-in-a-summer-2026-03-25-23-44-54-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-a-summer-park-2026-01-09-14-26-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-formal-wear-embracing-outdoors-2026-01-11-08-14-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-day-stroll-on-a-grassy-summer-lawn-2026-01-07-00-35-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-holding-roses-bouquet-in-wedding-dress-2026-03-18-10-59-35-utc.jpg"];
var allPhotos = ["/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-couple-in-love-a-guy-and-a-girl-on-a-walk-in-the-2026-01-07-00-24-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/a-happy-young-couple-in-walk-in-a-garden-a-man-in-2026-01-05-04-57-23-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-couple-kissing-each-other-in-park-2026-01-09-09-26-30-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/affectionate-young-couple-kissing-outdoors-on-thei-2026-01-07-06-23-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-and-groom-embrace-at-night-2026-03-16-22-55-01-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-bride-with-groom-embracing-her-2026-01-11-09-55-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-celebrating-their-wedding-day-tog-2026-01-11-09-56-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-couple-holding-hands-on-wedding-day-2026-01-11-08-12-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/beautiful-wedding-bouquet-held-by-a-loving-couple-2026-01-07-07-32-44-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-celebrate-with-wedding-guests-outd-2026-01-09-11-10-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-exchange-rings-at-wedding-ceremony-2026-01-07-07-32-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-bouquet-on-wedding-day-2026-03-09-05-39-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hold-hands-walking-in-woods-2026-03-10-01-03-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-holding-bouquet-in-their-hands-in-2026-01-11-08-15-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-hug-while-on-a-walk-in-the-park-2026-03-24-23-46-52-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-in-wedding-dress-and-suit-2026-03-26-09-10-33-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-on-wedding-day-with-guests-2026-03-26-04-28-53-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-posing-and-hugging-in-hotel-room-2026-01-09-00-45-27-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walk-together-in-the-park-pretty-2026-03-19-22-04-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-and-groom-walking-through-beautiful-garden-t-2026-01-08-06-25-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bride-with-her-groom-on-wedding-day-2026-01-05-01-07-39-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bridesmaid-helping-bride-with-her-wedding-dress-2026-03-10-04-45-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/bunch-of-fresh-flowers-at-the-garden-2026-01-07-23-43-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/cheerful-married-couple-near-old-building-2026-01-09-08-42-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-a-woman-fastening-the-back-of-a-lace-w-2026-08-05-20-36-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-bride-and-groom-holding-hands-at-a-wed-2026-01-09-10-40-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-of-vibrant-pink-red-and-white-flowers-2026-03-26-03-30-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/close-up-portrait-of-the-bride-and-groom-the-brid-2026-03-10-01-07-58-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-celebrate-wedding-on-rocky-shoreline-at-sun-2026-03-17-00-03-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/couple-walking-hand-in-hand-after-lakeside-wedding-2026-01-06-10-44-10-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-bride-and-groom-holding-hands-at-wedding-2026-01-08-05-33-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-celebrate-wedding-in-a-lush-garden-2026-03-19-22-09-00-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-at-outdoor-wedding-ceremony-2026-01-09-10-01-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-couple-embrace-surrounded-by-beautiful-nat-2026-01-09-10-57-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/elegant-wedding-bouquet-held-by-couple-close-up-2026-03-24-01-19-06-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/gorgeous-bride-and-stylish-groom-gently-hugging-on-2026-01-09-00-50-56-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/hands-of-bride-and-groom-holding-flowers-2026-01-07-07-20-33-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-01-07-00-04-47-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/handsome-young-man-in-stylish-suit-with-brunette-b-2026-03-26-09-43-25-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-posing-in-the-autumn-forest-2026-03-10-22-41-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-bride-and-groom-smiling-on-wedding-day-2026-01-11-09-56-51-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-embracing-under-green-leaves-2026-01-09-07-31-26-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-couple-hugging-on-rock-on-the-background-of-2026-03-24-09-11-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/happy-wedding-day-couple-posing-outdoors-together-2026-03-26-03-49-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/ill-stand-by-your-side-in-the-good-and-the-bad-2026-03-25-04-38-42-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/intimate-wedding-moment-with-rings-2026-01-08-00-29-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-holding-hands-and-looking-at-e-2026-01-05-23-53-15-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/just-married-couple-on-a-green-forest-2026-01-06-11-09-28-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/lovely-bride-reading-vows-to-her-husband-2026-01-09-12-03-57-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-celebrate-wedding-day-in-natural-set-2026-01-09-09-21-40-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/loving-couple-holding-hands-at-wedding-ceremony-2026-01-08-06-58-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-holding-hands-with-a-floral-bouquet-2026-03-25-22-58-38-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/newlyweds-walking-in-amazing-blossoming-flowers-fi-2026-03-09-04-36-36-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embrace-on-wedding-day-in-nature-2026-01-08-23-53-24-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-embracing-on-their-wedding-day-2026-01-08-08-07-47-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-flowers-on-wedding-day-2026-03-19-09-26-50-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-couple-holding-hands-at-wedding-reception-2026-01-07-23-20-29-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-moment-between-a-groom-and-bride-2026-01-09-11-05-56-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-ceremony-of-couple-exchanging-rin-2026-01-08-06-20-43-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/romantic-wedding-kiss-between-couple-in-sunlight-2026-01-09-09-43-02-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/shot-of-a-bride-and-bridegroom-holding-hands-walki-2026-01-08-00-25-39-utc.jpeg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/silhouette-of-couple-embracing-near-water-at-sunse-2026-01-08-06-31-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/smiling-bride-and-groom-pose-outdoors-on-wedding-d-2026-03-25-02-19-07-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-and-groom-are-walking-in-the-park-along-2026-01-11-10-58-34-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/the-bride-in-an-elegant-wedding-dress-holds-a-beau-2026-01-05-06-07-13-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/walk-just-married-on-the-background-of-the-old-cas-2026-01-09-13-09-03-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-bouquet-held-by-woman-in-white-dress-2026-01-09-06-33-05-utc.JPG", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-happy-bride-and-groom-in-a-summer-2026-03-25-23-44-54-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-holding-hands-on-wedding-day-2026-01-05-05-40-14-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-a-summer-park-2026-01-09-14-26-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-couple-in-formal-wear-embracing-outdoors-2026-01-11-08-14-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-day-stroll-on-a-grassy-summer-lawn-2026-01-07-00-35-19-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/wedding-rings-and-elegant-white-flower-bouquet-2026-03-25-09-55-21-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-holding-roses-bouquet-in-wedding-dress-2026-03-18-10-59-35-utc.jpg", "/Users/cp/Ronak/CC/Photobooks/Image_Library/Wedding/woman-in-white-wedding-dress-holding-bouquet-2026-03-26-03-59-20-utc.jpg"];

var landIdx = 0, portIdx = 0, sqIdx = 0, allIdx = 0;

for (var i = 0; i < 22; i++) {
    var ab = doc.artboards[i];
    var r = ab.artboardRect;
    var abLeft = r[0];
    var abTop = r[1];
    var abRight = r[2];
    var abBottom = r[3];

    var pagePhotoGroup = photoLayer.groupItems.add();
    pagePhotoGroup.name = "Photos_Page_" + (i + 1 < 10 ? "0" : "") + (i + 1);

    for (var k = 0; k < allLayoutPaths.length; k++) {
        var pi = allLayoutPaths[k];
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

                var pGroup = pagePhotoGroup.groupItems.add();

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
            }
        }
    }
}

// 9. Hide placeholder vector gray boxes on Layout layer so masked photos show cleanly
for (var k = 0; k < allLayoutPaths.length; k++) {
    allLayoutPaths[k].hidden = true;
}
app.redraw();

// 10. Capture 22 Populated Artboards
for (var i = 0; i < 22; i++) {
    var r = doc.artboards[i].artboardRect;
    var f = new File(rawFolder.fsName + "/pop_ab" + (i + 1 < 10 ? "0" : "") + (i + 1) + ".png");
    doc.imageCapture(f, r, capOpts);
}

// 11. Restore Layout Shapes visibility so user can edit both layers
for (var k = 0; k < allLayoutPaths.length; k++) {
    allLayoutPaths[k].hidden = false;
}

// 12. Save Master AI Document non-interactively and Close
var targetFile = new File("/Users/cp/Ronak/CC/Photobooks/New/Wedding-Test/Wedding_Landscape_12x8.ai");
var saveOpts = new IllustratorSaveOptions();
saveOpts.pdfCompatible = false;
saveOpts.compressed = true;
doc.saveAs(targetFile, saveOpts);
doc.close(SaveOptions.DONOTSAVECHANGES);
