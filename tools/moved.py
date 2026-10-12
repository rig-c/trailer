#!/usr/bin/env python3
"""Which bones did a change move? Two builds' posed frames, the loop only.

    python3 tools/moved.py out/prev/render/show@20fps/geometry.json out/render/show@20fps/geometry.json [bone]

Per bone, the largest difference in position and in angle between the two builds. With a bone named, the
table is split into what hangs under it and what does not — after a change to the breath, name `chest_ctl`
and everything outside it should read zero.
"""
import math
import sys

from _geo import UNIT_TO_FILM_PX, angle, load, turn

a, first = load(sys.argv[1])
b, _ = load(sys.argv[2])
root = sys.argv[3] if len(sys.argv) > 3 else None
parent = {x['name']: x.get('parent') for x in a['bones']}


def under(name):
    while name:
        if name == root:
            return True
        name = parent.get(name)
    return False


worst = {}
for fa, fb in zip(a['frames'][first:], b['frames'][first:]):
    for x, y in zip(fa['bones'], fb['bones']):
        d = math.hypot(x['worldX'] - y['worldX'], x['worldY'] - y['worldY'])
        r = abs(turn(angle(x), angle(y)))
        o = worst.get(x['name'], (0.0, 0.0))
        worst[x['name']] = (max(o[0], d), max(o[1], r))
for title, pick in ((f"under {root}", True), (f"not under {root}", False)) if root else (("all bones", None),):
    rows = {n: v for n, v in worst.items() if pick is None or under(n) == pick}
    moved = {n: v for n, v in rows.items() if v[0] > 1e-6 or v[1] > 1e-6}
    print(f"{title}: {len(rows)} bones, {len(moved)} moved")
    for n, v in sorted(moved.items(), key=lambda kv: -kv[1][0])[:12]:
        print(f"   {n:24s} {v[0]:9.3f} units ({v[0] * UNIT_TO_FILM_PX:6.2f} film px)   {v[1]:7.3f} degrees")
