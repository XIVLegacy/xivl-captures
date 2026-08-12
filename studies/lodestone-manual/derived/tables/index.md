# Tables index

Normalized CSVs pulled from the manual's inline data tables, built from the
rowspan-aware HTML grids (the Markdown flatten dropped some anchor rows, so
these are re-extracted from source for accuracy). Every row carries a
`source_page` column keyed to `../file-inventory.csv` (slug -> Lodestone URL).
Compatibility markers in the source (filled circle) are normalized to yes/no.

| CSV | rows | columns | source page(s) |
|---|---|---|---|
| [achievement-npcs.csv](achievement-npcs.csv) | 14 | category, npc, location | achievements-and-titles |
| [aetherial-transport.csv](aetherial-transport.csv) | 24 | city, destination, location, npc | getting-around |
| [classes.csv](classes.csv) | 18 | class, discipline, arms_or_tools_required, details | classes-and-jobs |
| [configuration-options.csv](configuration-options.csv) | 46 | category, option, description | configuration |
| [display-name-colors.csv](display-name-colors.csv) | 7 | display_name_color, meaning | the-game-screen |
| [emotes.csv](emotes.csv) | 53 | command, aliases, description | text-commands-and-macros |
| [grand-company-ranks.csv](grand-company-ranks.csv) | 9 | rank_index, commission_tier, maelstrom_rank, twin_adder_rank, immortal_flames_rank, requirement | grand-company-guide |
| [incapacitation-monster-parts.csv](incapacitation-monster-parts.csv) | 20 | monster, body_part, breakable_part | effect-inducing-tactics |
| [incapacitation-weaponskills.csv](incapacitation-weaponskills.csv) | 15 | weapon, body_part, weaponskill | effect-inducing-tactics |
| [job-crossclass-action-sources.csv](job-crossclass-action-sources.csv) | 7 | job, crossclass_action_sources | classes-and-jobs |
| [jobs.csv](jobs.csv) | 7 | job, base_class, details_and_requirements | classes-and-jobs |
| [keyboard-controls.csv](keyboard-controls.csv) | 96 | function, type_a, type_b | controlling-your-character |
| [main-menu.csv](main-menu.csv) | 33 | option, function | menus |
| [materia-catalysts.csv](materia-catalysts.csv) | 12 | gathering_class, catalyst, area | materia |
| [materia-grades.csv](materia-grades.csv) | 6 | operation, item_level_range, grade_i, grade_ii, grade_iii, grade_iv | materia |
| [path-companions.csv](path-companions.csv) | 9 | path_companion, description | quests |
| [repair-costs.csv](repair-costs.csv) | 5 | item_level_range, commission_gil, dark_matter_required | repair |
| [text-commands.csv](text-commands.csv) | 68 | command, aliases, parameters, description | text-commands-and-macros |
| [text-macro-placeholders.csv](text-macro-placeholders.csv) | 32 | placeholder, description | text-commands-and-macros |
