# Video Breakdown Template

Use this template to document a retail Final Fantasy XIV 1.x gameplay video.
The result is an observation record suitable for evidence intake. Follow the
"Video Breakdown Intake" section of
[`integrating-new-captures.md`](integrating-new-captures.md).

---

Record observations from gameplay captured in Final Fantasy XIV 1.x, using the
version 1.23b client where known. Treat the video as evidence, not design input.
Decoded client data and a 1.23b packet corpus can corroborate some details, but
the video remains the source for the behavior it shows. Archive the completed
record and verify each specific against client data and packets where available.
Leave a detail unresolved when the evidence does not establish it.

Identify the video and the fight or content shown. Use any prior breakdown only
as a formatting example.

# A note on the version

This is 1.x, NOT A Realm Reborn (2.0+). The two games share names but differ in
mechanics, numbers, action lists, zones, and UI. Almost every wiki you can find
describes ARR or later and silently applies those facts to 1.0. Treat anything
not visible in the video as version-suspect: a modern wiki number is not evidence
about 1.x. The available decoded 1.x client data - not the wiki - is the
real reference, so your job is to report what the video shows, cleanly separated
from anything you looked up.

If you do cite a reference, rank it honestly by how 1.0-specific it is:

- Usable for 1.0: community wiki pages whose TITLE carries the
  `(version 1.0)` suffix - reliable for the game, its systems, and its classes;
  confirm membership via `Category:Final Fantasy XIV (version 1.0)`. Caution for
  boss/primal fights: the franchise page (e.g. `Ifrit (Final Fantasy XIV)`) mixes
  1.0 and ARR on one page, and the 1.0 battle data is usually split off under the
  arena/encounter name (e.g. `Howling Eye (version 1.0)`), so a bare primal name
  does not isolate 1.0. Trust pages with a `(1.0)` title suffix or under a
  version 1.0 archive namespace; a hub page listing 1.0 topics is the index, and
  any unsuffixed numbers/gameplay page is current-version. Use a general
  orientation overview for orientation only, never for numbers.
- Corroboration only: archival 1.0 video footage dated 2010-2012, and only after
  you confirm the clip shows the 1.x HUD / action bar / Battle Regimen UI (it
  differs visibly from ARR).
- Do not use for 1.x: modern community databases and any unsuffixed current-version
  wiki page - all ARR-only.

Use 1.0-era vocabulary, not ARR: this game has Behest (not FATEs), guildleves
issued by levemetes, Anima-cost aetheryte teleport (not gil + tickets), and the
Battle Regimen party-combo system. If a term you are reaching for is a Duty
Finder / roulette / Hunt board / anima-relic concept, it is ARR - leave it out.

# Evidence discipline

Every claim belongs to exactly one tier, and the tier must be explicit:

1. **Observed from the video** - things directly visible: log lines, casts,
   weaponskills, abilities, dialogue, damage numbers, HP/MP/TP changes, spawn
   order, linking/aggro, phase transitions, Battle Regimen windows, win/loss
   triggers.
2. **Reference** - archived community pages or player reports. Always include a
   URL and version-confidence: is the claim specifically about 1.x, or is it
   ARR-era and merely assumed to hold? Never blend it into observed claims.
3. **Inference** - anything you concluded rather than saw. Label it.

Hard rules, ordered by common failure modes:

- **Quote the log, never normalize it.** The 1.x log uses distinct verbs for
  distinct action types, and they must be preserved exactly:
  - `[Name] begins casting [Spell].` is a spell (magic).
  - `[Name] readies [Action].` is a weaponskill, ability, or TP-style move (the
    client dispatches all of these as "commands").
  - An auto-attack or an instant hit often resolves with only a damage line and
    NO "begins casting" or "readies" line - do not invent an action name for an
    unlabeled hit.

  Never convert one form into another (a "readies" is not a "begins casting"),
  never substitute a similar-sounding action name, and never upgrade or downgrade
  a tier from memory. If the log says `Fire`, write `Fire` - do not reason that
  it was probably `Fire II`. If the log says `Rage`, do not "correct" it to a
  similar move you remember.
- **Keep the action types distinct.** Magic, weaponskill, ability, and
  auto-attack are different categories the log verb tells you apart. Do not
  reclassify a "readies" command as a spell because the name sounds magical, and
  do not guess whether a command was a weaponskill or an ability from its name
  alone - report the verb you saw and the damage/effect that followed.
- **Pair every dialogue line with its moment.** Quote the exact text, give the
  timestamp, and state which action, phase change, or log event it coincided
  with. Never infer the pairing from the line's wording or tone - a taunt that
  sounds like it belongs to an attack may actually fire with a different action.
  If the timestamp sequence alone cannot establish which event the line
  coincided with, classify the pairing as an inference, not an observation.
- **Observed counts come only from counting.** Report how many times each notable
  action fired, with timestamps ("the boss readies Rear Fang once at ~7:40"). A
  reference claim that something happens multiple times never inflates an
  observed count - report both, in their own tiers.
- **A quest step advances for exactly one visible reason.** When quest progress
  moves (journal update, new marker, new objective text), report what the player
  did immediately before: talked to a named NPC, walked to a spot (an invisible
  trigger), performed a specific emote, finished an instance, or read a
  linkshell message. If the footage cuts or the cause is off-screen, say the
  cause is unobserved - never assume "talked to the NPC" because that is the
  usual case.
- If a log line is partially obscured or OCR is doubtful, mark it unclear rather
  than completing it from context.
- Reference facts never upgrade an observation. If a wiki says an ability happens
  twice and you saw it once, report "observed once; wiki claims multiple
  (reference, version-uncertain)".

For quick orientation, the English 1.x client renders combat log lines in these
shapes. Transcribe whatever your video actually shows - if it deviates, quote the
video, not this list. The list exists so you never normalize one shape into
another:

```text
[Name] begins casting [Spell].
[Name] readies [Action].
[Name]'s attack hits [Target] for [N] points of damage.
[Action] hits [Target] for [N] points of damage.
[Target] takes [N] points of damage.
Critical! [Target] takes [N] points of damage.
[count]fold attack! [Target] takes a total of [M] points of damage.
Additional effect: [N] points of damage dealt.
[Name] recovers [N] HP.   /   [Name] recovers [N] MP.
[Name] gains the effect of [Status].
[Name] resists the effect of [Status].
[Action] misses [Target].   /   [Target] evades ...   /   [Target] parries ...
[Name] absorbs [N] HP from [Target].
[Name] is defeated.
The levequest target is defeated. ([N] of [M])
You are no longer bound by duty.
Your party is defeated. This duty will now end.
```

A few of these are easy to mistranscribe, so preserve them exactly:

- There are two damage-resolution families and they are NOT interchangeable.
  `[Name]'s attack hits [Target] for [N] points of damage` (auto-attack, may add
  `from the [direction]`) and `[Action] hits [Target] for [N] points of damage`
  (a single, attributed hit) name the attacker and action; `[Target] takes [N]
  points of damage` is the shared / AoE / multi-hit form with no attacker on that
  line. Record whichever the video shows - do not rewrite a `hits X for N` line
  into a `takes N` line or vice versa, and keep the attacker/action when present.
- The multi-hit line is `[count]fold attack!` - no hyphen, lowercase `attack`, and
  for counts of ten or fewer the client spells the multiplier out (`twofold
  attack!`, `threefold attack!`, ... `tenfold attack!`); larger counts use the
  number (`12fold attack!`). Transcribe whichever form the video shows; never
  convert `twofold` to `2-fold` or `2fold`.
- `Critical!`, `Counter!`, `Critical counter!`, and block/parry/evade lines are
  required damage evidence. Keep the leading marker; never reduce the line to
  the plain `takes [N] points of damage` form.

Do NOT include implementation recommendations, implementation logic,
pseudocode, battle-controller designs, spawn-system designs, or "implementation
priorities" of any kind. The consumer has the real engine APIs; invented code
and architecture suggestions have proven actively misleading. If you believe
an observation has a non-obvious implementation consequence, state the
observation and one plain-language sentence about why it matters - nothing more.

# Output format

Markdown, ASCII punctuation only (no curly quotes, em dashes, en dashes, or
arrows), suggested filename `<content_name>_video_breakdown.md`.

The document has a shared core (sections 1-3 and the two closing sections),
a battle track, and a quest/progression track. Fill every track the footage
supports - a quest video that includes a fight fills both. Within a track you
include, keep every section and write "not observed" where it applies; omit a
track only when the footage shows none of it (say so in Uncertainties).

## Shared core

1. **Video Context** - video title/filename and duration, player character name,
   class or job and rank/level (in 1.x the equipped weapon sets the class and a
   soul crystal toggles it to the matching job; note whichever the video shows),
   party / NPC-ally / companion composition, and ONE short paragraph on the
   player's defensive and offensive setup (damage numbers are uninterpretable
   without it - buffs, mitigation, weapon, and Battle Regimen context change
   everything). No blow-by-blow strategy narration beyond that paragraph.
2. **Entry and Duty/Leve Rules Observed** - the entry interaction (levemete,
   aetheryte, quest NPC, or instance gate), and the exact entry/restriction log
   lines: time limit, level correction/sync, "bound by duty" / "You are no longer
   bound by duty", party transport wording, leve difficulty rating, and anything
   observed about re-entry or failure ("Your party is defeated. This duty will
   now end."). For open-world content (behest, notorious monster) note the
   trigger and any timer instead.
3. **Dialogue Transcript** - every readable NPC/enemy line: exact text,
   timestamp, and the co-occurring action or moment. Note obscured lines as
   unclear. Variants are first-class evidence, not noise: if the player talks
   to the same NPC again during the same step and gets a different line, record
   both; record every ambient/bystander NPC line even when it does not advance
   anything; and record failure-branch dialogue (a wrong emote, a declined
   prompt, a re-entered room) - the "nothing happened" response is exactly the
   line unavailable from other sources.

## Battle track

4. **Enemy Roster and Observed Actions** - per enemy: name as displayed; spells
   begun (log form `begins casting X`) and whether they completed or were
   interrupted; weaponskills/abilities/TP moves readied (log form `readies X`)
   and how each resolved (damage, miss, status); auto-attacks; buffs gained (log
   form `gains the effect of X`), debuffs applied or resisted (`resists the
   effect of X`); whether actions continue during invulnerable or transition
   phases; link/aggro behavior; and anything observed about death or despawn
   (`is defeated`). Transcribe every spell and command name verbatim from the log
   - never infer a tier or a fuller name (`Fire` stays `Fire`, not `Fire II`).
5. **Sequence and Phases** - timestamped order of the major events: waves,
   spawns, phase transitions, one-time actions, win/loss trigger, and any Battle
   Regimen or behest/Hamlet wave structure. Count repetitions explicitly ("the
   boss readies Rear Fang once at ~7:40") - never let a reference claim inflate an
   observed count.
6. **Damage Observations** - per attacker/target pair with target context
   (defended player, NPC ally, companion), as ranges when values repeat; crits,
   resists, and 0-damage cases separately; spell, weaponskill, and auto-attack
   damage separately; additional-effect lines separately; healing amounts. These
   are tuning targets, not values to hard-code - say so once at the top of the
   section. Format example:

   ```md
   Observed boss auto-attack damage:

   - Against defended player (tank): normal hits 30-60, one higher hit ~110.
   - Against NPC ally / softer target: normal ~288, critical ~408.

   Observed boss weaponskill (Rear Fang, log form "readies Rear Fang", single
   target): 73-289 across players and allied NPCs.

   Observed boss spell (Fire, log form "begins casting Fire"): 120-180 to the
   player; "Additional effect: 20 points of damage dealt" seen twice.
   ```
## Quest/progression track

7. **Quest Step Sequence** - the quest's observed steps in order, one entry per
   journal/objective change. Per step: timestamp; the objective text if
   readable; the exact trigger that advanced it (talk to [NPC name] / walk into
   a spot, described by landmark / emote [which] at [NPC] / instance completed /
   linkshell message read), or "advance cause unobserved"; and where the player
   was standing, described by visible landmarks - never invent coordinates.
8. **NPC and UI State per Step** - what the interface showed during each step:
   icons over NPC heads (quest-offer plate vs in-progress marker vs none, and
   which NPCs carried them), map/minimap quest markers and where they pointed,
   journal progress numbers or percentages, and any tutorial/help widget that
   appeared. Note when an icon or marker changed mid-step.
9. **Transitions and Zone Changes** - every loading screen or scene change:
   timestamp, where from and where to (zone names from the UI when shown),
   whether the destination looked like a normal public zone, an instanced or
   "past"/Echo version of a familiar place, or a solo private room; any
   confirmation prompt at the boundary (join/enter dialogs, party-size wording,
   exact text); and where the player reappeared afterward.
10. **Rewards and Obtain Lines** - HIGHEST-PRIORITY quest evidence: reward
    numbers have no other retail source, so a video that shows one is often
    the only available anchor. Quote exactly: every `You obtain [item/key item]` line, gil and experience
    amounts at quest completion (and the on-screen reward window contents if
    shown), per-kill experience inside quest instances, and any rank/skill
    point gains tied to the quest. Timestamp each.
11. **Linkshell and System Messages** - NPC linkshell messages with sender
    name, exact text, and TWO timestamps: when the message notification
    arrived, and when the player actually read it (players may leave messages
    unread; the arrival moment is what ties it to a step). Plus system-channel
    lines tied to progress (attunement confirmations, "you learn..." lines,
    duty/leve status lines not already in section 2).

## Closing sections (all tracks)

12. **Reference Facts** - the relevant reference claims with URLs, kept
    strictly out of the sections above, and EACH flagged with version-confidence
    (1.x-specific, or ARR-era / version-uncertain).
13. **Uncertainties** - what the video could not establish: unread log lines,
    off-screen events, single-sample timings, quest-step advances whose cause
    was off-screen, anything where your confidence is low, and any doubt about
    whether the footage is 1.x at all (which patch, or possibly a later
    version) - record whether a clip might not be 1.23b-era.

If a section does not apply, keep it and say "not observed" - an explicit absence
is evidence too.
