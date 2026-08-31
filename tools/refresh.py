#!/usr/bin/env python3
"""Validate or regenerate canonical products in dependency order.

``--check`` compares temporary regeneration without modifying the tree.
Promoted and frozen products are parse-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS = REPO_ROOT / "tools"
DATA = REPO_ROOT / "derived"
RESTRICTED_OBJECTS = Path(os.environ.get(
    "XIVL_PCAP_OBJECTS_DIR",
    str(REPO_ROOT / "sources" / "pcap-1.23b" / "objects"),
))

PCAP_PRODUCTS = [
    "observations.json",
    "lane_observations.json",
    "sequences.json",
    "timing.json",
    "payload_samples.json",
    "content_samples.json",
    "property_targets.json",
    "request_response_pairs.json",
    "gam_keys.json",
    "spawn_observations.json",
    "gam_hash_names.json",
    "payload_layouts.json",
]
# These are the deterministic products reproduced by the retail PCAP lane.
# Keep this list aligned with the checks below so its contract count has a
# producer rather than a hand-maintained literal.
VERIFIED_PRODUCTS = tuple(
    [f"derived/{name}" for name in PCAP_PRODUCTS]
    + [
        "derived/opcode_names.json",
        "derived/spawn_location_validation.json",
        "studies/battle-result-backfit/derived/distribution-summary.csv",
        "studies/battle-result-backfit/derived/matched-comparison-sets.csv",
        "studies/battle-result-backfit/derived/hp-recovery-clusters.csv",
        "studies/battle-result-backfit/derived/distribution-accounting.json",
        "studies/battle-result-backfit/derived/matched-set-ratios.csv",
        "studies/battle-result-backfit/derived/recovery-model-observations.csv",
        "studies/battle-result-backfit/derived/model-fit-accounting.json",
        "studies/director-wire-identity/derived/group-packets.csv",
        "studies/director-wire-identity/derived/group-members.csv",
        "studies/director-wire-identity/derived/event-role-candidates.csv",
        "studies/director-wire-identity/derived/accounting.json",
        "studies/guildleve-journal-command-wire/derived/command-matches.csv",
        "studies/guildleve-journal-command-wire/derived/accounting.json",
        "studies/regional-guildleve-publisher-contract/derived/timeline.csv",
        "studies/regional-guildleve-publisher-contract/derived/accounting.json",
        "studies/regional-guildleve-publisher-contract/derived/verdicts.md",
        "studies/property-stream-hash-catalog/derived/property-records.csv",
        "studies/property-stream-hash-catalog/derived/accounting.json",
        "studies/login-018a-neighborhood/derived/timeline.csv",
        "studies/login-018a-neighborhood/derived/accounting.json",
        "studies/map-00da-00e1-comparison/derived/occurrences.csv",
        "studies/map-00da-00e1-comparison/derived/neighborhoods.csv",
        "studies/map-00da-00e1-comparison/derived/accounting.json",
        "studies/map-00da-00e1-comparison/derived/verdicts.md",
        "studies/status-wire-projection-census/derived/occurrences.csv",
        "studies/status-wire-projection-census/derived/status-projections.csv",
        "studies/status-wire-projection-census/derived/accounting.json",
        "studies/status-wire-projection-census/derived/verdicts.md",
        "studies/party-marker-018d-chronology/derived/occurrences.csv",
        "studies/party-marker-018d-chronology/derived/marker-records.csv",
        "studies/party-marker-018d-chronology/derived/neighborhoods.csv",
        "studies/party-marker-018d-chronology/derived/accounting.json",
        "studies/party-marker-018d-chronology/derived/verdicts.md",
        "studies/party-marker-018d-chronology/derived/field-census.json",
        "studies/party-marker-018d-chronology/derived/row-reuse.csv",
        "studies/party-marker-018d-chronology/derived/field-verdicts.md",
        "studies/lobby-handshake-triage/derived/lobby-record-census.json",
    ]
)
UNIT_TEST_MODULES = (
    "tools.tests.test_analyze_battle_result_distributions",
    "tools.tests.test_analyze_battle_result_fits",
    "tools.tests.test_extract_battle_results",
    "tools.tests.test_extract_property_stream_catalog",
    "tools.tests.test_extract_player_hp_calibration",
    "tools.tests.test_extract_equipment_property_correlation",
    "tools.tests.test_extract_streams",
    "tools.tests.test_extract_login_018a_timeline",
    "tools.tests.test_extract_guildleve_journal_command",
    "tools.tests.test_extract_regional_guildleve_publisher_contract",
    "tools.tests.test_extract_00da_00e1_comparison",
    "tools.tests.test_extract_status_wire_census",
    "tools.tests.test_extract_party_marker_chronology",
    "tools.tests.test_analyze_party_marker_fields",
    "tools.tests.test_extract_0193_clock_contract",
    "tools.tests.test_extract_0190_transaction_census",
    "tools.tests.test_extract_world_party_chat_00c9",
    "tools.tests.test_extract_lobby_record_census",
)

# The three gate modes share these command-level checks. Product-specific
# stages remain below because their result rows combine related commands.
CHECK_PLANS = {
    "public": (
        ([TOOLS / "verify_retail_pcap.py", "--check-contract"], "retail PCAP contract", (("retail PCAP contract", "validate"),)),
        ([TOOLS / "validate_capture_repo.py", "--check-storage"], "public manifest/catalog cross-check", (("public manifest/catalog cross-check", "validate"),)),
        ([TOOLS / "check_markdown_links.py"], "public in-repo links", (("public in-repo links", "validate"),)),
        ([TOOLS / "audit_study_conventions.py"], "public study conventions", (("public study conventions", "validate"),)),
        ([TOOLS / "soften_source_links.py", "--check"], "public study source citations", (("public study source citations", "validate"),)),
        ([TOOLS / "build_checksums.py", "--check"], "public study checksums", (("public study checksums", "validate"),)),
        ([TOOLS / "build_catalog.py", "--check"], "public catalog chain", (
            ("public scenario views", "validate"),
            ("public catalog registry", "validate"),
            ("public catalog axes", "validate"),
        )),
        ([TOOLS / "validate_digestion.py", "--public-shape"], "public digestion references", (("public digestion references", "validate"),)),
        ([TOOLS / "validate_schemas.py"], "public schemas and boundaries", (("public schemas and boundaries", "validate"),)),
        ([TOOLS / "build_dataset_meta.py", "--check"], "public dataset metadata", (("public dataset metadata", "validate"),)),
    ),
    "check": (
        ([TOOLS / "verify_retail_pcap.py", "--check-contract"], "retail PCAP contract", (("retail PCAP contract", "validate"),)),
        ([TOOLS / "validate_capture_repo.py", "--check-storage"], "validate_capture_repo.py", (("validate_capture_repo.py (studies/sources/catalog cross-check)", "validate"),)),
        ([TOOLS / "check_markdown_links.py"], "check_markdown_links.py", (("check_markdown_links.py (in-repo link resolution)", "validate"),)),
        ([TOOLS / "audit_study_conventions.py"], "audit_study_conventions.py", (("audit_study_conventions.py (study README and manifest shape)", "validate"),)),
        ([TOOLS / "soften_source_links.py", "--check"], "soften_source_links.py --check", (("shipping study source citations", "validate"),)),
        ([TOOLS / "build_checksums.py", "--check"], "build_checksums.py --check", (("study derived/ checksum anchors", "regen"),)),
        ([TOOLS / "build_catalog.py", "--check"], "build_catalog.py --check", (
            ("pcap-reference scenario views", "regen"),
            ("catalog/index.yaml + catalog/aliases.yaml", "regen"),
            ("catalog/by-*.md axis views", "regen"),
        )),
    ),
    "check-post": (
        ([TOOLS / "validate_schemas.py"], "validate_schemas.py", (("validate_schemas.py (schemas/sources/data-meta/pipelines)", "validate"),)),
        ([TOOLS / "build_dataset_meta.py", "--check"], "build_dataset_meta.py --check", (("derived/*.meta.yaml sidecars", "regen"),)),
    ),
    "write": (
        ([TOOLS / "build_catalog.py"], "build_catalog.py", (
            ("pcap-reference scenario views", "write"),
            ("catalog/index.yaml + catalog/aliases.yaml", "write"),
            ("catalog/by-*.md axis views", "write"),
        )),
        ([TOOLS / "validate_capture_repo.py", "--check-storage"], "validate_capture_repo.py", (("validate_capture_repo.py (studies/sources/catalog cross-check)", "validate"),)),
        ([TOOLS / "check_markdown_links.py"], "check_markdown_links.py", (("check_markdown_links.py (in-repo link resolution)", "validate"),)),
        ([TOOLS / "soften_source_links.py"], "soften_source_links.py", (("shipping study source citations", "write"),)),
        ([TOOLS / "build_checksums.py"], "build_checksums.py", (("study derived/ checksum anchors", "write"),)),
    ),
    "write-post": (
        ([TOOLS / "build_dataset_meta.py"], "build_dataset_meta.py", (("derived/*.meta.yaml sidecars", "write"),)),
        ([TOOLS / "validate_schemas.py"], "validate_schemas.py", (("validate_schemas.py (schemas/sources/data-meta/pipelines)", "validate"),)),
    ),
}
PCAP_BUILDER = TOOLS / "build_pcap_products.py"
BATTLE_RESULT_DISTRIBUTIONS = TOOLS / "analyze_battle_result_distributions.py"
BATTLE_RESULT_FITS = TOOLS / "analyze_battle_result_fits.py"
DIRECTOR_WIRE_IDENTITY = TOOLS / "extractors" / "extract_director_wire_identity.py"
GUILDLEVE_JOURNAL_COMMAND = TOOLS / "extractors" / "extract_guildleve_journal_command.py"
REGIONAL_GUILDLEVE_PUBLISHER_CONTRACT = TOOLS / "extractors" / "extract_regional_guildleve_publisher_contract.py"
PROPERTY_STREAM_CATALOG = TOOLS / "extractors" / "extract_property_stream_catalog.py"
PLAYER_HP_CALIBRATION = TOOLS / "extractors" / "extract_player_hp_calibration.py"
EQUIPMENT_PROPERTY_CORRELATION = TOOLS / "extractors" / "extract_equipment_property_correlation.py"
LOGIN_018A_TIMELINE = TOOLS / "extractors" / "extract_login_018a_timeline.py"
MAP_00DA_00E1_COMPARISON = TOOLS / "extractors" / "extract_00da_00e1_comparison.py"
STATUS_WIRE_CENSUS = TOOLS / "extractors" / "extract_status_wire_census.py"
PARTY_MARKER_CHRONOLOGY = TOOLS / "extractors" / "extract_party_marker_chronology.py"
PARTY_MARKER_FIELDS = TOOLS / "analyze_party_marker_fields.py"
MAP_0193_CLOCK_CONTRACT = TOOLS / "extractors" / "extract_0193_clock_contract.py"
MAP_0190_TRANSACTION_CENSUS = TOOLS / "extractors" / "extract_0190_transaction_census.py"
WORLD_PARTY_CHAT_00C9_CONTRACT = TOOLS / "extractors" / "extract_world_party_chat_00c9.py"
LOBBY_RECORD_CENSUS = TOOLS / "extractors" / "extract_lobby_record_census.py"

# Promoted or frozen products are parse-only.
PARSE_ONLY_PRODUCTS = [
    ("spawn_location_validation.json", "frozen historical artifact"),
]
SUBPROCESS_TIMEOUT_SECONDS = 300

def run(cmd: list, label: str) -> bool:
    try:
        proc = subprocess.run(
            [sys.executable] + [str(c) for c in cmd],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(f"--- {label} output ---")
        print("subprocess timed out")
        print(f"--- end {label} output ---")
        return False
    ok = proc.returncode == 0
    out = (proc.stdout or "") + (proc.stderr or "")
    if not ok:
        print(f"--- {label} output ---")
        print(out.rstrip())
        print(f"--- end {label} output ---")
    return ok


def run_plan(mode: str, results: list[tuple[str, str, bool, str]]) -> None:
    for cmd, label, entries in CHECK_PLANS[mode]:
        ok = run(cmd, label)
        note = "" if ok else "see output above"
        for product, level in entries:
            results.append((product, level, ok, note))


def parse_only_check(name: str, reason: str, results: list) -> None:
    committed = DATA / name
    if not committed.exists():
        results.append((f"derived/{name}", "parse-only", False, f"{reason}; committed file missing"))
        return
    try:
        json.loads(committed.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        results.append((f"derived/{name}", "parse-only", False, f"{reason}; invalid JSON ({exc})"))
        return
    results.append((f"derived/{name}", "parse-only", True, reason))


def sidecar_hash_check(results: list) -> None:
    """Verify every retained sidecar points to the committed output bytes."""
    import yaml

    failures = []
    checked = 0
    for sidecar in sorted(DATA.glob("*.meta.yaml")):
        doc = yaml.safe_load(sidecar.read_text(encoding="utf-8")) or {}
        output = doc.get("output") or {}
        relative = output.get("file")
        expected = output.get("sha256")
        target = REPO_ROOT / relative if relative else None
        if target is None or not target.is_file():
            failures.append(f"{sidecar.name}: output missing")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f"{sidecar.name}: output sha256 mismatch")
        checked += 1
    results.append((
        "retained derived sidecar output hashes",
        "validate",
        not failures,
        "; ".join(failures) if failures else f"{checked} outputs verified",
    ))


def do_public_check() -> int:
    results: list[tuple[str, str, bool, str]] = []

    ok = run(["-m", "unittest", *UNIT_TEST_MODULES], "explicit unit tests")
    results.append(("explicit unit tests", "validate", ok, "" if ok else "see output above"))

    run_plan("public", results)

    ok = run([LOBBY_RECORD_CENSUS, "--check", "--public-shape"],
             "public decrypted lobby record census")
    results.append(("sanitized decrypted lobby record census", "validate", ok,
                    "" if ok else "public fixture validation failed"))

    for json_path in sorted(DATA.glob("*.json")):
        parse_only_check(json_path.name, "retained public product", results)
    sidecar_hash_check(results)

    ok = run([PCAP_BUILDER, "--check"], "public pcap products")
    for name in ("gam_hash_names.json", "payload_layouts.json"):
        results.append((f"derived/{name}", "regen", ok,
                        "" if ok else "regenerated bytes differ, see output above"))

    ok = run([PLAYER_HP_CALIBRATION, "--check"],
             "public player HP calibration anchors")
    results.append(("player HP calibration anchors", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run(
        [BATTLE_RESULT_DISTRIBUTIONS, "--check"],
        "public battle-result distributions",
    )
    results.append(("battle-result Stage 2 products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([BATTLE_RESULT_FITS, "--check"], "public battle-result fits")
    results.append(("battle-result Stage 3 products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    return report(results)


def do_check() -> int:
    results: list[tuple[str, str, bool, str]] = []

    ok = run(["-m", "unittest", *UNIT_TEST_MODULES], "explicit unit tests")
    results.append(("explicit unit tests", "validate", ok, "" if ok else "see output above"))

    run_plan("check", results)

    ok = run([PCAP_BUILDER, "--check"], "build_pcap_products.py --check")
    digestion_ok = run([TOOLS / "validate_digestion.py"], "validate_digestion.py")
    products_ok = ok and digestion_ok
    for name in PCAP_PRODUCTS:
        results.append((f"derived/{name}", "regen", products_ok,
                        "" if products_ok else "regeneration or digestion failed, see output above"))

    for name, reason in PARSE_ONLY_PRODUCTS:
        parse_only_check(name, reason, results)

    ok = run(
        [BATTLE_RESULT_DISTRIBUTIONS, "--check"],
        "analyze_battle_result_distributions.py --check",
    )
    results.append(("battle-result Stage 2 products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run(
        [BATTLE_RESULT_FITS, "--check"],
        "analyze_battle_result_fits.py --check",
    )
    results.append(("battle-result Stage 3 products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([DIRECTOR_WIRE_IDENTITY, "--check"],
                "extract_director_wire_identity.py --check")
    results.append(("director wire identity products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([GUILDLEVE_JOURNAL_COMMAND, "--check"],
             "extract_guildleve_journal_command.py --check")
    results.append(("guildleve journal command products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([REGIONAL_GUILDLEVE_PUBLISHER_CONTRACT, "--check"],
             "extract_regional_guildleve_publisher_contract.py --check")
    results.append(("regional guildleve publisher contract", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([PROPERTY_STREAM_CATALOG, "--check"],
                "extract_property_stream_catalog.py --check")
    results.append(("property-stream catalog products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([PLAYER_HP_CALIBRATION, "--check"],
             "extract_player_hp_calibration.py --check")
    results.append(("player HP calibration anchors", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([EQUIPMENT_PROPERTY_CORRELATION, "--check"],
             "extract_equipment_property_correlation.py --check")
    results.append(("equipment property correlation", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([LOGIN_018A_TIMELINE, "--check"],
             "extract_login_018a_timeline.py --check")
    results.append(("login 0x018A timeline products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([MAP_00DA_00E1_COMPARISON, "--check"],
             "extract_00da_00e1_comparison.py --check")
    results.append(("0x00DA/0x00E1 comparison products", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([STATUS_WIRE_CENSUS, "--check"],
             "extract_status_wire_census.py --check")
    results.append(("status wire projection census", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([PARTY_MARKER_CHRONOLOGY, "--check"],
             "extract_party_marker_chronology.py --check")
    results.append(("party marker 0x018D chronology", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([PARTY_MARKER_FIELDS, "--check"],
             "analyze_party_marker_fields.py --check")
    results.append(("party marker 0x018D field census", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([MAP_0193_CLOCK_CONTRACT, "--check"],
             "extract_0193_clock_contract.py --check")
    results.append(("Map 0x0193 clock/value contract", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([MAP_0190_TRANSACTION_CENSUS, "--check"],
             "extract_0190_transaction_census.py --check")
    results.append(("Map 0x0190 transaction census", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([WORLD_PARTY_CHAT_00C9_CONTRACT, "--check"],
             "extract_world_party_chat_00c9.py --check")
    results.append(("World party-chat 0x00C9 contract", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    ok = run([LOBBY_RECORD_CENSUS, "--check"],
             "extract_lobby_record_census.py --check")
    results.append(("sanitized decrypted lobby record census", "regen", ok,
                    "" if ok else "regenerated bytes differ, see output above"))

    run_plan("check-post", results)

    return report(results)


def do_write() -> int:
    results: list[tuple[str, str, bool, str]] = []

    run_plan("write", results)

    ok = run([PCAP_BUILDER], "build_pcap_products.py")
    digestion_ok = run([TOOLS / "validate_digestion.py"], "validate_digestion.py")
    products_ok = ok and digestion_ok
    for name in PCAP_PRODUCTS:
        results.append((f"derived/{name}", "write", products_ok,
                        "" if products_ok else "generation or digestion failed, see output above"))
    for name, reason in PARSE_ONLY_PRODUCTS:
        parse_only_check(name, reason, results)

    ok = run(
        [BATTLE_RESULT_DISTRIBUTIONS],
        "analyze_battle_result_distributions.py",
    )
    results.append(("battle-result Stage 2 products", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([BATTLE_RESULT_FITS], "analyze_battle_result_fits.py")
    results.append(("battle-result Stage 3 products", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([DIRECTOR_WIRE_IDENTITY], "extract_director_wire_identity.py")
    results.append(("director wire identity products", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([GUILDLEVE_JOURNAL_COMMAND], "extract_guildleve_journal_command.py")
    results.append(("guildleve journal command products", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([REGIONAL_GUILDLEVE_PUBLISHER_CONTRACT],
             "extract_regional_guildleve_publisher_contract.py")
    results.append(("regional guildleve publisher contract", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([PROPERTY_STREAM_CATALOG], "extract_property_stream_catalog.py")
    results.append(("property-stream catalog products", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([PLAYER_HP_CALIBRATION], "extract_player_hp_calibration.py")
    results.append(("player HP calibration anchors", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([EQUIPMENT_PROPERTY_CORRELATION],
             "extract_equipment_property_correlation.py")
    results.append(("equipment property correlation", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([LOGIN_018A_TIMELINE], "extract_login_018a_timeline.py")
    results.append(("login 0x018A timeline products", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([MAP_00DA_00E1_COMPARISON], "extract_00da_00e1_comparison.py")
    results.append(("0x00DA/0x00E1 comparison products", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([STATUS_WIRE_CENSUS], "extract_status_wire_census.py")
    results.append(("status wire projection census", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([PARTY_MARKER_CHRONOLOGY], "extract_party_marker_chronology.py")
    results.append(("party marker 0x018D chronology", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([PARTY_MARKER_FIELDS], "analyze_party_marker_fields.py")
    results.append(("party marker 0x018D field census", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([MAP_0193_CLOCK_CONTRACT], "extract_0193_clock_contract.py")
    results.append(("Map 0x0193 clock/value contract", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([MAP_0190_TRANSACTION_CENSUS],
             "extract_0190_transaction_census.py")
    results.append(("Map 0x0190 transaction census", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([WORLD_PARTY_CHAT_00C9_CONTRACT],
             "extract_world_party_chat_00c9.py")
    results.append(("World party-chat 0x00C9 contract", "write", ok,
                    "" if ok else "generation failed, see output above"))

    ok = run([LOBBY_RECORD_CENSUS], "extract_lobby_record_census.py")
    results.append(("sanitized decrypted lobby record census", "write", ok,
                    "" if ok else "generation failed, see output above"))

    run_plan("write-post", results)

    return report(results)


def report(results: list) -> int:
    failed = [r for r in results if not r[2]]
    print()
    print("=== refresh.py summary ===")
    for product, level, ok, note in results:
        status = "PASS" if ok else "FAIL"
        suffix = f" - {note}" if note else ""
        print(f"[{status}] {product} ({level}){suffix}")
    print()
    if failed:
        print(f"FAIL: {len(failed)}/{len(results)} checks failed.")
        return 1
    print(f"PASS: all {len(results)} checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified gate over every canonical xivl-captures product.")
    parser.add_argument("--check", action="store_true",
                        help="validate only, write nothing, exit 1 if anything is stale")
    parser.add_argument("--public-shape", action="store_true",
                        help="validate a filtered fresh-init tree with restricted evidence absent")
    args = parser.parse_args()
    if args.public_shape:
        if not args.check:
            parser.error("--public-shape requires --check")
        os.environ["XIVL_CORPUS_ABSENT"] = "1"
        return do_public_check()
    if args.check and not RESTRICTED_OBJECTS.is_dir():
        print("SKIP: restricted capture objects are absent; using public-shape checks.")
        os.environ["XIVL_CORPUS_ABSENT"] = "1"
        return do_public_check()
    return do_check() if args.check else do_write()


if __name__ == "__main__":
    sys.exit(main())
