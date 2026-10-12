#!/usr/bin/env python3
"""How far does the film turn each bone from its setup pose? Read off the posed loop frames.

    python3 tools/bends.py out/render/show@20fps/geometry.json

For every bone of the character: its angle against its parent, as the largest turn away from the setup
pose over the loop (keys and physics together, as drawn; the lead-in frames are left out), and the
half-range beside it. The first number is the one to declare as `meshes.<part>.auto.stimulus` in
inputs/config.json — a stimulus bends each link by plus and minus that many degrees *from the setup pose*
— because a mesh is otherwise reduced against the idle, and the idle turns a chain by a degree or two.
"""
import sys

from _geo import HELPERS, angle, load, real_parent, turn

geo, first = load(sys.argv[1])
parent = {b['name']: b.get('parent') for b in geo['bones']}
setup = {b['name']: angle(b) for b in geo['setup']['bones']}
frames = [{b['name']: angle(b) for b in f['bones']} for f in geo['frames'][first:]]

print(f"loop frames {first}..{len(geo['frames']) - 1}")
print(f"{'bone':22s} {'largest turn from setup':>24s} {'half-range':>11s}")
for name in parent:
    p = real_parent(parent, name)
    if name.endswith(HELPERS) or not p:
        continue
    rest = turn(setup[name], setup[p])
    d = [turn(turn(f[name], f[p]), rest) for f in frames]
    if max(abs(x) for x in d) >= 1:
        print(f"{name:22s} {max(abs(x) for x in d):24.1f} {(max(d) - min(d)) / 2:11.1f}")
