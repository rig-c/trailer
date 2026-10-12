#!/usr/bin/env python3
"""The film layer: everything in the trailer that is not the rig.

    python3 film/compose.py <frames> <black frames> <sky.png> <show.json> <out dir> [fps]

<frames> is a `rigc render --geometry` frame directory of the film rig, and
<black frames> the same render of its black-tinted twin. This script

  * recovers an alpha channel from the pair (the render's ground is opaque),
  * drops the lead-in and keeps the loop,
  * lays the rig over the painted sky with a drop shadow, drifting lights,
    twinkling stars and the mark as a faint constellation,
  * for one beat draws the rig's meshes and bones over it — from geometry.json,
    the posed vertices and bone transforms the render itself wrote, not a drawing,
  * adds the caption beats,
  * writes s####.jpg at 1920x1080, trailer.webp at 960x540 and a contact sheet.

None of this is a rig-c capability: it is one consumer composing a take around
an object the tools made. The rig is what moves; the rest is staging.

Captions use Avenir Next where it exists (macOS). Elsewhere set TRAILER_FONT to
a .ttf/.ttc path (and TRAILER_FONT_INDEX for a collection); only the caption
glyphs differ.
"""
import glob
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
LOGO = [(255, 45, 85), (255, 149, 0), (48, 209, 88), (10, 132, 255), (191, 90, 242)]
# Where the rig sits in the scene: its 1216-unit stage drawn CHAR_H px tall,
# the seat bone (world y 499) at scene y SEAT_Y, the stage's centre at x CX.
CHAR_H, CX, SEAT_Y, SEAT_WORLD_Y = 1000, 780, 668, 499.0


def load_font(size=60):
    candidates = []
    if os.environ.get('TRAILER_FONT'):
        candidates.append((os.environ['TRAILER_FONT'], int(os.environ.get('TRAILER_FONT_INDEX', '0'))))
    candidates += [('/System/Library/Fonts/Avenir Next.ttc', 2),
                   ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 0),
                   ('C:/Windows/Fonts/arialbd.ttf', 0)]
    for path, index in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size, index=index)
    return ImageFont.load_default(size)


FONT = load_font()


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def with_alpha(im, k):
    """`im` with its alpha multiplied by a number or an array."""
    a = np.asarray(im, np.float32).copy()
    a[:, :, 3] *= k
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


# ---------------------------------------------------------------- the rig's frames, with alpha

def rgba_frames(open_dir, black_dir):
    """Yield (RGBA frame, viewport). On a ground g, a pixel is c*a + g*(1-a); the black twin gives
    g*(1-a), so a = 1 - black/g, and c = (open - g*(1-a)) / a."""
    meta = json.load(open(os.path.dirname(open_dir.rstrip('/')) + '/frames.json'))
    ground = np.array(meta['background'][:3], np.float32)
    viewport = meta['viewport']
    opens = sorted(glob.glob(open_dir + '/f*.png'))
    blacks = sorted(glob.glob(black_dir + '/f*.png'))
    assert opens and len(opens) == len(blacks), (len(opens), len(blacks))
    for fo, fb in zip(opens, blacks):
        o = np.asarray(Image.open(fo).convert('RGB'), np.float32)
        k = np.asarray(Image.open(fb).convert('RGB'), np.float32)
        alpha = np.clip(1 - (k / ground).mean(axis=2), 0, 1)
        a3 = alpha[:, :, None]
        rgb = np.where(a3 > 1e-3, (o - ground * (1 - a3)) / np.maximum(a3, 1e-3), 0)
        yield Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), 'RGBA'), viewport


# ---------------------------------------------------------------- staging

def cover(path):
    b = Image.open(path).convert('RGB')
    s = max(W / b.width, H / b.height)
    b = b.resize((int(b.width * s + 0.5), int(b.height * s + 0.5)), Image.LANCZOS)
    ox, oy = (b.width - W) // 2, (b.height - H) // 2
    return b.crop((ox, oy, ox + W, oy + H)).convert('RGBA')


def orb_sprite(r, col):
    """A soft glowing bead: a bright core and a coloured halo."""
    S = 3
    n = int((r * 2 + 90) * S)
    c = n / 2
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx - c, yy - c) / (r * S)
    core = np.clip(1 - d, 0, 1) ** 0.6
    halo = np.exp(-(d ** 2) / 1.9)
    a = np.zeros((n, n, 4), np.float32)
    for k in range(3):
        a[:, :, k] = np.clip(col[k] * (0.55 + 0.45 * halo) + (255 - col[k]) * core ** 2.2 * 0.95, 0, 255)
    a[:, :, 3] = np.clip(core * 235 + halo * 120 * (d > 0.85), 0, 255)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    hl = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((c - r * S * 0.5, c - r * S * 0.62, c - r * S * 0.08, c - r * S * 0.28), fill=(255, 255, 255, 150))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(1.5 * S)))
    return im.resize((n // S, n // S), Image.LANCZOS)


def constellation():
    """The mark, faint and far behind: five joints and four bones."""
    S = 2
    layer = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, radius = 1500 * S, 380 * S, 235 * S
    pts = [(cx + radius * math.cos(math.radians(a)), cy - radius * math.sin(math.radians(a))) for a in (-58, -118, 180, 118, 58)]
    for i in range(4):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        for k in range(120):
            t = k / 119
            col = tuple(int(LOGO[i][q] + (LOGO[i + 1][q] - LOGO[i][q]) * t) for q in range(3))
            x, y, w = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 13 * S
            d.ellipse((x - w, y - w, x + w, y + w), fill=col + (255,))
    for i, (x, y) in enumerate(pts):
        r = (50 if i == 2 else 38) * S
        d.ellipse((x - r, y - r, x + r, y + r), fill=LOGO[i] + (255,))
        k = r * 0.42
        d.ellipse((x - k, y - k, x + k, y + k), fill=(14, 18, 44, 255))
    out = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    out.alpha_composite(with_alpha(layer.filter(ImageFilter.GaussianBlur(34 * S)), 0.5))
    out.alpha_composite(with_alpha(layer, 0.30))
    return out.resize((W, H), Image.LANCZOS)


def caption_sprite(text, col):
    pad = 40
    _, _, right, _ = FONT.getbbox(text)
    w, h = right + pad * 2 + 34, 60 + pad * 2
    shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((pad + 34, pad - 6), text, font=FONT, fill=(4, 6, 22, 255))
    a = np.asarray(shadow.filter(ImageFilter.GaussianBlur(7)), np.float32)
    a[:, :, 3] = np.clip(a[:, :, 3] * 1.6, 0, 255)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((pad, pad + 2, pad + 10, pad + 58), 5, fill=col + (255,))
    d.text((pad + 34, pad - 6), text, font=FONT, fill=(255, 255, 255, 255))
    return im


# ---------------------------------------------------------------- the film

def main(open_dir, black_dir, sky_path, show, out_dir, fps):
    os.makedirs(out_dir, exist_ok=True)
    loop, lead = show['D'], show['WARM']
    first, count = int(round(lead * fps)), int(round(loop * fps))
    geo = json.load(open(open_dir + '/geometry.json'))
    s = CHAR_H / 1216.0

    def X(wx):
        return CX + wx * s

    def Y(wy):
        return SEAT_Y - (wy - SEAT_WORLD_Y) * s

    # Mesh edges, once: the triangles are the rest geometry's, the vertices each frame's.
    edges = {}
    kinds = {}
    for rest in geo['rest']:
        kinds[rest['slot']] = rest['kind']
        if rest['kind'] != 'mesh':
            continue
        tri = rest['triangles']
        owners = {}
        for i in range(0, len(tri), 3):
            a, b, c = tri[i:i + 3]
            for p in ((a, b), (b, c), (c, a)):
                owners[tuple(sorted(p))] = owners.get(tuple(sorted(p)), 0) + 1
        # An edge one triangle owns is the mesh's outline; the rest are inside it.
        edges[rest['slot']] = (sorted(k for k, n in owners.items() if n > 1), sorted(k for k, n in owners.items() if n == 1))

    # Bones to draw: not the helper twins (`_ctl` the idle keys, `_px` the parallax keys),
    # not the swing, not the palm that is hidden during this beat.
    parent = {b['name']: b['parent'] for b in geo['bones']}

    def up(n):
        p = parent[n]
        while p and p.endswith(('_ctl', '_px')):
            p = parent[p]
        return p

    drawn = [n for n in parent if not n.endswith(('_ctl', '_px')) and n not in ('root', 'swing', 'seat', 'palm_r', 'hand_r')]

    def chain_of(n):
        while up(n) not in (None, 'root', 'swing', 'seat', 'hip', 'chest', 'head'):
            n = up(n)
        return n

    tops = sorted({chain_of(n) for n in drawn})
    colour = {n: LOGO[tops.index(chain_of(n)) % 5] for n in drawn}

    # The reveal wipes in from the left and out to the right.
    WIRE, FADE, SOFT = (4.10, 6.62), 0.55, 90.0
    left, right = CX - 620, CX + 620
    xs = np.arange(W, dtype=np.float32)[None, :]

    def wipe(t):
        if t <= WIRE[0] or t >= WIRE[1]:
            return None
        if t < WIRE[0] + FADE:
            edge = left + (right - left + SOFT) * smooth((t - WIRE[0]) / FADE)
            return np.clip((edge - xs) / SOFT, 0, 1)
        if t > WIRE[1] - FADE:
            edge = left - SOFT + (right - left + SOFT) * smooth((t - (WIRE[1] - FADE)) / FADE)
            return np.clip((xs - edge) / SOFT, 0, 1)
        return np.ones((1, W), np.float32)

    # The counts in the caption are read from the render: bones in the skeleton,
    # mesh attachments drawn in the middle of the reveal.
    mid = geo['frames'][int((lead + 5.0) * fps)]
    meshes = sum(1 for a in mid['attachments'] if kinds.get(a['slot']) == 'mesh' and a.get('vertices'))
    captions = [(0.40, 1.75, 'One painting.', 0),
                (1.95, 3.95, 'Rigged by an AI agent.', 1),
                (4.20, 6.55, f"{len(geo['bones'])} bones · {meshes} meshes", 3),
                (6.95, 9.30, 'Physics on every strand.', 4),
                (9.70, 11.70, 'Verified before it is written.', 2)]
    captions = [(a, b, caption_sprite(text, LOGO[ci])) for a, b, text, ci in captions]

    sky = cover(sky_path)
    sky.alpha_composite(Image.new('RGBA', (W, H), (6, 8, 26, 40)))
    sky.alpha_composite(constellation())
    random.seed(11)
    w0 = 2 * math.pi / loop          # every period below divides the loop, so the staging loops with it
    orbs = [(150, 300, 20, 4, 0.0), (420, 170, 12, 1, 1.3), (1700, 900, 26, 0, 2.1), (1220, 830, 14, 2, 0.7),
            (1830, 230, 10, 3, 2.9), (980, 120, 9, 0, 3.3), (100, 840, 30, 3, 1.9), (1560, 720, 8, 1, 0.4),
            (600, 960, 11, 4, 2.5), (300, 560, 9, 2, 1.1), (1130, 250, 7, 3, 0.2), (1750, 560, 12, 4, 1.6)]
    sprites = [orb_sprite(r, LOGO[ci]) for (_, _, r, ci, _) in orbs]
    stars = [(random.random() * W, random.random() * H * 0.62, random.uniform(1.2, 2.6), random.random() * 6.28,
              random.choice((3, 4, 5, 6, 7))) for _ in range(70)]

    frames = []
    for i, (frame, vp) in enumerate(rgba_frames(open_dir, black_dir)):
        j = i - first
        if j < 0 or j >= count:
            continue
        t = j / fps
        scene = sky.copy()
        d = ImageDraw.Draw(scene, 'RGBA')
        for (x, y, r, phase, n) in stars:
            a = 0.5 + 0.5 * math.sin(t * w0 * n + phase)
            rr = r * (0.7 + 0.6 * a)
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 255, int(60 + 180 * a)))
        for (x, y, r, ci, phase), sprite in zip(orbs, sprites):
            yy = y + 12 * math.sin(t * w0 * 3 + phase)
            xx = x + 5 * math.sin(t * w0 * 2 + phase * 1.7)
            scene.alpha_composite(sprite, (int(xx - sprite.width / 2), int(yy - sprite.height / 2)))

        # The rig, by the render's own viewport: world units -> frame px -> scene px.
        k = s / vp['scale']
        rig = frame.resize((int(frame.width * k + 0.5), int(frame.height * k + 0.5)), Image.LANCZOS)
        ox = CX + vp['x'] * s
        oy = SEAT_Y - ((vp['y'] + vp['height']) - SEAT_WORLD_Y) * s
        silhouette = Image.new('L', (W, H), 0)
        silhouette.paste(rig.split()[3], (int(ox), int(oy)))
        shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        shadow.paste((6, 8, 24, 255), (int(ox + 10), int(oy + 18)), rig.split()[3])
        scene.alpha_composite(with_alpha(shadow.filter(ImageFilter.GaussianBlur(16)), 0.38))
        scene.alpha_composite(rig, (int(ox), int(oy)))

        visible = wipe(t)
        if visible is not None:
            g = geo['frames'][i]
            assert g['index'] == i
            tint = np.zeros((H, W, 4), np.float32)
            tint[:, :, 0:3] = (8, 12, 44)
            tint[:, :, 3] = np.asarray(silhouette, np.float32) * 0.40 * visible
            scene.alpha_composite(Image.fromarray(tint.astype(np.uint8), 'RGBA'))
            S2 = 2
            wire = Image.new('RGBA', (W * S2, H * S2), (0, 0, 0, 0))
            wd = ImageDraw.Draw(wire)
            for att in g['attachments']:
                e = edges.get(att['slot'])
                v = att.get('vertices')
                if not e or not v:
                    continue
                for group, fill, width in ((e[0], (170, 228, 255, 95), 2), (e[1], (255, 255, 255, 235), 4)):
                    for a_, b_ in group:
                        wd.line((X(v[2 * a_]) * S2, Y(v[2 * a_ + 1]) * S2, X(v[2 * b_]) * S2, Y(v[2 * b_ + 1]) * S2),
                                fill=fill, width=width)
            pos = {b['name']: (X(b['worldX']) * S2, Y(b['worldY']) * S2) for b in g['bones']}
            for n in drawn:
                p = up(n)
                if p in (None, 'root', 'swing'):
                    continue
                (x0, y0), (x1, y1) = pos[p], pos[n]
                if math.hypot(x1 - x0, y1 - y0) > 4:
                    wd.line((x0, y0, x1, y1), fill=colour[n] + (255,), width=9)
            for n in drawn:
                x, y = pos[n]
                wd.ellipse((x - 13, y - 13, x + 13, y + 13), fill=colour[n] + (255,))
                wd.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 255, 255, 255))
            scene.alpha_composite(with_alpha(wire.resize((W, H), Image.LANCZOS), visible))

        for (a0, b0, sprite) in captions:
            if a0 <= t <= b0:
                rise = smooth((t - a0) / 0.35)
                al = rise * smooth((b0 - t) / 0.35)
                scene.alpha_composite(sprite if al >= 0.999 else with_alpha(sprite, al), (60, int(890 + 16 * (1 - rise))))
        im = scene.convert('RGB')
        im.save(f'{out_dir}/s{j:04d}.jpg', quality=92)
        frames.append(im)
    return frames


if __name__ == '__main__':
    open_dir, black_dir, sky_path, show_path, out_dir = sys.argv[1:6]
    fps = int(sys.argv[6]) if len(sys.argv) > 6 else 20
    frames = main(open_dir, black_dir, sky_path, json.load(open(show_path)), out_dir, fps)
    small = [f.resize((960, 540), Image.LANCZOS) for f in frames]
    small[0].save(out_dir + '/trailer.webp', save_all=True, append_images=small[1:], duration=int(1000 / fps),
                  loop=0, quality=72, method=6)
    sheet = Image.new('RGB', (960 * 4, 540 * 2))
    for q, t in enumerate((1.0, 2.8, 3.0, 5.1, 7.08, 7.4, 10.12, 10.6)):
        sheet.paste(small[int(t * fps)], ((q % 4) * 960, (q // 4) * 540))
    sheet.save(out_dir + '/sheet.jpg', quality=88)
    print(len(frames), 'frames ->', out_dir + '/trailer.webp', os.path.getsize(out_dir + '/trailer.webp') // 1024, 'KB')
