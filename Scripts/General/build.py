#!/usr/bin/env python3
"""
Photobook background pipeline.

Master canvas : 5600 x 5600  (min viable is 5400; 5600 adds 200px slack per edge)
Trims (centre-cropped from the master, never upscaled):
    square    4000 x 4000
    portrait  3600 x 5400
    landscape 5400 x 3600

Universal safe zone = central 3600 x 3600 (the region every trim contains).
"""

import os, glob
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None

MASTER = 5600
TRIMS = {
    "square":    (4000, 4000),
    "portrait":  (3600, 5400),
    "landscape": (5400, 3600),
}
PROOF_COLORS = {           # matches the reference proof convention
    "landscape": (60, 200, 90),
    "portrait":  (235, 70, 60),
    "square":    (95, 105, 225),
}
SAFE = 3600

OUT = "/agent/workspace/photobook/out"
DIRS = {
    "master":    f"{OUT}/01_masters_5600x5600",
    "square":    f"{OUT}/02_square_4000x4000",
    "portrait":  f"{OUT}/03_portrait_3600x5400",
    "landscape": f"{OUT}/04_landscape_5400x3600",
    "proof":     f"{OUT}/05_crop_proofs",
}


def centre_box(w, h, canvas=MASTER):
    """Centred crop window for a trim inside the master."""
    left = (canvas - w) // 2
    top = (canvas - h) // 2
    return (left, top, left + w, top + h)


# Image models often render the artwork as a "sheet" with a thin lighter margin,
# or leave a soft edge artefact. Shaving the outer 3% before upscaling removes
# that generically, so no page needs a hand fix.
GUARD_PCT = 0.03


def upscale_master(src_path):
    im = Image.open(src_path).convert("RGB")
    g = int(min(im.size) * GUARD_PCT)
    if g:
        im = im.crop((g, g, im.width - g, im.height - g))
    if im.size != (MASTER, MASTER):
        # Lanczos: preserves soft watercolour gradients without inventing
        # the crunchy false detail an ESRGAN-style upscaler adds to smooth areas.
        im = im.resize((MASTER, MASTER), Image.LANCZOS)
    return im


def make_proof(master, path):
    """Guide overlay: the three crop frames + the universal safe zone."""
    proof = master.copy()
    d = ImageDraw.Draw(proof)
    for name in ("landscape", "portrait", "square"):
        w, h = TRIMS[name]
        d.rectangle(centre_box(w, h), outline=PROOF_COLORS[name], width=14)
    d.rectangle(centre_box(SAFE, SAFE), outline=(20, 20, 20), width=8)
    proof.resize((1600, 1600), Image.LANCZOS).save(path, quality=92)


def validate_band(master):
    """
    Report the strongest horizontal tonal break. If a page uses a banded
    layout, that boundary must fall inside y 1000-4600 or one of the three
    trims loses a zone.
    """
    import statistics
    g = master.convert("L").resize((64, MASTER // 10), Image.LANCZOS)
    rows = [statistics.mean(g.crop((0, y, 64, y + 1)).getdata()) for y in range(g.height)]
    deltas = [(abs(rows[i + 1] - rows[i]), i) for i in range(len(rows) - 1)]
    mx, idx = max(deltas)
    y = int((idx / g.height) * MASTER)
    return y, mx


def main():
    for p in DIRS.values():
        os.makedirs(p, exist_ok=True)

    sources = sorted(glob.glob("/agent/workspace/photobook/src/*.png"))
    for src in sources:
        stem = os.path.splitext(os.path.basename(src))[0]
        master = upscale_master(src)
        master.save(f"{DIRS['master']}/{stem}_master_5600x5600.jpg",
                    quality=96, subsampling=0)

        for name, (w, h) in TRIMS.items():
            master.crop(centre_box(w, h)).save(
                f"{DIRS[name]}/{stem}_{name}_{w}x{h}.jpg",
                quality=96, subsampling=0, dpi=(300, 300))

        make_proof(master, f"{DIRS['proof']}/{stem}_crop_proof.jpg")

        y, mx = validate_band(master)
        flag = "inside" if 1000 <= y <= 4600 else "OUTSIDE -- unsafe"
        print(f"{stem}: strongest horizontal break at y={y} ({flag}), delta={mx:.1f}")

    print(f"\n{len(sources)} pages -> master + 3 trims + proof each")


if __name__ == "__main__":
    main()
