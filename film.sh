#!/usr/bin/env bash
# Steps 2-5 of build.sh, reusing out/parts: for a change to film/ (the performance or the staging).
# A change to inputs/config.json needs ./build.sh — the parts and the rig are rebuilt there.
set -euo pipefail
cd "$(dirname "$0")"; BIN=node_modules/.bin; OUT=${TRAILER_OUT:-out/v2-final}; FPS=20
# The last build's frames are kept as out/prev, because every reading in WORKING.md compares two builds.
if [ -d "$OUT/scene" ] && [ -d "$OUT/render" ]; then
  rm -rf "$OUT/prev" && mkdir "$OUT/prev" && mv "$OUT/scene" "$OUT/render" "$OUT/prev/" && cp -R "$OUT/film" "$OUT/prev/film"
fi
rm -rf "$OUT/film" "$OUT/build" "$OUT/build_black" "$OUT/render" "$OUT/render_black" "$OUT/scene"
python3 film/rig.py "$OUT/parts/rig" "$OUT/palm" "$OUT/film"
"$BIN/rigc" build --rig "$OUT/film/rig.json" --motion "$OUT/film/motion.json" --out "$OUT/build" --profile spine
"$BIN/rigc" build --rig "$OUT/film/rig_black.json" --motion "$OUT/film/motion.json" --out "$OUT/build_black" --profile spine
"$BIN/rigc" render --candidate "$OUT/build" --animation show --fps "$FPS" --max 900 --geometry --extremes --folds --out "$OUT/render"
"$BIN/rigc" render --candidate "$OUT/build_black" --animation show --fps "$FPS" --viewport-from "$OUT/render/frames.json" --out "$OUT/render_black"
python3 film/compose.py "$OUT/render/show@${FPS}fps" "$OUT/render_black/show@${FPS}fps" inputs/sky.png "$OUT/film/show.json" "$OUT/scene" "$FPS"
python3 tools/loop.py "$OUT/render/show@${FPS}fps/geometry.json"
python3 tools/bends.py "$OUT/render/show@${FPS}fps/geometry.json"
python3 tools/delivery.py "$OUT/scene" "$OUT/render/show@${FPS}fps/geometry.json" "$OUT/render/show@${FPS}fps/extremes.json" "$OUT/film/show.json"
echo "done: $OUT/scene/trailer.webp"
