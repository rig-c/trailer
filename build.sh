#!/usr/bin/env bash
# One painting to the trailer. Needs bun >= 1.2 (the tools run on it), npm, and python3 with numpy and pillow.
set -euo pipefail
cd "$(dirname "$0")"
BIN=node_modules/.bin
OUT=out
FPS=20
[ -x "$BIN/rig-parts" ] || npm install
python3 -c 'import json, pathlib, re; v = lambda k: json.load(open(f"node_modules/{k}/package.json"))["version"]; vp, vr = v("@rig-c/parts"), v("rig-c"); p = pathlib.Path("README.md"); p.write_text(re.sub(r"# installs @rig-c/parts [0-9.]+ and rig-c [0-9.]+", f"# installs @rig-c/parts {vp} and rig-c {vr}", p.read_text()))'

# 1. rig-parts: the painting and its two See-through layer sets -> parts -> rig -> check.
#    requirements.json says what the scene knows and the tool cannot: she sits, and one forearm is raised.
"$BIN/rig-parts" build --config inputs/config.json --source inputs/painting.png \
  --full inputs/layers/full --head inputs/layers/head \
  --requirements inputs/requirements.json --out "$OUT/parts"

# 2. The film rig: the swing, the physics, the face's axis, the palm, the performance.
python3 film/palm.py inputs/palm.png "$OUT/parts/rig/images/handwear_r.png" "$OUT/palm"
python3 film/rig.py "$OUT/parts/rig" "$OUT/palm" "$OUT/film"

# 3. rig-c: compile and gate, twice — the rig, and its black-tinted twin for the alpha channel.
"$BIN/rigc" build --rig "$OUT/film/rig.json" --motion "$OUT/film/motion.json" --out "$OUT/build" --profile spine
"$BIN/rigc" build --rig "$OUT/film/rig_black.json" --motion "$OUT/film/motion.json" --out "$OUT/build_black" --profile spine

# 4. rig-c: pose every frame. --geometry also writes the posed vertices and bones the reveal is drawn from.
"$BIN/rigc" render --candidate "$OUT/build" --animation show --fps "$FPS" --max 900 --geometry --out "$OUT/render"
"$BIN/rigc" render --candidate "$OUT/build_black" --animation show --fps "$FPS" --max 900 --out "$OUT/render_black"

# 5. The film layer: sky, lights, the mesh-and-bone reveal, captions.
python3 film/compose.py "$OUT/render/show@${FPS}fps" "$OUT/render_black/show@${FPS}fps" \
  inputs/sky.png "$OUT/film/show.json" "$OUT/scene" "$FPS"
echo "done: $OUT/scene/trailer.webp"
