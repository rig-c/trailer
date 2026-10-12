#!/usr/bin/env python3
"""Does the loop close, and does anything jump inside it? From the posed frames.

    python3 tools/loop.py out/render/show@20fps/geometry.json

1. The loop's first frame against the animation's last frame (the same loop time, one loop later):
   the largest bone and vertex offsets. A loop that closes reads 0 on both.
2. How far every bone turns against its parent from one frame to the next, and the frames where
   several bones turn over three times as far as on the frames around — a pop, unless a key put it there.
"""
import math
import sys

from _geo import UNIT_TO_FILM_PX, angle, load, turn

geo, first = load(sys.argv[1])
F = geo['frames']
a, b = F[first], F[-1]
bone = max(((math.hypot(x['worldX'] - y['worldX'], x['worldY'] - y['worldY']), x['name']) for x, y in zip(a['bones'], b['bones'])))
vert = (0.0, None)
for x, y in zip(a['attachments'], b['attachments']):
    v, w = x.get('vertices'), y.get('vertices')
    if v and w and len(v) == len(w):
        m = max(math.hypot(v[i] - w[i], v[i + 1] - w[i + 1]) for i in range(0, len(v), 2))
        vert = max(vert, (m, x['slot']))
print(f"loop time 0 (frame {first}) against one loop later (frame {len(F) - 1}):")
print(f"  largest bone offset   {bone[0]:8.3f} units = {bone[0] * UNIT_TO_FILM_PX:6.2f} film px  ({bone[1]})")
print(f"  largest vertex offset {vert[0]:8.3f} units = {vert[0] * UNIT_TO_FILM_PX:6.2f} film px  ({vert[1]})")

parent = {x['name']: x.get('parent') for x in geo['bones']}
names = [n for n in parent if parent[n]]
local = [{x['name']: angle(x) for x in f['bones']} for f in F]
turns = [[abs(turn(turn(local[i + 1][n], local[i + 1][parent[n]]), turn(local[i][n], local[i][parent[n]]))) for n in names]
         for i in range(len(F) - 1)]
pops = {}
for i in range(2, len(turns) - 2):
    for k, n in enumerate(names):
        around = sorted((turns[i - 2][k], turns[i - 1][k], turns[i + 1][k], turns[i + 2][k]))[1:3]
        if turns[i][k] > 1.0 and turns[i][k] > 3 * (sum(around) / 2 + 0.05):
            pops.setdefault(i, []).append(n)
print("frames where a bone turns over three times as far as on the frames around it (animation frame n -> n+1: bones).")
print("A keyed beat belongs here (a hop, a kick); a frame where only bones on springs appear does not:")
found = False
for i, ns in sorted(pops.items()):
    if len(ns) >= 3:
        found = True
        print(f"  {i} -> {i + 1}: {len(ns)} bones ({', '.join(ns[:6])}{', …' if len(ns) > 6 else ''})")
if not found:
    print("  none")
