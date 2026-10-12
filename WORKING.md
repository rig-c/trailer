# Working on the film

For an agent picking this repository up with no memory of how it got here, and asked to change the film.
[README.md](README.md) says what the film is and how to rebuild it; this page says how to change it and
how to know the change is right. Everything on it was learned by getting it wrong first — the
*what review caught* table in the README is the same history from the other side.

## Three layers, three places

| You are asked to change | Edit | Rebuild with |
| --- | --- | --- |
| **the rig** — bones, chains, meshes, weights, what a part is | `inputs/config.json`, `inputs/requirements.json` | `./build.sh` (about 12 min) |
| **the performance** — what she does and when; physics; the breath | `film/rig.py` | `./film.sh` (about 7 min) |
| **the staging** — sky, lights, captions, the mesh-and-bone reveal | `film/compose.py` | `./film.sh`, or its last line alone — composing 240 frames at 1920×1080 is most of the 7 min |

`./film.sh` reuses `out/parts` and runs steps 2–5. If you changed the config and ran only `./film.sh`,
you are looking at the old rig.

## The timeline

The loop is 12 s. `film/rig.py` writes one animation, `show`, of 16 s: the loop's last 4 s first (so the
springs are already where the loop's end leaves them), then the loop. `film/compose.py` drops the lead-in.
Times below are loop time.

| s | beat | written as |
| --- | --- | --- |
| whole loop | the swing, 4 s a period | `swing` rotate ±2.5° about a pivot far above |
| whole loop | the breath, 3 s — four to the loop, never in step with the swing | `chest_ctl` rise and widen; shoulders 0.12 s late; head 0.2 s late |
| 0.9, 5.2, 8.6 | blinks | the `eyes` group's `scaley` |
| 1.9 – 3.7 | head tilt and a closed-eye smile | `head` rotate; eyes to 0.38, iris and white faded out; brows; mouth |
| 4.2 – 6.55 | the reveal: every mesh and bone drawn over her | `compose.py`, from `geometry.json` |
| 4.3 – 6.4 | kicking legs | `leg0`, `leg1` rotate |
| 6.74 – 7.8 | the hop, and a startled face | `seat` translate; everything on a spring follows late |
| 9.8 – 11.3 | the wave | `sleeve_r0` from the elbow; the palm and a bare forearm swapped in; `hand_r` a quarter beat late |

A gesture is a list of `(time, value)` pairs passed through `lay()`, which lays it over the lead-in for
you. It has to start and end on the same value, or the loop will not close.

## How to look, when you cannot watch

You cannot play the film. These are the readings that replaced watching, cheapest first.

1. **The same frame from two builds.** Keep the previous `out/scene` beside the new one and compare frame
   by frame: the count of pixels differing by more than 40, and their bounding box. It says *where* a
   change landed and whether anything moved that should not have. The reveal (frames 86–129) changes
   whenever the bone count does.
2. **Crop and enlarge.** A defect at film scale is a few pixels. The skirt's kinked hem was invisible in
   the whole frame and plain at 2.4× on a 400 × 200 crop.
3. **With and without, at the extreme.** For anything periodic (the breath), compare the frame at its peak
   with the same frame built without it, overlaid red and cyan. If the fringes are a pixel wide, a viewer
   will not see it either.
4. **`rigc inspect`** for the rig itself — bones and names over the art, one mesh's weights, the density
   of every mesh against the figure (`--show art,density`). See the README's *Looking at the rig*.
5. **`tools/bends.py`** for what the performance asks of the rig: how far each bone bends against its
   parent over the whole film.
6. **A person.** Encode `out/scene/s%04d.jpg` to an mp4 and ask. Two of the last three defects — "the eyes
   do not follow the face", "I cannot feel the breath" — were found this way and by no reading above.
   What a reading can do is tell you *why* afterwards.

## Rules this film was corrected into

Each is here because the film broke it once.

- **The eyes follow the face.** A blink squashes along the eye bone's own axis; on a tilted head that axis
   has to be the line through the eyes. `@rig-c/parts` now builds it and `rig-c` gates it (A51).
- **An open hand is the size of the face.** The palm was drawn at 58 rig px and read as a child's; at 78
   (1.35×) it reads.
- **A limb bends at its joints and nowhere else.** The waving arm follows the sleeve's axis from the elbow
   and the hand turns at the wrist crease, late and a little. Rotating one sprite at the cuff broke the
   wrist.
- **A closed eye is the lash alone.** Squashing the iris and the white with it leaves dashes; fade them out.
- **The breath is sized for the frame, not for the body.** 2.5 % of the torso is right for a standing figure
   in close-up. Here she is small and swinging, and at 6.5 px nobody could see it; it is 14 px. It also
   needs its own period — on the swing's 4 s it reads as the swing.
- **A mesh is reduced against the motion the film performs, not against the idle.** The idle bends a chain
   one or two degrees; the film bends the skirt 24°, the legs 12°, the waving arm 32°. A mesh reduced on
   the idle built green, passed every check, and kinked the skirt's hem. Measure with `tools/bends.py`,
   declare each chain's bend as `auto.stimulus` in the config, and say how far from the unreduced mesh you
   accept at those bends (`auto.motion.maxLocalDeformation`: 3 px here; 1 px is not reachable at such
   bends — one removed vertex on the legs already reads 1.16).
- **What the viewer is shown has to be visible.** The reveal drew every mesh edge alike and the outlines did
   not read; the outline of each mesh is now drawn over its inner edges.

## The meshes, as they stand

`inputs/config.json`, per part: nine on `auto` (a traced outline reduced under declared bounds), `hair_long`
on `contour` (a traced outline with its grid inside, not reduced — its unreduced mesh already folds seven
triangles at a 10° bend, so no reduction of it can pass; that is a weight-rule defect,
[parts#284](https://github.com/rig-c/parts/issues/284), and not something to work around here), and the
soft chest as a declared region of `topwear`. 1,745 triangles where a lattice at each part's own spacing
had 3,081.

If you change the performance so that a chain bends further than its declared `stimulus`, re-measure and
raise it, or the mesh is again one that was never asked about the motion it carries.

## Before you publish

- `./build.sh` from a clean clone with the versions `package.json` pins, twice; the two `trailer.webp`
  agree byte for byte on one machine.
- The README's figures (the gate line, counts, the build time) are the ones this build printed.
- If the published loop changes, `rig-c/.github`'s `profile/trailer.webp` is the same file.

## Open, for whoever makes the next cut

- `hair_long` waits on parts#284; when the weight rule is continuous it should go to `auto` like the rest.
- The soft chest's region is generous (503 triangles in `topwear`); it has not been tightened because the
  first complaint about this film was a chest that did not move.
- The turn control `@rig-c/parts` 1.9.0 drafts (a dial that carries each part by its depth) is not used;
  the parallax here is still three hand-written tracks. The drafted depths push the legs the wrong way on
  a seated figure ([parts#271](https://github.com/rig-c/parts/issues/271)).
