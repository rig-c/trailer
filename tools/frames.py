#!/usr/bin/env python3
"""The same frame from two builds: where a change landed, and whether anything else moved.

    python3 tools/frames.py out/prev/scene out/scene [threshold]

Per frame: how many pixels differ — "differ" meaning the largest of the three channel differences is over
the threshold (40 by default; two builds of the same pose differ by up to about 33 on these JPEGs, so 40
is just above the encoder's noise) — and the box those pixels lie in. The last line sums the run.

A box is only as fine as the skeleton: 61 of the 83 bones hang under the chest, so a change to anything
there fills the whole figure. For "which bones moved" use tools/moved.py.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

a_dir, b_dir = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 40
fa, fb = sorted(glob.glob(a_dir + '/s[0-9]*.jpg')), sorted(glob.glob(b_dir + '/s[0-9]*.jpg'))
assert fa and len(fa) == len(fb), (len(fa), len(fb))
total = same = touched = 0
for pa, pb in zip(fa, fb):
    d = np.abs(np.asarray(Image.open(pa).convert('RGB'), np.int16) - np.asarray(Image.open(pb).convert('RGB'), np.int16)).max(axis=2)
    over = d > limit
    n = int(over.sum())
    same += int(d.max() == 0)
    touched += int(n > 0)
    total += n
    ys, xs = np.nonzero(over)
    box = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if n else None
    print(f"{os.path.basename(pa)}  over {limit}: {n:7d}  box {box}  largest difference {int(d.max())}")
print(f"{len(fa)} frames; {same} identical; {touched} with pixels over {limit}; {total} such pixels in all")
