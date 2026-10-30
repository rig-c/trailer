#!/usr/bin/env python3
"""Inspect the encoded 960x540 delivery; crops keep its actual pixels, without resizing."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, __version__ as pillow_version

scene, geometry, extrema, show_path = map(Path, sys.argv[1:5])
geo = json.loads(geometry.read_text())
show = json.loads(show_path.read_text())
observations = json.loads(extrema.read_text())
yaw = next(c for c in observations['channels'] if c['path'] == ['bone', 'yaw_dial', 'rotate'])
spec = importlib.util.spec_from_file_location('trailer_compose', Path(__file__).resolve().parents[1] / 'film/compose.py')
compose = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compose)
movie = scene / 'trailer.webp'
out = scene / 'delivery-inspection'
out.mkdir(exist_ok=True)
fps = geo['fps']
lead = round(show['WARM'] * fps)
count = round(show['D'] * fps)
vp = geo['viewport']
scale = compose.CHAR_H / 1216.0
resize_width = int(vp['pixelWidth'] * scale / vp['scale'] + 0.5)
resize_height = int(vp['pixelHeight'] * scale / vp['scale'] + 0.5)
paste_x = int(compose.CX + vp['x'] * scale)
paste_y = int(compose.SEAT_Y - ((vp['y'] + vp['height']) - compose.SEAT_WORLD_Y) * scale)
head_slots = {'face', 'ear_r', 'ear_l', 'hair_front', 'hair_back', 'hairpin'}


def to_delivery(x, y):
    """Transport render-pixel boundaries through compose.py's actual integer resize/paste."""
    return ((paste_x + x * resize_width / vp['pixelWidth']) / 2,
            (paste_y + y * resize_height / vp['pixelHeight']) / 2)


def head_box(frame):
    vertices = [a['vertices'] for a in frame['attachments'] if a['slot'] in head_slots]
    xs = [v for a in vertices for v in a[0::2]]
    ys = [v for a in vertices for v in a[1::2]]
    left, top = to_delivery((min(xs) - vp['x']) * vp['scale'],
                            (vp['y'] + vp['height'] - max(ys)) * vp['scale'])
    right, bottom = to_delivery((max(xs) - vp['x']) * vp['scale'],
                                (vp['y'] + vp['height'] - min(ys)) * vp['scale'])
    return [max(0, math.floor(left) - 6), max(0, math.floor(top) - 6),
            min(960, math.ceil(right) + 6), min(540, math.ceil(bottom) + 6)]


selected = {'min-yaw': yaw['min']['index'] - lead, 'max-yaw': yaw['max']['index'] - lead,
            'art-before-reveal': round(3.90 * fps), 'art-after-reveal': round(5.70 * fps)}
assert all(0 <= n < count for n in selected.values())
sample_frames = [round(i * fps / 2) for i in range(24)]
sheet = Image.new('RGB', (5 * 240, 5 * 155), 'white')
draw = ImageDraw.Draw(sheet)
report = {'source': str(movie), 'source_sha256': hashlib.sha256(movie.read_bytes()).hexdigest(),
          'delivery_size': [960, 540], 'fps': fps, 'yaw_degrees': [yaw['min']['value'], yaw['max']['value']],
          'reveal_seconds': show['reveal'], 'head_crops': {}, 'legacy_rim_rois': {},
          'method': 'Decode the encoded WebP. All full frames and head/rim crops retain delivery pixels at 1:1. '
                    'Only the labelled whole-loop overview uses thumbnails. Max yaw lies during the reveal; '
                    'art-before/after-reveal frames are included separately.'}
durations = []
with Image.open(movie) as webp:
    assert webp.size == (960, 540) and webp.n_frames == count
    for n in range(count):
        webp.seek(n)
        frame = webp.convert('RGB')
        durations.append(webp.info.get('duration', 0))
        for label, index in selected.items():
            if n != index:
                continue
            box = head_box(geo['frames'][lead + n])
            frame.save(out / (label + '-frame-native.png'))
            frame.crop(box).save(out / (label + '-head-native.png'))
            report['head_crops'][label] = {'delivery_frame': n, 'rig_frame': lead + n,
                                         'loop_time': n / fps, 'box': box}
            if label == 'max-yaw':
                for name, original in {'bob': [535, 226, 548, 262], 'ahoge': [375, 140, 488, 187]}.items():
                    left, top = to_delivery(*original[:2])
                    right, bottom = to_delivery(*original[2:])
                    roi = [math.floor(left), math.floor(top), math.ceil(right), math.ceil(bottom)]
                    frame.crop(roi).save(out / (name + '-max-yaw-native.png'))
                    report['legacy_rim_rois'][name] = {'rig_render_box': original, 'delivery_box': roi}
        if n in sample_frames:
            i = sample_frames.index(n)
            thumbnail = frame.resize((240, 135), Image.Resampling.LANCZOS)
            x, y = i % 5 * 240, i // 5 * 155
            sheet.paste(thumbnail, (x, y + 18))
            draw.text((x + 3, y + 2), f'delivery {n / fps:.2f}s', fill='black')
assert sum(durations) == round(show['D'] * 1000), durations
sheet.save(out / 'delivery-loop-sheet.jpg', quality=92)
report.update(frame_count=count, duration_ms=sum(durations), pillow=pillow_version)
font_path = getattr(compose.FONT, 'path', None)
if isinstance(font_path, bytes):
    font_path = font_path.decode()
report['caption_font'] = {'path': font_path, 'sha256': hashlib.sha256(Path(font_path).read_bytes()).hexdigest()
                          if font_path and Path(font_path).is_file() else None}
report['files'] = [{'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
                   for p in sorted(out.iterdir()) if p.suffix in {'.png', '.jpg'}]
(out / 'delivery.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'delivery: {count} frames, {sum(durations)} ms, native 960x540; yaw {report["yaw_degrees"]}')
print(f'delivery crops and loop sheet: {out}')
