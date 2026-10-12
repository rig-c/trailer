#!/usr/bin/env python3
"""How far does the film bend each bone? Read off the posed frames rigc render --geometry wrote.

    python3 tools/bends.py out/render/show@20fps/geometry.json

For every bone, the angle between it and its parent over all frames — keys and physics together, as
drawn. A chain's largest half-range is what its mesh has to carry, and it is the number to declare as
`meshes.<part>.auto.stimulus` in inputs/config.json: the mesh is reduced against the idle unless told
otherwise, and the idle bends a chain by a degree or two.
"""
import json
import math
import sys

geo = json.load(open(sys.argv[1]))
names = [b['name'] for b in geo['bones']]
parent = {b['name']: b.get('parent') for b in geo['bones']}
angle = {n: [] for n in names}
for frame in geo['frames']:
    for b in frame['bones']:
        angle[b['name']].append(math.degrees(math.atan2(b['c'], b['a'])))

HELPERS = ('_ctl', '_px', '_phys', '_breath')
print(f"{'bone':24s} {'against its parent, degrees':>28s} {'half-range':>11s}")
for n in names:
    p = parent.get(n)
    if n.endswith(HELPERS) or not p:
        continue
    # A helper twin sits between a bone and the parent it bends against: skip up to the first real bone.
    while p and p.endswith(HELPERS):
        p = parent.get(p)
    if not p:
        continue
    d = [((a - b + 180) % 360) - 180 for a, b in zip(angle[n], angle[p])]
    half = (max(d) - min(d)) / 2
    if half >= 1:
        print(f"{n:24s} {min(d):12.1f} .. {max(d):7.1f} {half:11.1f}")
