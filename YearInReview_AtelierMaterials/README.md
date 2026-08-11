# Photobook — Year in Review / Atelier Materials

Pilot delivery: **5 pages**, produced end to end by the photobook system.
Every page passed the automated crop-safety validator before previews were built.

## Structure

```
YearInReview_AtelierMaterials/
├── masters_5400x5400/   5 background masters, 5400x5400 @ 72 DPI, sRGB
├── previews/
│   ├── square/          10  (1000x1000)   10x10 in book
│   ├── portrait/        10  ( 667x1000)    8x12 in book
│   └── landscape/       10  (1000x 667)   12x8  in book
├── svg/                 12 theme stickers, single-colour, recolourable
├── photos/               7 AI fill photos, aspects 0.67 - 2.36
├── validation/          validator scores + compositor decision log
├── tools/               the pipeline itself
└── MANIFEST.sha256      every file with size and hash
```

Per page the deliverable is 7 files: 1 master + (3 books x 2 variants).

## Specs held

| Rule | Value |
|---|---|
| Master canvas | 5400x5400, 72 DPI, sRGB — delivered uncut |
| Universal safe zone | central 3600x3600 (x/y 900-4500) |
| Margin | physical **1 inch** every side, so the fraction differs per axis per book |
| Preview cap | 1000px long edge |
| Placeholder grey | exactly (138,138,138) |
| Text | one heading of 4-5 words + optional supporting line, plain system sans |
| Photo fitting | crop-to-fill by closest aspect, never stretched, solid outline |

## Validation

All 5 masters: **5 PASS / 0 FAIL** against eight checks (EDGE_FRAME, EDGE_STEP,
CORNER_SPREAD, LR_SYMMETRY, BAND, INK_DISTRIBUTION, FOCAL, PALETTE).
Scores in `validation/validation_yir_atelier.json`.

The first pass was 1 pass / 4 fail. Three were genuine artwork faults and were
re-rendered against the specific number that failed; one was a mis-specified
palette band on my side, corrected by measuring the art (walnut sits at hue
5-17, oat/linen at 26-32) rather than guessing.

## Reproducing

Requires Python 3, Pillow and cairosvg.

```
python3 tools/validate.py yir_atelier <src_4096_renders> <out>
python3 tools/compose.py <masters> <photos> <svg> <previews_out>
```

`compose.py` decides what the layout does not encode: which of the 23 library
designs a page uses, whether text fits, whether a sticker is warranted, and the
outline colour. Text and stickers are placed only over a measurably quiet
region — structural luminance variation under threshold and ink contrast above
it — so nothing lands on a busy background. Where a page wants text and the
design leaves no room, slots are compressed by up to 15% to open a caption band.

## Known gaps in this pilot

- The fill photos do not hold one consistent family across all seven images.
- The densest layout (12-13 slots) exceeds the 7-photo pack, so photos repeat on
  that page. A pack of 13+ removes this.
- Stickers land as small ornaments in corner pockets; placement is functional
  rather than considered.
