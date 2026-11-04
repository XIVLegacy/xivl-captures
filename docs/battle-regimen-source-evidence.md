# Battle Regimen announced rules and client limits

The October 6, 2010 official announcement described Battle Regimens as party
members queuing commands against one enemy, then having one participant
initiate their automatic execution. Each participant could queue one action.
The announcement's combinations describe intended behavior for that earlier
version. They do not establish Battle Regimen availability in 1.23b.

## Retained source

The [announcement](../sources/lodestone-dev-patch/objects/pages/battle-regimens-2010-10-06.md)
is a 5967-byte transcription, SHA-256
`d679fd8f846d06f67961edf98f2219056018cc6ff10dd8106704d216c39a9914`,
pinned by the [source manifest](../sources/lodestone-dev-patch/manifest.yaml).
Its title, source date and original topic URL are recorded in the
[page inventory](../studies/lodestone-dev-patch/derived/file-inventory.csv),
row `battle-regimens-2010-10-06`.

The [study's evidence qualification](../studies/lodestone-dev-patch/README.md)
applies: this is first-party announced intent, not confirmation of shipped
1.23b behavior. The source's Battle Regimens section, lines 9-13, supplies
the queue and execution description above.

## Announced combinations

The source table at lines 21-28 distinguishes these eight rows. Actions are
listed in execution order.

| Announced effect | Actions and class condition |
| --- | --- |
| Reduced physical defense | Normal attack, then normal attack. |
| Reduced magic defense | Normal attack, then magic attack. |
| Longer casting time and higher MP costs | Normal attack, then magic spell. |
| Reduced TP progression and higher TP costs | Normal attack, then weaponskill. |
| Preserved class-ability effectiveness when used by different classes | Two magic spells, both from the same class. |
| Preserved class-ability effectiveness when used by different classes | Two weaponskills, both from the same class. |
| Increased player damage | Two weaponskills from different classes, optionally followed by a magic spell. |
| Increased player damage | Two magic spells from different classes, optionally followed by a weaponskill. |

For the last two rows, the different-class condition applies to the initial
pair. A third action is optional, and the source does not require a third
class. Magic attack and magic spell remain distinct source terms. The
normal-attack label does not establish equivalence to a later auto-attack.

## Separate 1.23b client evidence

`xivl-decomp:docs/actor/battle-regimen-combination.md`, section 2, owns the
published static client finding for extraction `2012.09.19.0001`.
It records `canStartCombination` returning `false`, while
`getStackedCombinationNum`, `getStackedCombinationTimer` and
`getMyCombinationStackedNum` return `0`.

These selected static results establish client-layer restrictions. The
finding leaves packet and runtime execution unresolved. Neither the earlier
announcement nor these static restrictions establish universal runtime
availability or unavailability, a removal date, or an enabled historical
1.23b execution.
