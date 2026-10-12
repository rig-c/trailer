#!/usr/bin/env python3
"""Two frames laid over each other, red and cyan: how far apart are they, in pixels a viewer would see?

    python3 tools/overlay.py <frame A> <frame B> out.png [x0 y0 x1 y1 [scale]]

A in the red channel, B in green and blue: grey where they agree, a red or cyan fringe where they do not.
Prints the count of pixels differing by more than 40 and how wide the fringes run, vertically and
horizontally. For something periodic, A is the frame at its peak and B the same frame built without it —
and a fringe a pixel wide is something a viewer will not see either.

It measures how far, not how fast: a breath of the same size at half the speed gives the same numbers.
"""
import sys

import numpy as np
from PIL import Image

pa, pb, out = sys.argv[1:4]
box = tuple(int(v) for v in sys.argv[4:8]) if len(sys.argv) >= 8 else None
scale = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
A, B = Image.open(pa).convert('RGB'), Image.open(pb).convert('RGB')
if box:
    A, B = A.crop(box), B.crop(box)
picture = Image.fromarray(np.dstack([np.asarray(A.convert('L')), np.asarray(B.convert('L')), np.asarray(B.convert('L'))]), 'RGB')
if scale != 1:
    picture = picture.resize((int(picture.width * scale), int(picture.height * scale)), Image.LANCZOS)
picture.save(out)
over = np.abs(np.asarray(A, np.int16) - np.asarray(B, np.int16)).max(axis=2) > 40


def runs(mask):
    padded = np.pad(mask, ((0, 0), (1, 1))).astype(np.int8)
    edges = np.diff(padded, axis=1)
    return (np.nonzero(edges == -1)[1] - np.nonzero(edges == 1)[1])


for name, r in (('vertical', runs(over.T)), ('horizontal', runs(over))):
    print(f"{name} fringes: " + (f"{len(r)} runs, median {np.median(r):.0f} px, 90th percentile {np.percentile(r, 90):.0f}, widest {r.max()}" if len(r) else 'none'))
print(f"{out}: {int(over.sum())} pixels differ by more than 40")
