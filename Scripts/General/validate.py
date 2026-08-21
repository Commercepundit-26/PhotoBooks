#!/usr/bin/env python3
"""
Automated crop-safety validator + master builder.

Replaces per-page visual review with numeric tests for the failure modes that
actually occur. Every check is cheap, deterministic and runs locally.

    MASTER 5400 x 5400 @ 72 DPI
    SAFE ZONE central 3600 x 3600 (x/y 900-4500)

Checks
  1 EDGE_FRAME    outer ring vs next ring inward — catches sheet edges, white
                  margins, printed borders
  2 EDGE_STEP     abrupt long-run luminance step inside the outer 8% — catches
                  spine gutters, page edges, folds
  3 CORNER_SPREAD luminance spread across the 4 corners — catches mockups,
                  props and one-sided vignettes
  4 LR_SYMMETRY   left strip vs right strip — THE core test: if these match,
                  cropping from either side cannot look odd
  5 BAND          if a horizontal band exists, its boundary must sit inside
                  y 900-4500 or a trim loses a zone
  6 FOCAL         centre patch contrast vs global — catches a big hero object
  7 PALETTE       share of pixels outside the locked gold/ivory hue range —
                  enforces one design language across all 22 pages
"""

import os, glob, sys, json
from PIL import Image, ImageStat

Image.MAX_IMAGE_PIXELS = None

MASTER = 5400
DPI = 72
SAFE_MIN, SAFE_MAX = 900, 4500
GUARD_PCT = 0.03

# thresholds tuned so a clean page passes and the observed failures trip
T = {
    # calibrated against 3 known-good pages and 1 known-bad book-photo render
    "edge_frame":    14.0,   # max mean-luminance delta, outer ring vs inward
    "edge_step":     20.0,   # max abrupt step inside the outer 8%, per edge
    "corner_spread": 26.0,   # max left-vs-right corner delta
    "lr_symmetry":   11.0,   # max mean-luminance delta, left vs right strip
    "focal":         22.0,   # max centre-vs-global mean delta
    "palette":       0.06,   # max share of off-palette pixels
    "ink_min":       0.50,   # min share of ink inside the safe window per axis
}

SRC = "/agent/workspace/photobook/src"
OUT = "/agent/workspace/photobook/out/masters_5400x5400"


def L(im):
    return im.convert("L")


def mean(im):
    return ImageStat.Stat(L(im)).mean[0]


def build_master(path):
    im = Image.open(path).convert("RGB")
    g = int(min(im.size) * GUARD_PCT)
    if g:
        im = im.crop((g, g, im.width - g, im.height - g))
    if im.size != (MASTER, MASTER):
        im = im.resize((MASTER, MASTER), Image.LANCZOS)
    return im


def check_edge_frame(im):
    w, h = im.size
    r = int(w * 0.02)
    ring_out = [im.crop((0, 0, w, r)), im.crop((0, h - r, w, h)),
                im.crop((0, 0, r, h)), im.crop((w - r, 0, w, h))]
    ring_in = [im.crop((0, r, w, 2 * r)), im.crop((0, h - 2 * r, w, h - r)),
               im.crop((r, 0, 2 * r, h)), im.crop((w - 2 * r, 0, w - r, h))]
    return max(abs(mean(a) - mean(b)) for a, b in zip(ring_out, ring_in))


def check_edge_step(im):
    """
    Scan inward from each edge for an abrupt full-length luminance step.
    Each edge is its own sequence — comparing the top edge against the bottom
    edge would flag every legitimately banded page.
    """
    w, h = im.size
    band = int(w * 0.08)
    g = L(im)
    seqs = [
        [mean(g.crop((x, 0, x + 12, h))) for x in range(0, band, 12)],                # left
        [mean(g.crop((x, 0, x + 12, h))) for x in range(w - band, w - 12, 12)],       # right
        [mean(g.crop((0, y, w, y + 12))) for y in range(0, band, 12)],                # top
        [mean(g.crop((0, y, w, y + 12))) for y in range(h - band, h - 12, 12)],       # bottom
    ]
    def smooth(seq, k=5):
        # kills the periodic ripple of a regular grid/stripe/dot pattern while
        # leaving a genuine sheet edge or gutter intact
        return [sum(seq[max(0, i - k // 2):i + k // 2 + 1]) /
                len(seq[max(0, i - k // 2):i + k // 2 + 1]) for i in range(len(seq))]

    worst = 0.0
    for seq in seqs:
        s = smooth(seq)
        for i in range(len(s) - 1):
            worst = max(worst, abs(s[i + 1] - s[i]))
    return worst


def check_corner_spread(im):
    """
    Compare corners in HORIZONTAL pairs only. A banded page legitimately has
    dark top corners and light bottom corners; what must never differ is left
    versus right, since that is what left/right cropping exposes.
    """
    w, h = im.size
    s = int(w * 0.12)
    tl, tr = mean(im.crop((0, 0, s, s))), mean(im.crop((w - s, 0, w, s)))
    bl, br = mean(im.crop((0, h - s, s, h))), mean(im.crop((w - s, h - s, w, h)))
    return max(abs(tl - tr), abs(bl - br))


def check_lr_symmetry(im):
    w, h = im.size
    s = int(w * 0.06)
    left, right = im.crop((0, 0, s, h)), im.crop((w - s, 0, w, h))
    top, bottom = im.crop((0, 0, w, s)), im.crop((0, h - s, w, h))
    # left/right is the hard requirement; top/bottom is reported only
    return abs(mean(left) - mean(right)), abs(mean(top) - mean(bottom))


def check_band(im):
    """
    A band is two SUSTAINED regions, not a local step. For each candidate
    boundary compare the mean of everything above it with everything below.
    A periodic pattern (grid, dot rows, motif rows) scores near zero here,
    which is what a local adjacent-row difference got wrong.
    """
    import statistics
    g = L(im).resize((64, 180), Image.LANCZOS)
    rows = [statistics.mean(g.crop((0, y, 64, y + 1)).getdata()) for y in range(180)]

    best, best_i = 0.0, 90
    for i in range(18, 162):                      # ignore the outer 10%
        above = statistics.mean(rows[:i])
        below = statistics.mean(rows[i:])
        d = abs(above - below)
        if d > best:
            best, best_i = d, i

    y = int((best_i / 180) * MASTER)
    if best < 6:
        return y, best, True, "no band"
    ok = SAFE_MIN <= y <= SAFE_MAX
    return y, best, ok, "inside" if ok else "OUTSIDE SAFE ZONE"


def check_ink_distribution(im):
    """
    Share of the page's visual 'ink' that falls inside the safe window on each
    axis. Catches soft-gradient bands that check_band misses: if most of the
    interest sits outside y 900-4500, the landscape crop returns a blank page.
    An evenly covered page scores ~0.67 ((4500-900)/5400) on both axes.
    """
    g = L(im).resize((90, 90), Image.LANCZOS)
    px = list(g.getdata())
    paper = sorted(px)[int(len(px) * 0.95)]          # paper-white reference
    lo, hi = int(90 * SAFE_MIN / MASTER), int(90 * SAFE_MAX / MASTER)

    rows = [sum(max(0, paper - px[y * 90 + x]) for x in range(90)) for y in range(90)]
    cols = [sum(max(0, paper - px[y * 90 + x]) for y in range(90)) for x in range(90)]

    def share(seq):
        tot = sum(seq)
        return 1.0 if tot < 1 else sum(seq[lo:hi]) / tot

    return min(share(rows), share(cols))


def check_focal(im):
    w, h = im.size
    c = im.crop((int(w * .4), int(h * .4), int(w * .6), int(h * .6)))
    return abs(mean(c) - mean(im))


def check_palette(im):
    """Share of pixels whose hue sits outside the locked ivory/champagne/gold range."""
    small = im.resize((220, 220), Image.LANCZOS).convert("HSV")
    px = list(small.getdata())
    off = 0
    for hh, ss, vv in px:
        if ss < 40:                      # near-neutral ivory/paper — always fine
            continue
        deg = hh * 360 / 255
        if not (20 <= deg <= 65):        # warm gold / champagne band
            off += 1
    return off / len(px)


def validate(path):
    im = build_master(path)
    lr, tb = check_lr_symmetry(im)
    by, bd, bok, bmsg = check_band(im)
    r = {
        "page": os.path.splitext(os.path.basename(path))[0],
        "edge_frame": round(check_edge_frame(im), 1),
        "edge_step": round(check_edge_step(im), 1),
        "corner_spread": round(check_corner_spread(im), 1),
        "lr_symmetry": round(lr, 1),
        "tb_delta": round(tb, 1),
        "band_y": by, "band_delta": round(bd, 1), "band_msg": bmsg,
        "focal": round(check_focal(im), 1),
        "palette_off": round(check_palette(im), 3),
        "ink_share": round(check_ink_distribution(im), 3),
    }
    fails = []
    if r["edge_frame"] > T["edge_frame"]:       fails.append("EDGE_FRAME")
    if r["edge_step"] > T["edge_step"]:         fails.append("EDGE_STEP")
    if r["corner_spread"] > T["corner_spread"]: fails.append("CORNER_SPREAD")
    if r["lr_symmetry"] > T["lr_symmetry"]:     fails.append("LR_SYMMETRY")
    if not bok:                                 fails.append("BAND")
    if r["focal"] > T["focal"]:                 fails.append("FOCAL")
    if r["palette_off"] > T["palette"]:         fails.append("PALETTE")
    if r["ink_share"] < T["ink_min"]:           fails.append("INK_OUTSIDE_SAFE")
    r["fails"] = fails
    r["verdict"] = "PASS" if not fails else "FAIL"
    return im, r


def main():
    os.makedirs(OUT, exist_ok=True)
    results, failed = [], []
    for path in sorted(glob.glob(f"{SRC}/*.png")):
        im, r = validate(path)
        results.append(r)
        if r["verdict"] == "PASS":
            im.save(f"{OUT}/{r['page']}_5400x5400.jpg",
                    quality=92, subsampling=0, optimize=True, dpi=(DPI, DPI))
        else:
            failed.append(r["page"])
        print(f"{r['verdict']:4} {r['page']:>22} "
              f"frame={r['edge_frame']:5} step={r['edge_step']:5} "
              f"corner={r['corner_spread']:5} LR={r['lr_symmetry']:4} "
              f"focal={r['focal']:5} pal={r['palette_off']:5} ink={r['ink_share']:5} "
              f"band={r['band_y']}/{r['band_msg']} {' '.join(r['fails'])}")

    json.dump(results, open("/agent/workspace/photobook/validation.json", "w"), indent=1)
    print(f"\n{len(results) - len(failed)} pass / {len(failed)} fail")
    if failed:
        print("REGENERATE:", ", ".join(failed))


if __name__ == "__main__":
    main()
