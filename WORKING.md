# Working on the film

For an agent picking this repository up with no memory of how it got here, and asked to change the film.
[README.md](README.md) says what the film is and how to rebuild it; this page says how to change it and
how to know the change is right. Everything on it was learned by getting it wrong first, and the page
itself was corrected by handing it to an agent that had nothing else: what that reader had to work out
alone is now written down, and what it found wrong has been fixed (see *What the cold reader found*).

Units: the rig's own units, which are the painting's pixels. `film/compose.py` draws them at 0.822 px per
unit in the 1920×1080 frames and 0.411 in the 960×540 WebP. "Film px" below means the 1080p frames.

## Three layers, three places

| You are asked to change | Edit | Rebuild with |
| --- | --- | --- |
| **the rig** — bones, chains, meshes, weights, what a part is | `inputs/config.json`, `inputs/requirements.json` | `./build.sh` (11–12 min) |
| **the performance** — what she does and when; physics; the breath | `film/rig.py` | `./film.sh` (5–7 min) |
| **the staging** — sky, lights, captions, the mesh-and-bone reveal | `film/compose.py` | `./film.sh` |

- `./film.sh` reuses `out/parts` and runs steps 2–5. If you changed the config and ran only `./film.sh`,
  you are looking at the old rig.
- `./film.sh` moves the last build's `out/scene`, `out/render` and `out/film` to `out/prev` before it
  builds, because every reading below compares two builds. One generation is kept; copy `out/prev`
  elsewhere if you need a baseline for longer.
- **The posed frames are ready about 16 seconds in** (`out/render/show@20fps/geometry.json`); composing the
  240 frames is the rest. For a change of timing or motion, stop after step 4 and read the geometry
  (`tools/moved.py`, `tools/loop.py`, `tools/bends.py`) before paying for the composite.
- A green `./film.sh` ends with the gate line twice (`52 assertions: 21 measured (21 passed, 0 failed) …`)
  and `240 frames -> out/scene/trailer.webp`. `rig-parts check` is not rerun by it and measures the
  **idle**: its `BREATH_VISIBLE` is about the idle's breath, which the film replaces. It says nothing about
  a change under `film/`.

## The timeline

The loop is 12 s. `film/rig.py` writes one animation, `show`, of 16 s: the loop's last 4 s first (so the
springs have settled into the motion), then the loop. `film/compose.py` drops the lead-in: animation frame
80 is loop time 0. Times here are loop time and are each beat's outer extent, as in the README's table;
the keys are in `rig.py` and are the authority.

| s | beat | written as |
| --- | --- | --- |
| whole loop | the swing, 4 s a period | `swing` rotate ±2.5° about a pivot far above |
| whole loop | the breath, 3 s | see *The breath* |
| 0.9, 5.2, 8.6 | blinks | the `eyes` group's `scaley` |
| 1.5 – 4.1 | head tilt (eyes closed in a smile 1.9 – 3.7) | `head` rotate; eyes to 0.38, iris and white faded out; brows; mouth |
| 4.1 – 6.6 | the reveal: every mesh and bone drawn over her (caption 4.2 – 6.55) | `compose.py`, from `geometry.json` |
| 4.3 – 6.4 | kicking legs | `leg0`, `leg1` rotate |
| 6.7 – 7.8 | the hop, and a startled face | `seat` translate 6.74 – 7.52; everything on a spring follows late |
| 9.6 – 11.7 | the wave (palm shown 9.8 – 11.4) | `sleeve_r0` from the elbow; the palm and a bare forearm swapped in; `hand_r` a quarter beat late |

A gesture is a list of `(time, value)` pairs passed through `lay()`, which lays it over the lead-in for
you. It has to start and end on the same value.

## The breath

Not a gesture: three constants in `film/rig.py` (`BREATH, RISE, IN`), a function `breath(t)` that is 0 at
the bottom and 1 at the top, and `sampled()`, which turns a function of loop time into keys.

- `BREATH`, the period. **A whole number of breaths has to fit the 12 s loop** (an `assert` holds it), and
  4 s is the swing's own period, on which a breath reads as part of the swing. So the choices are 3 s, 6 s
  and 12 s, and nothing between — "a little slower" does not exist here; the next slower breath is half
  the speed. It is 3.
- `RISE`, how far the chest rises, 14 units (11.5 film px). See the rule below before lowering it.
- `IN`, the share of a breath spent breathing in, 0.42: in is quicker than out.
- The followers are lags in **seconds**: the shoulders 0.12 s behind the chest, the head 0.2 s. The head's
  track is the difference between the breath now and 0.2 s ago, so a slower breath moves the head less
  (at 6 s its excursion roughly halves). If you change the period, decide what the lags should do.
- `inputs/config.json` also has a breath, under `motion` (`chest`, `translatey`, period 4). That is the
  idle's; `rig.py` drops it (`replaced`). Changing it changes nothing in the film and costs a full build.

## How to look, when you cannot watch

You cannot play the film. These readings replaced watching; each is a script in `tools/`, cheapest first.

1. **The same frame from two builds** — `python3 tools/frames.py out/prev/scene out/scene`. Pixels
   differing by more than 40 per frame, and their box. Says whether a change landed and when. It cannot
   say *which part* moved for anything under the chest (61 of the 83 bones): the box is the whole figure.
2. **Which bones moved** — `python3 tools/moved.py out/prev/render/show@20fps/geometry.json
   out/render/show@20fps/geometry.json chest_ctl`. Per bone, the largest difference between the builds,
   split by an ancestor. After a change to the breath, everything not under `chest_ctl` reads zero.
3. **Crop and enlarge.** A defect at film scale is a few pixels. The skirt's kinked hem was invisible in
   the whole frame and plain at 2.4× on a 400 × 200 crop.
4. **With and without, at the extreme** — `python3 tools/overlay.py <with> <without> out.png x0 y0 x1 y1
   2.4`. For anything periodic: the frame at its peak against the same frame built without it (for the
   breath: a copy of `rig.py` whose `breath()` returns 0, built into another directory; the peaks are at
   loop time `IN × BREATH` plus whole periods — frames 25–26, 85–86, 145–146, 205–206 today). Red and cyan
   fringes; if they are a pixel wide a viewer will not see it either. **It measures how far, not how
   fast**: the same breath at half the speed gives the same number.
5. **Does any triangle fold** — `rigc render … --folds` (the command is under *The meshes, as they
   stand*). One line per mesh that folds, none on this cut.
6. **Does the loop close, does anything pop** — `python3 tools/loop.py out/render/show@20fps/geometry.json`.
   Loop time 0 against one loop later, and frames where bones turn several times further than on the
   frames around them. On this cut it prints 0.000 and only the hop's own frames; anything else is yours.
7. **`rigc inspect`** for the rig itself — bones and names over the art, one mesh's weights, every mesh's
   density against the figure (`--show art,density`). See the README's *Looking at the rig*.
8. **`tools/bends.py`** for what the performance asks of the rig: how far each bone turns from its setup
   pose over the loop.
9. **A person.** `ffmpeg -stream_loop 1 -framerate 20 -i out/scene/s%04d.jpg -c:v libx264 -pix_fmt yuv420p
   -crf 18 out.mp4` — the loop twice, so the seam is seen once — and ask. Two of the last three defects,
   "the eyes do not follow the face" and "I cannot feel the breath", were found this way and by no
   reading above. There is no reading here for whether a motion can be *felt*; a slow, small motion on a
   figure that is swinging is exactly the case no script answers.

"Not in step with the swing" has a reading too, if you need it: the chest's height in the seat's own
frame, from `geometry.json`, has no component at the swing's 4 s period when the breath's period is 3 or 6
(and nearly all of it there at 4).

## Rules this film was corrected into

Each is here because the film broke it once.

- **The eyes follow the face.** A blink squashes along the eye bone's own axis; on a tilted head that axis
  has to be the line through the eyes. `@rig-c/parts` now builds it and `rig-c` gates it (A51).
- **An open hand is the size of the face.** The palm was drawn at 58 units and read as a child's; at 78
  (1.35×) it reads.
- **A limb bends at its joints and nowhere else.** The waving arm follows the sleeve's axis from the elbow
  and the hand turns at the wrist crease, late and a little. Rotating one sprite at the cuff broke the
  wrist.
- **A closed eye is the lash alone.** Squashing the iris and the white with it leaves dashes; fade them out.
- **The breath is sized for the frame, not for the body.** 2.5 % of the torso is right for a standing figure
  in close-up. Here she is small and swinging, and at 6.5 units nobody could see it; it is 14. It also
  needs its own period — on the swing's 4 s it reads as the swing.
- **A mesh is reduced against the motion the film performs, not against the idle.** The idle turns a chain
  one or two degrees; the film turns the skirt 24°, the legs 10°, the waving arm 32°. A mesh reduced on
  the idle built green, passed every check, and kinked the skirt's hem. Measure with `tools/bends.py`,
  declare each chain's largest turn from its setup pose as `auto.stimulus` in the config, and say how far
  from the unreduced mesh you accept at those bends (`auto.motion.maxLocalDeformation`: 3 here; 1 is not
  reachable at such bends — one removed vertex on the legs already reads 1.16).
- **Build a part both ways before keeping its mesh.** A reduction held to a large bend is not the small
  mesh it sounds like. On the skirt (24°) and the waving sleeve (33°) the `auto` reduction kept 276 and 148
  triangles; `rig-parts mesh-draft`, which traces the outline around a coarse grid and keeps it only where
  it holds against that grid, wrote 132 and 49, and the two films could not be told apart at the largest
  bend, enlarged. On parts that bend a few degrees `auto` wins by as much. Nothing reports this; you find
  it by building the part on a lattice at the figure's spacing (`"grid": 30` here), running `mesh-draft`,
  and comparing the `[rig] mesh` lines.
- **What the viewer is shown has to be visible.** The reveal drew every mesh edge alike and the outlines did
  not read; the outline of each mesh is now drawn over its inner edges.

## The meshes, as they stand

`inputs/config.json`, per part. 1,420 triangles where a lattice at each part's own spacing had 3,081 (the lattice figures were measured before the hip loops were erased from the long hair).

| part | mode | triangles | built the other way |
| --- | --- | --- | --- |
| `topwear` | `auto`, with the soft chest as a declared region | 503 | — |
| `hair_long` | `contour`, `influences` with no cap and a continuous floor | 434 | lattice 578 |
| `bottomwear` | `contour`, as `mesh-draft` drafted it | 132 | `auto` at the film's bends 276; lattice 140 |
| `hair_front` | `auto` | 112 | lattice 114 |
| `legwear` | `auto` | 77 | lattice 176 |
| `handwear_r` | `contour`, as `mesh-draft` drafted it | 49 | `auto` at the film's bends 148; lattice 52 |
| `hairpin` | `contour` at the draft's settings, `influences` with a continuous floor | 47 | `contour` at its own spacing 120; lattice 46 |
| `handwear_l` | `auto` | 31 | lattice 72 |
| `hair_back` | `auto` | 28 | lattice 120 |
| `neck` | `auto` | 7 | lattice 12 |

"Lattice" is `"grid": 30`, the spacing `rig-parts propose` drafts for this figure. `mesh-draft` left the
hairpin on its lattice — its candidate sat 1.055 rig px from the lattice over the idle, against a line of
1 — and the candidate's settings were then written by hand, which is an author's call and is why that
entry carries no drafted note.

**Folds.** `node_modules/.bin/rigc render --candidate out/build --animation show --fps 20 --max 900 --folds --out <dir>`
names every mesh with a triangle turned over against the setup pose, and the frames. On this cut it names
none. On the last one it named `hair_long` (three slivers at a curl's tip, 88 frames) and `hairpin` (91
frames); a continuous floor cleared the hairpin and two of the hair's three, and lifting the cap on the
long hair cleared the last. Both are `meshes.<part>.influences` in the config. Each line gives the folded
triangles' world box and their share of the mesh's area, and
`rigc inspect --candidate out/build --animation show --fps 20 --at <s> --show art,mesh,folds --zoom folds --max 900`
frames a picture to them; a fold that still draws as a hairline wants a larger `--max`. Size is the triage:
the long hair's three were 0.07 % of its mesh, at a nearly transparent tip.

The declared bends against what `tools/bends.py` reads on this cut:

| chain | declared `stimulus` | largest turn from setup, over the loop |
| --- | --- | --- |
| `skirt_r` / `skirt_c` / `skirt_l` (on `contour` since this cut: nothing is reduced, so nothing is declared) | — | 23.8 / 11.8 / 22.4 |
| `leg` | 12 | 10.6 |
| `sleeve_r` (the wave; on `contour` since this cut) | — | 32.5 |
| `sleeve_l` | 4 | 2.0 |
| `bang_r` / `bang_c` / `bang_l` | 11 / 10 / 11 | 11.0 / 10.0 / 10.4 |
| `hairpin_tassel`, `tail_r` / `tail_l` (on `contour`: nothing is reduced, so nothing is declared) | — | 95.0, 8.8 / 11.2 |

Every declared value covers what the film does. If you change the performance so that a chain turns
further than its declared `stimulus`, re-measure and raise it, or the mesh is again one that was never
asked about the motion it carries. (A bone's motion does not depend on its mesh, so one measurement after
the change is enough — but it does depend on the renderer: the fringe read 9.7 before `rig-c` 2.45.2 and
11.0 after.)

## What the cold reader found

Three defects, each of which this page or the README had denied or not known. All three are fixed in this
cut; they stay here because how they were found is the method.

- **The loop did not close on its springs** — 26 film px at the seam, and springs jumping together on
  three frames — while the README said it closed. The reader measured a claim instead of repeating it.
  The cause was the renderer's ([core#1380](https://github.com/rig-c/core/issues/1380)); `tools/loop.py`
  is that measurement, kept.
- **The reveal drew three helper bones**, the breath's twins, because `compose.py` listed two helper
  suffixes and a third had been added in `rig.py`.
- **The declared bends did not match the tool that measures them**: `bends.py` read the lead-in frames and
  printed a half-range, where a stimulus is a turn from the setup pose. Three chains were under-declared.

## Before you publish

- `./build.sh` from a clean clone with the versions `package.json` pins, twice; the two `trailer.webp`
  agree byte for byte on one machine.
- Copy `out/scene/trailer.webp` over the repository's `trailer.webp`.
- The README's figures (the gate line, counts, the build time) are the ones this build printed, and any
  number you changed is changed everywhere it is written: grep the old value in `README.md`, this page and
  the comments in `film/`.
- If the published loop changes, `rig-c/.github`'s `profile/trailer.webp` is the same file.

## Open, for whoever makes the next cut

- `hair_long` and `hairpin` are on `contour` with their weight cut declared. Whether `auto` now accepts
  them (it refused both while their unreduced meshes folded) has not been tried on this cut; by the table
  above it is worth trying on `hair_long` and not on `hairpin`.
- The soft chest's region is generous (503 triangles in `topwear`); it has not been tightened because the
  first complaint about this film was a chest that did not move.
- The turn control `@rig-c/parts` 1.9.0 drafts (a dial that carries each part by its depth) is not used;
  the parallax here is still three hand-written tracks. The drafted depths push the legs the wrong way on
  a seated figure ([parts#271](https://github.com/rig-c/parts/issues/271)).
