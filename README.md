# The rig-c trailer, reproducible

<p align="center">
  <img src="trailer.webp" alt="A character on a swing under a night sky tilts her head, smiles, kicks her legs, hops and waves, her twin tails following; for one beat her meshes and bones are drawn over her" width="100%" />
</p>

The loop on the [rig-c organisation's front page](https://github.com/rig-c), with everything that made it:
one generated painting, its two See-through layer sets, the config an agent wrote for
[`@rig-c/parts`](https://github.com/rig-c/parts), and three short scripts. One command rebuilds the loop
from them with the published packages.

It is here as a worked case, not as a template: a character that is not standing, a prop that is part of
her skeleton, a performance longer than an idle, and a record of what review caught on the way.

## Reproduce

```bash
git clone https://github.com/rig-c/trailer && cd trailer
pip install -r requirements.txt      # numpy, pillow
./build.sh                           # installs @rig-c/parts 1.6.0 and rig-c 2.39.1, then runs the five steps
```

Needs [bun](https://bun.sh) ≥ 1.2 (the tools run on it), npm, and python3. No GPU and no ComfyUI: the
painting, the sky, the palm and the See-through layers are inputs, already in `inputs/`.
The whole build took 7 min 43 s on an Apple M4 (measured once).

The result is `out/scene/trailer.webp` (960×540, 240 frames, 12 s at 20 fps), with the 1920×1080 frames
beside it and a contact sheet. Run from a clean directory with the published packages, on the machine the trailer was made on, it reproduced the published loop byte for byte — all 240 frames and the WebP (python 3.13.1, pillow 12.2.0, numpy 2.4.4, bun 1.4.2). Another machine's encoders and caption font can move bytes without moving the picture.

| | |
| --- | --- |
| **An input, not rebuilt** | `inputs/painting.png`, `inputs/layers/` (See-through), `inputs/sky.png`, `inputs/palm.png` — generated on a ComfyUI box; `generation.json`, `sky.json` and `palm.json` record how |
| **Written by the author (an AI agent)** | `inputs/config.json`, `keypoints.json`, `requirements.json`, and `film/` |
| **Rebuilt by `build.sh`** | the parts, the rig, the compiled skeleton, every rendered frame, the composite |

## The five steps

**1. Parts, rig, check** — `rig-parts build`. The painting and the two See-through runs are assembled into
23 rig-ready parts, meshed and weighted to the bones `config.json` declares, given a four-second idle, and
checked. The check passes nine bars of nine, two of them through a declaration:

```
BREATH_VISIBLE: PASS — declared_not_planted shoes; …
TIP_OVER_ROOT: PASS — declared_rises handwear_r; …
check: PASS; 9 of 9 bar(s) measured, 0 skipped
```

`rig-parts check` assumes a figure that stands. `inputs/requirements.json` says what the scene knows and the
tool cannot: she sits, so her shoes are not planted, and her right forearm rises from the elbow. A relaxed
bar prints the declaration first, so it never reads as a passed one.

**2. The film rig** — `film/palm.py`, `film/rig.py`. Plain rig-spec and motion-spec data added to what
step 1 wrote: the swing, a physics constraint on every chain, the face's axis, the palm, and one animation.
The sections below say what each is for.

**3. Compile and gate** — `rigc build`, twice. Nothing is written unless the gate is green:

```
52 assertions: 19 measured (19 passed, 0 failed), 17 skipped, 16 not in profile "spine"
bones=79 slots=29 animations=2 regionAttachments=18 meshAttachments=11 physicsConstraints=24
```

The second build is the same rig with every slot tinted black; step 5 needs it.

**4. Pose** — `rigc render --geometry`. 321 frames of the rig, and `geometry.json`: every bone's world
transform and every mesh vertex after skinning, per frame.

**5. The film layer** — `film/compose.py`. Sky, lights, the mesh-and-bone reveal, captions.

## What the rig is

| Beat | Seconds | What moves it |
| --- | --- | --- |
| Sway | whole loop | `swing` rotates ±2.5° about a pivot far above the frame; `seat` and the whole character hang under it |
| Tilt and smile | 1.5 – 4.1 | `head` rotation; the `eyes` group's `scaley`, `brows`, `mouth` |
| Kicking legs | 4.3 – 6.4 | `leg1` rotation, with a spring on both leg bones |
| The reveal | 4.1 – 6.6 | not the rig: the film layer drawing the render's own geometry |
| Hop | 6.7 – 7.8 | `seat` jumps 44 units; everything on a spring arrives late |
| Wave | 9.6 – 11.7 | the forearm from the elbow, an open palm swapped in, the hand trailing at the wrist |

**The swing is two bones of her skeleton** (`root > swing > seat > hip`), and its bar and ropes are three
attachments on `seat`. So the sway is ordinary bone motion, and it reaches her hair the way any motion of a
parent does: through the physics constraints on the chains. Nothing synchronises a character to a prop.

**24 physics constraints.** `rig-parts` keys its idle on a `<bone>_ctl` parent of every chain link, which
leaves the link itself free for a constraint; `rig.py` gives one to each link of the twin tails, bangs,
tassel, skirt, sleeve and legs, tapering in strength toward the tip, and one to the chest.

**The soft chest** is the recipe from the parts guide: a bone under `chest`, a circular region of the
`topwear` mesh handed to it in `config.json`, and a spring on its x and y. It moves 4 – 6 units through the
sway and about 20 on the hop.

**Depth by parallax.** Three bones get a keyed twin above them (`leg0_px`, `leg1_px`, `chest_jiggle_px`),
keyed in step with the swing: what is nearer the viewer — knees, feet, the chest's front — travels a little
further than what is behind it, and the torso leans 1.5° against the sway. It is bone motion bending
meshes, not a depth model.

**The loop closes with a lead-in.** Springs make an animation's first frame differ from its last. The
animation is 16 s: the loop's last four seconds, then the loop. By the loop's first frame the springs are
where they will be at its last, and step 5 keeps only the loop.

## What review caught

The author of a rig cannot see it; an agent reads a handful of frames. Every row below was green at the
gate and wrong in the picture, and was found by a person watching the loop.

| Seen | Cause | Fix here | Where it went |
| --- | --- | --- | --- |
| "The eyes do not match the tilt of the face" | The head is painted 23.7° off vertical and the five face bones were written with the page's axes, so a blink's `scaley` squashed the eyes along the page | `rig.py` rotates `eye_*`, `brow_*` and `mouth` to the line through the eyes and turns their attachments back | [parts#239](https://github.com/rig-c/parts/issues/239) (build it that way), [core#1351](https://github.com/rig-c/core/issues/1351) (gate it) |
| "The chest does not move — a paper doll" | The torso was one mesh on two rigid bones | the soft region and its spring; the parallax | — |
| "The hand is too small: an open hand goes by the size of the face" | The palm was sized from the painted, half-hidden hand | wrist to fingertip 58 → 78 units, about half the face's width | — |
| "Her wrist breaks when she waves" | Two things: the palm's forearm pointed the way the painted wrist did, 14° off the sleeve; and the whole palm turned ±15° at the cuff, against the arm | the forearm follows the sleeve's axis; the palm is two pieces, and only the hand turns, at the wrist, ±7°, a quarter beat behind the arm | — |
| "Hair lying over the seat will be hard to swing" | In the first painting the twin tails draped over the swing | a new painting, hair hanging behind the seat line (`generation.json`) | — |
| The swing's end joints read as eyes | Glossy balls with a dark centre | flat open rings | — |

Four more were found by the tools refusing, or by the author reading their reports, and became issues:
long hair behind the back dropped from the assembly plan
([parts#233](https://github.com/rig-c/parts/issues/233)), a cut piece given its base's chains a second time
([parts#230](https://github.com/rig-c/parts/issues/230)), the check's standing-figure bars
([parts#231](https://github.com/rig-c/parts/issues/231)), and a `tip` on a single bone accepted and ignored
(in #239). The first three shipped in `@rig-c/parts` 1.6.0, which is why step 1 is one green command here.

## What is the rig and what is staging

`rig-c` makes an object that can be directed; composing a take is the consumer's. This repository is a
consumer. So:

- **The rig**: every motion in the table above, compiled by `rigc build` and posed by `rigc render`.
- **Staging**: the sky, the lights, the shadow, the captions, and the choice of when she does what.
- **The reveal** is in between and is honest about it: the lines are drawn by `compose.py`, at the
  positions `geometry.json` gives for that frame. The caption's counts — bones in the skeleton, meshes
  drawn — are read from the same file.

The frames are posed by `rigc render`, not played by [`@rig-c/play`](https://github.com/rig-c/play): the
trailer is a video. The compiled model in `out/build/` is what `@rig-c/play` loads.

## Files

```
build.sh                 the five steps
inputs/painting.png      the generated painting, 1664×2432; generation.json and pose_seated.json record it
inputs/layers/           the two See-through runs (full body, head crop) and what each was fed
inputs/config.json       the rig-parts config: plan, bones, meshes, regions, motion
inputs/keypoints.json    the joints, read off the painting
inputs/requirements.json what the scene declares to the check
inputs/sky.png           the painted sky; sky.json records it
inputs/palm.png          the generated open hand; palm.json records it
film/palm.py             the palm, cut out, recoloured and split at the wrist
film/rig.py              the film rig
film/compose.py          the film layer
trailer.webp             what build.sh makes
```

## Licence

MIT, covering the scripts, the generated images and the trailer — see `LICENSE`. `NOTICE.md` names the
checkpoint the images were generated with, See-through, and the tools the build runs.
