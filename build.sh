#!/usr/bin/env bash
# One painting to the trailer. Needs bun >= 1.2 (the tools run on it), npm, and python3 with numpy and pillow.
set -euo pipefail
cd "$(dirname "$0")"
BIN=node_modules/.bin
OUT=${TRAILER_OUT:-out/v2-final}
FPS=20
[ -x "$BIN/rig-parts" ] || npm ci

# 1. rig-parts: the painting and its two See-through layer sets -> parts -> rig -> check.
#    requirements.json says what the scene knows and the tool cannot: she sits, and one forearm is raised.
python3 tools/derive_trimmed_full.py inputs/layers-v2/full "$OUT/derived-full"
"$BIN/rig-parts" build --config inputs/config.json --source inputs/painting.png \
  --full "$OUT/derived-full" --head inputs/layers-v2/head \
  --requirements inputs/requirements.json --out "$OUT/parts"
bun tools/preflight.ts parts "$OUT/parts"

# 2. The film rig: the swing, the physics, the face's axis, the palm, the performance.
python3 film/palm.py inputs/palm.png "$OUT/parts/rig/images/handwear_r.png" "$OUT/palm"
python3 film/rig.py "$OUT/parts/rig" "$OUT/palm" "$OUT/film"
bun tools/preflight.ts film "$OUT/film"

# 3. rig-c: compile and gate, twice — the rig, and its black-tinted twin for the alpha channel.
"$BIN/rigc" build --rig "$OUT/film/rig.json" --motion "$OUT/film/motion.json" --out "$OUT/build" --profile spine
"$BIN/rigc" build --rig "$OUT/film/rig_black.json" --motion "$OUT/film/motion.json" --out "$OUT/build_black" --profile spine

# 4. rig-c: pose every frame. --geometry also writes the posed vertices and bones the reveal is drawn from.
"$BIN/rigc" render --candidate "$OUT/build" --fps "$FPS" --max 900 --geometry --extremes --folds --out "$OUT/render"
"$BIN/rigc" render --candidate "$OUT/build_black" --animation show --fps "$FPS" --viewport-from "$OUT/render/frames.json" --out "$OUT/render_black"

# 5. The film layer: sky, lights, the mesh-and-bone reveal, captions.
python3 film/compose.py "$OUT/render/show@${FPS}fps" "$OUT/render_black/show@${FPS}fps" \
  inputs/sky.png "$OUT/film/show.json" "$OUT/scene" "$FPS"
python3 tools/loop.py "$OUT/render/show@${FPS}fps/geometry.json"
python3 tools/bends.py "$OUT/render/show@${FPS}fps/geometry.json"
python3 tools/delivery.py "$OUT/scene" "$OUT/render/show@${FPS}fps/geometry.json" "$OUT/render/show@${FPS}fps/extremes.json" "$OUT/film/show.json"
echo "v2 delivery: $OUT/scene/trailer.webp"
