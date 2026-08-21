#!/usr/bin/env python3
"""
Packer + splitter.

These pages are grain- and glitter-heavy, so JPEG cannot compress them far:
even at a q74 floor the 22 masters total ~61 MB, over the 50 MB attachment cap.
Rather than degrade the sparkle to force one file, hold quality at q88 and split
the set into balanced parts that each fit under the cap.
"""

import os, glob, shutil
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

QUALITY = 88
DPI = (72, 72)
PARTS = 3
CAP = 48_000_000

SRC = "out/masters_5400x5400"
STAGE = "packed"


def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE, exist_ok=True)

    sized = []
    for p in sorted(glob.glob(f"{SRC}/*.jpg")):
        im = Image.open(p).convert("RGB")
        out = os.path.join(STAGE, os.path.basename(p))
        im.save(out, "JPEG", quality=QUALITY, subsampling=0, optimize=True, dpi=DPI)
        sized.append((os.path.getsize(out), out))

    total = sum(s for s, _ in sized)
    print(f"q{QUALITY}: {total/1e6:.1f} MB total across {len(sized)} pages")

    # greedy balance: largest first into the lightest bin, keeps parts even
    bins = [[] for _ in range(PARTS)]
    loads = [0] * PARTS
    for size, path in sorted(sized, reverse=True):
        i = loads.index(min(loads))
        bins[i].append(path)
        loads[i] += size

    for n, (group, load) in enumerate(zip(bins, loads), 1):
        folder = f"wedding_gold_22_part{n}/masters_5400x5400"
        shutil.rmtree(f"wedding_gold_22_part{n}", ignore_errors=True)
        os.makedirs(folder, exist_ok=True)
        for f in sorted(group):
            shutil.copy(f, folder)
        for extra in ("out/SPECS.txt", "validate.py", "pack.py", "validation.json"):
            if os.path.exists(extra):
                shutil.copy(extra, f"wedding_gold_22_part{n}/")
        shutil.make_archive(f"wedding_gold_22_part{n}", "zip", ".", f"wedding_gold_22_part{n}")
        zsize = os.path.getsize(f"wedding_gold_22_part{n}.zip")
        flag = "OK" if zsize < CAP else "OVER CAP"
        print(f"part{n}: {len(group)} pages, {zsize/1e6:5.1f} MB  {flag}")


if __name__ == "__main__":
    main()
