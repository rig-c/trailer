#!/usr/bin/env python3
"""The film rig: the character rig-parts built, plus what the trailer needs of her.

    python3 film/rig.py <rig dir from rig-parts> <palm dir from palm.py> <out dir>

Reads rig.json, motion.json and images/ from the first directory and writes the
same three into the last, with these additions — all of them rig-spec and
motion-spec data that `rigc build` compiles and gates like any other:

  * the swing: two bones (a far pivot and the seat) above the hip, and three
    drawn pieces on the seat bone — so the character and the swing are one
    skeleton, and the sway reaches every strand as ordinary bone motion;
  * a physics constraint on every hanging chain, and one on the soft chest;
  * the face bones stood on the face's own axis (the eye line), so a blink
    squashes across the eye and not along the page;
  * a second, keyed bone above three bones a physics constraint or a gesture
    already owns, for the parallax that reads as depth;
  * the open palm of the wave, as two pieces that meet at the wrist;
  * one animation, `show`: the idle rig-parts authored, tiled, with the
    performance keyed over it.

A second rig, rig_black.json, is the same rig with every slot tinted black.
`rigc render` draws on an opaque ground; rendering both gives the film layer an
alpha channel (compose.py).
"""
import json
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC, PALM, DST = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(DST, exist_ok=True)
rig = json.load(open(f'{SRC}/rig.json'))
motion = json.load(open(f'{SRC}/motion.json'))
if os.path.isdir(f'{DST}/images'):
    shutil.rmtree(f'{DST}/images')
shutil.copytree(f'{SRC}/images', f'{DST}/images')

LOGO = [(255, 45, 85), (255, 149, 0), (48, 209, 88), (10, 132, 255), (191, 90, 242)]
bones = rig['bones']
skin = rig['skins']['default']


def bone(name):
    return next(b for b in bones if b['name'] == name)


# ---------------------------------------------------------------- the swing's art
# Drawn here rather than painted: a gradient bar with a flat ring at each end,
# and a rope that fades out upward. 2x supersampled.

def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def seat_bar(half, thickness, ring_radius):
    S = 2
    W = int((2 * half + 2 * ring_radius + 80) * S)
    H = int((2 * ring_radius + 80) * S)
    cx, cy = W / 2, H / 2
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1 = cx - half * S, cx + half * S
    n = 400
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t
        f = t * 3
        k = min(2, int(f))
        col = lerp(LOGO[k], LOGO[k + 1], f - k)
        for j, (dy, shade) in enumerate(((0, 0.78), (-thickness * S * 0.10, 1.0), (-thickness * S * 0.24, 1.22))):
            rr = thickness * S / 2 * (1 - 0.28 * j)
            c = tuple(int(min(255, v * shade + (18 if j == 2 else 0))) for v in col)
            d.ellipse((x - rr, cy + dy - rr, x + rr, cy + dy + rr), fill=c + (255,))
    # A ring, open in the middle. A glossy ball with a dark centre read as an eye.
    for x, col in ((x0, LOGO[0]), (x1, LOGO[3])):
        r = ring_radius * S
        hole = r * 0.56
        punch = Image.new('L', (W, H), 0)
        ImageDraw.Draw(punch).ellipse((x - r, cy - r, x + r, cy + r), fill=255)
        a = np.asarray(im).copy()
        a[:, :, 3] = np.where(np.asarray(punch) > 0, 0, a[:, :, 3])
        im = Image.fromarray(a, 'RGBA')
        ring = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        rd.ellipse((x - r, cy - r, x + r, cy + r), fill=tuple(int(v * 0.80) for v in col) + (255,))
        rd.ellipse((x - r * 0.94, cy - r * 0.97, x + r * 0.94, cy + r * 0.90),
                   fill=tuple(int(min(255, v * 1.06 + 8)) for v in col) + (255,))
        ra = np.asarray(ring).copy()
        hm = Image.new('L', (W, H), 0)
        ImageDraw.Draw(hm).ellipse((x - hole, cy - hole, x + hole, cy + hole), fill=255)
        ra[:, :, 3] = np.where(np.asarray(hm) > 0, 0, ra[:, :, 3])
        im.alpha_composite(Image.fromarray(ra, 'RGBA'))
    glow = im.filter(ImageFilter.GaussianBlur(22 * S))
    a = np.asarray(glow, np.float32)
    a[:, :, 3] *= 0.55
    out = Image.fromarray(a.astype(np.uint8), 'RGBA')
    out.alpha_composite(im)
    return out.resize((W // S, H // S), Image.LANCZOS)


def rope(length, w=16):
    a = np.zeros((length, w + 16, 4), np.float32)
    ys = np.linspace(0, 1, length)[:, None]
    xs = np.abs(np.arange(w + 16) - (w + 16) / 2)[None, :]
    core = np.clip(1 - xs / (w / 2), 0, 1)
    a[:, :, 0:3] = 235
    a[:, :, 2] = 255
    a[:, :, 3] = 255 * np.clip(core * 1.6, 0, 1) * np.clip(ys * 1.4, 0, 1) * 0.95
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


HALF, THICKNESS, RING, ROPE = 560, 54, 66, 760
seat_bar(HALF, THICKNESS, RING).save(f'{DST}/images/seat_bar.png')
rope(ROPE).save(f'{DST}/images/rope.png')

# ---------------------------------------------------------------- root > swing > seat > hip
# The pivot is far above the frame, so 2.5 degrees of it is a wide, shallow arc.
PIVOT_Y, SEAT_Y = 3200.0, 499.0
hip = bone('hip')
root_at = next(i for i, b in enumerate(bones) if b['name'] == 'root')
bones.insert(root_at + 1, {"name": "swing", "parent": "root", "x": 0, "y": PIVOT_Y})
bones.insert(root_at + 2, {"name": "seat", "parent": "swing", "x": 0, "y": SEAT_Y - PIVOT_Y})
hip['parent'] = 'seat'
hip['y'] = hip['y'] - SEAT_Y

slots = [{"name": "rope_r", "bone": "seat", "attachment": "rope_r"},
         {"name": "rope_l", "bone": "seat", "attachment": "rope_l"}] + rig['slots']
# The bar hangs in front of the long hair and behind the body.
behind = next(i for i, s in enumerate(slots) if s['name'] == 'hair_long')
slots.insert(behind + 1, {"name": "seat_bar", "bone": "seat", "attachment": "seat_bar"})
rig['slots'] = slots
skin['seat_bar'] = {"seat_bar": {"image": "seat_bar.png", "x": 0, "y": 0}}
skin['rope_r'] = {"rope_r": {"image": "rope.png", "x": -HALF, "y": ROPE / 2 + RING * 0.78}}
skin['rope_l'] = {"rope_l": {"image": "rope.png", "x": HALF, "y": ROPE / 2 + RING * 0.78}}

# ---------------------------------------------------------------- physics on every strand
# rig-parts keys its idle on a `<bone>_ctl` parent, which leaves the plain bone
# free for a constraint. Strength tapers down a chain: the tip is the loosest.
physics = {}


def chain(prefix, links, strength, damping, inertia, taper=0.85, start=0):
    for k in range(start, links):
        physics[f'{prefix}{k}_phys'] = {
            "bone": f'{prefix}{k}', "rotate": 1, "inertia": inertia,
            "strength": round(strength * (taper ** k), 1), "damping": damping, "mass": 1.0, "mix": 1}


chain('tail_r', 4, 105, 0.88, 0.5, taper=0.8, start=1)
chain('tail_l', 4, 105, 0.88, 0.5, taper=0.8, start=1)
for bang in ('bang_r', 'bang_c', 'bang_l'):
    chain(bang, 2, 130, 0.86, 0.5)
chain('hairpin_tassel', 2, 60, 0.80, 0.7)
chain('sleeve_l', 2, 150, 0.88, 0.4, start=1)
chain('skirt_r', 2, 70, 0.82, 0.6)
chain('skirt_l', 2, 70, 0.82, 0.6)
chain('skirt_c', 2, 120, 0.86, 0.5)
chain('leg', 2, 95, 0.84, 0.55)

# ---------------------------------------------------------------- the face's own axis
# The head is painted tilted, and rig-parts 1.6.0 writes the face bones with the
# page's axes (rig-c/parts#239). A blink keys scaley, which squashes along the
# bone's own y: with the page's axes the closed eye is a horizontal stroke on a
# tilted face. Rotate the five bones to the line through the two eyes, and turn
# their attachments back by the same angle so the setup pose does not move.
eye_r, eye_l = bone('eye_r'), bone('eye_l')
TILT = math.degrees(math.atan2(eye_l['y'] - eye_r['y'], eye_l['x'] - eye_r['x']))
cos_t, sin_t = math.cos(math.radians(-TILT)), math.sin(math.radians(-TILT))
FACE = ('eye_r', 'eye_l', 'brow_r', 'brow_l', 'mouth')
for name in FACE:
    bone(name)['rotation'] = round(TILT, 4)
for slot in rig['slots']:
    if slot['bone'] in FACE:
        for att in skin[slot['name']].values():
            assert att.get('type', 'region') == 'region', slot['name']
            x, y = att.get('x', 0), att.get('y', 0)
            att['x'] = round(x * cos_t - y * sin_t, 4)
            att['y'] = round(x * sin_t + y * cos_t, 4)
            att['rotation'] = round(att.get('rotation', 0) - TILT, 4)

# ---------------------------------------------------------------- a keyed twin above a bone
# A track owns one bone's one property, and a physics constraint owns its bone.
# `<bone>_px` takes the bone's place in the tree and the bone becomes its
# identity child, so the parallax can key the twin and leave the bone alone.


def twin(name, suffix='_px'):
    i = next(k for k, b in enumerate(bones) if b['name'] == name)
    b = bones[i]
    t = dict(b)
    t['name'] = name + suffix
    for key in ('x', 'y', 'rotation'):
        b.pop(key, None)
    b['parent'] = t['name']
    bones.insert(i, t)


for name in ('leg0', 'leg1', 'chest_jiggle'):
    twin(name)
# The soft chest: `chest_jiggle` carries a region of the topwear mesh (the
# rig-parts config declares it); this is the spring that moves it.
physics['bust_phys'] = {"bone": "chest_jiggle", "x": 0.7, "y": 1, "inertia": 0.5,
                        "strength": 85, "damping": 0.87, "mass": 1, "mix": 1}

# ---------------------------------------------------------------- the open palm
# The painting's right hand cups the cheek. For the wave, that arm piece is
# shown without its hand (arm_r_front) and an open palm is put in its cuff:
# `palm_r` is the bare forearm, rigid with the sleeve; `hand_r` is the hand,
# turning at the wrist. All three are hidden in the setup pose.
palm = json.load(open(f'{PALM}/palm_r.json'))
for f in ('palm_hand.png', 'palm_arm.png', 'handwear_r_arm.png'):
    shutil.copy(f'{PALM}/{f}', f'{DST}/images/{f}')
by_name = {b['name']: b for b in bones}


def world(name):
    """A bone's setup-pose world (x, y, rotation). No bone of this rig is scaled or sheared at setup."""
    b = by_name[name]
    x, y, r = b.get('x', 0), b.get('y', 0), b.get('rotation', 0)
    if not b.get('parent'):
        return x, y, r
    px, py, pr = world(b['parent'])
    c, s = math.cos(math.radians(pr)), math.sin(math.radians(pr))
    return px + x * c - y * s, py + x * s + y * c, pr + r


# Where the skin leaves the cuff: read off the arm piece (image px 93, 90; the
# piece sits at stage px 280, 255), turned into world units (y up, origin at the
# stage's bottom centre: 832 x 1216).
CUFF = (280 + 93 - 416.0, 1216 - (255 + 90.0))
wx, wy, wr = world('sleeve_r1')
c, s = math.cos(math.radians(-wr)), math.sin(math.radians(-wr))
dx, dy = CUFF[0] - wx, CUFF[1] - wy
# The forearm points the way the sleeve does (rotation 3: by eye). Pointing it
# the way the painted wrist did left a 14-degree kink at the cuff.
bones.append({"name": "palm_r", "parent": "sleeve_r1", "x": round(dx * c - dy * s, 3),
              "y": round(dx * s + dy * c, 3), "rotation": 3.0, "length": 60})
k = palm['scale']
# The palm image stands upright; turned -90 degrees its "up" is the bone's +x.
# An offset (right, up) in image axes is therefore (up, -right) in the bone's.
wrist_right = (palm['wrist'][0] - palm['cuff'][0]) * k
wrist_up = (palm['cuff'][1] - palm['wrist'][1]) * k
bones.append({"name": "hand_r", "parent": "palm_r", "x": round(wrist_up, 3), "y": round(-wrist_right, 3), "length": 40})
arm_slot = next(s for s in rig['slots'] if s['name'] == 'handwear_r')
rig['slots'] += [{"name": "palm_r", "bone": "palm_r", "attachment": None},
                 {"name": "hand_r", "bone": "hand_r", "attachment": None},
                 {"name": "arm_r_front", "bone": arm_slot["bone"], "attachment": None}]
w, h = palm['w'] * k, palm['h'] * k


def placed(image, anchor):
    """A region attachment whose image point `anchor` (image px) sits on the bone's origin."""
    right, up = w / 2 - anchor[0] * k, anchor[1] * k - h / 2
    return {"image": image, "x": round(up, 3), "y": round(-right, 3), "rotation": -90, "scaleX": k, "scaleY": k}


skin['palm_r'] = {"palm_r": placed("palm_arm.png", palm['cuff'])}
skin['hand_r'] = {"hand_r": placed("palm_hand.png", palm['wrist'])}
skin['arm_r_front'] = {"handwear_r_arm": {**skin['handwear_r']['handwear_r'], "image": "handwear_r_arm.png"}}
motion['physics'] = physics

# ---------------------------------------------------------------- keys


def sine_keys(amp, period, dur, phase=0.0):
    """A sine as eight Bezier segments a period, each handle on the true tangent."""
    step = period / 8
    w_ = 2 * math.pi / period
    keys = []
    n = int(round(dur / step))
    for i in range(n + 1):
        t = i * step
        v = amp * math.sin(w_ * t + phase)
        key = {"t": round(t, 5), "v": [round(v, 4)]}
        if i < n:
            t2 = (i + 1) * step
            d1 = amp * w_ * math.cos(w_ * t + phase)
            v2 = amp * math.sin(w_ * t2 + phase)
            d2 = amp * w_ * math.cos(w_ * t2 + phase)
            key["curve"] = [round(t + step / 3, 5), round(v + d1 * step / 3, 4),
                            round(t2 - step / 3, 5), round(v2 - d2 * step / 3, 4)]
        keys.append(key)
    return keys


def tile(track, period, dur):
    """One looping track repeated to `dur`. A curve's control points are absolute times, so they move too."""
    out = dict(track)
    keys = []
    for r in range(int(round(dur / period))):
        for i, key in enumerate(track['keys']):
            if r > 0 and i == 0:
                continue
            moved = {"t": round(key['t'] + r * period, 5), "v": key['v']}
            if 'curve' in key:
                cv = key['curve']
                moved['curve'] = ([round(cv[0] + r * period, 5), cv[1], round(cv[2] + r * period, 5), cv[3]]
                                  if isinstance(cv, list) and len(cv) == 4 else cv)
            keys.append(moved)
    out['keys'] = keys
    return out


def gesture(points):
    """[(t, v), ...] as keys, eased in and out between each pair."""
    keys = []
    for i, (t, v) in enumerate(points):
        key = {"t": round(t, 5), "v": [v]}
        if i < len(points) - 1:
            t1, v1 = points[i + 1]
            span = t1 - t
            key["curve"] = [round(t + span * 0.42, 5), v, round(t1 - span * 0.42, 5), v1]
        keys.append(key)
    return keys


# The loop is LOOP seconds. The animation is LEAD + LOOP: it first replays the
# loop's last LEAD seconds, so that by the loop's first frame the physics are
# where they will be at its last. compose.py drops the lead-in.
LOOP, LEAD = 12.0, 4.0
TOTAL = LOOP + LEAD
CUT = LOOP - LEAD


def lay(points):
    """Points in loop time [0, LOOP], first and last value equal -> keys over [0, TOTAL]."""
    pts = sorted(points)
    assert pts[0][0] == 0 and pts[-1][0] == LOOP and pts[0][1] == pts[-1][1], points
    if not any(abs(t - CUT) < 1e-9 for t, _ in pts):
        before = max(p for p in pts if p[0] < CUT)
        after = min(p for p in pts if p[0] > CUT)
        assert before[1] == after[1], ('a key is needed at', CUT, points)
        pts = sorted(pts + [(CUT, before[1])])
    return gesture([(t - CUT, v) for t, v in pts if t >= CUT - 1e-9][:-1] + [(t + LEAD, v) for t, v in pts])


def steps(points):
    """Stepped keys (an attachment name or None) in loop time -> over [0, TOTAL]."""
    def at(t):
        return [v for q, v in points if q <= t][-1]
    keys = [(0.0, at(CUT))] + [(q - CUT, v) for q, v in points if q > CUT] + [(q + LEAD, v) for q, v in points]
    return [{"t": round(q, 5), "v": v} for q, v in keys]


def blink(t, low=0.12):
    return [(t, 1), (t + 0.07, low), (t + 0.15, low), (t + 0.27, 1)]


# ---------------------------------------------------------------- the performance
idle = motion['animations']['idle']
PERIOD = idle['duration']        # 4 s, which is also the swing's period
D = LOOP

# The idle's own blink and brow tracks are replaced: the expression is written here.
replaced = {('eyes', 'scaley'), ('brows', 'translatey')}
tracks = [tile(t, PERIOD, TOTAL) for t in idle['tracks'] if (t.get('group'), t['property']) not in replaced]

#        blink        closed-eye smile                              blink        startled                                      blink        smile through the wave
eyes = ([(0, 1)] + blink(0.9) + [(1.9, 1), (2.15, 0.38), (3.45, 0.38), (3.7, 1)] + blink(5.2)
        + [(6.88, 1), (6.98, 1.14), (7.45, 1.14), (7.75, 1)] + blink(8.6)
        + [(10.0, 1), (10.14, 0.38), (11.2, 0.38), (11.4, 1)] + [(D, 1)])
brows = [(0, 0), (1.9, 0), (2.15, 2.0), (3.45, 2.0), (3.7, 0), (6.88, 0), (6.98, 7.0), (7.45, 7.0), (7.8, 0), (D, 0)]
SHOW, HIDE = 9.82, 11.44         # the hand changes while the arm is already moving, clear of the face

tracks += [
    {"bone": "swing", "property": "rotate", "keys": sine_keys(2.5, 4.0, TOTAL)},
    # Depth by parallax, in step with the swing: what is nearer the viewer
    # (knees, feet, the chest's front) travels a little further than what is behind it.
    {"bone": "leg0_px", "property": "rotate", "keys": sine_keys(4.5, 4.0, TOTAL)},
    {"bone": "leg1_px", "property": "rotate", "keys": sine_keys(-1.5, 4.0, TOTAL)},
    {"bone": "leg0_px", "property": "translatey", "keys": sine_keys(7.0, 4.0, TOTAL)},
    {"bone": "chest_jiggle_px", "property": "translatex", "keys": sine_keys(4.0, 4.0, TOTAL)},
    {"bone": "chest", "property": "rotate", "keys": sine_keys(-1.5, 4.0, TOTAL, phase=-0.35)},
    # The face.
    {"group": "eyes", "property": "scaley", "keys": lay(eyes)},
    {"group": "brows", "property": "translatey", "keys": lay(brows)},
    {"bone": "mouth", "property": "scalex", "keys": lay(
        [(0, 1), (1.9, 1), (2.15, 1.22), (3.45, 1.22), (3.7, 1), (6.88, 1), (6.98, 0.78), (7.45, 0.78), (7.8, 1), (D, 1)])},
    {"bone": "mouth", "property": "scaley", "keys": lay(
        [(0, 1), (1.9, 1), (2.15, 1.10), (3.45, 1.10), (3.7, 1), (6.88, 1), (6.98, 1.7), (7.45, 1.7), (7.8, 1), (D, 1)])},
    {"bone": "head", "property": "rotate", "keys": lay(
        [(0, 0), (1.5, 0), (2.0, 7.5), (3.5, 7.5), (4.1, 0), (6.88, 0), (7.02, -3.5), (7.5, -2.0), (8.0, 0),
         (9.7, 0), (10.1, -5.5), (11.2, -5.5), (11.7, 0), (D, 0)])},
    # Kicking legs, then the hop: the seat jumps and everything on a spring follows late.
    {"bone": "leg1", "property": "rotate", "keys": lay(
        [(0, 0), (4.3, 0), (4.65, 9), (5.1, -8), (5.55, 9), (6.0, -7), (6.4, 0), (6.88, 0), (7.05, -12), (7.5, 3), (7.9, 0), (D, 0)])},
    {"bone": "leg0", "property": "rotate", "keys": lay(
        [(0, 0), (4.3, 0), (4.65, 2.5), (5.1, -2.5), (5.55, 2.5), (6.0, -2), (6.4, 0), (D, 0)])},
    {"bone": "seat", "property": "translatey", "keys": lay(
        [(0, 0), (6.74, 0), (6.88, -9), (7.06, 44), (7.30, -7), (7.52, 0), (D, 0)])},
    # The wave: the forearm from the elbow.
    {"bone": "sleeve_r0", "property": "rotate", "keys": lay(
        [(0, 0), (9.55, 0), (9.9, 27), (10.12, 32), (10.36, 22), (10.6, 32), (10.84, 22), (11.08, 30), (11.3, 26), (11.68, 0), (D, 0)])},
    # The hand follows the forearm a quarter beat late and only a little:
    # largest where the forearm is fastest, level where it turns.
    {"bone": "hand_r", "property": "rotate", "keys": lay(
        [(0, 0), (9.55, 0), (9.74, -6), (9.95, 0), (10.12, 0), (10.24, 7), (10.36, 0), (10.48, -7), (10.6, 0), (10.72, 7),
         (10.84, 0), (10.96, -6), (11.08, 0), (11.3, 0), (11.5, 5), (11.68, 0), (D, 0)])},
    {"slot": "handwear_r", "property": "attachment", "keys": steps([(0, "handwear_r"), (SHOW, None), (HIDE, "handwear_r")])},
    {"slot": "arm_r_front", "property": "attachment", "keys": steps([(0, None), (SHOW, "handwear_r_arm"), (HIDE, None)])},
    {"slot": "palm_r", "property": "attachment", "keys": steps([(0, None), (SHOW, "palm_r"), (HIDE, None)])},
    {"slot": "hand_r", "property": "attachment", "keys": steps([(0, None), (SHOW, "hand_r"), (HIDE, None)])},
]
# A closed eye is the lash alone: the iris and the white go out with the lid.
tracks += [{"slot": name, "property": "alpha", "keys": lay([(t, [1.0, 0.0][v < 0.5]) for t, v in eyes])}
           for name in ("iris_r", "iris_l", "eyewhite_r", "eyewhite_l")]

motion['animations'] = {"idle": idle, "show": {"duration": TOTAL, "loop": False, "tracks": tracks}}

json.dump({"D": LOOP, "WARM": LEAD, "physics": len(physics),
           "beats": {"smile": [1.9, 3.7], "kick": [4.3, 6.4], "hop": [6.74, 7.8], "wave": [9.8, 11.3]}},
          open(f'{DST}/show.json', 'w'))
json.dump(rig, open(f'{DST}/rig.json', 'w'))
json.dump(motion, open(f'{DST}/motion.json', 'w'))
black = dict(rig)
black['slots'] = [{**s, "color": "000000ff"} for s in rig['slots']]
json.dump(black, open(f'{DST}/rig_black.json', 'w'))
print('bones', len(bones), 'slots', len(rig['slots']), 'physics', len(physics), 'animations', list(motion['animations']))
