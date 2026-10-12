"""Shared by the readings in tools/: the posed frames rigc render --geometry wrote, cut to the loop."""
import json
import math
import os

HELPERS = ('_ctl', '_px', '_phys', '_breath')    # twins a bone is keyed through; never a bone of the character
UNIT_TO_FILM_PX = 1000 / 1216.0                   # film/compose.py draws the rig's 1216-unit stage 1000 px tall at 1920x1080


def load(path):
    """geometry.json, and the index of the loop's first frame (the animation plays a lead-in first)."""
    geo = json.load(open(path))
    show = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(path)))), 'film', 'show.json')
    lead = json.load(open(show))['WARM'] if os.path.exists(show) else 0
    return geo, int(round(lead * geo['fps']))


def angle(b):
    return math.degrees(math.atan2(b['c'], b['a']))


def turn(a, b):
    return ((a - b + 180) % 360) - 180


def real_parent(parent, name):
    p = parent.get(name)
    while p and p.endswith(HELPERS):
        p = parent.get(p)
    return p
