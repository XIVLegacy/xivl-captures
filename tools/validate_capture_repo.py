"""Validate manifests, storage policy, catalog coverage, and hint recall."""

from __future__ import annotations

import argparse
import os
import hashlib
import re
import sys
from pathlib import Path

import yaml

from restricted_paths import EXCLUDED_DERIVED_IDS

CORPUS_ABSENT = os.environ.get("XIVL_CORPUS_ABSENT") == "1"

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[1]

VALID_STATUSES = {"indexed", "distilled", "validated", "raw-only"}
# Referenced sources are checked when present; local-only pointers are never checked.
VALID_ORIGINAL_STATES = {"in-repo", "cold-stored", "cold-storage-pending",
                         "referenced-sibling", "local-only"}

# Leve scope and objectives are tags; discipline determines content kind.
VALID_CONTENT_KINDS = {
    "main-scenario",
    "main-scenario-battle",
    "side-quest",
    "class-quest",
    "job-quest",
    "grand-company-quest",
    "battlecraft-leve",
    "tradecraft-leve",
    "fieldcraft-leve",
    "behest",
    "notorious-monster",
    # Hamlet defense covers the three instanced settlement raids.
    "instanced-dungeon",
    "primal-battle",
    "hamlet-defense",
    "skirmish-battle",
    "crafting-synthesis",
    "gathering-node",
    "fishing-node",
    "npc-interaction",
    "zone-mechanic",
    "inventory-mechanic",
    "shop-vendor",
    "player-economy",
    "aetheryte-mechanic",
    "chocobo-mechanic",
    "battle-regimen",
    "status-effect-mechanic",
    "action-mechanic",
    "materia-mechanic",
    # Packet scenarios classify the exercised client subsystem.
    "session-mechanic",
    "chat-mechanic",
    "social-mechanic",
    "movement-mechanic",
    "character-mechanic",
    "emote-mechanic",
    "cutscene-mechanic",
}
VALID_SYSTEMS = {
    "guildleve",
    "behest",
    "grand-company",
    "battle-regimen",
    "aetheryte-travel",
    "hamlet-defense",
    "instanced-content",
    "materia",
    "chocobo",
    "player-economy",
    "surplus-fatigue",
}
# Ishgard was not a playable city-state in 1.23b and is intentionally excluded.
VALID_CITY_STATES = {
    "limsa-lominsa",
    "gridania",
    "uldah",
}
VALID_GRAND_COMPANIES = {
    "maelstrom",
    "twin-adder",
    "immortal-flames",
}
# 1.23b progression includes Artifact gear for the seven soul-crystal jobs.
VALID_PROGRESSION_TRACKS = {
    "class-rank",
    "physical-level",
    "class-quest",
    "job-quest",
    "artifact-gear",
    "grand-company-rank",
}


def validate_taxonomy_fields(scope: str, entry_id: str, entry: dict, errors: list[str]) -> None:
    """Validate optional taxonomy fields and attribute errors to ``scope``."""
    content_kind = entry.get("content_kind")
    if content_kind is not None and content_kind not in VALID_CONTENT_KINDS:
        errors.append(f"{scope}/{entry_id}: invalid content_kind `{content_kind}`")

    system = entry.get("system")
    if system is not None and system not in VALID_SYSTEMS:
        errors.append(f"{scope}/{entry_id}: invalid system `{system}`")

    city_state = entry.get("city_state")
    if city_state is not None and city_state not in VALID_CITY_STATES:
        errors.append(f"{scope}/{entry_id}: invalid city_state `{city_state}`")

    grand_company = entry.get("grand_company")
    if grand_company is not None and grand_company not in VALID_GRAND_COMPANIES:
        errors.append(f"{scope}/{entry_id}: invalid grand_company `{grand_company}`")

    progression_track = entry.get("progression_track")
    if progression_track is not None and progression_track not in VALID_PROGRESSION_TRACKS:
        errors.append(
            f"{scope}/{entry_id}: invalid progression_track `{progression_track}`"
        )

    zones = entry.get("zones")
    if zones is not None:
        if not isinstance(zones, list):
            errors.append(f"{scope}/{entry_id}: zones must be a list")
        else:
            for index, zone in enumerate(zones):
                if not isinstance(zone, str) or not zone.strip():
                    errors.append(
                        f"{scope}/{entry_id}: zones[{index}] must be a non-empty string"
                    )

    tags = entry.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            errors.append(f"{scope}/{entry_id}: tags must be a list")
        else:
            for index, tag in enumerate(tags):
                if not isinstance(tag, str) or not tag.strip():
                    errors.append(
                        f"{scope}/{entry_id}: tags[{index}] must be a non-empty string"
                    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate xivl-captures retention and path policy.")
    parser.add_argument(
        "--check-storage",
        action="store_true",
        help="Also validate locally configured cold-storage paths for sources/*.",
    )
    parser.add_argument(
        "--recall",
        action="store_true",
        help="Advisory: report search_hints/tags recall against evidence-map.md anchors "
        "(NPC/enemy/item names, Event/Message refs). Does not fail the build.",
    )
    parser.add_argument(
        "--recall-show",
        type=int,
        default=40,
        help="With --recall, number of worst-covered captures to list (default 40).",
    )
    parser.add_argument(
        "--recall-verbose",
        action="store_true",
        help="With --recall, list every missing anchor for every capture with gaps.",
    )
    parser.add_argument(
        "--recall-json",
        action="store_true",
        help="With --recall, emit per-capture missing anchors as JSON (for tooling/audit).",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_storage_root(repo_root: Path, storage_id: str, local_config: dict | None) -> Path | None:
    if storage_id in ("repo", "repo-lfs"):
        return repo_root
    if not local_config:
        return None
    storage = local_config.get("storages", {}).get(storage_id)
    if not storage:
        return None
    base_path = storage.get("base_path")
    if not base_path:
        return None
    return Path(base_path)


def validate_study(
    repo_root: Path,
    manifest_path: Path,
    errors: list[str],
) -> None:
    manifest = load_yaml(manifest_path)
    study_dir = manifest_path.parent
    study_id = manifest.get("id", study_dir.name)
    status = manifest.get("status")

    if status not in VALID_STATUSES:
        errors.append(f"{study_id}: invalid status `{status}`")

    validate_taxonomy_fields("studies", study_id, manifest, errors)

    for relative_path in manifest.get("primary_paths", []):
        target = study_dir / relative_path
        if not target.exists():
            errors.append(f"{study_id}: missing primary path `{relative_path}`")

    source_refs = manifest.get("source_refs") or []
    for ref in source_refs:
        source_id = ref.get("source") if isinstance(ref, dict) else None
        if not source_id:
            errors.append(f"{study_id}: source_refs entry missing `source`")
            continue
        source_manifest = repo_root / "sources" / source_id / "manifest.yaml"
        if not source_manifest.exists():
            errors.append(
                f"{study_id}: source_refs `{source_id}` does not resolve to "
                f"sources/{source_id}/manifest.yaml"
            )

    distilled = manifest.get("distilled")
    if distilled is None:
        return
    if not isinstance(distilled, dict):
        errors.append(f"{study_id}: `distilled` must be a mapping")
        return

    is_distilled = distilled.get("distilled")
    if is_distilled is not None and not isinstance(is_distilled, bool):
        errors.append(f"{study_id}: distilled.distilled must be true or false")
    if status in {"distilled", "validated"} and not is_distilled:
        errors.append(f"{study_id}: status `{status}` requires distilled.distilled=true")

    distilled_artifacts = distilled.get("distilled_artifacts") or []
    if is_distilled:
        if not distilled_artifacts:
            errors.append(f"{study_id}: distilled study is missing distilled.distilled_artifacts entries")
        for relative_path in distilled_artifacts:
            target = study_dir / relative_path
            if not target.exists():
                errors.append(f"{study_id}: missing distilled artifact `{relative_path}`")


def validate_source(
    repo_root: Path,
    manifest_path: Path,
    check_storage: bool,
    local_config: dict | None,
    errors: list[str],
) -> None:
    manifest = load_yaml(manifest_path)
    source_dir = manifest_path.parent
    source_id = manifest.get("id", source_dir.name)
    storage = manifest.get("storage")

    if not isinstance(storage, dict):
        errors.append(f"{source_id}: missing storage block")
        return

    original_state = storage.get("original_state")
    storage_id = storage.get("storage_id")
    storage_path = storage.get("path")

    if original_state not in VALID_ORIGINAL_STATES:
        errors.append(f"{source_id}: invalid storage.original_state `{original_state}`")

    if original_state == "in-repo":
        if storage_id not in ("repo", "repo-lfs"):
            errors.append(
                f"{source_id}: in-repo storage should use storage_id `repo` (plain git) "
                "or `repo-lfs` (actual LFS object)"
            )
        objects_dir = source_dir / "objects"
        if not objects_dir.is_dir() and not CORPUS_ABSENT:
            errors.append(f"{source_id}: in-repo source is missing an objects/ dir")

    if original_state == "cold-stored":
        if not storage_id or storage_id in ("repo", "repo-lfs"):
            errors.append(f"{source_id}: cold-stored originals require a non-repo storage_id")
        if not storage_path:
            errors.append(f"{source_id}: cold-stored originals require storage.path")

        if check_storage and storage_id and storage_path:
            storage_root = resolve_storage_root(repo_root, storage_id, local_config)
            if storage_root is None:
                errors.append(f"{source_id}: storage_id `{storage_id}` could not be resolved locally")
            else:
                target = storage_root / storage_path
                if not target.exists():
                    errors.append(f"{source_id}: cold-stored file `{target}` is missing")
                else:
                    # Cold-stored member hashes verify the restored file directly.
                    members = manifest.get("members") or []
                    if len(members) == 1:
                        actual = sha256_file(target)
                        expected = members[0].get("sha256")
                        if expected and actual != expected:
                            errors.append(
                                f"{source_id}: cold-stored file `{target}` sha256 mismatch "
                                f"(manifest {expected}, disk {actual})"
                            )
                    elif len(members) > 1:
                        errors.append(
                            f"{source_id}: cold-stored source has {len(members)} members; "
                            "expected exactly 1 to hash-verify against the single cold file"
                        )

    if original_state == "local-only":
        # Local-only pointers are documentary and may be absent.
        pass

    if original_state == "referenced-sibling":
        # Verify a referenced source only when its checkout is present.
        if not storage_id or storage_id in ("repo", "repo-lfs"):
            errors.append(f"{source_id}: referenced-sibling originals require a non-repo storage_id")
        if not storage_path:
            errors.append(f"{source_id}: referenced-sibling originals require storage.path")
        else:
            target = source_dir / storage_path
            if target.parent.exists() and not target.exists():
                errors.append(f"{source_id}: referenced sibling path `{storage_path}` is missing")


def validate_catalog(
    repo_root: Path,
    study_paths: list[Path],
    source_paths: list[Path],
    scenario_ids: set[str],
    dataset_ids: set[str],
    errors: list[str],
) -> None:
    catalog_path = repo_root / "catalog" / "index.yaml"
    catalog = load_yaml(catalog_path) or {}

    def check_section(section: str, disk_ids: set[str]) -> None:
        entries = catalog.get(section) or []
        catalog_ids: set[str] = set()
        for entry in entries:
            entry_id = entry.get("id", "<unknown>")
            if entry_id in catalog_ids:
                errors.append(f"catalog/{section}/{entry_id}: duplicate id")
            catalog_ids.add(entry_id)
            if section == "studies":
                validate_taxonomy_fields("catalog-study", entry_id, entry, errors)
                for relative_path in entry.get("primary_paths", []):
                    target = repo_root / relative_path
                    if not target.exists():
                        errors.append(f"catalog/{section}/{entry_id}: missing primary path `{relative_path}`")
            if section == "scenarios":
                validate_taxonomy_fields("catalog-scenario", entry_id, entry, errors)

        for missing in sorted(disk_ids - catalog_ids):
            errors.append(f"catalog/{section}: `{missing}` exists on disk but has no catalog entry")
        for missing in sorted(catalog_ids - disk_ids):
            errors.append(f"catalog/{section}: entry `{missing}` has no matching item on disk")

    study_ids = {p.parent.name for p in study_paths}
    source_ids = {p.parent.name for p in source_paths}
    dataset_ids = dataset_ids - EXCLUDED_DERIVED_IDS
    check_section("studies", study_ids)
    check_section("sources", source_ids)
    check_section("scenarios", scenario_ids)
    check_section("derived", dataset_ids)


# Advisory recall filters FFXIV 1.0 evidence-map anchors.

_BACKTICK = re.compile(r"`([^`]+)`")
# Negative-claim sections must not contribute search anchors.
_GAPS_HEADING = re.compile(
    r"^#{1,6}\s*(gaps?|negative|not\s+(covered|in|present)|"
    r"limitations?|caveats?|missing|absent|out\s+of\s+scope)\b", re.I)
_ARTICLE = re.compile(r"^(a|an|the)\s+", re.I)
# Event variants collapse to ``event N``; other namespaces remain distinct.
_EVENT_REF = re.compile(r"^(events?(?:\s*para|\s*update)?|messages?|mes(?:sage)?num|msgnum|opcodes?|csid|cs)\s*(\d+)$", re.I)
# Split compound names and references before classification.
_COMPOUND = re.compile(r"^(.+?)\s+(events?|messages?|opcodes?|csid|cs)\s*(\d+)$", re.I)
_OPTION_REF = re.compile(r"^options?\s*\d+$", re.I)
_PARAM_REF = re.compile(
    r"^(endpara|startpara|params?|id|idx|index|frame|seq|lv|lvl|level|"
    r"messagenumber|messagenum|mesnum|msgnum|msg|actindex|act|eventnum|"
    r"mode|animationsub|animation|anim|cat|category)\.?\s*\d+$", re.I)
_TRAILING_ID = re.compile(r"\s+\d{6,}$")
_RANGE_REF = re.compile(r"^(events?|options?|messages?|opcodes?)\s*\d+\s*-\s*\d+$", re.I)
_VERSION = re.compile(r"^[a-z]+\s+[\d]+(\.\d+)+$", re.I)
_RECOVERS = re.compile(r"^.+\s+recovers?\s+\d+\s+(mp|hp|tp)$", re.I)
# Capture-tool names are not game-content anchors.
_TOOL_REF = re.compile(
    r"^(packetlog(?:ger)?|packetdb|opcodelog|chatlog|hexdump|pcap|wireshark|"
    r"actionlog|combatlog|info)(\s+v?\d{1,3})?$", re.I)
_MAP_GRID = re.compile(r"^[A-Za-z]-\d{1,2}$")
# Combat-log outcomes are not search anchors.
_LOG_TAIL = {"boost", "up", "down", "resists", "resist", "resisted",
             "recovers", "recover", "recovered", "misses", "miss", "missed",
             "evades", "evade", "evaded", "parries", "parry", "parried",
             "blocks", "block", "blocked", "absorbs", "absorb", "absorbed",
             "gains", "gain", "loses", "lose", "regains", "regain",
             "suppressed", "enhanced", "incapacitated", "defeated", "engaged",
             "dealt"}
_NAME_OK = re.compile(r"^[A-Za-z][A-Za-z0-9 ':.\-]*$")
_COORD = re.compile(r"[xyz]\s*=\s*-?\d")
_HEX = re.compile(r"0x[0-9A-Fa-f]+$|[0-9A-Fa-f]{16,}$")
_MONTHS = {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"}

# Tool words remain noise even below the document-frequency threshold.
_TOOL_WORDS = {
    "waypoint", "packetlog", "packet log", "opcode", "opcodes", "chatlog",
    "chat log", "combatlog", "combat log", "actionlog", "hexdump", "pcap",
    "worldmaster", "world master", "subpacket", "sub packet", "no effect",
    "zone dump", "zonedump", "packets", "zones", "zone", "history",
}

# Exact generic-family matches are noise; specific names containing them survive.
_GENERIC = {
    "amalj'aa", "amaljaa", "ixal", "ixali", "kobold", "sylph", "qiqirn",
    "goblin",
    "puk", "raptor", "antelope", "hippogryph", "opo-opo", "gnat", "basilisk",
    "buffalo", "sabotender", "morbol", "crab", "vulture", "salamander", "wolf",
    "hyena", "hellhound", "boar", "bomb", "ahriman", "zombie", "wight",
    "cockatrice", "coblyn", "drake", "aldgoat", "juggernaut", "ogre", "imp",
    "flytrap", "treant", "apkallu", "antling", "gigantoad", "coeurl", "goobbue",
    "flan", "gargoyle", "wyvern", "weevil", "rat", "bat", "slug", "ghost",
    "phurble", "angler", "elemental", "swarm", "jellyfish", "yarzon", "chigoe",
    "hedgemole", "firefly", "funguar", "sheep", "spriggan", "dragon", "golem",
    "dodo", "marmot", "ladybug",
    "aetheryte", "treasure coffer", "gate", "campfire", "levemete",
}

# Lowercase prose words distinguish log fragments from proper names.
_PROSE_WORDS = {
    "has", "have", "is", "are", "was", "were", "will", "appears", "appear",
    "using", "obtained", "nothing", "here", "this", "that", "you", "your",
    "out", "ordinary", "cannot", "does", "do", "it", "they", "there", "but",
    "chatlog",
    "absorb", "absorbs", "anticipate", "anticipates", "attack", "attacks",
    "begin", "begins", "belong", "belongs", "block", "blocks", "bound", "call",
    "calls", "cast", "casting", "casts", "counter", "cover", "covers",
    "critical", "damage", "dealt", "defeat", "defeated", "defeats", "disrupt",
    "disrupts", "duty", "effect", "engaged", "evade", "evades", "expend",
    "expends", "fail", "fails", "fall", "falls", "fold", "gain", "gains",
    "heals", "hit", "hits", "incapacitated", "interrupt", "interrupts", "join",
    "joins", "leave", "leaves", "lose", "loses", "miss", "misses", "parries",
    "parry", "point", "points", "ready", "readies", "recover", "recovers",
    "regain", "regains", "resist", "resists", "steal", "steals", "switch",
    "switches", "take", "takes", "taking", "use", "uses", "vanish", "vanishes",
}


def _load_action_vocab(repo_root: Path) -> set[str]:
    """Load normalized action names. An absent advisory vocabulary suppresses nothing."""
    path = repo_root / "tools" / "ffxiv-action-names.txt"
    if not path.is_file():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def _norm_term(text: str) -> str:
    return re.sub(r"[\s_]+", " ", str(text).strip().lower())


def _tight(text: str) -> str:
    """Collapse punctuation and spacing variants for comparison."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _split_gaps(text: str) -> str:
    """Remove negative-claim sections before extracting anchors."""
    lines = text.splitlines()
    kept, in_gaps = [], False
    for line in lines:
        if re.match(r"^#{1,6}\s", line):
            in_gaps = bool(_GAPS_HEADING.match(line))
        if not in_gaps:
            kept.append(line)
    return "\n".join(kept)


def _classify_term(token: str) -> tuple[str | None, str]:
    """Classify a backtick token as a name, reference, or noise."""
    ts = token.strip()
    if not ts:
        return None, ""
    # Match glued annotations before splitting CamelCase names.
    m = _EVENT_REF.match(ts)
    if m:
        prefix = m.group(1).lower().replace(" ", "")
        kind = "event" if prefix.startswith("event") else "message" if (prefix.startswith("mes") or prefix.startswith("msg")) else "opcode" if prefix.startswith("opcode") else prefix
        return "ref", "%s %s" % (kind, m.group(2))
    if _OPTION_REF.match(ts) or _PARAM_REF.match(ts) or _RANGE_REF.match(ts):
        return None, ""
    if _TOOL_REF.match(ts):
        return None, ""
    if _VERSION.match(ts) or _RECOVERS.match(ts):
        return None, ""
    if "..." in ts:
        return None, ""
    ts = _TRAILING_ID.sub("", ts)
    if _MAP_GRID.match(ts):
        return None, ""
    if re.fullmatch(r"\d+", ts):
        return None, ""
    if _COORD.search(ts):
        return None, ""
    if re.fullmatch(r"[-\d.,\s]+", ts):
        return None, ""
    if ts[:3].lower() in _MONTHS and re.search(r"\b(19|20)\d\d\b", ts):
        return None, ""
    if "/" in ts or ts.endswith((".zip", ".log", ".lua", ".sqlite", ".csv",
                                 ".md", ".txt", ".db", ".json", ".dat", ".bin")):
        return None, ""
    if _HEX.match(ts):
        return None, ""
    # Split CamelCase only when every piece is long enough to exclude acronyms.
    if " " not in ts and re.search(r"[a-z][A-Z]", ts):
        pieces = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", ts).split()
        if all(len(p) >= 2 for p in pieces):
            ts = " ".join(pieces)
    if not _NAME_OK.match(ts):
        return None, ""
    if not any(c.isupper() for c in ts):
        return None, ""
    words = ts.split()
    if len(words) > 6 or ts.endswith("."):
        return None, ""
    if ":" in ts:
        return None, ""
    if len(words) >= 2 and words[-1].lower() in _LOG_TAIL:
        return None, ""
    if "npc" in (w.lower() for w in words):
        return None, ""
    if any(w.lower() in _PROSE_WORDS for w in words):
        return None, ""
    norm = _norm_term(ts)
    if norm in _TOOL_WORDS:
        return None, ""
    if norm in _GENERIC:
        return None, ""
    return "name", norm


def _set_terms(text: str) -> tuple[set[str], set[str]]:
    names: set[str] = set()
    refs: set[str] = set()
    for token in _BACKTICK.findall(_split_gaps(text)):
        ts = token.strip()
        compound = _COMPOUND.match(ts)
        if compound and not _EVENT_REF.match(ts):
            head_kind, head_norm = _classify_term(compound.group(1))
            if head_kind == "name":
                names.add(head_norm)
            pfx = compound.group(2).lower()
            kind = "event" if pfx.startswith("event") else "message" if (pfx.startswith("mes") or pfx.startswith("msg")) else "opcode" if pfx.startswith("opcode") else pfx
            refs.add("%s %s" % (kind, compound.group(3)))
            continue
        kind, norm = _classify_term(ts)
        if kind == "name":
            names.add(norm)
        elif kind == "ref":
            refs.add(norm)
    return names, refs


def _hint_covers(hints: list[str], term: str) -> bool:
    """Return whether hints cover a term under supported normalization."""
    cands = {term}
    stripped = _ARTICLE.sub("", term)
    if stripped:
        cands.add(stripped)
    for c in cands:
        if any(c == h or c in h or h in c for h in hints):
            return True
    cand_keys = {_tight(c) for c in cands if _tight(c)}
    return any(_tight(h) in cand_keys for h in hints)


def validate_search_hints_recall(
    repo_root: Path, df_max: int | None = None, worst: int = 40,
    verbose: bool = False, as_json: bool = False,
) -> None:
    catalog = load_yaml(repo_root / "catalog" / "index.yaml") or {}
    entries: dict[str, dict] = {}
    for entry in catalog.get("studies") or []:
        entries[entry.get("id")] = entry
    for entry in catalog.get("scenarios") or []:
        entries[entry.get("id")] = entry
    action_vocab = _load_action_vocab(repo_root)

    evidence: dict[str, str] = {}
    for path in sorted((repo_root / "studies").glob("*/derived/evidence-map.md")):
        evidence[path.parent.parent.name] = path.read_text(encoding="utf-8", errors="replace")
    for path in sorted((repo_root / "catalog" / "scenarios").glob("*/evidence-map.md")):
        evidence[path.parent.name] = path.read_text(encoding="utf-8", errors="replace")

    if not evidence:
        print("search_hints recall (advisory): no evidence-map.md files yet - nothing to check.")
        return

    # Ubiquitous names cannot distinguish a capture.
    doc_freq: dict[str, int] = {}
    for text in evidence.values():
        for name in _set_terms(text)[0]:
            doc_freq[name] = doc_freq.get(name, 0) + 1
    if df_max is None:
        df_max = max(15, round(0.03 * len(evidence)))

    # Score names separately from secondary event and message references.
    rows: list[tuple[int, str, list[str], list[str]]] = []
    name_total = name_covered = 0
    ref_total = ref_covered = 0
    perfect_names = no_entry = 0
    for capture_id, text in sorted(evidence.items()):
        entry = entries.get(capture_id)
        if entry is None:
            no_entry += 1
            continue
        # Tags are the fallback only when computed search hints are absent.
        raw_hints = entry.get("search_hints") if entry.get("search_hints") is not None else entry.get("tags")
        hints = [_norm_term(h) for h in (raw_hints or [])]
        names, refs = _set_terms(text)
        # Actions and ubiquitous names do not identify a capture.
        names = {n for n in names if n not in action_vocab and doc_freq.get(n, 0) <= df_max}
        miss_names = sorted(n for n in names if not _hint_covers(hints, n))
        miss_refs = sorted(r for r in refs if not _hint_covers(hints, r))
        name_total += len(names); name_covered += len(names) - len(miss_names)
        ref_total += len(refs); ref_covered += len(refs) - len(miss_refs)
        if names and not miss_names:
            perfect_names += 1
        if miss_names or miss_refs:
            rows.append((len(miss_names), capture_id, miss_names, miss_refs))

    rows.sort(key=lambda r: (-r[0], -len(r[3]), r[1]))
    name_pct = (100.0 * name_covered / name_total) if name_total else 100.0
    ref_pct = (100.0 * ref_covered / ref_total) if ref_total else 100.0
    name_gaps = sum(1 for r in rows if r[0])

    if as_json:
        import json
        payload = {
            "df_max": df_max,
            "evidence_maps": len(evidence),
            "names": {"total": name_total, "covered": name_covered, "pct": round(name_pct, 1)},
            "refs": {"total": ref_total, "covered": ref_covered, "pct": round(ref_pct, 1)},
            "captures": [
                {"id": capture_id, "missing_names": miss_names, "missing_refs": miss_refs}
                for _, capture_id, miss_names, miss_refs in rows
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    print("search_hints recall (advisory) - evidence-map.md anchors covered by search_hints/tags")
    print(f"  corpus: {len(evidence)} evidence-maps (DF suppression > {df_max} captures)")
    print(f"  NAMES (NPC/enemy/item): {name_covered}/{name_total} covered ({name_pct:.1f}%), "
          f"{perfect_names} captures complete, {name_gaps} with name gaps")
    print(f"  EVENT/MSG refs:         {ref_covered}/{ref_total} covered ({ref_pct:.1f}%)")
    if no_entry:
        print(f"  note: {no_entry} evidence-maps have no catalog entry (skipped)")
    shown = rows if verbose else rows[:worst]
    for _, capture_id, miss_names, miss_refs in shown:
        names_show = miss_names if verbose else miss_names[:15]
        more = "" if verbose or len(miss_names) <= 15 else f" (+{len(miss_names) - 15} more)"
        print(f"\n  {capture_id}")
        if miss_names:
            print(f"    missing names ({len(miss_names)}){more}: " + ", ".join(names_show))
        if miss_refs:
            refs_show = miss_refs if verbose else miss_refs[:8]
            rmore = "" if verbose or len(miss_refs) <= 8 else f" (+{len(miss_refs) - 8} more)"
            print(f"    missing refs ({len(miss_refs)}){rmore}: " + ", ".join(refs_show))
    if not verbose and len(rows) > worst:
        print(f"\n  ... {len(rows) - worst} more captures with gaps (use --recall-verbose)")


def main() -> int:
    args = parse_args()
    repo_root = REPO_ROOT_DEFAULT
    if args.recall:
        validate_search_hints_recall(
            repo_root, worst=args.recall_show, verbose=args.recall_verbose,
            as_json=args.recall_json,
        )
        return 0
    local_config_path = repo_root / "config" / "cold-storage.local.yaml"
    local_config = load_yaml(local_config_path) if local_config_path.exists() else None

    errors: list[str] = []

    study_paths = sorted((repo_root / "studies").glob("*/manifest.yaml"))
    for manifest_path in study_paths:
        validate_study(repo_root=repo_root, manifest_path=manifest_path, errors=errors)

    source_paths = sorted((repo_root / "sources").glob("*/manifest.yaml"))
    for manifest_path in source_paths:
        validate_source(
            repo_root=repo_root,
            manifest_path=manifest_path,
            check_storage=args.check_storage,
            local_config=local_config,
            errors=errors,
        )

    pcap_manifest_path = repo_root / "sources" / "pcap-1.23b" / "manifest.yaml"
    scenario_ids: set[str] = set()
    if pcap_manifest_path.exists():
        pcap_manifest = load_yaml(pcap_manifest_path) or {}
        scenario_ids = {s["id"] for s in (pcap_manifest.get("scenarios") or [])}

    dataset_ids = {
        (load_yaml(p) or {}).get("dataset", p.name[: -len(".meta.yaml")])
        for p in sorted((repo_root / "derived").glob("*.meta.yaml"))
    }

    validate_catalog(repo_root, study_paths, source_paths, scenario_ids, dataset_ids, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Validated {len(study_paths)} studies, {len(source_paths)} sources, "
          f"{len(scenario_ids)} scenarios, {len(dataset_ids)} derived.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
