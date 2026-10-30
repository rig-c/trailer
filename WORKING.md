# Working on trailer v2

Current distal tail inertia is 0.5 instead of 0.1; the current trailer is `a441e98601de6910d549facb0391a6c5b597fe53a69c0854239c1c365ae81ee4` from the 243.808 s build excluding installation, while `BUILD-FINAL.json`, `631e7496…` and the 237.841 s measurement below describe the #8 baseline; lower-curl frame-step maxima at 3.55–3.75 s are L 3.56 → 1.69 / R 5.17 → 1.52 px and at 8.10–8.25 s L 2.45 → 1.08 / R 3.80 → 2.11 px, with outside-window maxima L 2.34 → 2.91 / R 2.66 → 3.34 px.
Production derives the original FULL run into `$TRAILER_OUT/derived-full` and keeps the original HEAD run. The rejected 607 HEAD experiment is not used.
Source/rig changes live in `inputs/config.json`; performance in `film/rig.py`; staging in
`film/compose.py`. Build with `./build.sh`; use `./film.sh` only when the already-built parts are valid.
Default output is `out/v2-final`. The owner-approved selected delivery is copied to root `trailer.webp`; build.sh itself keeps its output separate.

## Measured delivery and build

Final yaw is ±12°. Delivery is 960×540, 240 frames at 20 fps and 12,000 ms. The selected film has
107 compiled bones, 29 slots and 26 physics constraints, including eight generated stop helper bones.
`BUILD-FINAL.json` records the new source build, compiler/profile counts, source guard, media identity
and known RED dispositions. The build is timed once after a locked install, with no carried output or
node_modules; its base archive and exact source overlay are independently hashed. The successful build took **237.841 s**, excluding installation. Delivery is 6,405,916 bytes and is
byte-identical to the selected reviewed take (SHA256 631e74967074dd59d405cd137a4d4783820559b852c1485e0a13cd365139ad24).
Both normal/black spine gates read 26 PASS / 0 FAIL / 12 SKIP / 14 outside profile (52 total).
Parts check reads 12/12 counted bars PASS; separate seam/settles SKIPs and 0 temporal declarations remain.
All five 20 fps animation sets have 0 folded meshes: idle/turn/tilt/body_turn 0/11, show 0/12.
Bone and vertex closure both print 0.000 units. The final show geometry and producer JSON exactly match
the selected take; all 495 nonhair poses across five animations plus their setup poses remain exact.

The 24-frame labelled loop overview is a thumbnail sheet; native decoded 960×540 frames and unscaled
head crops are the delivery-scale evidence. Encoding/font identity is recorded. No comparative
benchmark or cross-platform byte-equality claim is implied.

## Beats and depth

The 16 s show includes a 4 s lead-in, then a 12 s loop. Sway 4 s; breath 3 s/14 rig units; tilt/smile 1.5–3.75;
gaze 3.60–5.40; depth look 3.85–5.90 at 12°; reveal 3.95–5.65; kick 6.0–7.7; hop 8.1–8.88;
wave 9.55–11.68. All three gaze onsets lead the corresponding head change 0.25 s. The actual motion file and
rendered channels are the authority, not this table alone.

The rig stage is 832×1216 from a 1664×2432 painting at assemble scale 0.5. Compose draws 0.8224 px per
rig unit in 1920×1080 working frames and 0.4112 in 960×540 delivery. Rig render native pixels have their
own recorded viewport scale; they are not 1 rig unit per pixel.

Full and HEAD generation: canvas 1024, depth inference 512, seed 42, steps 30, offload true. No painting
regeneration. Every retained head/neck consumer is scalar-sheet bound. Face is surface; independently
registered unit depths: front hair 65, back hair −14, long hair −22, headwear −8, ears 20/12, neck 52.1765.
The actual neck proposal wrote config, rather than treating a collar fragment as the neck.

The chosen keep/yield flags retain original amodal material beneath soft covers and conditionally yield
drift-refused front pixels to matching opaque holders. Rest error is not a visual gate: the earlier
all-flag comparison changed mean absolute error 2.718→2.897 with uncovered error 4383 unchanged. Removing
only hair keep measured 2.846; removing its yield too measured 2.932. These numbers do not establish
motion cleanliness or justify a cut.

## Restoring the accepted hip-hair cleanup

The initial v2 FULL run restored two horizontal oval loops at hip height: its `st_input_full.png`
still contains them, although the published v1 back-hair layer and `painting.png` were already trimmed.
The build now reuses the accepted v1 `tools/trim_loops.py` keep mask, unchanged in source coordinates,
through `tools/derive_trimmed_full.py`. It derives into `$TRAILER_OUT/derived-full` and passes that exact
run to `--full`; it never regenerates a checked source in `inputs/`.

Only back-hair alpha and the corresponding opaque grayscale depth samples change. The 1024-square
registration and every layer box stay fixed. Depth stays opaque L; the same trim mask restores the
erased-loop field toward its background level 255. Raw art/depth and the already-trimmed painting stay
byte-identical. The operation changes 3,460 alpha pixels and 3,179 scalar samples; RGB everywhere,
pixels outside the affected mask, lower tail ends and the other 56 run PNGs are unchanged. Actual
assembly changes only `hair_long.png` and its depth sheet: the other 44 images are pixel-identical.
The full motion JSON is identical to the pre-fix performance, including ±12° look, gaze lead and reveal.

The first correction build wrote derived PNGs under `inputs/`: its script took 237.859s but the unchanged
source guard/pool exited 1, so it is rejected as a clean build. Pixel equality did not waive that refusal.
The earlier corrected output-only build took 233.453s, with build, guard and pool all exiting 0 and no source
hash changes. `BUILD-V2.json` preserves the earlier uncorrected-v2 measurement; `BUILD-RING-FIX.json`
preserves that correction measurement; `BUILD-LAYERING.json` preserves the draw-order measurement; `BUILD-PHYSICS.json` preserves the earlier hanging-only revision; `BUILD-FINAL.json` binds the selected moving-seat-stop delivery.

All 240 decoded delivery hip crops were read at 1:1, in five 1880×2016 lossless pages with frame/time
labels; ten 1880×1008 half-pages support smaller viewers. All crop/tile pixel hashes match the decoded
WebP. No restored outboard hip oval was observed, including swing/hop extremes. The fully removed
3,347-pixel source mask has zero remaining positive alpha. White pixel counts include normal clothing
and hair and are diagnostics, not an automatic oval classifier. Native setup/min/max/diff and 4×NN
boundary views show no new tail severing, ghost or gap at the removed-loop joins. This is separate from
the retained head-edge highlight discussed below and from owner publication approval.

## Long hair in front of the swing bar (prior ordering revision)

The film inserts `seat_bar` immediately before `hair_long` in the slots array. Back-to-front order is
ropes, bar, long hair, then the body/skirt/legs; rope order stays unchanged. The pinned published-v1
writer instead inserted the bar after long hair, so this is an explicit new ordering, not a restoration
of v1 ordering. No source pixels, mesh shape, bone, weight, spring or motion changed for that ordering-only revision. The following physics revision preserves its exact draw order.

The old-order negative control is labelled “bar IN FRONT OF hair”; the new candidate “hair IN FRONT OF
bar”. Native full-frame delivery comparisons use swing-key extrema f020 (1.00 s, +2.5°) and f060
(3.00 s, −2.5°). Both show hair covering the bar while skirt/legs cover hair. All 240 decoded hip crops
were read again with no restored oval or new hip gap observed. All 495 rendered poses across five
animations have identical bone matrices and attachment vertices to the ring-corrected old order;
image arrays and motion/show JSON bytes match too. Native setup/min/max/diff witnesses and 4×NN
hair/bar boundaries were read with no new tear or ghost at those boundaries. Native render grid
900×783 uses 0.5288951917064656 pixels per world unit; native pixels are not one rig unit each.

## Hair rim: source evidence, failed ladder, delivery disposition

At the original native 900×783 max-yaw frame 166, bob ROI [535,226,548,262] has 468 pixels; ahoge
ROI [375,140,488,187] has 5311. Existing-frame UV/alpha reconstruction matches every pixel in both ROIs
with RGB error 0; no pixels were excluded. Bob visible contributors: 201 long-hair, 80 back-hair pixels.
Both corresponding registered original source crops contain the light/double contour. Official transparent
RGBA over dark ground retains it; recomposition against the opaque render differs by at most 1 channel.
This is bounded source-edge provenance, not proof of global renderer correctness.

Source ladder 1: HEAD-owner with FULL only below the head box cannot be represented by current declarations.
`extend_below_crop` continues connected full components only where HEAD reaches the crop probe. Actual
probe row 377 has 0 HEAD support columns (last alpha>128 row 336): 0 continuation pixels, versus 116209 in
the full/full positive control. No bounds API was invented. FULL-owner alone preserved tails but the
light rim remained; setup uncovered error 4383→4558, so it was not called clean.

Source ladder 2: one exact 607 crop [506,121,1113,728], same 1024 canvas/depth 512/seed 42/steps 30/offload.
Preflight clipped raw union alpha>=1: 81001 texels, >=8: 164, >=128: 0, maximum clipped alpha 36.
These were reported and admitted as faint haze; zero clipped faint alpha was not a package contract.
The new HEAD produced a detached 4015 pixel bead ring in headwear. A documented structural accessory
split preserved 14277 positive-alpha pixels with zero RGBA differences/loss/addition/overlap and identical
rest recomposite; it did not erase the ring. It remained visible as a necklace and the rim survived the
posed comparison. That source/config was rejected and preserved. No second generation was submitted.

Delivery-scale comparison of the original ±12° turn uses unobscured same-pose controls at 4.30 s
and 5.15 s, full 960×540 frames and unscaled head crops, alongside v1. At that size the outer edge was
accepted as a hair highlight; this does not establish zero edge pixels or erase the thin edge visible
under enlargement. The more legible ±12° turn is retained. The ±8° candidate
(`20261029T211507Z-eab47773702546c59b13ac821d7e4dc1`) was rejected for lower turn legibility.

The same-pose control imports the actual compositor with `show.reveal=[0,0]`; camera, sky, captions,
rig pose and downsampling remain the same. Five outside-reveal JPEG byte matches per amplitude control
the earlier comparison. The final contour candidate also has a bounded same-compositor peak-pose
control and outside-reveal byte match. Diagnostic PNGs precede WebP encoding; actual delivery crops
are decoded from the encoded WebP. The reveal intentionally overlaps the maximum turn, so only an
unobscured control can support the underlying-source observation. No source edge was repainted or masked.

## Meshes, bends and failures kept

| Part | Final mode | Triangles |
| --- | --- | --- |
| hair_long | contour | 434 |
| hair_back | auto | 28 |
| handwear_l | auto | 30 |
| legwear | contour | 158 |
| neck | grid | 304 |
| bottomwear | contour | 133 |
| topwear | contour | 384 |
| handwear_r | contour | 58 |
| hairpin | contour | 46 |
| hair_front | contour | 127 |

The ten producer meshes total 1,702 triangles. The face surface adds 360 and the film’s duplicated sleeve adds 58: 2,120 mesh triangles stored in the compiled model. The wave swaps attachments, so the 12 stored mesh slots are not all active together.

The failed auto attempt printed 122 hair_front / 65 legwear triangles; those refused outputs are not accepted baselines. The chosen contours have 127 / 158.

Earlier producer diagnostics: topwear auto refused a reference-identity mismatch (1,382 deform values versus an attachment array of
460 entries); no accepted auto triangle count exists for that attempt. Its documented contour
replacement initially had 352 triangles and folded at region band 20. Band 27 follows the measured
21.181708 rig-unit chest-relative displacement plus margin. Hairpin uses heat weights with continuous,
uncapped influences; a rigid cap-one alternative produced a discontinuity and eight folded frames and
was rejected. These historical diagnostic counts are not the final producer counts in the table above.

The final auto-source attempt declared actual setup-relative bends: bang_r 14°, bang_c 12°, bang_l 13°, leg 16°. It failed before compilation: the unreduced hair_front source inverted three triangles at bang_r +14°, and reduced motion residuals were 5.550295 px for hair_front and 5.901466 px for legwear against the unchanged 3 px limit. That 42.448 s attempt is RED, not the successful final timing.

The documented contour route replaces only these two automatic meshes: tolerance 2, margin 2, spacing/maxEdge 30, hair_front stray 3 and legwear stray 1. Both preserve their previous segments, r, distance rule and four-influence cap with a continuous floor. The front-hair contour reports 23 dust islands / 26 pixels excluded under its declared stray limit; the original RGBA/depth files remain unchanged. The automatic mesh's motion residual comparison does not apply to contour; no 3 px auto result is claimed for it. The contour candidate is measured by all-animation rendered folds, rig-parts check, actual setup-relative bends and native/delivery inspection.
Fresh final film readings: bang_r 13.1°, bang_c 11.1°, bang_l 12.4°, leg 15.4°, headwear tassel 93.2°, yaw 12.0°. `tools/bends.py` excludes the lead-in and measures largest setup-relative local turn;
half-range is a separate reading. Source confidence, gate arithmetic and visual acceptance are different.

## Earlier hanging-hair response controls (7beaf)

The earlier hanging-only writer removed the producer’s existing `tail_*_ctl` idle rotations and tunes eight
public rotation-physics constraints. All four links retain their original strengths
105/84/67.2/53.8, mass 1 and mix 1. Damping is 0.85; inertia is 0.2 on links 0/1 and 0.1 on links 2/3.
Root links respond to gravity 120 in the default downward world; lower links have gravity 0 to keep
the painted curl. That earlier revision added no new tail keys, pixel edits, mesh/weight changes or custom solver. The later stop revision changes only documented drawn-link binding names and their child parentage.
That earlier delivery’s complete rig/motion JSON and all 321 show poses matched its selected physics control. These response measurements are not reused as measurements of the later seat-stop take.
Other part tracks are byte-equal; non-tail bones and other attachments match the previous delivery
across all five animations. Raw sources, ring removal and hair-in-front-of-bar order are unchanged.

The formal first-tilt window is 1.5–3.75 s, sampled at 20 fps. The head angle is its world x-axis;
primary tip angle is the last physical link’s world x-axis, and the secondary measure is the chord
from root origin to its last link’s length tip. Angles unwrap from setup; the ranges below subtract
the seat’s world rotation. A painted curl is not assumed to point along that physical axis.

| Range, degrees | Head | Right tail | Left tail |
| --- | ---: | ---: | ---: |
| Previous last-link axis | 8.131925 | 28.931 | 26.938 |
| 7beaf last-link axis | 8.131925 | 7.310295 | 8.184749 |
| 7beaf root-to-tip chord | 8.131925 | 5.644725 | 5.889145 |

The left axis exceeds the fixed head-order bar by **0.052823°: partial RED remains**. Delivery-scale
visual review adopted the more inward/downward hanging silhouette as a nonblocking product choice;
the number was not relabelled PASS. All three adjacent joint ranges vary by about 1.35–2.72°, above
the segment-length-derived one-delivery-pixel angular bounds, so this is distributed bending.
Root-anchor position error is at most 1.14e-13 rig units. The measured post-beat velocity/acceleration
max/RMS readings are below the previous version’s (largest ratio 0.539552).

The LOCAL head input reaches 7.5° at 2.00 s and holds to 3.50 s. In paired head/no-head controls,
response peaks occur 0.35 s later on both last-link axes and 0.25 s later on both chords, on the
0.05 s frame grid. These are lags from local input ramp completion, **not world-maximum lags**.
The world head/no-head angle varies 0.081311° during that held local input; its cause was not
isolated. Exact-argmax and float-plateau measurement attempts are retained as rejected evidence.
Hop and wave windows are full-response stress/settle readings, not additional attenuation bars.

A no-tail-physics control retains the old idle keys. It reduces some amplification but does not
meet the same range/bend checks. The chosen change combines key removal with physics tuning;
these controls do not prove gravity alone caused the improvement or form a full factorial study.

For the earlier 7beaf delivery, all 240 decoded frames were self-read in 20 native hair pages and five hip pages, without
resizing. No new tear, tail severing, doubled strand or restored hip oval was observed in that
frame-sheet read. Separate old/new full 960×540 tilt frames use the identical camera; the new hair
crop does not stand in for the old extent. Native setup/min/max/diff and boundary evidence remain
separate from delivery frames. The angle table/CSV and four-panel plot are bound to exact final
production geometry. This is frame-by-frame inspection, not a continuous-playback verdict.

## Moving-seat angular stops (selected delivery)

The selected producer adopts the reviewed two-stop declaration exactly: `tail_r_seat` stops `tail_r1`
against `seat` at `[-246,27]`; `tail_l_seat` stops `tail_l1` at `[255,27]`. Both use inward 0/outward 60.
All eight tail physics entries move unchanged from the motion table into the rig constraints, before
the stop’s copy/clamp reads them. `tail_r2_ctl` and `tail_l2_ctl` hang from the respective `_d` drawn
links, and mesh weight names for link1 point to `_d`; all local binding coordinates and weights stay
unchanged. The underlying raw RGBA/depth, hip-loop restoration, draw order, head/face/body motion,
look-around amplitude and reveal are unchanged. The other 18 springs stay in the motion table.

The public mechanism aims a frame at a point attached to the moving obstacle bone and clamps rotation.
It has no positional line projection, friction or surface collision. It therefore does not certify
that the hair rests on the bar. On all 240 loop frames, the link2 control origins remain above the
nominal opaque bar top (seat-local y 27): minimum clearance R11.789459/L12.486742 delivery px;
0/240 below-bar frames on both sides. The normal RMS from the setup centerline height 47 is
R5.716630/L5.832207px against the unchanged <=1px criterion: **RED on both sides remains**.
These are moving-seat-frame link-center measurements, not a pixel-surface contact certificate.

At f040/2.00s and f070/3.50s, last-link endpoint separation grows from the earlier hanging-only
79.156/77.739px to 169.038/177.611px. Because the painted tips curl, a separate actual distal mesh
measurement uses vertices with side-link2/3 weight>=0.5: outer spans 223.763/221.509px become
275.533/280.584px (+51.770/+59.076px). The wider fan and normal-RMS RED were accepted as known
limits of the selected delivery-scale silhouette. No metric was relaxed or relabelled PASS.

A later bounded analytical correction was not rendered or adopted: an unconstrained fit put its aim
points far above the bar; a bar-constrained one-step fit still predicted right-side RMS 1.017707px.
Those estimates did not establish a universal impossibility and did not justify a new collider or
parameter sweep. The selected production inputs are the original reviewed stop candidate, unchanged.

## Reading and publishing

Read setup/min/max/diff at native pixels, then native and nearest-neighbour 4 x boundary crops. Record
tear/ghost/clean per observed boundary and its scope; absence at two endpoints is not a whole-loop claim.
The final show geometry-extrema pair is SKIP when the wave changes attachment identity; channel extrema
remain READ. Keep that SKIP, use actual yaw-channel witnesses, and inspect the whole loop.

Final bars/skips: `A00_ROUNDTRIP_PARSE` unrun without the optional spine SDK. Show global geometry pair SKIP due to wave attachment changes; sampled channels remain READ. Parts check reads the producer’s idle and diagnostic turns; its no-physics CLOTH_SETTLES note does not assess the film’s later 26 springs. Temporal contact/follow/aim/range/stretch/seam requirements are undeclared. RECOMPOSITE_HOLES is reported, not barred: 4,093 uncovered error pixels after the hip-loop restoration (the earlier source read was 4,383). No full suite, native browser viewer or cross-encoder byte-equality claim. The selected delivery has owner approval; organisation/site publication is separate. The current loop prints 0.000 for both bone and vertex offsets; this is rounded, not mathematical zero. The earlier hanging-only hair component offset projected to 0.00009646 delivery pixels; that historical figure is not a new seat-stop measurement. Earlier native beat/boundary and unobscured head-turn controls remain source-bound. The selected seat-stop take retains its approved fullframe comparisons and native whole-loop sheet. A new all 240 frame-by-frame visual read is not claimed; contact RED and the wider fan are explicitly retained.
The root `trailer.webp` is updated to the owner-approved selected v2 delivery. Organisation/site changes remain separate; no publishing script or automatic root copy runs as part of build.sh.
