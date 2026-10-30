"""Erase the two curled hair loops that stick out sideways at hip height.

Review: the loops read as hair lying on a floor, so on a figure sitting in
mid-air they look like they float. Each loop is a thin ring
on the outside of a twin tail. The tail's outer edge is measured on the rows
just above and below the ring (where nothing else is there) and joined by
straight segments across the ring's rows; everything outside that edge is
erased from the See-through layer (alpha -> 0, a 1.5 px ramp) and from the
painting (-> its white background).

Already applied: inputs/painting.png and the See-through layer are the edited
files. Run it on the generated painting and an untouched See-through run to
repeat the edit; run on the edited files it would trim nothing more.

usage: python3 tools/trim_loops.py <trailer dir>
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROWS = (527, 567)  # the rings' rows, layer px, with a margin
# Tail outer edge, (row, x) in layer px, measured where alpha > 128 on rows clear of the ring.
LEFT = ([520, 526, 532, 568, 574, 580], [339, 332, 324, 253, 246, 242])    # erase x < edge
RIGHT = ([520, 526, 532, 562, 568, 574], [706, 714, 723, 769, 775, 779])   # erase x > edge
X_LEFT, X_RIGHT = (150, 450), (600, 900)  # the halves each rule may touch
RAMP = 1.5

def keep_mask(size):
    """The accepted v1 trim in its registered 1024-square source grid."""
    if tuple(size) != (1024, 1024):
        raise ValueError('loop trim requires the original 1024-square registration')
    keep = np.ones((size[1], size[0]), dtype=np.float64)
    xs = np.arange(size[0], dtype=np.float64)
    for y in range(*ROWS):
        el = np.interp(y, *LEFT)
        er = np.interp(y, *RIGHT)
        kl = np.clip((xs - (el - RAMP)) / RAMP, 0, 1)
        kr = np.clip(((er + RAMP) - xs) / RAMP, 0, 1)
        row = np.ones_like(xs)
        row[X_LEFT[0]:X_LEFT[1]] = kl[X_LEFT[0]:X_LEFT[1]]
        row[X_RIGHT[0]:X_RIGHT[1]] = kr[X_RIGHT[0]:X_RIGHT[1]]
        keep[y] = row
    return keep


def main(root):
    layer_p = root / 'inputs/layers/full/parts/back hair.png'
    paint_p = root / 'inputs/painting.png'
    layer = Image.open(layer_p).convert('RGBA')
    a = np.array(layer.split()[3]).astype(np.float64)
    keep = keep_mask(layer.size)
    removed = (a > 0) & (keep < 1)
    layer.putalpha(Image.fromarray(np.round(a * keep).astype(np.uint8)))
    layer.save(layer_p)
    print('layer px touched:', int(removed.sum()))

    # Legacy CLI only: also edit the original painting. The v2 derivation does not call this.
    paint = Image.open(paint_p).convert('RGB')
    P = np.array(paint)
    sq = 2432
    pad = (sq - paint.width) // 2
    m = Image.fromarray((removed * 255).astype(np.uint8)).resize((sq, sq), Image.NEAREST)
    m = m.filter(ImageFilter.MaxFilter(5))
    M = np.array(m)[:, pad:pad + paint.width] > 0
    P[M] = (255, 254, 255)
    Image.fromarray(P).save(paint_p)
    print('painting px whitened:', int(M.sum()))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
