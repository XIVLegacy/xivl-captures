# Evidence Map - Hyrstmill Hamlet Defense Video

## Source and scope

The source is a public [YouTube video](https://www.youtube.com/watch?v=xi9NlNB8t5M) titled `FFXIV 1.0 - 65,000 points Hamlet Defense, Hystmill [65,000スコア・ハムレット防衛戦]`, uploaded by TidteeToey. The page lists duration 21:44 and displayed "14y ago" during review on 2026-09-23. The source observation record is
`sources/hamlet-defense-hyrstmill-video-breakdown/objects/hyrstmill_video_breakdown.md`.

The uploader's description says Patch 1.22a. The footage is therefore not evidence of 1.23b runtime behavior.

## Observed from the video

- At 05:16, the combat log displays `Xenora Meep uses Cure on the militia second line archer.` and `The militia second line archer recovers 1279 HP.` The screen also displays `All enemies are inflicted with the effect of decreased attack!` and `All militia archers are granted the effect of increased attack!`.
- At 10:21, the combat log displays `Sazel Ciloc the Divine has joined the fray!`.
- At 19:35, the log displays `You begin casting Stone.`, `Sazel Ciloc the Divine's Wing Clipper hits you from the left for 102 points of damage.`, and `Sazel Ciloc the Divine's Wing Clipper inflicts you with the effect of Heavy.`

These are sampled messages and values, not a complete roster, full timeline, or repeated damage samples.

## Client-data cross-check

`Wing Clipper` appears as command 23394 in `xivl-client-data:derived/command_battle_params.csv:524`, revision `5f447434feb4063bd67eabb3adb5bd75c20fdc99`, file SHA-256 `bc043bbd5558916a971de4d3a3a8dac5ec9d8ca36571bb534d0e964cd0b55d6a`. The matching name does not establish the clip's exact client build or 1.23b runtime selection. The message strings have not been cross-checked against a decoded `worldMaster.csv` in the public data checkout.

## Unverifiable

- The video page description labels the recording Patch 1.22a, but the executable build is not independently authenticated.
- The exact publication date is not exposed by the reviewed page.
- The complete party and enemy rosters, encounter phases between sampled frames, score calculation, status duration, and server behavior are not established.
- The title's 65,000-point claim is not independently verified by these samples.

## Contradicted

No sampled frame directly contradicts another claim. Unseen behavior remains unresolved rather than contradicted.
