"""Restore the accepted hip-loop trim on a copy of a raw FULL run and its scalar sheet.

    python3 tools/derive_trimmed_full.py <raw-full-directory> <derived-directory>

Raw generation files and the already-trimmed painting are never edited. All layer boxes stay
registered to the original 1024 grid. Only back-hair alpha and corresponding loop depth samples
change. The scalar stays opaque grayscale, as rig-parts requires; its empty background is 255.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from trim_loops import keep_mask


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive(raw, out):
    if raw.resolve() == out.resolve() or raw.resolve() in out.resolve().parents or out.resolve() in raw.resolve().parents:
        raise ValueError('derived source must be separate from raw source')
    manifest = json.loads((raw / 'layers.json').read_text())
    art = np.array(Image.open(raw / 'parts/back hair.png').convert('RGBA'))
    scalar_image = Image.open(raw / 'parts/back hair_depth.png')
    if scalar_image.mode != 'L' or scalar_image.size != (1024, 1024):
        raise ValueError('expected the raw full-resolution opaque grayscale scalar')
    scalar = np.array(scalar_image)
    keep = keep_mask((art.shape[1], art.shape[0]))
    affected = (art[:, :, 3] > 0) & (keep < 1)
    corrected = art.copy()
    corrected[:, :, 3] = np.round(art[:, :, 3] * keep).astype(np.uint8)
    depth = scalar.copy()
    depth[affected] = np.round(scalar[affected] * keep[affected] + 255 * (1 - keep[affected])).astype(np.uint8)
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(raw / 'parts', out / 'parts', dirs_exist_ok=True)
    Image.fromarray(corrected).save(out / 'parts/back hair.png')
    Image.fromarray(depth).save(out / 'parts/back hair_depth.png')
    # Plain extracted filenames describe this derivation, not another generated run.
    manifest['prefix'] = 'derived_full_without_hip_loops'
    manifest['timestamp'] = 'deterministic-v1-trim'
    for row in manifest['layers']:
        row['filename'] = row['name'] + '.png'
        if 'depth_filename' in row:
            row['depth_filename'] = row['name'] + '_depth.png'
    (out / 'layers.json').write_text(json.dumps(manifest, indent=2) + '\n')
    changed = [p.name for p in sorted((raw / 'parts').glob('*.png')) if sha(p) != sha(out / 'parts' / p.name)]
    assert changed == ['back hair.png', 'back hair_depth.png'], changed
    assert np.array_equal(art[:, :, :3], corrected[:, :, :3])
    assert np.array_equal(art[~affected], corrected[~affected])
    assert np.array_equal(scalar[~affected], depth[~affected])
    assert np.array_equal(art[keep == 1], corrected[keep == 1])
    report = {
        'spec': 'trailer-derived-layers/1', 'operation': 'accepted v1 trim_loops keep mask; painting not rerun',
        'raw_directory': str(raw), 'raw_meta_sha256': sha(raw / 'meta.json'),
        'raw_manifest_sha256': sha(raw / 'layers.json'),
        'legacy_helper_sha256': sha(Path(__file__).with_name('trim_loops.py')),
        'deriver_sha256': sha(Path(__file__)),
        'registration': 'unchanged 1024-square source canvas and all layer boxes',
        'alpha_changed_pixels': int(np.count_nonzero(art[:, :, 3] != corrected[:, :, 3])),
        'scalar_changed_pixels': int(np.count_nonzero(scalar != depth)),
        'depth_background': 255, 'depth_mode': 'L; opaque grayscale',
        'only_changed_files': changed, 'unaffected_pixels_equal': True, 'all_other_parts_byte_equal': True,
        'files_sha256': {str(p.relative_to(out)): sha(p) for p in sorted((out / 'parts').glob('*.png'))},
        'manifest_sha256': sha(out / 'layers.json'),
    }
    (out / 'meta.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['alpha_changed_pixels', 'scalar_changed_pixels', 'only_changed_files', 'unaffected_pixels_equal']}))


if __name__ == '__main__':
    derive(Path(sys.argv[1]), Path(sys.argv[2]))
