# Contributing

`rig-c/trailer` builds the animated loop on the rig-c organisation front page from a single generated painting, its See-through layer sets in `inputs/`, and the authoring scripts in `film/` and `tools/`.

## Getting the code running

Building requires [Bun](https://bun.sh) 1.4+, `npm`, and Python 3 with `numpy` and `pillow`. No GPU or ComfyUI is needed; the painting and layer sets are already in `inputs/`.

```sh
pip install -r requirements.txt
./build.sh
```

`./build.sh` (also `npm run build`) runs `npm ci` if `node_modules` is missing and writes all five stages to `out/v2-final/` (or `TRAILER_OUT=<dir> ./build.sh`), ending with `scene/trailer.webp` and `scene/delivery-inspection/`. Once step 1 (`out/v2-final/parts`) has been built, `./film.sh` re-runs steps 2–5 for edits under `film/`.

## Before you open a pull request

Run the full build end to end (a multi-minute run that builds the parts and rig, compiles twice through `rigc build`, poses 495 frames across five animations with `rigc render --folds`, composes the 240-frame loop, and runs every verification script):

```sh
./build.sh
```

Every check inside `./build.sh` must exit 0:

- `bun tools/preflight.ts parts "$OUT/parts"` — verifies every part's art and depth sheet.
- `bun tools/preflight.ts film "$OUT/film"` — parses the film rig and motion specs and checks timeline invariants.
- `rigc build` and `rigc render --geometry --extremes --folds` — gates the compiled skeletons and checks that no mesh triangle folds over.
- `python3 tools/loop.py`, `python3 tools/bends.py`, and `python3 tools/delivery.py` — verify seamless loop closure, bone bend ranges, and the encoded WebP frame count and duration.

## Reporting a change

- **Issue first.** Open an issue before changing `inputs/config.json`, `film/`, or `tools/`, stating the beat or part affected and the measured reading before and after.
- **One issue per pull request.** Keep each pull request scoped to one issue.
- **Conventional Commits.** Write commit messages and documentation in English using [Conventional Commits](https://www.conventionalcommits.org/) with a scope (`feat(film):`, `fix(rig):`, `docs(working):`). Include no private names or local filesystem paths.

## Where further rules live

- [WORKING.md](WORKING.md) — where each kind of change goes, how to inspect builds, and the measurements behind each beat.
- [README.md](README.md) — overview of the five build steps and beat table.
- [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE) — model attribution and MIT licence terms.
