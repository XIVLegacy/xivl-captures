# Impish Impositions video evidence map

## Source and scope

Evidence ID: `seasonal-impish-impositions-video-breakdown`.
Source: [Final Fantasy XIV 1.0 - Original Halloween Event (All Saints' Wake)](https://www.youtube.com/watch?v=Yn8L_t8sCTk),
Leonesaurus, published October 19, 2011, duration 8:42. Source identity and
storage are in
`sources/seasonal-impish-impositions-video-breakdown/manifest.yaml`.
The original observation record is
`sources/seasonal-impish-impositions-video-breakdown/objects/impish_impositions_video_breakdown.md`,
4,227 bytes, SHA-256
`6f7e1821abbe9c7a349da880d7d816211220b3259ee7896537eb46da9d329e90`.
That digest identifies the record, not the external video's bytes.

Evidence class: `notes-and-transcripts`, video tier 2. These are selected
frames, not a full transcript or continuous input trace. The HUD and action
bar are 1.x. The exact patch and capture date are unknown; the 2011
publication is not a 1.23b runtime witness.

## Confirmed

Confirmed here means visible in the sampled footage, with the cross-check
scope below. It does not mean packet-confirmed or live-validated in 1.23b.

| Video locator | Observed finding | Verdict |
| --- | --- | --- |
| [5:03](https://www.youtube.com/watch?v=Yn8L_t8sCTk&t=303s), question widget | Three choices, ordered The Coffer & Coffin; The Roost; The Red Rooster Stead | Video-observed. By wording, the question corresponds to 1.23b text row 131 and the choices to rows 136, 132, 135. This does not identify runtime argument types or prove those row IDs were sent. |
| [5:13](https://www.youtube.com/watch?v=Yn8L_t8sCTk&t=313s), imp response | Acknowledgement of a correct answer | Video-observed. The samples do not identify the submitted choice or numeric expected-answer value. |
| [5:28](https://www.youtube.com/watch?v=Yn8L_t8sCTk&t=328s), log and basket | Nine-cookie obtain message, a basket drop/vanishing message, and a visible basket | Video-observed reported acquisition after the earlier correct response. This corroborates the nine-cookie presentation in the later script, without proving its settlement. |
| [5:38](https://www.youtube.com/watch?v=Yn8L_t8sCTk&t=338s), log | A distinct three-cookie obtain message followed by an empty-basket message | Video-observed. This supports a separate basket reward in the recorded 2011 sequence. Sharing, eligibility and expiry are not established. |

### Client cross-check

The comparison used extraction `2012.09.19.0001`, game version 1.23b,
identified by `xivl-client-data:manifests/tables.json`, SHA-256
`239cb63fb00de5f434b92924696c043cb80ddcd9abc7f334075afb6b28d5626d`.
Selected members were read with Python `csv` from the decoded archive,
SHA-256 `006f9438a8cfd9277376f0ab28474500c67e4665050aa631cae64c9e6f38a5b0`,
and matched their manifest sizes and hashes:

| Member | Bytes / SHA-256 | Useful locator |
| --- | --- | --- |
| populaceHalloweenTrans.csv | 54,587 / cda55dc5fe76ac4b9ec528c83016076311266922ef6d565242c589a8d889681f | English sheet column 1 after the row ID: row 13 correct response, row 15 parameterized cookie promise, row 24 obtain template, row 25 drop message, row 26 empty basket, rows 131-136 riddle group |
| xtx_itemName.csv | 4,428,170 / 917c34eb0621b7d7a8261145023d0bb95cd8ca9eb52288ceb66e80d08f0d78c2 | Row 3010417, sheet column 5: Pumpkin Cookie |

The riddle and choice wording match the identified text group after formatting
markup is removed. The correct response and cookie promise are compatible
with rows 13/15. The empty-basket wording matches row 26. Row 24 supplies a
parameterized obtain template, not a literal nine- or three-cookie record.
Neither this text comparison nor a matching item name identifies the runtime
emitter, transmitted item ID or inventory transaction.

`xivl-client-scripts:docs/impish-impositions-client-contract.md`, Imp question
arguments and answer returns, owns the original-LPB proof that the 1.23b
matching branch presents nine and returns 0, while the non-equal branch
presents five and returns 1. The video does not execute or identify that
later chunk. No battle/action-name check applies to these selected samples.

The retained packet boundary is in
[Director Wire Identity](../../director-wire-identity/README.md#impish-question-packet-boundary).
It has no target invocation or reward vector for comparison. That absence
does not contradict the video, and no packet search was repeated for this
intake.

## Contradicted

There is a literal version difference: the 2011 drop message refers to a
basket of treats, while 1.23b `populaceHalloweenTrans.csv` row 25 says the imp
drops the cookies. Severity: wording/version distinction. Do not replace
the observed message with the later string or infer an identical callback
from their shared meaning.

No positive packet contradiction was identified. These frames do not show
a wrong answer and therefore do not settle the five-cookie consolation
presentation or conflicting secondary claims about wrong-answer rewards.

## Unverifiable

- Exact client patch, 1.23b runtime settlement and inventory mutations.
- The native/server question producer, callback name and binding, argument
  vector, choice selection rule and expected-answer encoding.
- Which highlighted choice was submitted. The first choice at 5:03 is only
  the highlight in that frame.
- The precise basket input action, universal payout, sharing, per-player
  eligibility, depletion, expiry and respawn.
- Acceptance/completion, first-trade rules, calendar, population and placement.

## Unique value

The footage supplies reported acquisitions missing from the retained target
packet sample: nine cookies after a correct response, then three more with
an empty-basket message. These are separate acquisitions in the shown
sequence, not competing values for the same reward or proof of a universal
twelve-cookie payout. The later three-choice UI contract is also consistent
with the observed menu, without recovering its caller.

## Gaps

The 1.23b producer and settlement ceiling remains. The source video is
external and has no preserved media digest or identified archive snapshot.
The record's hash preserves this transcription only. The selected frames
do not establish wrong-answer outcomes or any basket sharing or expiry rule.
