# Evidence map - elemen-battlecraft-leve-objectives

A deliberately **narrow** harvest of the eLeMeN regional battlecraft leve pages:
the readable objective choreography only. It exists because a client-first recon
of the whole guildleve section found everything else redundant with the client -
this is the one slice with independent value. Evidence tier: **wiki** (packet
captures > video breakdown > wiki), so CALIBRATION-grade.

## Client-first scoping (why only objectives)

The guildleve section was recon'd client-first. The client ships
almost all of it as primary evidence, so those fields were **dropped**, not
transcribed:

| field the source shows | client source (primary) | kept here? |
|---|---|---|
| leve name (JP/EN/DE/FR) | `xtx_guildleve.csv` (623 named leves) | as the join key only |
| flavor description | `xtx_guildleve.csv` | dropped |
| reward candidates | `guildleve.csv` reward-id columns | dropped |
| contract period | `guildleve.csv` (e.g. c22=30 = 30 min) | dropped |
| objective counts / mob-item ids | `guildleve.csv` (e.g. c40=5 = the "x5") | see below |
| **objective choreography (readable)** | **not in usable client form** | **KEPT** |

The client encodes objective *parameters* (spawn counts, mob/item ids, party
flags) numerically, but the **readable runtime choreography** - wave structure,
sequential spawns, flee/add behavior, "find-the-right-one" lottery mechanics,
item-gated triggers - is the site's synthesis and is tedious/lossy to
reconstruct from the numeric params. That runtime-behavior description is closer
to a video-breakdown observation than a static decode, which is why it clears
the client-first bar when the rest of the section does not.

Note the site carries **no** reward gil/exp amounts (just "ギル", one "1,000ギル"
across all three pages) and **no** star ratings - so the fields that would have
been a second web-unique slice (reward tuning) are simply absent.

## Scope

The 3 regional **battlecraft** city pages, all camps:

- `guildleve/regional/{LimsaLominsa,Gridania,Ul'dah}_BattlecraftLeves.html`

177 leves, 59 per city. The regional **fieldcraft** (gathering) pages and the
**local** tradecraft (crafting) leve pages are out of scope - fieldcraft/craft
objectives are gather/synth targets the client carries plainly, without the
battle choreography that motivates this set.

## Best table (unique value)

- `derived/battlecraft-leve-objectives.csv` - 177 rows: `city`, `camp_jp`,
  `leve_name_jp`, `leve_name_en_client`, `client_leve_id`, `objective_text`,
  `name_match_note`. The `objective_text` column is the payload - the readable
  wave/spawn/mechanic choreography per leve.

## Client cross-check

Every leve name joins `xivl-client-data/csv/xtx_guildleve.csv` (JP col10 ->
EN col11, id col0), NFKC-normalized. **177/177 resolve to a client leve id** -
174 directly, 3 via audited overrides for site transcription variants
(触覚 vs client 触角 "antenna"; ｢｣/「」 bracket width; a dropped ・). The three
are listed in `glossary.md` with their client ids and EN names. The join
confirms all 177 are 1.x client leves rather than ARR entries and
supplies the official EN names.

## Gaps / caveats

- `objective_text` is the site's terse shorthand (verbatim JP); the enemy/item
  names inside are not separately resolved to the client here - cross-reference
  via `elemen-bestiary` if needed.
- The choreography is the site's observation, wiki tier -> CALIBRATION-grade.
  Corroborate against `guildleve.csv` numeric params or packet/video evidence
  before treating a specific wave detail as retail-confirmed.
- Reward amounts, exp, star scaling, and contract period are NOT in this set
  (absent from the source or client-carried and dropped).
- The JS `document.write` flavor text on each leve name was dropped (it is the
  client's `xtx_guildleve` description, reachable via `client_leve_id`).

## Verdict

Confirmed as a faithful transcription of the source objective column, with every
leve joined to its client id (177/177). The set carries only the web-unique
objective choreography; all client-primary fields were dropped by design. No
claim promoted to retail-confirmed.
