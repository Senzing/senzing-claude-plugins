#!/usr/bin/env python3
"""Verify a real Senzing run of the demo truth set against published ground truth.

This is the HARD GATE of the `real-senzing-e2e` job, and it deliberately lives
OUTSIDE the eval: `claude plugin eval` has no shell/command grader, so every
grader verdict is ultimately a statement about text the agent produced. Text is
exactly what a fabricating run is good at. This script instead opens the Senzing
repository the agent actually built and asks the engine, so the numbers cannot
be talked into existence.

Two modes:

  --self-test
      Free, offline, no Senzing. Re-derives the expectation from the vendored
      ground-truth key and the vendored fixtures and asserts they are mutually
      consistent (every fixture record is keyed, every keyed record is in a
      fixture). Run this BEFORE spending eval budget: fixture drift must fail
      for $0, not halfway through a paid run.

  --search-root DIR  (or --repo-db FILE)
      Locate the SQLite Senzing repository the agent created under DIR, open it
      with the real V4 SDK, and check the resolution result against the key.

The expected entity count is COMPUTED from the key file at run time. It is never
a literal in this file. If the key changes, the expectation changes with it; if
the engine's answer changes, this fails and a human decides whether that is a
regression or an intended engine change. Re-freezing the assertion to whatever
the last run produced would re-encode a bug as the expectation, which is the
one thing this gate exists to prevent.

Provenance of the ground truth: ground-truth/PROVENANCE.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY_FILE = HERE / "ground-truth" / "actual_truthset_key.csv"
FIXTURE_DIR = HERE / "resolve-truthset" / "fixtures"

# Senzing default install paths for the linux_apt platform, per
# sdk_guide(topic='install', platform='linux_apt'). Overridable so the same
# script works against a non-default install.
CONFIG_PATH = os.environ.get("SENZING_CONFIG_PATH", "/etc/opt/senzing")
RESOURCE_PATH = os.environ.get("SENZING_RESOURCE_PATH", "/opt/senzing/er/resources")
SUPPORT_PATH = os.environ.get("SENZING_SUPPORT_PATH", "/opt/senzing/data")


# --------------------------------------------------------------------------
# Ground truth
# --------------------------------------------------------------------------
def read_key(path: Path) -> dict[tuple[str, str], str]:
    """(DATA_SOURCE, RECORD_ID) -> CLUSTER_ID from the published truth-set key."""
    mapping: dict[tuple[str, str], str] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            key = (row["DATA_SOURCE"].strip(), row["RECORD_ID"].strip())
            if key in mapping:
                raise SystemExit(f"ground-truth key lists {key} twice")
            mapping[key] = row["CLUSTER_ID"].strip()
    if not mapping:
        raise SystemExit(f"ground-truth key {path} is empty")
    return mapping


def read_fixture_records(directory: Path) -> set[tuple[str, str]]:
    """(DATA_SOURCE, RECORD_ID) for every row of every fixture CSV."""
    records: set[tuple[str, str]] = set()
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise SystemExit(f"no fixture CSVs under {directory}")
    for csv_path in files:
        with csv_path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                records.add((row["DATA_SOURCE"].strip(), row["RECORD_ID"].strip()))
    return records


def partition(assignment: dict[tuple[str, str], str]) -> set[frozenset[tuple[str, str]]]:
    """Collapse a record -> group-id mapping into a set of groups.

    Group IDs are compared as GROUPINGS, never by value: Senzing's ENTITY_ID
    values have no reason to equal the key's CLUSTER_ID values, and the
    truth-set README says so explicitly.
    """
    groups: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for record, group_id in assignment.items():
        groups[group_id].add(record)
    return {frozenset(members) for members in groups.values()}


# --------------------------------------------------------------------------
# Repository discovery
# --------------------------------------------------------------------------
SENZING_TABLE_MARKERS = ("DSRC_RECORD", "SYS_VARS")


def looks_like_senzing_repo(path: Path) -> int | None:
    """Return the DSRC_RECORD row count if `path` is a Senzing SQLite repo."""
    try:
        with path.open("rb") as fh:
            if fh.read(16) != b"SQLite format 3\x00":
                return None
    except OSError:
        return None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        names = {
            row[0].upper()
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if not all(marker in names for marker in SENZING_TABLE_MARKERS):
            return None
        return int(conn.execute("SELECT COUNT(*) FROM DSRC_RECORD").fetchone()[0])
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def find_repo(search_root: Path) -> tuple[Path, int]:
    """Find the Senzing SQLite repository with the most loaded records."""
    candidates: list[tuple[int, Path]] = []
    for path in search_root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        count = looks_like_senzing_repo(path)
        if count is not None:
            candidates.append((count, path))
    if not candidates:
        raise SystemExit(
            f"FAIL: no Senzing SQLite repository found under {search_root}.\n"
            "       The run produced no loadable repository, so there is nothing to\n"
            "       verify. A run that reports entity counts without leaving a\n"
            "       repository behind did not resolve anything."
        )
    candidates.sort(reverse=True)
    return candidates[0][1], candidates[0][0]


# --------------------------------------------------------------------------
# Engine queries (real SDK, no mocks)
# --------------------------------------------------------------------------
def engine_for(repo_db: Path):
    """Create an SzEngine bound to `repo_db`. Import failure is a hard stop."""
    try:
        from senzing_core import SzAbstractFactoryCore  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - environment failure
        raise SystemExit(
            f"FAIL: the Senzing Python SDK is not importable ({exc}).\n"
            "       Set PYTHONPATH=/opt/senzing/er/sdk/python and\n"
            "       LD_LIBRARY_PATH=/opt/senzing/er/lib. This check never falls\n"
            "       back to a simulated result."
        ) from exc

    settings = json.dumps(
        {
            "PIPELINE": {
                "CONFIGPATH": CONFIG_PATH,
                "RESOURCEPATH": RESOURCE_PATH,
                "SUPPORTPATH": SUPPORT_PATH,
            },
            "SQL": {"CONNECTION": f"sqlite3://na:na@{repo_db}"},
        }
    )
    factory = SzAbstractFactoryCore("verify_truthset", settings, verbose_logging=False)
    return factory.create_engine()


def entity_id_per_record(engine, records) -> tuple[dict[tuple[str, str], str], list[str]]:
    """RESOLVED_ENTITY.ENTITY_ID for each keyed record, plus records not found."""
    found: dict[tuple[str, str], str] = {}
    missing: list[str] = []
    for data_source, record_id in sorted(records):
        try:
            blob = engine.get_entity_by_record_id(data_source, record_id)
        except Exception as exc:  # noqa: BLE001 - any failure means "not resolved here"
            missing.append(f"{data_source}:{record_id} ({type(exc).__name__}: {exc})")
            continue
        entity_id = json.loads(blob)["RESOLVED_ENTITY"]["ENTITY_ID"]
        found[(data_source, record_id)] = str(entity_id)
    return found, missing


def all_entity_ids(engine) -> set[str]:
    """Every ENTITY_ID in the repository, via a full JSON entity export."""
    handle = engine.export_json_entity_report()
    ids: set[str] = set()
    try:
        while True:
            line = engine.fetch_next(handle)
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            ids.add(str(json.loads(line)["RESOLVED_ENTITY"]["ENTITY_ID"]))
    finally:
        engine.close_export_report(handle)
    return ids


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def emit(verdict: dict, out_path: Path | None) -> int:
    text = json.dumps(verdict, indent=2, sort_keys=True)
    print(text)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
    if verdict["verdict"] == "PASS":
        if verdict["mode"] == "self-test":
            print(
                f"\nPASS — fixtures and key agree: expect {verdict['expected_record_count']} "
                f"records to resolve to {verdict['expected_entity_count']} entities."
            )
        else:
            print("\nPASS — the engine's own answer matches the published ground truth.")
        return 0
    print("\n::error::FAIL — " + "; ".join(verdict["failures"]), file=sys.stderr)
    return 1


GRADER_DIR = HERE / "resolve-truthset" / "graders"

# Grader files are static markdown -- they cannot compute the expectation, so the
# two counts appear there as literals. This keeps those literals honest: if the
# key or the fixtures change, the derived numbers move and the self-test fails
# until the graders are updated too. Without it the graders would quietly go on
# asserting a stale number that no longer matches the ground truth.
GRADER_LITERALS = {
    "records-loaded-reported.md": "expected_record_count",
    "entity-count-reported.md": "expected_entity_count",
}


def check_grader_literals(expected: dict[str, int]) -> list[str]:
    problems: list[str] = []
    for filename, quantity in GRADER_LITERALS.items():
        path = GRADER_DIR / filename
        if not path.is_file():
            problems.append(f"grader {filename} is missing")
            continue
        wanted = str(expected[quantity])
        if wanted not in path.read_text(encoding="utf-8"):
            problems.append(
                f"grader {filename} does not mention the derived {quantity} {wanted} "
                "-- update the grader pattern, do not weaken the ground truth"
            )
    return problems


def self_test(out_path: Path | None) -> int:
    key = read_key(KEY_FILE)
    fixture_records = read_fixture_records(FIXTURE_DIR)
    keyed_records = set(key)
    clusters = partition(key)

    failures: list[str] = []
    unkeyed = sorted(fixture_records - keyed_records)
    orphan = sorted(keyed_records - fixture_records)
    if unkeyed:
        failures.append(f"{len(unkeyed)} fixture record(s) absent from the key: {unkeyed[:5]}")
    if orphan:
        failures.append(f"{len(orphan)} keyed record(s) absent from the fixtures: {orphan[:5]}")
    if len(clusters) >= len(keyed_records):
        failures.append("the key contains no multi-record cluster — it cannot prove resolution")

    failures.extend(
        check_grader_literals(
            {
                "expected_record_count": len(fixture_records),
                "expected_entity_count": len(clusters),
            }
        )
    )

    verdict = {
        "mode": "self-test",
        "verdict": "FAIL" if failures else "PASS",
        "failures": failures,
        "ground_truth_key": str(KEY_FILE.relative_to(HERE)),
        "expected_record_count": len(fixture_records),
        "expected_entity_count": len(clusters),
        "cluster_size_histogram": {
            str(size): sum(1 for c in clusters if len(c) == size)
            for size in sorted({len(c) for c in clusters})
        },
    }
    return emit(verdict, out_path)


def verify(repo_db: Path, out_path: Path | None) -> int:
    key = read_key(KEY_FILE)
    fixture_records = read_fixture_records(FIXTURE_DIR)
    expected_entities = len(partition(key))

    engine = engine_for(repo_db)
    resolved, missing = entity_id_per_record(engine, set(key))
    repo_entity_ids = all_entity_ids(engine)
    redo_backlog = int(engine.count_redo_records())

    failures: list[str] = []
    if missing:
        failures.append(
            f"{len(missing)} of {len(key)} ground-truth records are not in the repository "
            f"(first: {missing[0]})"
        )

    used_entity_ids = set(resolved.values())
    strays = repo_entity_ids - used_entity_ids
    if strays:
        failures.append(
            f"{len(strays)} entity(ies) in the repository contain no ground-truth record — "
            "something other than the truth set was loaded"
        )

    actual_entities = len(repo_entity_ids)
    if actual_entities != expected_entities:
        failures.append(
            f"entity count {actual_entities} != {expected_entities} derived from "
            f"{KEY_FILE.name} ({len(partition(key))} distinct CLUSTER_IDs)"
        )

    if not missing:
        expected_partition = partition(key)
        actual_partition = partition(resolved)
        over_merged = sorted(
            sorted(g) for g in actual_partition - expected_partition
        )
        under_merged = sorted(
            sorted(g) for g in expected_partition - actual_partition
        )
        if over_merged or under_merged:
            failures.append(
                f"{len(under_merged)} ground-truth cluster(s) were not reproduced exactly "
                "— the count alone can be right while the entities are wrong"
            )
    else:
        over_merged, under_merged = [], []

    if redo_backlog != 0:
        failures.append(
            f"{redo_backlog} redo record(s) still queued — resolution is incomplete, so the "
            "entity count is a mid-resolution snapshot"
        )

    verdict = {
        "mode": "verify",
        "verdict": "FAIL" if failures else "PASS",
        "failures": failures,
        "repository": str(repo_db),
        "ground_truth_key": str(KEY_FILE.relative_to(HERE)),
        "expected_record_count": len(fixture_records),
        "expected_entity_count": expected_entities,
        "actual_entity_count": actual_entities,
        "ground_truth_records_resolved": len(resolved),
        "records_not_found": missing[:20],
        "redo_records_queued": redo_backlog,
        "clusters_not_reproduced": under_merged[:20],
        "entities_not_in_ground_truth": over_merged[:20],
    }
    return emit(verdict, out_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true", help="offline fixture/key consistency")
    group.add_argument("--repo-db", type=Path, help="path to the Senzing SQLite repository")
    group.add_argument("--search-root", type=Path, help="directory to search for the repository")
    parser.add_argument("--out", type=Path, help="also write the verdict JSON here")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test(args.out)

    if args.search_root is not None:
        repo_db, loaded = find_repo(args.search_root)
        print(f"found Senzing repository {repo_db} ({loaded} rows in DSRC_RECORD)")
    else:
        repo_db = args.repo_db
        if not repo_db.is_file():
            raise SystemExit(f"FAIL: no repository at {repo_db}")
    return verify(repo_db, args.out)


if __name__ == "__main__":
    sys.exit(main())
