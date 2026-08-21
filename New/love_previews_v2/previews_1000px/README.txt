LOVE THEME PREVIEWS — REAL COPY
===============================
18 files = 3 pages x 3 books x 2 variants. Same layouts, same slot geometry and
same placement as before; only the words and the text treatment changed.

COPY (drafted as working text — replace with your own)
  love_p01  caption  "OUR LOVE STORY"
  love_p02  heading  "Just the two of us"
            body     "Every ordinary day became something worth keeping,
                      simply because we spent it together."
  love_p03  heading  "Where it began"
            body     "A quiet afternoon, a shared laugh, and the start of
                      every story we would tell for years after."

Copy lives in the COPY dict at the top of previews.py, keyed by page stem, with
a FALLBACK for any page not listed. Editing text means editing that dict only.

READABILITY — MEASURED, NOT EYEBALLED
Each text zone is tested before drawing and must satisfy BOTH conditions:

  contrast >= 4.5:1   between the ink and the actual pixels behind it
  busyness <= 11.0    standard deviation of the zone, i.e. it must be QUIET

Mean contrast alone is not sufficient. A cream page scattered with flowers has
a light mean and passes a contrast test instantly while the text still sits on
top of petals. The busyness condition is what forces a clean zone.

When a zone fails, a soft-edged scrim is laid over it, toned from the page's own
paper colour, and strengthened step by step (0.45, 0.62, 0.76, 0.86, 0.93) until
both conditions pass. The scrim has a feathered rounded edge so it reads as part
of the design rather than a pasted box, and it is applied only as strongly as
the measurement demands.

Ink colour is chosen per zone: near-black on light pages, white on dark ones,
decided from the zone's own luminance rather than assumed.

MEASURED RESULT, ALL 18 ZONES
  contrast 14.4 to 18.0   (threshold 4.5)
  busyness 8.7 to 10.8    (threshold 11.0)
  scrim 0.62 on the floral scatter page, 0.45 to 0.86 on parts of p01,
  and 0.00 on the watercolour page, which was already quiet enough to leave
  untouched. Every zone resolved to dark ink; the white-ink path exists for
  dark themes.

The compositor prints the scrim strength, contrast and busyness for every zone,
so this is verifiable on any future run rather than taken on trust.
