# Official patch-note timer announcements

This note records timer rules stated in the linked official FFXIV 1.x patch
notes. They are first-party announcements of intended behavior, not proof of
the installed 1.23b client's runtime state or server policy. The local
Lodestone transcription does not contain these later numbered patch-note pages;
the links below are direct source pages, not archive transcriptions.

## Announced rules

- **Patch 1.18:** The notes say Behest participants must wait before
  participating again and that the wait is visible on the Attributes tab's
  Timers subcommand ([Behest changes][patch-118]).
- **Patch 1.19:** The notes specify a two-minute Behest signup wait after a
  successful participation and one minute after a failure, measured from the
  next recruitment start. The Ifrit battle has a fifteen-minute wait after
  success and five minutes after failure ([Behest and Ifrit changes][patch-119]).
- **Patch 1.21:** Aurum Vale and Cutter's Cry are listed with a fifteen-minute
  wait after clearing and five minutes after failure; voluntarily leaving
  applies a fifteen-minute wait ([dungeon changes][patch-121]).
- **Patch 1.22b:** The notes say the next beastman-strike timer is shown in
  Timers after the player has participated in Hamlet Defense at least once.
  The wording does not identify a specific Hamlet or say that participation
  immediately initializes a particular row ([Hamlet Defense changes][patch-122b]).
- **Patch 1.23:** Skirmish is announced for level 45 or higher, with four to
  eight players, all party members at least level 45 and fully enlisted, a
  thirty-minute duration, and a fifteen-minute wait after victory or five
  minutes after defeat. This page does not state a timer first-appearance
  condition ([Skirmish changes][patch-123]).
- **Patch 1.23a:** Completing "Living on a Prayer" unlocks Rivenroad and
  Rivenroad (Hard) as repeatable battles; the Hard battle lists fifteen
  minutes after victory and five after defeat ([Rivenroad changes][patch-123a]).
- **Patch 1.23b:** The reviewed [Patch 1.23b Notes][patch-123b] announce
  Atomos and other content changes and known issues; the page has no timer,
  Rivenroad, or Skirmish section. That page-scoped omission does not establish
  that no related change appeared elsewhere.

## Evidence boundary

The [client timer-consumer inventory][client-timers] records recovered
client-side display consumers. The patch notes add
historical announcements, but do not identify the 1.23b native timer unit,
producer, exact initialization event, active server rule, or runtime value for
each widget row. Contributor-server reports about first nonzero values,
commands, and relog behavior remain implementation claims unless independently
supported by retail evidence.

In particular, the 1.22b wording supports a minimum participation condition
for timer visibility; it does not prove that a Hamlet Defense immediately
discovers that Hamlet's timer. The 1.23 Skirmish announcement does not supply
an equivalent first-appearance rule. Neither gap is resolved by the installed
client's timer consumers.

## Sources

- [Patch 1.18 Notes][patch-118] - Behest changes.
- [Patch 1.19 Notes][patch-119] - Behest and Ifrit battle changes.
- [Patch 1.21 Notes][patch-121] - instanced dungeon changes.
- [Patch 1.22b Notes][patch-122b] - Hamlet Defense timer visibility.
- [Patch 1.23 Notes][patch-123] - Skirmish requirements and waits.
- [Patch 1.23a Notes][patch-123a] - Rivenroad requirements and waits.
- [Patch 1.23b Notes][patch-123b] - Atomos, content changes, and known issues.
- [MyPlayer timer consumers][client-timers] - recovered client-side consumers.

[patch-118]: https://forum.square-enix.com/ffxiv/threads/17007-patch1.18-Patch-1.18-Notes
[patch-119]: https://forum.square-enix.com/ffxiv/threads/24910-patch1.19-Patch-1.19-Notes
[patch-121]: https://forum.square-enix.com/ffxiv/threads/39024-patch1.21-Patch-1.21-Notes?p=580985&viewfull=1
[patch-122b]: https://forum.square-enix.com/ffxiv/threads/47128?langid=2
[patch-123]: https://forum.square-enix.com/ffxiv/threads/50278-patch1.23-Patch-1.23-Notes
[patch-123a]: https://forum.square-enix.com/ffxiv/threads/51545
[patch-123b]: https://forum.square-enix.com/ffxiv/threads/54142
[client-timers]: https://github.com/XIVLegacy/xivl-client-scripts/blob/main/docs/myplayer-timer-consumers.md
