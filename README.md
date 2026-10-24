# The rig-c trailer, reproducible

<p align="center">
  <img src="trailer.webp" alt="A character on a swing under a night sky breathes, tilts her head, smiles, kicks her legs, hops and waves, her twin tails following; for one beat her meshes and bones are drawn over her" width="100%" />
</p>

The loop on the [rig-c organisation's front page](https://github.com/rig-c), with everything that made it:
one generated painting, its two See-through layer sets, the config an agent wrote for
[`@rig-c/parts`](https://github.com/rig-c/parts), and three short scripts. One command rebuilds the loop
from them with the published packages.

It is here as a worked case, not as a template: a character that is not standing, a prop that is part of
her skeleton, a performance longer than an idle, and a record of what review caught on the way.

To change the film rather than rebuild it, read [WORKING.md](WORKING.md): where each kind of change goes,
how to check one without being able to watch it, and the rules this film was corrected into.

## Reproduce

```bash
git clone https://github.com/rig-c/trailer && cd trailer
pip install -r requirements.txt      # numpy, pillow
./build.sh                           # installs @rig-c/parts 1.61.0 and rig-c 2.69.0, then runs the five steps
```

Needs [bun](https://bun.sh) ≥ 1.2 (the tools run on it), npm, and python3. No GPU and no ComfyUI: the
painting, the sky, the palm and the See-through layers are inputs, already in `inputs/`.
The whole build took 12 min 29 s on an Apple M4 that was doing other work (measured once, this cut).

The result is `out/scene/trailer.webp` (960×540, 240 frames, 12 s at 20 fps), with the 1920×1080 frames
beside it and a contact sheet. Run from a clean directory with the published packages, on the machine the trailer was made on, it reproduced the published loop byte for byte — all 240 frames and the WebP (python 3.13.1, pillow 12.2.0, numpy 2.4.4, bun 1.4.2). Another machine's encoders and caption font can move bytes without moving the picture.

| | |
| --- | --- |
| **An input, not rebuilt** | `inputs/painting.png`, `inputs/layers/` (See-through), `inputs/sky.png`, `inputs/palm.png` — generated on a ComfyUI box; `generation.json`, `sky.json` and `palm.json` record how, and `tools/trim_loops.py` the one edit made to the painting and its back-hair layer afterwards |
| **Written by the author (an AI agent)** | `inputs/config.json`, `keypoints.json`, `requirements.json`, and `film/` |
| **Rebuilt by `build.sh`** | the parts, the rig, the compiled skeleton, every rendered frame, the composite |

## The five steps

**1. Parts, rig, check** — `rig-parts build`. The painting and the two See-through runs are assembled into
23 rig-ready parts, meshed and weighted to the bones `config.json` declares (1,420 triangles in ten meshes; a
lattice at each part's own spacing had 3,081 — see *The meshes*), given a four-second idle, and
checked. The check passes twelve bars of twelve, two of them through a declaration:

```
BREATH_VISIBLE: PASS — declared_not_planted shoes; …
TIP_OVER_ROOT: PASS — declared_rises handwear_r; …
STRESS_OFF_CHAIN: PASS — tags handwear; turns 90 | -90 | 180; parts_read 2; reading 1; …
check: PASS; 12 of 12 bar(s) measured, 0 skipped
```

`rig-parts check` assumes a figure that stands. `inputs/requirements.json` says what the scene knows and the
tool cannot: she sits, so her shoes are not planted, and her right forearm rises from the elbow. A relaxed
bar prints the declaration first, so it never reads as a passed one.

**2. The film rig** — `film/palm.py`, `film/rig.py`. Plain rig-spec and motion-spec data added to what
step 1 wrote: the swing, a physics constraint on every chain, the breath, the palm, and one animation.
The sections below say what each is for.

**3. Compile and gate** — `rigc build`, twice. Nothing is written unless the gate is green:

```
52 assertions: 21 measured (21 passed, 0 failed), 17 skipped, 14 not in profile "spine"
bones=83 slots=29 animations=2 regionAttachments=18 meshAttachments=11 physicsConstraints=24
```

The second build is the same rig with every slot tinted black; step 5 needs it.

**4. Pose** — `rigc render --geometry`. 321 frames of the rig, and `geometry.json`: every bone's world
transform and every mesh vertex after skinning, per frame.

**5. The film layer** — `film/compose.py`. Sky, lights, the mesh-and-bone reveal, captions.

## What the rig is

| Beat | Seconds | What moves it |
| --- | --- | --- |
| Sway | whole loop | `swing` rotates ±2.5° about a pivot far above the frame; `seat` and the whole character hang under it |
| Breath | whole loop, 3 s | the chest rises 14 units and widens; the shoulders follow 0.12 s late and the head 0.2 s late; hair and the soft chest take it through their springs |
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

**The breath** replaces the idle's own (2.6 units on the swing's 4 s, which read as part of the swing).
Three seconds a breath, four to the loop, so it never falls in step with the sway. The shoulders and the
head each ride a twin bone above the one `rig-parts` keys, and follow by lagging rather than by a motion
of their own.

**The meshes.** Six parts are on `auto` — a traced outline reduced under declared bounds — and four on
`contour`, a traced outline with a coarse grid inside: the skirt and the waving sleeve as
`rig-parts mesh-draft` drafted them, the hairpin at the same settings, and the long hair. Each part is on
the mode that came out smaller when both were built. Where the film bends a chain a few degrees `auto` is
far the smaller (the back hair, 28 triangles against a lattice's 120). Where it bends one 24° or 33°, a
reduction held to those bends kept two to three times what the draft needs — the skirt 276 against 132,
the sleeve 148 against 49 — and the film is the same to the eye. Each `auto` chain's bend in this film is
declared in `config.json` (`auto.stimulus`, measured with `tools/bends.py`), because a mesh is otherwise
reduced against the idle, and the idle bends a chain one or two degrees. No triangle folds over anywhere
in the film (`rigc render --folds` names no mesh): the long hair and the hairpin, which folded three and
two in the last cut, declare their weight cut (`influences`). The per-part counts and the declared bends
are tabled in WORKING.md. The reveal draws each mesh's outline over its inner edges, so the silhouettes
read.

**The loop closes with a lead-in.** Springs make an animation's first frame differ from its last. The
animation is 16 s: the loop's last four seconds, then the loop. By the loop's first frame the springs are
where they will be at its last, and step 5 keeps only the loop. `tools/loop.py` reads it: 0.000 units
between loop time 0 and one loop later, on every bone and vertex.

That was not true of this film until `rig-c` 2.45.2. Through seven cuts the springs were up to 26 px apart
at the seam and jumped together on three frames inside the loop, and the page said the loop closed. See
the last row of the table below.

## What review caught

The author of a rig cannot see it; an agent reads a handful of frames. Every row below was green at the
gate and wrong in the picture, and was found by a person watching the loop.

| Seen | Cause | Fix here | Where it went |
| --- | --- | --- | --- |
| "The eyes do not match the tilt of the face" | The head is painted 23.7° off vertical and the five face bones were written with the page's axes, so a blink's `scaley` squashed the eyes along the page | first by hand in `rig.py`; since `@rig-c/parts` 1.7.0 the rig stage stands the five bones on the line through the eyes and declares it, `rig-c` 2.40.0's gate holds the build to it (`A51`), and `rig.py` only checks that it was done | [parts#239](https://github.com/rig-c/parts/issues/239), [core#1351](https://github.com/rig-c/core/issues/1351) — both shipped |
| "The chest does not move — a paper doll" | The torso was one mesh on two rigid bones | the soft region and its spring; the parallax | — |
| "The hand is too small: an open hand goes by the size of the face" | The palm was sized from the painted, half-hidden hand | wrist to fingertip 58 → 78 units, about half the face's width | — |
| "Her wrist breaks when she waves" | Two things: the palm's forearm pointed the way the painted wrist did, 14° off the sleeve; and the whole palm turned ±15° at the cuff, against the arm | the forearm follows the sleeve's axis; the palm is two pieces, and only the hand turns, at the wrist, ±7°, a quarter beat behind the arm | — |
| "Hair lying over the seat will be hard to swing" | In the first painting the twin tails draped over the swing | a new painting, hair hanging behind the seat line (`generation.json`) | — |
| The swing's end joints read as eyes | Glossy balls with a dark centre | flat open rings | — |
| "The curled loops beside her hips read as hair lying on the ground; she is in the air, so they float" | The painting drew a ring of hair on the outside of each twin tail at hip height | both rings erased from the painting and the See-through layer (`tools/trim_loops.py`: the tail's edge measured on the rows above and below each ring, everything outside it removed) | — |
| "I cannot feel her breathing" | The idle's breath was 2.6 units, and at 6.5 (2.5 % of the torso, right for a standing figure in close-up) it was still lost: she is small in the frame and swinging | 14 units, its own 3 s period, shoulders and head following late | the drafted breath now scales with the torso ([parts#252](https://github.com/rig-c/parts/issues/252), [#270](https://github.com/rig-c/parts/issues/270)) |
| The loop did not close on its springs, and springs jumped on three frames | Not the film: the renderer advanced physics in steps of 1/60 s under frames of 1/20 s, and three such steps are not exactly a twentieth in floating point, so what a spring showed flipped between two states (the official runtime does the same on the same calls) | nothing here; rebuilt on the fixed renderer | `rigc render` got a physics clock of its own ([core#1380](https://github.com/rig-c/core/issues/1380), rig-c 2.45.2). Found by an agent handed this repository and nothing else, checking a claim this page made |
| "The meshes have no outline" | The reveal drew every edge alike, and the largest mesh was still a lattice whose blocks covered the rest | the long hair on a traced outline; outlines drawn over inner edges | — |

Four more were found by the tools refusing, or by the author reading their reports, and became issues:
long hair behind the back dropped from the assembly plan
([parts#233](https://github.com/rig-c/parts/issues/233)), a cut piece given its base's chains a second time
([parts#230](https://github.com/rig-c/parts/issues/230)), the check's standing-figure bars
([parts#231](https://github.com/rig-c/parts/issues/231)), and a `tip` on a single bone accepted and ignored
(in #239). All of them have shipped; the first three in `@rig-c/parts` 1.6.0, which is why step 1 is one green command here.

One was found by the author comparing two builds frame by frame: with every mesh reduced on the idle, the
build and every check were green and the skirt's hem kinked in the film. The film bends its chains ten to
twenty times further than the idle does. That became the rule in WORKING.md, the declared bends in the
config, and two issues — what a mesh should be reduced against ([parts#265](https://github.com/rig-c/parts/issues/265))
and a weight rule that folds triangles under a large bend ([parts#284](https://github.com/rig-c/parts/issues/284)).
Both have shipped, and this cut uses them: the figure's own spacing and `rig-parts mesh-draft` for the
first, `meshes.<part>.influences` for the second. The hairpin's tassel swings 95° from rest, and at that
bend its mesh folded before anything was reduced — the tool now says so in one sentence
([parts#280](https://github.com/rig-c/parts/issues/280)) rather than leaving it to be found, and with the
weight cut declared it no longer folds.

Rebuilding this repository on each new release is itself a check. Moving it to 1.7.0 found one more: a face bone that takes its own `tip` from the config gets no declared axis, and nothing says so ([parts#258](https://github.com/rig-c/parts/issues/258)) — this config had done exactly that as the 1.6.0 workaround. Moving it to 1.10.0 and 1.11.0 found the count in *The meshes*: the author's own reduction of the three most-bent parts was two to three times heavier than what the new draft command wrote, and nothing had said so because nothing had built both. `rig-c` 2.46.0's fold reading named triangles nobody had seen at two curl tips and on the hairpin's outline; that it named them without saying where they were became [core#1386](https://github.com/rig-c/core/issues/1386), and 2.47.0 prints the box and frames a picture to it. Moving it to 1.61.0 caught a chest segment left in `meshes.handwear_l.segments`: `CHECK_STRESS_OFF_CHAIN` refused the 0.532 off-chain chest weight that pinned the cuff when the left sleeve turned (ratio 27.9 at 180° against 1.0 rigid; dropping the chest segment leaves `handwear_l` on `sleeve_l` alone at ratio 1).

## Looking at the rig

`rig-c` draws a build for an agent to read — bones, names, a coordinate grid, what the rig declares, any mesh's
weights and every mesh's density against the figure, over the art — with a legend beside the picture that maps pixels back to rig coordinates:

```bash
node_modules/.bin/rigc inspect --candidate out/build --show art,bones,names,declared --dim --zoom bone:head:120 --out head.png
```

Most of the findings in the table above were first seen in pictures like that one, drawn by throwaway scripts before the command existed.

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
film.sh                  steps 2-5 alone, for a change to film/
WORKING.md               how to change the film and check the change
inputs/painting.png      the generated painting, 1664×2432; generation.json and pose_seated.json record it, tools/trim_loops.py the edit after
inputs/layers/           the two See-through runs (full body, head crop) and what each was fed
inputs/config.json       the rig-parts config: plan, bones, meshes, regions, motion
inputs/keypoints.json    the joints, read off the painting
inputs/requirements.json what the scene declares to the check
inputs/sky.png           the painted sky; sky.json records it
inputs/palm.png          the generated open hand; palm.json records it
film/palm.py             the palm, cut out, recoloured and split at the wrist
film/rig.py              the film rig
film/compose.py          the film layer
tools/                   the readings WORKING.md describes: frames.py (two builds, frame by frame),
                         moved.py (which bones a change moved), overlay.py (two frames, red and cyan),
                         loop.py (does the loop close; does anything pop), bends.py (how far the film
                         turns each bone from its setup pose); trim_loops.py is the input edit, not a reading
trailer.webp             what build.sh makes
```

## Licence

MIT, covering the scripts, the generated images and the trailer — see `LICENSE`. `NOTICE.md` names the
checkpoint the images were generated with, See-through, and the tools the build runs.
