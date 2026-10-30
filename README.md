# The rig-c trailer v2, reproducible

<p align="center">
  <img src="trailer.webp" alt="A character on a swing under a night sky breathes, tilts, smiles and looks around, her long hair draping over the seat; she kicks, hops and waves while a reveal shows her moving meshes and bones" width="100%" />
</p>

The loop on the [rig-c organisation's front page](https://github.com/rig-c), with everything that made it:
one generated painting, its See-through layer sets, the config an agent wrote for
[`@rig-c/parts`](https://github.com/rig-c/parts), and a few short scripts. One command rebuilds the loop
from them with the published packages.

v2 is the same painting, character, swing and sky as v1, and the same 12-second performance with one beat
added: she looks around, through a sampled 2.5D depth turn built from the layers' depth sheets, and the
mesh-and-bone reveal now runs during that turn. Her long hair is drawn in front of the swing bar and drapes
over the seat, held there by angular stops on the moving seat rather than by keys; the twin tails move on
springs alone.

It is here as a worked case, not as a template: a character that is not standing, a prop that is part of
her skeleton, a performance longer than an idle, a depth turn on a painting that was never regenerated,
and a record of what was measured on the way — including the two things this film does not do.

To change the film rather than rebuild it, read [WORKING.md](WORKING.md): where each kind of change goes,
how to check one without being able to watch it, and every measurement behind the figures on this page.

## Reproduce

```bash
git clone https://github.com/rig-c/trailer && cd trailer
pip install -r requirements.txt      # numpy 2.4.4, pillow 12.2.0
./build.sh                           # npm ci if node_modules is missing, then the five steps
```

Needs [bun](https://bun.sh) ≥ 1.4 (the packages declare it as their engine), npm, and python3. The
lockfile pins `@rig-c/parts` 1.79.1, `@rig-c/pose` 1.5.4 and `rig-c` 2.81.1. No GPU and no ComfyUI: the
painting, the sky, the palm and both See-through layer sets are inputs, already in `inputs/`.

The result is `out/v2-final/scene/trailer.webp` (960×540, 240 frames, 12 s at 20 fps), with the 1920×1080
frames beside it, a contact sheet, and a `delivery-inspection/` folder of frames and crops read from the
encoded file. `TRAILER_OUT=<dir>` puts all of it somewhere else. The build never touches the root
`trailer.webp`; that file is the published loop, copied there by hand, and the last line `build.sh` prints
is the path of the one it just wrote.

The whole build took **3 min 58 s** (237.841 s, excluding the install) on a Linux x86-64 runner, measured
once from a fresh locked install with nothing carried over — `BUILD-FINAL.json` is that run's record. It
reproduced the root `trailer.webp` byte for byte: 6,405,916 bytes, SHA-256
`631e74967074dd59d405cd137a4d4783820559b852c1485e0a13cd365139ad24` (python 3.12.3). Another machine's
encoders and caption font can move bytes without moving the picture; the figure is one measurement, not a
benchmark.

| | |
| --- | --- |
| **An input, not rebuilt** | `inputs/painting.png` (the v1 painting, unchanged), `inputs/layers-v2/` (the two v2 See-through runs: full body and head crop, 29 art/depth pairs each), `inputs/sky.png`, `inputs/palm.png` — generated on a ComfyUI box; `generation.json` (its `v2_depth` block for the new runs), `sky.json` and `palm.json` record how. `inputs/layers/` is v1's layer sets, kept. `tools/trim_loops.py` is the one edit made to the painting in v1; its mask is reused in step 1 |
| **Written by the author (an AI agent)** | `inputs/config.json`, `keypoints.json`, `requirements.json`, `film/`, and the three readers `build.sh` runs between steps: `tools/derive_trimmed_full.py`, `tools/preflight.ts`, `tools/delivery.py` |
| **Rebuilt by `build.sh`** | the derived full-body run, the parts, the rig, the compiled skeletons, every rendered frame of five animations, the composite, the inspection crops |

## The five steps

**1. Parts, rig, check** — `tools/derive_trimmed_full.py`, then `rig-parts build`. The full-body run is
copied to `out/v2-final/derived-full` with v1's hip-loop trim applied to its back-hair layer and that
layer's depth sheet (3,460 alpha pixels and 3,179 depth samples change; the script asserts that every
other file came through byte-identical). The raw run in `inputs/` is never edited. The painting and the two
runs are then assembled into 23 rig-ready parts, meshed and weighted to the bones `config.json` declares
(ten meshes, 1,702 triangles — seven on a traced `contour`, two on `auto`, the neck on a grid; the per-part
table is in WORKING.md), given a four-second idle and three diagnostic turns, and checked. Twelve bars are
measured and all twelve pass, two of them through a declaration: `rig-parts check` assumes a figure that
stands, and `inputs/requirements.json` says what the scene knows and the tool cannot — she sits, so her
shoes are not planted, and her right forearm rises from the elbow. Two more bars print as SKIP notes
rather than counting (`SEAM_OVER_MOTION`: no neighbour pair; `CLOTH_SETTLES`: the parts carry no physics
yet — the springs arrive in step 2), and `RECOMPOSITE_HOLES` reports 4,093 uncovered pixels without being
a bar. `tools/preflight.ts parts` then confirms every part has both its art and its depth sheet.

**2. The film rig** — `film/palm.py`, `film/rig.py`. Plain rig-spec and motion-spec data added to what
step 1 wrote: the swing, a physics constraint on every chain and the soft chest (26 in all), the breath,
two gaze bones under the eyes, the palm, the two seat stops, and one animation. `tools/preflight.ts film`
parses the result with the packages' own parsers and refuses a timeline that does not increase or a last
key that carries a curve.

**3. Compile and gate** — `rigc build`, twice. Nothing is written unless the gate is green, and each build
ends on the same summary line:

```
  ..    52 assertions: 26 measured (26 passed, 0 failed), 12 skipped, 14 not in profile "spine"
```

One of the twelve skips is `A00_ROUNDTRIP_PARSE`, the parse by the official Spine runtime: the published
package does not carry `spine-core`, so rigc's own validator gates the build in its place and says so. The
compiled rig has 107 bones (99 authored, 8 generated for the stops), 29 slots, 26 physics constraints and
2,120 mesh triangles. The second build is the same rig with every slot tinted black; step 5 needs it.

**4. Pose** — `rigc render`. Every animation of the build — the idle and three diagnostic turns from step
1, and `show` — posed at 20 fps, 495 frames in all; `--geometry` writes every bone's world transform and
every mesh vertex after skinning per frame, `--extremes` writes each animation's two farthest poses, and
`--folds` names any triangle that turns over. None does, in any of the five. Then the black twin, `show`
only, framed by the first render's viewport.

**5. The film layer and the readings** — `film/compose.py`. Sky, lights, the mesh-and-bone reveal, captions;
240 frames at 1920×1080, the WebP at 960×540, a contact sheet. Then three readers over what was just
written: `tools/loop.py` (does the loop close — 0.000 units on both the largest bone offset and the
largest vertex offset), `tools/bends.py` (how far the film turns each bone from its setup pose), and
`tools/delivery.py`, which decodes the encoded WebP, asserts 240 frames and 12,000 ms, and writes the
inspection folder: full frames and head crops at both yaw extremes and on either side of the reveal, all
at the file's own pixels, plus a labelled whole-loop sheet and a JSON of hashes.

## What the rig is

| Beat | Seconds | What moves it |
| --- | --- | --- |
| Sway | whole loop | `swing` rotates ±2.5° on a 4 s period about a pivot far above the frame; `seat` and the whole character hang under it |
| Breath | whole loop, 3 s | the chest rises 14 units and widens; the shoulders follow 0.12 s late and the head 0.2 s late; hair and the soft chest carry it through their springs |
| Tilt and smile | 1.5 – 3.75 | `head` rotation to 7.5°; the `eyes` group's `scaley`, `brows`, `mouth` |
| Look around | gaze 3.60 – 5.40, head 3.85 – 5.90 | `yaw_dial` turns the sampled depth field to +12°, then −12°, then back; the irises move 3 units ahead of it, each change 0.25 s before the head's |
| The reveal | 3.95 – 5.65 | not the rig: the film layer drawing the render's own geometry, over the turn |
| Kicking legs | 6.0 – 7.7 | `leg1` rotation ±9°, `leg0` ±2.5°, with a spring on both leg bones |
| Hop | 8.1 – 8.88 | `seat` jumps 44 units; everything on a spring arrives late |
| Wave | 9.55 – 11.68 | the forearm from the elbow to 32°, an open palm swapped in from 9.82 to 11.44, the hand trailing at the wrist by ±7° |

The animation is 16 s: a 4 s lead-in that replays the loop's last four seconds, then the loop, so that by
the loop's first frame every spring is where it will be at its last. Step 5 keeps only the loop.

**The swing is two bones of her skeleton** (`root > swing > seat > hip`), and its bar and ropes are three
attachments on `seat`. So the sway is ordinary bone motion, and it reaches her hair the way any motion of a
parent does: through the physics constraints on the chains. Nothing synchronises a character to a prop.

**26 physics constraints.** `rig-parts` keys its idle on a `<bone>_ctl` parent of every chain link, which
leaves the link itself free for a constraint; `rig.py` gives one to each link of the twin tails, bangs,
tassel, skirt, sleeve and legs, tapering in strength toward the tip, and one to the chest. The eight tail
springs live in the rig's own constraint list, where the stops can read them; the other eighteen stay in
the motion table.

**Depth by parallax, and now by a sampled surface.** Three bones get a keyed twin above them (`leg0_px`,
`leg1_px`, `chest_jiggle_px`), keyed in step with the swing: what is nearer the viewer travels a little
further than what is behind it, and the torso leans 1.5° against the sway. That is v1's depth and it is
still here. The look-around is the new kind — see *The depth turn*.

**The meshes.** Each part is on the mode that measured smaller or did not fold: `hair_back` and
`handwear_l` on `auto`, the neck on a grid, and the other seven — including the long hair at 434
triangles and the topwear at 384 — on a traced `contour`. The front hair and the legwear were tried on
`auto` first and refused: at the bends this film puts them through their reduced motion residuals were
5.55 px and 5.90 px against a 3 px limit, so they went to `contour` at 127 and 158 triangles. The topwear's
soft region sits on `chest_jiggle` with band 27. The hairpin declares continuous, uncapped influences
because a cap of one bone produced a discontinuity and eight folded frames; the long hair and the topwear
declare the same. The
largest turns the film makes from the setup pose, read by `tools/bends.py`: the bangs 13.1°, 11.1° and
12.4°, the leg 15.4°, the hairpin's tassel 93.2°, the yaw dial 12.0°.

## The depth turn

The painting was not regenerated. Two new See-through runs of it — the full body and the head crop, 29
layers each at 1024² with depth inferred at 512, seed 42, 30 steps — give every part an art image and a
depth sheet, and `inputs/generation.json` binds the runs to their input bytes, settings and prompt.

`config.json`'s `turn` block says how the head reads them: the face is a sampled *surface*; the hair,
hairpin, ears, eyes, brows, lashes and mouth are *units* at declared depths (front hair 65, back hair −14,
long hair −22, hairpin −8, ears 20 and 12). The body has a turn of its own on `chest`, with the topwear as
its surface and the neck as a unit at 52.1765 — a figure `rig-parts propose --write-config` drafted from
the neck layer rather than from a collar fragment. `keep_under_occluders` names nine parts whose complete
content is kept beneath translucent covers, and `yield_refused` lets front pixels the depth read refused
pass to the opaque part that holds them, under the package's own ownership rule.

The look itself is one keyed bone, `yaw_dial`, at ±12°: the sampled field displaces each part by
−depth·sin(yaw), so the head does not spin, it turns. A ±8° version was built and compared at 960×540 and
in head crops; ±12° reads more clearly and is the one kept. At the far end of the turn, under enlargement,
the hair's outer edge shows a light double contour. It is in the source layers — the registered source
crops carry it, and a reconstruction of the rendered frame from the layers matches every pixel of the two
regions measured — and nothing here repainted or masked it; at the trailer's own size it reads as a
highlight. WORKING.md records the two attempts at a cleaner source and why neither was used.

## Hair, swing and seat

**Draw order.** Back to front: the ropes, the bar, the long hair, then the body, skirt and legs. v1 drew the
bar in front of the hair; here `rig.py` inserts the bar's slot immediately before `hair_long`, so the
tails fall across the bar and the skirt and legs still cover them. Nothing else changed for that: no
pixel, mesh, weight, spring or key.

**The tails move on springs alone.** The idle's keyed tail motion is removed and each of the four links on
either side carries a rotation spring: strengths 105, 84, 67.2 and 53.8 down the chain, damping 0.85,
inertia 0.2 on the upper two links and 0.1 on the lower two, and gravity 120 on the root link only, so the
hair hangs below its moving attachment while the painted curl at the tip is kept. The key removal and the
spring settings are one change; the film does not show that gravity alone would have done it.

**Two stops drape the hair over the seat.** `rig.json` declares `tail_r_seat` and `tail_l_seat`: each
clamps the second link of a tail (`tail_r1`, `tail_l1`) against a point that rides on `seat` — (−246, 27)
and (255, 27) in the seat's own frame — with 0° of travel inward and 60° outward. The compiler generates
eight helper bones for them; the clamped link is drawn through its `_d` twin and the links below it keep
their own springs.

**What that is and is not.** It is an angular stop that follows a point on a moving bone. It is not a
surface-contact solver: there is no line projection, no friction, no collision against the bar's pixels.
So the hair is not certified as resting on the bar. Measured over all 240 loop frames in the seat's
frame, the third link's origin never drops below the bar's top (its clearance is at least 11.79 px on the
right and 12.49 px on the left), but the clamped link's centre moves off the height it rests at in the
setup pose by an RMS of 5.72 px on the right and 5.83 px on the left, against a bar 1 px thick at that
scale — the check for "resting on the bar" reads red on both sides, and the film is published with it
red. The tails also fan wider than in the earlier build where they hung straight down: the outer span of
their lower material grows by 51.8 px at 2.0 s and 59.1 px at 3.5 s. At 960×540 the hair reads as lying
over the seat; those three numbers are what that reading is worth.

**The hip loops.** v1's painting had a ring of hair erased beside each hip (`tools/trim_loops.py`),
because on a figure sitting in mid-air they read as hair lying on a floor that is not there. The v2
full-body run was made from the untrimmed source and brought both rings back; step 1 applies the same
mask to the derived copy, and all 240 frames' hip regions were read at 1:1 from the decoded WebP with no
ring restored and no gap or severed strand where they were.

## Validation and inspection

`build.sh` assembles, rigs and checks the parts, writes the film rig, compiles and gates both skeletons,
poses five animations, composes the loop and reads it back. What those readings say of this build,
recorded in `BUILD-FINAL.json`:

| Reading | Result |
| --- | --- |
| `rigc build`, normal and black | 52 assertions each: 26 pass, 0 fail, 12 skip, 14 outside the `spine` profile |
| `rig-parts check` | 12 bars measured, 12 pass; `SEAM_OVER_MOTION` and `CLOTH_SETTLES` as SKIP notes; no temporal requirement declared |
| `rigc render --folds` | 0 folded meshes in every animation (11 meshes in idle, turn, tilt and body_turn; 12 in show, with the wave's sleeve copy) |
| `tools/loop.py` | largest bone and vertex offset at the seam both 0.000 units (rounded, not mathematical zero) |
| `tools/delivery.py` | 240 frames, 12,000 ms, 960×540; yaw channel read at −12° and +12° |
| the seat stops | clearance ≥ 11.79 / 12.49 px; centreline RMS 5.72 / 5.83 px against 1 px, red |

A green gate is not a verdict on the picture, and this page does not pretend it is. What was looked at:
the inspection folder's native frames and head crops at both ends of the turn, the same frames with the
reveal switched off so the underlying art could be read, the hip regions of every frame at 1:1, and
full-frame comparisons at the swing's two extremes for the hair-over-bar order and the seat stops. The
hair's double contour, the red contact check and the wider fan are the limits that reading found, and
they are stated above rather than fixed in the picture.

`rig-c` makes an object that can be directed; composing the shot is the consumer's, and this repository
is a consumer. The rig is every motion in the table above, compiled by `rigc build` and posed by
`rigc render`. The staging is the sky, the lights, the shadow, the captions and the choice of when she
does what. The reveal is in between and honest about it: `compose.py` draws the lines at the positions
`geometry.json` gives for that frame, and the caption's counts — bones in the skeleton, meshes drawn —
are read from the same file. The frames are posed, not played by [`@rig-c/play`](https://github.com/rig-c/play):
the trailer is a video. The compiled model in `out/v2-final/build/` is an ordinary rig-c model and is
what `@rig-c/play` would load.

## Files

```
build.sh                    the five steps
film.sh                     steps 2-5 alone, reusing the built parts, for a change to film/
WORKING.md                  how to change the film, and every measurement behind this page
BUILD-FINAL.json            the record of the measured build; BUILD-V2, -RING-FIX, -LAYERING, -PHYSICS.json are the builds before it
inputs/painting.png         the generated painting, 1664×2432; generation.json and pose_seated.json record it
inputs/layers-v2/           the two v2 See-through runs (full body, head crop): art and depth per layer, and what each was fed
inputs/layers/              v1's two runs, kept for the record
inputs/config.json          the rig-parts config: plan, bones, meshes, regions, motion, depth, turn
inputs/keypoints.json       the joints, read off the painting
inputs/requirements.json    what the scene declares to the check
inputs/sky.png              the painted sky; sky.json records it
inputs/palm.png             the generated open hand; palm.json records it
film/palm.py                the palm, cut out, recoloured and split at the wrist
film/rig.py                 the film rig: swing, springs, stops, gaze, palm, the performance
film/compose.py             the film layer
tools/derive_trimmed_full.py  the hip-loop trim applied to a copy of the full-body run
tools/preflight.ts          the inputs of steps 1 and 2 parsed before anything is compiled
tools/delivery.py           the encoded loop decoded and cropped at its own pixels
tools/                      the readings WORKING.md describes: frames.py (two builds, frame by frame),
                            moved.py (which bones a change moved), overlay.py (two frames, red and cyan),
                            loop.py (does the loop close; does anything pop), bends.py (how far the film
                            turns each bone from its setup pose); trim_loops.py is v1's input edit
trailer.webp                the published loop; build.sh writes its own under out/
```

## Licence

MIT, covering the scripts, the generated images and the trailer — see `LICENSE`. `NOTICE.md` names the
checkpoint the images were generated with, See-through, and the tools the build runs.
