# Third-party notices

The scripts here are MIT (see `LICENSE`). The images were generated for this
repository; what generated them, and what the build runs, is below. Naming a
project identifies where something comes from; it does not imply that its
authors endorse this repository. Statements marked **[observed]** carry the date
and the place they were read; upstream terms can change.

## The tools the build runs

- [`@rig-c/parts`](https://github.com/rig-c/parts) and
  [`rig-c`](https://github.com/rig-c/core), both MIT, installed from npm by
  `build.sh`. Their own notices cover what they depend on; in particular the
  skeleton data `rigc build` writes is in the Spine 4.3 format, and rig-c's
  `NOTICE.md` says what that does and does not involve.

## See-through

`inputs/layers/` holds two See-through decompositions of the painting, made
with the ComfyUI wrapper. No See-through code or weights are in this
repository. Project, paper, licences and weights:
[rig-c/parts `NOTICE.md` §1](https://github.com/rig-c/parts/blob/main/NOTICE.md).

## Checkpoint

The painting, the sky and the palm were generated with
`novaAnimeXL_ilV80.safetensors` —
[Nova Anime XL](https://civitai.com/models/376130) "IL v8.0" by Crody, an
Illustrious-base checkpoint — with no LoRA. The checkpoint is not
redistributed. *Painted with Nova Anime XL IL v8.0 by Crody
(https://civitai.com/models/376130).*
**[observed 2026-10-11]** CivitAI's model API reported for model 376130
`allowCommercialUse: ["RentCivit", "Image", "Rent"]`, `allowNoCredit: true`,
`allowDerivatives: true` and `allowDifferentLicense: true`; version 1854228 is
named "IL v8.0" with base model "Illustrious".

The painting was posed with `controlnet-openpose-sdxl-1.0.safetensors` and
upscaled with `4x-AnimeSharp.pth`; `inputs/generation.json` records every
setting. The prompts name and describe no existing character.

## Font

The captions in the published `trailer.webp` are set in Avenir Next, a font
that ships with macOS. No font file is in this repository; `film/compose.py`
uses whatever the machine has.
