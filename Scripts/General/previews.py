#!/usr/bin/env python3
"""
Preview compositor.

Builds the two developer preview sets from the 5400 masters:
  A  placeholder — photo slots as flat grey boxes
  B  filled      — the SAME slots filled with photographs

A and B come from one layout resolution in a single pass, so their geometry is
pixel-identical by construction.

MARGIN IS PHYSICAL. Books are 10x10, 8x12 and 12x8 inches with a 1 inch margin,
so the margin fraction differs per axis per book. A single percentage would give
physically unequal borders.
"""

import os, json, glob
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None

LONG_EDGE = 1000
MARGIN_IN = 1.0
GUTTER_IN = 0.28
GREY = (138, 138, 138)

# name -> (width_in, height_in)
BOOKS = {
    "square":    (10, 10),
    "portrait":  (8, 12),
    "landscape": (12, 8),
}

# Fonts resolve in this order: next to this script, the working directory, a
# local cache, and finally a one-time download into that cache. This removes
# the fonts/ directory as a hard dependency — the script is self-sufficient
# wherever it is run from, including inside a skill's script folder.
_HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "photobook_fonts")

_FONT_URLS = {
    "Anton.ttf":      "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
    "Caveat.ttf":     "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat%5Bwght%5D.ttf",
    "Montserrat.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
}


def _font(name):
    for base in (_HERE, os.getcwd()):
        cand = os.path.join(base, "fonts", name)
        if os.path.exists(cand):
            return cand
    cached = os.path.join(_CACHE, name)
    if os.path.exists(cached):
        return cached
    try:
        import urllib.request
        os.makedirs(_CACHE, exist_ok=True)
        urllib.request.urlretrieve(_FONT_URLS[name], cached)
        print(f"fetched font {name} -> {cached}")
        return cached
    except Exception as e:
        raise FileNotFoundError(
            f"font {name} not found in {_HERE}/fonts or {os.getcwd()}/fonts, "
            f"and download failed ({e}). Place the fonts/ directory beside the "
            f"script, or substitute your licensed faces.")


F_DISPLAY = _font("Anton.ttf")
F_SCRIPT  = _font("Caveat.ttf")
F_BODY    = _font("Montserrat.ttf")

# Real copy per page. Same placement as the supplied layout samples; only the
# words change. Keyed by page stem, with a neutral fallback.
COPY = {
    "love_p01": {"caption": "OUR LOVE STORY"},
    "love_p02": {"heading": "Just the two of us",
                 "body": "Every ordinary day became something worth keeping, "
                         "simply because we spent it together."},
    "love_p03": {"heading": "Where it began",
                 "body": "A quiet afternoon, a shared laugh, and the start of "
                         "every story we would tell for years after."},
}
FALLBACK = {"caption": "OUR LOVE STORY",
            "heading": "Us, always",
            "body": "The small moments we never thought to photograph turned "
                    "out to be the ones we remember best."}

MASTERS = "out/masters_5400x5400"
PHOTOS = "photos"
VALJSON = "validation_wedding_gold.json"
OUT = "previews"


# ---------------------------------------------------------------- geometry
def preview_size(book):
    w_in, h_in = BOOKS[book]
    if w_in >= h_in:
        return LONG_EDGE, round(LONG_EDGE * h_in / w_in)
    return round(LONG_EDGE * w_in / h_in), LONG_EDGE


def content_box(book):
    """Content rect in normalised page coords, from a physical 1in margin."""
    w_in, h_in = BOOKS[book]
    mx, my = MARGIN_IN / w_in, MARGIN_IN / h_in
    return mx, my, 1 - mx, 1 - my


def crop_master(master, book):
    """Centre-crop the square master to the book ratio, then downscale."""
    w_in, h_in = BOOKS[book]
    W, H = master.size
    target = w_in / h_in
    if target >= 1:
        ch = round(W / target)
        box = (0, (H - ch) // 2, W, (H - ch) // 2 + ch)
    else:
        cw = round(H * target)
        box = ((W - cw) // 2, 0, (W - cw) // 2 + cw, H)
    return master.crop(box).resize(preview_size(book), Image.LANCZOS)


def remap_band(book, band_frac):
    """
    Translate a band position measured on the SQUARE MASTER into the cropped
    page. Landscape takes the master's middle 3600px, so a band at 0.678 of the
    master sits at 0.767 of the landscape page. Square and portrait keep the
    full height, so they map 1:1.
    """
    if band_frac is None:
        return None
    w_in, h_in = BOOKS[book]
    target = w_in / h_in
    if target <= 1:
        return band_frac
    ch = 1.0 / target                      # cropped height as a fraction of master
    top = (1.0 - ch) / 2
    y = (band_frac - top) / ch
    return y if 0.22 <= y <= 0.88 else None   # unusable band -> caller falls back


def pick_photo(photos, w, h, used):
    """Choose the photo whose aspect is closest to the slot, preferring unused."""
    import math
    want = w / h
    ranked = sorted(photos, key=lambda p: abs(math.log((p.width / p.height) / want)))
    for p in ranked:
        if id(p) not in used:
            used.add(id(p))
            return p
    return ranked[0]


def cover(img, w, h):
    """Crop-to-fill: fills the slot with no distortion."""
    if w <= 0 or h <= 0:
        return None
    src = img.width / img.height
    dst = w / h
    if src > dst:
        nw = round(img.height * dst)
        img = img.crop(((img.width - nw) // 2, 0, (img.width - nw) // 2 + nw, img.height))
    else:
        nh = round(img.width / dst)
        img = img.crop((0, (img.height - nh) // 2, img.width, (img.height - nh) // 2 + nh))
    return img.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- layouts
def layout_hero(book, band_frac):
    """
    Family A — one photo at full content width, caption below.
    On a banded background the photo stops at the band boundary so the caption
    lands in the quiet field. Falls back to 0.62 when the page has no band.
    """
    x0, y0, x1, y1 = content_box(book)
    bottom = band_frac if band_frac else 0.62
    bottom = max(y0 + 0.25, min(bottom - 0.012, y1 - 0.18))
    return {
        "slots": [(x0, y0, x1, bottom)],
        "text": {"kind": "caption", "box": (x0, bottom, x1, y1)},
    }


def layout_three(book):
    """Family B — 2x2 grid; cells 1-3 photos, cell 4 the text block."""
    x0, y0, x1, y1 = content_box(book)
    w_in, h_in = BOOKS[book]
    gx, gy = GUTTER_IN / w_in, GUTTER_IN / h_in
    cw = (x1 - x0 - gx) / 2
    ch = (y1 - y0 - gy) / 2
    return {
        "slots": [
            (x0, y0, x0 + cw, y0 + ch),
            (x0 + cw + gx, y0, x1, y0 + ch),
            (x0, y0 + ch + gy, x0 + cw, y1),
        ],
        "text": {"kind": "block", "box": (x0 + cw + gx, y0 + ch + gy, x1, y1)},
    }


# ---------------------------------------------------------------- readability
def _rel_lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = [f(x) for x in c]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1, c2):
    a, b = _rel_lum(c1), _rel_lum(c2)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def prepare_text_zone(page, box, pad=0.02):
    """
    Guarantee the text is legible wherever it lands.

    Lays a soft-edged scrim over the text area, strengthening it step by step
    until the measured contrast between the chosen ink and the actual pixels
    behind it clears 4.5:1. Returns the ink colour to draw with.

    The scrim is toned from the page's own paper colour, so it reads as part of
    the design rather than a pasted box.
    """
    from PIL import ImageFilter, ImageStat
    W, H = page.size
    x0 = max(0, int((box[0] - pad) * W)); y0 = max(0, int((box[1] - pad) * H))
    x1 = min(W, int((box[2] + pad) * W)); y1 = min(H, int((box[3] + pad) * H))
    if x1 <= x0 or y1 <= y0:
        return (17, 17, 17)

    region = page.crop((x0, y0, x1, y1))
    # paper tone = the page's own light end, so the scrim never looks foreign
    grey = region.convert("L")
    px = sorted(grey.getdata())
    light = px[int(len(px) * 0.92)]
    dark = px[int(len(px) * 0.08)]
    page_is_light = ImageStat.Stat(grey).mean[0] > 128
    scrim = (255, 255, 255) if page_is_light else (10, 10, 12)
    ink = (17, 17, 17) if page_is_light else (255, 255, 255)

    # soft-edged mask so the scrim has no hard boundary
    mask = Image.new("L", region.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [4, 4, region.width - 5, region.height - 5],
        radius=max(8, region.width // 22), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(6, region.width // 40)))

    overlay = Image.new("RGB", region.size, scrim)

    # Two conditions, not one. Mean contrast alone is not enough: a cream page
    # scattered with flowers has a light mean and passes instantly, while the
    # text still sits on top of petals. So also require the zone to be visually
    # QUIET — low local variation — before accepting it.
    inner = (int(region.width * .08), int(region.height * .08),
             int(region.width * .92), int(region.height * .92))
    for alpha in (0.0, 0.45, 0.62, 0.76, 0.86, 0.93):
        blended = Image.blend(region, overlay, alpha) if alpha else region
        test = Image.composite(blended, region, mask)
        probe = test.crop(inner)
        st = ImageStat.Stat(probe)
        mean = tuple(int(v) for v in st.mean[:3])
        busy = ImageStat.Stat(probe.convert("L")).stddev[0]
        if contrast(ink, mean) >= 4.5 and busy <= 11.0:
            if alpha:
                page.paste(test, (x0, y0))
            print(f"    text zone: scrim {alpha:.2f}  contrast "
                  f"{contrast(ink, mean):.1f}  busy {busy:.1f}  "
                  f"ink {'dark' if ink[0] < 128 else 'light'}")
            return ink
    page.paste(Image.composite(Image.blend(region, overlay, 0.96), region, mask), (x0, y0))
    return ink


# ---------------------------------------------------------------- text
def fit_font(path, text, max_w, max_h, start):
    size = start
    while size > 8:
        f = ImageFont.truetype(path, size)
        b = f.getbbox(text)
        if (b[2] - b[0]) <= max_w and (b[3] - b[1]) <= max_h:
            return f
        size -= 2
    return ImageFont.truetype(path, 8)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_caption(im, box, copy):
    text = copy.get("caption", FALLBACK["caption"])
    ink = prepare_text_zone(im, box)
    d = ImageDraw.Draw(im)
    W, H = im.size
    x0, y0, x1, y1 = [box[0] * W, box[1] * H, box[2] * W, box[3] * H]
    f = fit_font(F_DISPLAY, text, (x1 - x0) * 0.94, (y1 - y0) * 0.42, 200)
    b = f.getbbox(text)
    d.text(((x0 + x1) / 2 - (b[2] - b[0]) / 2 - b[0],
            (y0 + y1) / 2 - (b[3] - b[1]) / 2 - b[1]),
           text, font=f, fill=ink)


def draw_block(im, box, copy):
    heading = copy.get("heading", FALLBACK["heading"])
    body = copy.get("body", FALLBACK["body"])
    ink = prepare_text_zone(im, box)
    d = ImageDraw.Draw(im)
    W, H = im.size
    x0, y0, x1, y1 = [box[0] * W, box[1] * H, box[2] * W, box[3] * H]
    bw = (x1 - x0)
    hf = fit_font(F_SCRIPT, heading, bw * 0.92, (y1 - y0) * 0.26, 120)
    bf = ImageFont.truetype(F_BODY, max(9, int(bw * 0.066)))
    lines = wrap(d, body, bf, bw * 0.94)
    lh = bf.size * 1.42
    hb = hf.getbbox(heading)
    total = (hb[3] - hb[1]) + lh * len(lines) + bw * 0.05
    cy = (y0 + y1) / 2 - total / 2
    d.text(((x0 + x1) / 2 - (hb[2] - hb[0]) / 2 - hb[0], cy - hb[1]),
           heading, font=hf, fill=ink)
    cy += (hb[3] - hb[1]) + bw * 0.05
    for ln in lines:
        d.text(((x0 + x1) / 2 - d.textlength(ln, font=bf) / 2, cy), ln,
               font=bf, fill=ink)
        cy += lh


# ---------------------------------------------------------------- render
def render(master, book, layout, photos, filled, copy):
    page = crop_master(master, book).convert("RGB")
    W, H = page.size
    used = set()
    for i, (sx0, sy0, sx1, sy1) in enumerate(layout["slots"]):
        px0, py0 = round(sx0 * W), round(sy0 * H)
        px1, py1 = round(sx1 * W), round(sy1 * H)
        if filled:
            src = pick_photo(photos, px1 - px0, py1 - py0, used)
            page.paste(cover(src, px1 - px0, py1 - py0), (px0, py0))
        else:
            ImageDraw.Draw(page).rectangle([px0, py0, px1 - 1, py1 - 1], fill=GREY)
    t = layout["text"]
    (draw_caption if t["kind"] == "caption" else draw_block)(page, t["box"], copy)
    return page


def main():
    global MASTERS, PHOTOS, VALJSON, OUT
    import sys
    if len(sys.argv) > 4:
        MASTERS, PHOTOS, VALJSON, OUT = sys.argv[1:5]
    os.makedirs(OUT, exist_ok=True)
    band = {}
    if os.path.exists(VALJSON):
        for r in json.load(open(VALJSON)):
            band[r["page"]] = (r["band_y"] / 5400) if r["band_msg"] == "inside" else None

    photos = [Image.open(p).convert("RGB") for p in sorted(glob.glob(f"{PHOTOS}/*.jpg"))]
    pages = sorted(glob.glob(f"{MASTERS}/*.jpg"))
    made = 0
    for mp in pages:
        stem = os.path.basename(mp).split("_5400")[0]
        master = Image.open(mp)
        b = band.get(stem)
        for book in BOOKS:
            bb = remap_band(book, b)
            lay = layout_hero(book, bb) if bb else layout_three(book)
            for filled in (False, True):
                im = render(master, book, lay, photos, filled, COPY.get(stem, FALLBACK))
                tag = "filled" if filled else "placeholder"
                im.save(f"{OUT}/{stem}_{book}_{tag}.jpg", quality=88, optimize=True)
                made += 1
        print(f"{stem}: {'hero (banded @%.3f)' % b if b else 'three-up'}  -> 6 previews")
    print(f"\n{made} previews written to {OUT}/")


if __name__ == "__main__":
    main()
