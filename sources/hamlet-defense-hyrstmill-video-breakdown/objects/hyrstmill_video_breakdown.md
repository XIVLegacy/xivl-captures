# Hyrstmill Hamlet Defense: sampled video observations

## 1. Video Context

The source is a public [YouTube video](https://www.youtube.com/watch?v=xi9NlNB8t5M) titled `FFXIV 1.0 - 65,000 points Hamlet Defense, Hystmill [65,000スコア・ハムレット防衛戦]`, uploaded by TidteeToey. The page lists a duration of 21:44 and displayed "14y ago" during review on 2026-09-23; the exact publication date was not exposed. The description lists `1 WAR, 2 WHM, 2 DoH, 3 DoL`, `Patch 1.22a`, and `Legacy Core, Excalibur`. Those are uploader-provided details, not independently verified party or patch state. Sampled frames show the 1.x HUD. The exact client build is not independently identified.

The sampled HUD identifies the recording character as White Mage (Conjurer Level 50). The reviewed frames do not establish the character's weapon, party composition, or defensive and offensive setup.

## 2. Entry and Duty Rules Observed

Not observed in the reviewed frames.

## 3. Dialogue Transcript

No NPC or enemy dialogue is transcribed. The sampled frames show combat-log and system messages only.

## 4. Enemy Roster and Observed Actions

At 10:21, the combat log displays `Sazel Ciloc the Divine has joined the fray!`. This establishes the displayed name and message, not the complete roster or the underlying spawn mechanism.

At 19:35, the combat log displays `You begin casting Stone.` and `Sazel Ciloc the Divine's Wing Clipper hits you from the left for 102 points of damage.` It also displays `Sazel Ciloc the Divine's Wing Clipper inflicts you with the effect of Heavy.` This is one sampled hit and status message; it does not establish the action's full behavior or a damage range.

## 5. Sequence and Phases

- At 05:16, the combat log shows a Cure on a militia second-line archer and two settlement/enemy effect messages.
- At 10:21, the combat log announces Sazel Ciloc the Divine's arrival.
- At 19:35, the log shows a Stone cast and one Wing Clipper hit for 102 points of damage, followed by Heavy.

These are sampled frames in video order. They do not establish all intervening events or exact phase timing.

## 6. Damage Observations

These are single visible values, not tuning ranges.

- At 05:16, the militia second-line archer recovers 1,279 HP after Xenora Meep uses Cure on it.
- At 19:35, Sazel Ciloc the Divine's Wing Clipper hits the player for 102 points of damage.

No repeated sample establishes a damage or healing range.

## 7. Quest Step Sequence

Not observed in the reviewed frames.

## 8. NPC and UI State per Step

The sampled frames show the Hamlet battle HUD, party list, combat log, and visible militia nameplates. Quest markers, journal progress, tutorial widgets, and state changes are not established.

## 9. Transitions and Zone Changes

Not observed in the reviewed frames.

## 10. Rewards and Obtain Lines

Not observed in the reviewed frames. The title's score is a title-level claim, not a score result independently checked in the sampled frames.

## 11. Linkshell and System Messages

- At 05:16, the combat log displays `The militia second line archer recovers 1279 HP.` and `All enemies are inflicted with the effect of decreased attack!`. The scene also displays `All militia archers are granted the effect of increased attack!`.
- At 10:21, the combat log displays `Sazel Ciloc the Divine has joined the fray!`.
- At 19:35, the combat log displays the Stone cast, Wing Clipper hit, and Heavy effect quoted above.
- No linkshell message is transcribed.

The exact quoted message strings have not been cross-checked against a decoded `worldMaster.csv` in the public data checkout. They remain video observations only.

## 12. Reference Facts

The YouTube page identifies the video title and uploader. Its description labels the recording `Patch 1.22a`; this is uploader metadata, not an independently authenticated executable build. The page does not establish 1.23b behavior.

The displayed action name `Wing Clipper` also appears as command 23394 in `xivl-client-data:derived/command_battle_params.csv:524` at revision `5f447434feb4063bd67eabb3adb5bd75c20fdc99`. That is a client-data name match, not proof that the footage used the 1.23b executable.

## 13. Uncertainties

The frames are samples, not a complete transcript or a recording of every event. The uploader identifies Patch 1.22a, so this clip is not evidence of the 1.23b runtime branch. Exact publication date, executable identity, complete roster, full party composition, score calculation, status duration, and all server-side behavior are not established. No video media or screenshot is retained in this repository.
