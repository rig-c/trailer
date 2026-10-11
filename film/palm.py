#!/usr/bin/env python3
"""The open palm for the wave, and the arm piece without its hand.

    python3 film/palm.py <generated palm.png> <rig images>/handwear_r.png <out dir>

The painting's right hand cups the cheek, so a wave needs a hand the painting
does not have. inputs/palm.png is a separately generated open hand on a white
ground. This script:

  * cuts it off its ground (flood fill from the corners; the outline closes it),
  * recolours it to the painting's skin and line colours,
  * stands its forearm upright, and scales it so wrist-to-fingertip is 78 rig px
    — an open hand is sized by the face: this one is about half the face's width,
  * writes it as two pieces that overlap by a few pixels at the wrist crease —
    palm_arm.png (the bare forearm) and palm_hand.png (the hand) — with the two
    points the rig needs in palm_r.json: where the skin leaves the cuff, and the
    wrist the hand turns on,
  * erases the cupped hand from a copy of the arm piece (handwear_r_arm.png).

Everything is written at twice rig resolution and placed at scale 0.5.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, arm_src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(dst, exist_ok=True)
im = Image.open(src).convert('RGB')
W, H = im.size

# ---- off its ground
filled = im.copy()
for seed in ((0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0)):
    if filled.getpixel(seed) != (255, 0, 255):
        ImageDraw.floodfill(filled, seed, (255, 0, 255), thresh=40)
ground = np.all(np.asarray(filled) == (255, 0, 255), axis=2)
alpha = Image.fromarray(((~ground) * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.2))

# ---- the painting's colours: luminance picks between the line and the skin
a = np.asarray(im, np.float32)
lum = a.mean(axis=2, keepdims=True) / 255.0            # 0 on the line, about 0.93 on the skin
SKIN = np.array((254, 233, 226), np.float32)
LINE = np.array((92, 40, 46), np.float32)
t = np.clip((lum - 0.12) / 0.75, 0, 1)
rgb = LINE * (1 - t) + SKIN * t
rows = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
shade = np.clip((rows - 0.60) / 0.40, 0, 1) * 0.16 * t     # a soft warm shade toward the cuff
rgb = rgb * (1 - shade) + np.array((236, 150, 150), np.float32) * shade
out = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.asarray(alpha, np.float32)]).astype(np.uint8), 'RGBA')

# ---- upright, cropped, scaled. Points are in the source image's pixels.
TURN = -6.7                    # clockwise: the forearm stands upright
CUFF = (930.0, 1640.0)         # on the forearm's centre line, below the wrist: where the sleeve ends
WRIST = (880.0, 1270.0)        # the centre of the wrist crease
out = out.rotate(TURN, resample=Image.BICUBIC, center=CUFF)
box = out.getbbox()
box = (box[0], box[1], box[2], min(box[3], 1790))
out = out.crop(box)
K = 2 * 78 / 1030.0            # wrist to fingertip is 1030 source px; 78 rig px on the figure, written at 2x
small = out.resize((int(out.width * K + 0.5), int(out.height * K + 0.5)), Image.LANCZOS)
cuff = ((CUFF[0] - box[0]) * K, (CUFF[1] - box[1]) * K)
th = math.radians(-TURN)       # the wrist, carried through the same turn about the cuff
dx, dy = WRIST[0] - CUFF[0], WRIST[1] - CUFF[1]
wrist = ((CUFF[0] + dx * math.cos(th) - dy * math.sin(th) - box[0]) * K,
         (CUFF[1] + dx * math.sin(th) + dy * math.cos(th) - box[1]) * K)

# ---- two pieces that meet at the wrist
px = np.asarray(small).copy()
row = np.arange(small.height)[:, None]
LAP = 3
hand = px.copy()
hand[:, :, 3] = np.where(row <= wrist[1] + LAP, hand[:, :, 3], 0)
Image.fromarray(hand, 'RGBA').save(f'{dst}/palm_hand.png')
forearm = px.copy()
forearm[:, :, 3] = np.where(row >= wrist[1] - LAP, forearm[:, :, 3], 0)
Image.fromarray(forearm, 'RGBA').save(f'{dst}/palm_arm.png')
json.dump({"w": small.width, "h": small.height, "cuff": list(cuff), "wrist": list(wrist), "scale": 0.5},
          open(f'{dst}/palm_r.json', 'w'))

# ---- the arm piece without its hand: everything above the cuff's rim, by a polygon read off the piece
arm = Image.open(arm_src).convert('RGBA')
mask = Image.new('L', arm.size, 0)
ImageDraw.Draw(mask).polygon([(36, 0), (118, 0), (118, 84), (112, 87), (101, 98), (90, 93), (80, 87), (78, 63), (60, 50), (36, 30)], fill=255)
apx = np.asarray(arm).copy()
apx[:, :, 3] = np.where(np.asarray(mask) > 0, 0, apx[:, :, 3])
Image.fromarray(apx, 'RGBA').save(f'{dst}/handwear_r_arm.png')
print('palm', small.size, 'cuff at', [round(v, 1) for v in cuff], 'wrist at', [round(v, 1) for v in wrist])
