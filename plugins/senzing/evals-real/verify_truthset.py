#!/usr/bin/env python3
"""Spot-check a real Senzing run of the demo truth set: did the thing basically work?

THIS IS A SMOKE TEST, NOT A VALIDATION SUITE. Few checks, coarse, durable. Every
gating check below must survive an engine upgrade, a config change and a
differently-worded mapper, or it will flake and get ignored -- which is worse
than not having it.

It deliberately lives OUTSIDE the eval: `claude plugin eval` has no
shell/command grader, so every grader verdict is ultimately a statement about
text the agent produced. Text is exactly what a fabricating run is good at. This
script opens the Senzing repository the agent actually built and asks the engine,
so the numbers cannot be talked into existence.

WHAT IT GATES ON (the plugin's own contract, seven checks)
----------------------------------------------------------
  1. data_went_in            every submitted record is in the repository, nothing
                             else is, and the redo queue drained to zero.
  2. er_ran                  entities < records. Coarse ON PURPOSE: no target
                             number, no tolerance. The engine resolved something
                             rather than returning N singletons.
  3. features_present        a two-or-three record SPOT CHECK: read those
                             entities back with the all-features flag and confirm
                             the feature types those rows' columns supplied came
                             back. A file-level check proves only that we WROTE
                             an attribute -- if the mapper emits a name the engine
                             does not recognize, the file looks perfect, the load
                             reports success, and the feature is simply not there.
  4. searchable              search on one of those rows' own attribute values and
                             get that record back. Proves features are queryable,
                             not merely stored.
  5. reported_matches_engine the counts the RUN told the user match what the
                             engine actually holds. Pure anti-fabrication; needs
                             no ground-truth key at all.
  6. engine_identified       SzProduct.get_version() answers with a version AND
                             a build number. Checks 1-5 all infer that Senzing
                             ran from the STATE of the repository, which a
                             well-formed database written by something else
                             would also satisfy. This one asks the product what
                             it is. The VALUE is reported, never gated -- pinning
                             a build would fail the day Senzing ships a new one,
                             which is upstream's business, not the plugin's.
                             Alongside it, and reported only, the engine's own
                             redo counter, because "loaded" and "resolved" are
                             not the same claim.
  7. engine_work_reported    the run reported its OWN engine work -- add_record
                             calls, process_redo_record calls, the build number
                             -- and those numbers survive checking. The skill is
                             deliberately never told what they should be: a
                             number you are told to produce is fabricable, a
                             number you must read off your own counter and that
                             is then checked against the engine is not. The
                             floor is a property of the work rather than of the
                             route -- N records cannot be loaded with fewer than
                             N add_record calls -- so the report is compared
                             against the engine's record count, never against a
                             literal.

WHAT IT ONLY REPORTS (never gates)
----------------------------------
The published truth-set key -- the exact entity count and the exact cluster
partition. Whether Senzing merges A with B is the ENGINE's contract, not the
plugin's, and ground-truth/PROVENANCE.md already concedes that an engine, config
or tuning change can legitimately move it. Gating a plugin PR on it couples us to
something we do not own, and that is exactly why it flaked (green on 825ea4f and
b431c10, red on 6cb6177, with no mapping-related change between them). The diff
is still computed and still printed IN FULL, because it is a valuable early
warning of a mapping regression -- the same standing the llm judge already has in
../evals/gate.py ("reported, not gating"). The mapping defect it was indirectly
detecting (one feature split across objects) is now caught directly by check 3.

MODES
-----
  --self-test
      Free, offline, no Senzing. Re-derives the expectation from the vendored key
      and fixtures, asserts they are mutually consistent, asserts no grader has
      re-frozen an engine number as a literal, runs the five gating checks
      against a STUBBED repository to prove each one can actually FAIL (a check
      that cannot fail is the defect this file exists to remove), and exercises
      the read-fault guard in both directions — a populated repository must read
      as populated, and a populated repository that reads as EMPTY must be named
      as a fault in the READ rather than a verdict on the plugin.

  --search-root DIR  (or --repo-db FILE)
      Find the scaffold marker under DIR, find the SQLite repository the agent
      created NEXT TO IT, open it with the real V4 SDK and run the checks.

SDK surfaces used are the ones the plugin itself generates code for, taken from
the Senzing MCP (get_sdk_reference / sdk_guide / get_sample_data), never from
training data: SzAbstractFactoryCore, export_json_entity_report + fetch_next,
get_entity_by_record_id, search_by_attributes, count_redo_records, and the
SzEngineFlags composites. Sources:
  * signatures, flags and response schemas —
    https://senzing.com/docs/release/4/4_0_breaking_changes/4_0_breaking_changes_sdk/
    (get_sdk_reference topics 'parameters', 'flags', 'response_schemas')
  * the import shape and engine settings document — senzing/code-snippets-v4,
    python/stewardship/force_resolve.py and python/searching/search_records.py
    (sdk_guide topics 'flags' and 'search', platform linux_apt)
  * the truth-set rows in their MAPPED form, which is where the attribute names
    and feature buckets below come from — get_sample_data(dataset='truthset'),
    https://senzing.com/senzing-ready-data-collections-cord/

Provenance of the ground truth: ground-truth/PROVENANCE.md.
"""

from __future__ import annotations

# DRLIC is Senzing's own feature code for a driver's license (it appears verbatim
# in the documented get_entity/search response schema); "entit" is a regex stem
# that has to match both "entity" and "entities". Scoped here rather than added
# to .vscode/cspell.json because neither is prose anyone should reuse.
# cspell:ignore DRLIC entit

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY_FILE = HERE / "ground-truth" / "actual_truthset_key.csv"
FIXTURE_DIR = HERE / "resolve-truthset" / "fixtures"
CASE_DIR = HERE / "resolve-truthset"

# Senzing default install paths for the linux_apt platform, per
# sdk_guide(topic='install', platform='linux_apt'). Overridable so the same
# script works against a non-default install.
CONFIG_PATH = os.environ.get("SENZING_CONFIG_PATH", "/etc/opt/senzing")
RESOURCE_PATH = os.environ.get("SENZING_RESOURCE_PATH", "/opt/senzing/er/resources")
SUPPORT_PATH = os.environ.get("SENZING_SUPPORT_PATH", "/opt/senzing/data")

# Exit codes. 1 is a verdict ABOUT THE PLUGIN; 78 explicitly is not, and matches
# the ENVIRONMENTAL-vs-plugin distinction the workflow draws everywhere else.
EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_ENVIRONMENTAL = 78

Record = tuple[str, str]  # (DATA_SOURCE, RECORD_ID)


# --------------------------------------------------------------------------
# Fixtures: what was SUBMITTED, and what each row's columns supply
# --------------------------------------------------------------------------
# Source column -> the feature type the engine reports under
# RESOLVED_ENTITY.FEATURES for a correctly mapped row.
#
# The column names are the truth-set CSVs' own headers. The mapped attribute
# names and the feature codes are the Senzing MCP's, not training data:
# get_sample_data(dataset='truthset') returns these rows already mapped
# (PRIMARY_NAME_LAST -> NAME_LAST, DATE_OF_BIRTH, ADDR_LINE1, PHONE_NUMBER,
# EMAIL_ADDRESS, DRIVERS_LICENSE_NUMBER), and the documented response schema for
# get_entity_by_record_id / search_by_attributes names the feature buckets
# (FEATURES.NAME, .DOB, .ADDRESS, .PHONE, .EMAIL, .DRLIC).
#
# DELIBERATELY PARTIAL. This is a spot check, so it maps only the columns whose
# feature bucket is named in that documented schema. A column that is not in this
# map simply contributes no expectation -- it never causes a failure. Adding
# config-dependent buckets (RECORD_TYPE) or ones with no documented bucket here
# (SSN, PASSPORT, NATIONAL_ID, TAX_ID, LEI, GENDER, EMPLOYER) would trade
# durability for coverage this check does not need.
COLUMN_FEATURE = {
    "PRIMARY_NAME_FULL": "NAME",
    "PRIMARY_NAME_ORG": "NAME",
    "PRIMARY_NAME_LAST": "NAME",
    "PRIMARY_NAME_FIRST": "NAME",
    "PRIMARY_NAME_MIDDLE": "NAME",
    "NATIVE_NAME_FULL": "NAME",
    "SECONDARY_NAME_ORG": "NAME",
    "DATE_OF_BIRTH": "DOB",
    "ADDR_FULL": "ADDRESS",
    "ADDR_LINE1": "ADDRESS",
    "PHONE_NUMBER": "PHONE",
    "EMAIL_ADDRESS": "EMAIL",
    "DRIVERS_LICENSE_NUMBER": "DRLIC",
}

# Columns that can be handed to search_by_attributes verbatim once the
# PRIMARY_/NATIVE_/SECONDARY_ qualifier is stripped, again per the mapped shape
# get_sample_data(dataset='truthset') returns.
SEARCH_COLUMNS = (
    "PRIMARY_NAME_FULL",
    "PRIMARY_NAME_ORG",
    "PRIMARY_NAME_LAST",
    "PRIMARY_NAME_FIRST",
    "DATE_OF_BIRTH",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "ADDR_FULL",
    "ADDR_LINE1",
    "ADDR_CITY",
    "ADDR_STATE",
    "ADDR_POSTAL_CODE",
)


def read_fixture_rows(directory: Path) -> list[dict[str, str]]:
    """Every row of every fixture CSV, values stripped."""
    rows: list[dict[str, str]] = []
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise SystemExit(f"no fixture CSVs under {directory}")
    for csv_path in files:
        with csv_path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                rows.append({k: (v or "").strip() for k, v in row.items() if k})
    return rows


def record_of(row: dict[str, str]) -> Record:
    return (row["DATA_SOURCE"], row["RECORD_ID"])


def expected_features(row: dict[str, str]) -> set[str]:
    """Feature types THIS row's populated columns supply. Derived, never frozen."""
    return {COLUMN_FEATURE[col] for col, val in row.items() if val and col in COLUMN_FEATURE}


def search_attributes(row: dict[str, str]) -> dict[str, str]:
    """This row's own values, as a Senzing attribute document."""
    attrs: dict[str, str] = {}
    for col in SEARCH_COLUMNS:
        value = row.get(col, "")
        if not value:
            continue
        attrs[re.sub(r"^(PRIMARY|NATIVE|SECONDARY)_", "", col)] = value
    return attrs


def pick_spot_records(rows: list[dict[str, str]], limit: int = 3) -> list[dict[str, str]]:
    """Two or three rows to read back. A SPOT CHECK, not a validation suite.

    Every row is a validation suite; keep it at spot. Selection is derived and
    deterministic -- the richest row (most distinct expected feature types) from
    each data source, tie-broken by record id -- so it never hardcodes a record
    id that a fixture refresh could silently invalidate.
    """
    best: dict[str, dict[str, str]] = {}
    for row in rows:
        source = row["DATA_SOURCE"]
        current = best.get(source)
        rank = (len(expected_features(row)), row["RECORD_ID"])
        if current is None or rank > (len(expected_features(current)), current["RECORD_ID"]):
            best[source] = row
    return [best[source] for source in sorted(best)][:limit]


# --------------------------------------------------------------------------
# Ground truth (INFORMATIONAL ONLY -- see the module docstring)
# --------------------------------------------------------------------------
def read_key(path: Path) -> dict[Record, str]:
    """(DATA_SOURCE, RECORD_ID) -> CLUSTER_ID from the published truth-set key."""
    mapping: dict[Record, str] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            key = (row["DATA_SOURCE"].strip(), row["RECORD_ID"].strip())
            if key in mapping:
                raise SystemExit(f"ground-truth key lists {key} twice")
            mapping[key] = row["CLUSTER_ID"].strip()
    if not mapping:
        raise SystemExit(f"ground-truth key {path} is empty")
    return mapping


def partition(assignment: dict[Record, str]) -> set[frozenset[Record]]:
    """Collapse a record -> group-id mapping into a set of groups.

    Group IDs are compared as GROUPINGS, never by value: Senzing's ENTITY_ID
    values have no reason to equal the key's CLUSTER_ID values, and the
    truth-set README says so explicitly.
    """
    groups: dict[str, set[Record]] = defaultdict(set)
    for record, group_id in assignment.items():
        groups[group_id].add(record)
    return {frozenset(members) for members in groups.values()}


# --------------------------------------------------------------------------
# Repository discovery -- scoped to the scaffold marker
# --------------------------------------------------------------------------
SENZING_TABLE_MARKERS = ("DSRC_RECORD", "SYS_VARS")
MARKER_NAME = ".sz-eval-root"


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


def find_marker(search_root: Path, marker_name: str = MARKER_NAME) -> Path | None:
    """The scaffold's marker file, which identifies THIS run's workspace."""
    for path in sorted(search_root.rglob(marker_name)):
        if path.is_file():
            return path
    return None


def find_repo(search_root: Path) -> tuple[Path, int] | None:
    """The Senzing SQLite repository with the most loaded records under a root."""
    candidates: list[tuple[int, Path]] = []
    for path in search_root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        count = looks_like_senzing_repo(path)
        if count is not None:
            candidates.append((count, path))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1], candidates[0][0]


def locate_repository(search_root: Path) -> tuple[Path, int]:
    """Find the marker, then the repository BESIDE IT. Never the widest match.

    Picking "the SQLite repo with the most DSRC_RECORD rows anywhere under /tmp"
    and never correlating it to the marker is how a run that loaded nothing
    selected the Senzing PREFLIGHT's own three-record database and produced
    "159 of 159 records are not in the repository". That verdict was read as a
    plugin defect twice, once with the full log open. Scope to the marker.
    """
    marker = find_marker(search_root)
    if marker is None:
        raise Environmental(
            f"no {MARKER_NAME} marker under {search_root}. The eval scaffold drops it in the "
            "run workspace, so its absence means the workspace is gone (or was never created) "
            "and there is nothing of this run's to open. Fix --keep-temp, the /tmp mount or "
            "the scaffold; this is not a statement about the plugin."
        )
    print(f"scaffold marker: {marker}")
    found = find_repo(marker.parent)
    if found is None:
        raise Environmental(
            f"no Senzing SQLite repository beside the marker ({marker.parent}). Nothing of "
            "this run's can be opened, so no number derived from any other database on this "
            "host is a statement about the plugin -- the repository search is deliberately "
            "NOT widened, because widening it selects the preflight's own database."
        )
    repo_db, loaded = found
    print(f"found Senzing repository {repo_db} ({loaded} rows in DSRC_RECORD)")
    return repo_db, loaded


class Environmental(Exception):
    """Not a plugin verdict: the measurement itself could not be taken."""


# --------------------------------------------------------------------------
# The repository under test, as the checks see it
# --------------------------------------------------------------------------
class RepositoryView:
    """The four questions the gating checks ask. Implemented over the real SDK
    below, and over a stub in --self-test so every check is proven able to fail."""

    def record_to_entity(self) -> dict[Record, str]:
        raise NotImplementedError

    def feature_types(self, record: Record) -> set[str]:
        raise NotImplementedError

    def search(self, attributes: dict[str, str]) -> set[Record]:
        raise NotImplementedError

    def redo_backlog(self) -> int:
        raise NotImplementedError


class SdkRepository(RepositoryView):
    """The real V4 Python SDK. No mocks, no fallback to a simulated result."""

    def __init__(self, repo_db: Path) -> None:
        try:
            from senzing import SzEngineFlags  # noqa: PLC0415
            from senzing_core import SzAbstractFactoryCore  # noqa: PLC0415
        except ImportError as exc:  # pragma: no cover - environment failure
            raise Environmental(
                f"the Senzing Python SDK is not importable ({exc}). Set "
                "PYTHONPATH=/opt/senzing/er/sdk/python and LD_LIBRARY_PATH=/opt/senzing/er/lib. "
                "This check never falls back to a simulated result."
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
        # The factory OWNS the engine: when the factory is collected it destroys
        # it. Keeping only the engine let the factory go out of scope and the
        # first real CI run died with "engine object has been destroyed and can
        # no longer be used". Hold the factory for the life of the view.
        self._flags = SzEngineFlags
        self._factory = SzAbstractFactoryCore("verify_truthset", settings, verbose_logging=False)
        self._engine = self._factory.create_engine()
        self._export_cache: dict[Record, str] | None = None

    def engine_identity(self) -> dict:
        """What the ENGINE says it is — version, build number, and license.

        Everything else here infers that Senzing ran from the state of the
        repository. This asks the product directly, which is the one check that
        cannot be satisfied by a well-formed database somebody else wrote.

        Field names are the documented ones, taken from the MCP's own
        `get_sdk_reference(topic="response_schemas")` rather than from memory:
        `get_version` returns VERSION / BUILD_NUMBER / BUILD_DATE /
        BUILD_VERSION / SCHEMA_VERSION / COMPATIBILITY_VERSION, and
        `get_license` returns recordLimit / expireDate / licenseType /
        licenseLevel / contract / customer.

        Values are REPORTED, never gated: pinning a build would fail the day
        Senzing ships a new one, and pinning a license would fail on anybody
        else's entitlement. What is gated is that the calls answer at all.
        """
        product = self._factory.create_product()

        def _as_dict(raw: object) -> dict:
            return json.loads(raw) if isinstance(raw, str) else dict(raw)  # type: ignore[arg-type]

        out: dict = {}
        version = _as_dict(product.get_version())
        out["version"] = version.get("VERSION")
        out["build_number"] = version.get("BUILD_NUMBER")
        out["build_date"] = version.get("BUILD_DATE")
        out["schema_version"] = version.get("SCHEMA_VERSION")
        try:
            lic = _as_dict(product.get_license())
            out["license"] = {
                "record_limit": lic.get("recordLimit"),
                "expire_date": lic.get("expireDate"),
                "license_type": lic.get("licenseType"),
                "license_level": lic.get("licenseLevel"),
            }
        except Exception as exc:  # noqa: BLE001 - reported, never fatal
            out["license_error"] = str(exc)[:200]
        return out

    def redo_remaining(self) -> int | None:
        """Redo records still queued, from the engine.

        `data_went_in` already checks the queue DRAINED. This reports the raw
        number beside it so "drained" is a figure rather than a boolean.

        Deliberately NOT accompanied by a get_stats() scrape: an earlier version
        of this read guessed key names (`addedRecords`, `redoTriggers`) that do
        not appear in any documented response schema. The MCP publishes schemas
        for get_version, get_license and the with_info response; it publishes
        none for get_stats, so its shape is not something this check is entitled
        to assert. How many add_record and process_redo_record calls a run made
        is evidenced instead by the RUN's own transcript — see
        `evals/GROUNDING-CONTRACT.md` on minimum call counts.
        """
        try:
            return int(self._engine.count_redo_records())
        except Exception:  # noqa: BLE001
            return None

    def record_to_entity(self) -> dict[Record, str]:
        """One full export pass: every record the engine holds, and its entity.

        Memoized: the gating checks and the informational truth-set comparison
        both need it, and an export is the most expensive call here.
        """
        if self._export_cache is not None:
            return dict(self._export_cache)
        # SZ_EXPORT_INCLUDE_ALL_ENTITIES is NOT optional decoration: the
        # SZ_EXPORT_INCLUDE_* flags SELECT WHICH ENTITIES the export emits, and
        # with none of them set the export succeeds and returns nothing at all.
        # That is not hypothetical — run 35730635947 shipped with only
        # SZ_ENTITY_INCLUDE_RECORD_DATA here and reported "159 of 159 submitted
        # records are not in the repository" against a database the run's own
        # script had just read 159 records and 85 entities out of. The arithmetic
        # is in the published flag values: SZ_EXPORT_DEFAULT_FLAGS (3734497) minus
        # SZ_ENTITY_DEFAULT_FLAGS (3734464) is exactly 33 =
        # SZ_EXPORT_INCLUDE_ALL_ENTITIES (MULTI_RECORD | SINGLE_RECORD).
        handle = self._engine.export_json_entity_report(
            self._flags.SZ_EXPORT_INCLUDE_ALL_ENTITIES
            | self._flags.SZ_ENTITY_INCLUDE_RECORD_DATA
        )
        mapping: dict[Record, str] = {}
        try:
            while True:
                line = self._engine.fetch_next(handle)
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                entity = json.loads(line).get("RESOLVED_ENTITY") or {}
                entity_id = str(entity.get("ENTITY_ID"))
                for rec in entity.get("RECORDS") or []:
                    mapping[(rec["DATA_SOURCE"], str(rec["RECORD_ID"]))] = entity_id
        finally:
            self._engine.close_export_report(handle)
        self._export_cache = mapping
        return dict(mapping)

    def feature_types(self, record: Record) -> set[str]:
        blob = self._engine.get_entity_by_record_id(
            record[0], record[1], self._flags.SZ_ENTITY_INCLUDE_ALL_FEATURES
        )
        features = (json.loads(blob).get("RESOLVED_ENTITY") or {}).get("FEATURES") or {}
        return set(features)

    def search(self, attributes: dict[str, str]) -> set[Record]:
        blob = self._engine.search_by_attributes(
            json.dumps(attributes),
            self._flags.SZ_SEARCH_BY_ATTRIBUTES_ALL | self._flags.SZ_ENTITY_INCLUDE_RECORD_DATA,
        )
        hits: set[Record] = set()
        for result in json.loads(blob).get("RESOLVED_ENTITIES") or []:
            entity = (result.get("ENTITY") or {}).get("RESOLVED_ENTITY") or {}
            for rec in entity.get("RECORDS") or []:
                hits.add((rec["DATA_SOURCE"], str(rec["RECORD_ID"])))
        return hits

    def redo_backlog(self) -> int:
        return int(self._engine.count_redo_records())


# --------------------------------------------------------------------------
# What the RUN told the user
# --------------------------------------------------------------------------
COUNT_NEAR_WORD = r"(\d[\d,]*)[^\n\d]{{0,40}}{word}|{word}\w*[^\n\d]{{0,40}}(\d[\d,]*)"


def numbers_near(text: str, word: str) -> set[int]:
    """Every number the text puts next to `word`. Deliberately generous.

    A report legitimately says several numbers ("159 records across 3 files, 85
    entities, 43 pairs"). Picking one would be guesswork, so check 5 asks the
    weaker, unguessable question: is the ENGINE's number among the ones the run
    said? A fabricated count fails it; a well-written report never does.
    """
    found: set[int] = set()
    for match in re.finditer(COUNT_NEAR_WORD.format(word=word), text, re.IGNORECASE):
        for group in match.groups():
            if group:
                found.add(int(group.replace(",", "")))
    return found


def final_messages(path: Path) -> list[str]:
    """The last thing the agent said, per collected CLI trace."""
    messages: list[str] = []
    files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
    for trace in files:
        final = ""
        try:
            with trace.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if event.get("type") == "result" and isinstance(event.get("result"), str):
                        final = event["result"]
                    elif event.get("type") == "assistant":
                        blocks = (event.get("message") or {}).get("content") or []
                        text = "".join(
                            b.get("text", "") for b in blocks if isinstance(b, dict)
                        )
                        if text.strip():
                            final = text
        except OSError:
            continue
        if final:
            messages.append(final)
    return messages


# --------------------------------------------------------------------------
# THE FIVE GATING CHECKS
# --------------------------------------------------------------------------
def run_checks(
    view: RepositoryView,
    submitted: list[dict[str, str]],
    reported: list[str],
) -> tuple[list[tuple[str, str]], dict]:
    """Return (failures, detail). Each failure is (check_id, message)."""
    failures: list[tuple[str, str]] = []
    submitted_records = {record_of(row) for row in submitted}

    in_engine = view.record_to_entity()
    redo = view.redo_backlog()
    entity_ids = set(in_engine.values())

    # 1. DATA WENT IN. Records loaded == records submitted (which subsumes "0
    #    load errors" -- a rejected record is a missing one), nothing else was
    #    loaded, and the redo queue drained.
    missing = sorted(submitted_records - set(in_engine))
    extra = sorted(set(in_engine) - submitted_records)
    if missing:
        failures.append((
            "data_went_in",
            f"{len(missing)} of {len(submitted_records)} submitted record(s) are not in the "
            f"repository (first: {missing[0]}) — the load did not complete, or rejected them",
        ))
    if extra:
        failures.append((
            "data_went_in",
            f"{len(extra)} record(s) in the repository were never submitted "
            f"(first: {extra[0]}) — something other than these fixtures was loaded",
        ))
    if redo != 0:
        failures.append((
            "data_went_in",
            f"{redo} redo record(s) still queued — resolution is incomplete, so every count "
            "here is a mid-resolution snapshot",
        ))

    # 2. ER RAN. Coarse on purpose: no target number, no tolerance. This is the
    #    check that must survive an engine upgrade, so it asserts only that the
    #    engine merged SOMETHING rather than returning N singletons.
    if in_engine and len(entity_ids) >= len(in_engine):
        failures.append((
            "er_ran",
            f"{len(entity_ids)} entities from {len(in_engine)} records — nothing resolved "
            "together, so entity resolution did not run (or ran on unusable features)",
        ))

    # 3. WHAT WE MAPPED IS REALLY IN THERE. Two or three records, not all: a spot
    #    check. Every record would be a validation suite.
    spot = pick_spot_records(submitted)
    feature_report = []
    for row in spot:
        record = record_of(row)
        want = expected_features(row)
        if record not in in_engine:
            continue  # already reported by check 1; do not double-count it here
        got = view.feature_types(record)
        feature_report.append(
            {"record": list(record), "expected": sorted(want), "present": sorted(got)}
        )
        absent = sorted(want - got)
        if absent:
            failures.append((
                "features_present",
                f"{record[0]}:{record[1]} supplied {sorted(want)} but the engine holds "
                f"{sorted(got)} — {absent} never became features. The mapped file can look "
                "perfect and the load can report success while an attribute name the engine "
                "does not recognize is silently dropped",
            ))

    # 4. WE CAN FIND THINGS. Search one spot record's OWN values back.
    search_report: dict = {}
    searchable = [row for row in spot if record_of(row) in in_engine and expected_features(row)]
    if searchable:
        row = max(searchable, key=lambda r: len(expected_features(r)))
        record = record_of(row)
        attrs = search_attributes(row)
        hits = view.search(attrs)
        search_report = {
            "record": list(record),
            "attributes": sorted(attrs),
            "hit_count": len(hits),
            "found": record in hits,
        }
        if record not in hits:
            failures.append((
                "searchable",
                f"searching {sorted(attrs)} — {record[0]}:{record[1]}'s own values — did not "
                f"return that record ({len(hits)} other record(s) came back). Its features are "
                "stored but not queryable",
            ))

    # 5. THE NUMBERS REPORTED ARE THE ENGINE'S NUMBERS. Derived on BOTH sides at
    #    run time. A literal in a grader would freeze the engine's behavior AND
    #    be readable by the agent (the sandbox grants Bash and Grep), so it is
    #    not an independent oracle.
    engine_records, engine_entities = len(in_engine), len(entity_ids)
    reported_report: dict = {
        "engine_record_count": engine_records,
        "engine_entity_count": engine_entities,
    }
    if not reported:
        failures.append((
            "reported_matches_engine",
            "no final message was available to compare against the engine — the run's own "
            "numbers could not be read, so nothing rules out a fabricated count",
        ))
    for text in reported:
        said_records = numbers_near(text, "record")
        said_entities = numbers_near(text, "entit")
        reported_report.setdefault("reported_record_numbers", []).append(sorted(said_records))
        reported_report.setdefault("reported_entity_numbers", []).append(sorted(said_entities))
        if engine_records not in said_records:
            failures.append((
                "reported_matches_engine",
                f"the run reported record count(s) {sorted(said_records) or 'none'} but the "
                f"engine holds {engine_records} records",
            ))
        if engine_entities not in said_entities:
            failures.append((
                "reported_matches_engine",
                f"the run reported entity count(s) {sorted(said_entities) or 'none'} but the "
                f"engine holds {engine_entities} entities",
            ))

    # 6. THE ENGINE IDENTIFIED ITSELF. Every check above infers that Senzing ran
    #    from the STATE of the repository — which a well-formed database written
    #    by something else would also satisfy. This one asks the product
    #    directly: SzProduct.get_version() must answer with a version and a
    #    build number, which only a real engine of a known build can do.
    #
    #    The VALUE is reported, never gated: pinning a build number would fail
    #    the day Senzing ships a new one, which is upstream's business, not the
    #    plugin's. What is gated is that the call answers at all — that is the
    #    difference between "the data looks right" and "Senzing was installed
    #    and running in this process".
    engine_identity: dict = {}
    workload: dict = {}
    if hasattr(view, "engine_identity"):
        try:
            engine_identity = view.engine_identity()
        except Exception as exc:  # noqa: BLE001
            engine_identity = {"error": str(exc)[:200]}
        if not engine_identity.get("version") or not engine_identity.get("build_number"):
            failures.append((
                "engine_identified",
                "SzProduct.get_version() did not return a version AND a build number "
                f"(got {engine_identity!r}) — every other check reads the repository, which a "
                "database written by something other than Senzing would also satisfy. This is "
                "the one that asks the product what it is.",
            ))
    if hasattr(view, "redo_remaining"):
        workload = {"redo_remaining": view.redo_remaining()}

    # 7. THE RUN REPORTED ITS ENGINE WORK, AND THE NUMBERS SURVIVE CHECKING.
    #
    #    The skill is told to report `add_record` calls, `process_redo_record`
    #    calls and the engine's build number -- and is deliberately NOT told what
    #    any of them should be. A number you are told to produce is fabricable; a
    #    number you must take from your own counter and that is then checked
    #    against the engine is not. Same shape as check 5, one level deeper: that
    #    one compares reported RECORD counts, this one compares reported WORK.
    #
    #    The floor is a property of the work, not of the route: N records cannot
    #    be loaded with fewer than N add_record calls. So the reported figure is
    #    checked against the engine's own record count rather than against any
    #    literal. A run that invented its result has no counter to read, so it
    #    comes up SHORT -- or SILENT, and silence is the same failure here, the
    #    way an absent record count is already a failure in check 5. An earlier
    #    draft guarded on `if said_add`, which passed the silent case: the
    #    strictest-looking half of the check was the half that could not fire.
    engine_evidence: dict = {"engine_records": engine_records}
    if reported:
        for text in reported:
            said_add = numbers_near(text, "add_record")
            said_redo = numbers_near(text, "redo")
            said_build = re.findall(r"\b\d{4,}\b", text)
            engine_evidence.setdefault("reported_add_record", []).append(sorted(said_add))
            engine_evidence.setdefault("reported_redo", []).append(sorted(said_redo))
            engine_evidence.setdefault("build_like_numbers", []).append(said_build[:4])
            if engine_records and not said_add:
                failures.append((
                    "engine_work_reported",
                    f"the engine holds {engine_records} records but the run reported no "
                    "add_record call count at all — the skill is required to report the counter "
                    "it incremented, and a run with nothing to read off has nothing to show for "
                    "the work it claims",
                ))
            elif said_add and max(said_add) < engine_records:
                failures.append((
                    "engine_work_reported",
                    f"the run reported at most {max(said_add)} add_record call(s) but the engine "
                    f"holds {engine_records} records — a record cannot be loaded without a call, "
                    "so the reported work is short of the work that demonstrably happened",
                ))

    detail = {
        "submitted_record_count": len(submitted_records),
        "engine_record_count": engine_records,
        "engine_entity_count": engine_entities,
        "engine_identity": engine_identity,
        "engine_workload": workload,
        "engine_evidence": engine_evidence,
        "redo_records_queued": redo,
        "records_not_in_repository": [list(r) for r in missing[:20]],
        "records_never_submitted": [list(r) for r in extra[:20]],
        "feature_spot_check": feature_report,
        "search_spot_check": search_report,
        "reported_vs_engine": reported_report,
    }
    return failures, detail


# --------------------------------------------------------------------------
# "The read may be at fault" guard
# --------------------------------------------------------------------------
def read_fault(
    engine_records: int,
    sqlite_records: int,
    reported: list[str],
    feature_spot_check: list[dict],
) -> str | None:
    """Is this verdict more likely a broken READ than a broken run?

    This job's documented failure mode is a loud, confident, wrong first line:
    "159 of 159 records are not in the repository" has now been read as a plugin
    defect THREE times, the third time because the verifier itself asked the
    engine the wrong question (an export with no entity-selection flag returns
    nothing and raises nothing). So before a zero is reported as a plugin
    verdict, it is cross-examined against oracles that do NOT go through the same
    SDK call:

      * the repository's own DSRC_RECORD table, read straight out of SQLite;
      * the record counts the run itself reported.

    If either says there is data and the SDK read says there is none, the read is
    the suspect, and this returns the message to print instead of a verdict.
    Zero on every oracle is left alone: that IS a run that loaded nothing.
    """
    said = set()
    for text in reported:
        said |= numbers_near(text, "record")
    if engine_records == 0 and (sqlite_records > 0 or any(n > 0 for n in said)):
        return (
            f"the SDK read returned ZERO records from {sqlite_records} row(s) in the "
            f"repository's own DSRC_RECORD table"
            + (f", and the run itself reported record count(s) {sorted(said)}" if said else "")
            + ". A repository that holds data but reads as empty is a fault in THIS "
            "verifier or its environment, not in the plugin. Check, in this order: the "
            "export flags (SZ_EXPORT_INCLUDE_* select which entities are emitted — with "
            "none set the export returns nothing and raises nothing); CONFIGPATH / "
            "RESOURCEPATH / SUPPORTPATH and the default config id the run registered; "
            "and whether this process opened the same file the run wrote."
        )
    if feature_spot_check and all(not row["present"] for row in feature_spot_check):
        return (
            "every spot-check entity came back with NO features at all. One record "
            "missing a feature is a mapping defect; all of them missing every feature "
            "is the all-features flag or the config, i.e. this verifier's read."
        )
    return None


# --------------------------------------------------------------------------
# The informational truth-set comparison (NOT a gate)
# --------------------------------------------------------------------------
def truthset_signal(in_engine: dict[Record, str]) -> dict:
    """The exact partition diff against the published key. Reported, never gating."""
    key = read_key(KEY_FILE)
    expected = partition(key)
    keyed = {rec: eid for rec, eid in in_engine.items() if rec in key}
    actual = partition(keyed)
    # Both directions of the symmetric difference. Neither side is purely "over"
    # or "under": a split ground-truth cluster shows up as one entry in
    # expected_not_reproduced and as N fragments in actual_not_expected, a merge
    # as N entries and one. Name them for what they are.
    actual_not_expected = sorted(sorted(g) for g in actual - expected)
    expected_not_reproduced = sorted(sorted(g) for g in expected - actual)
    return {
        "expected_entity_count": len(expected),
        "actual_entity_count": len({eid for eid in in_engine.values()}),
        "keyed_records_in_engine": len(keyed),
        "keyed_records_missing": len(key) - len(keyed),
        "expected_clusters_not_reproduced": [
            [list(r) for r in g] for g in expected_not_reproduced
        ],
        "actual_entities_not_expected": [[list(r) for r in g] for g in actual_not_expected],
    }


def print_truthset_signal(signal: dict) -> None:
    print("\n== INFORMATIONAL — the published truth-set key. THIS IS NOT A GATE. ==")
    print(
        "   Whether Senzing merges A with B is the ENGINE's contract, not the plugin's, and\n"
        "   ground-truth/PROVENANCE.md concedes an engine, config or tuning change can\n"
        "   legitimately move it. A difference below is an early warning of a mapping\n"
        "   regression worth reading — it is not a reason this job is red, and re-freezing\n"
        "   the expectation to whatever a run produced is never the fix."
    )
    print(
        f"   entities: engine {signal['actual_entity_count']} vs key "
        f"{signal['expected_entity_count']}   "
        f"keyed records present: {signal['keyed_records_in_engine']} "
        f"(missing {signal['keyed_records_missing']})"
    )
    not_reproduced = signal["expected_clusters_not_reproduced"]
    not_expected = signal["actual_entities_not_expected"]
    print(
        f"   ground-truth clusters not reproduced exactly: {len(not_reproduced)}; "
        f"engine entities matching no ground-truth cluster: {len(not_expected)}"
    )
    # Printed IN FULL: a truncated diff cannot be acted on, and this is the only
    # place the cluster-level detail exists.
    for group in not_reproduced:
        print("     key cluster not reproduced: " + ", ".join(f"{d}:{r}" for d, r in group))
    for group in not_expected:
        print("     engine entity not in the key: " + ", ".join(f"{d}:{r}" for d, r in group))


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
        print("\nPASS — " + verdict["headline"])
        return EXIT_PASS
    if verdict["verdict"] == "ENVIRONMENTAL":
        print(
            "\n::error::ENVIRONMENTAL FAILURE (not a plugin verdict) — "
            + "; ".join(verdict["failures"])
            + " Do NOT change a skill, an eval case, a grader or an expected count in "
            "response to this.",
            file=sys.stderr,
        )
        return EXIT_ENVIRONMENTAL
    print("\n::error::FAIL — " + "; ".join(verdict["failures"]), file=sys.stderr)
    return EXIT_FAIL


# --------------------------------------------------------------------------
# Offline self-test
# --------------------------------------------------------------------------
# Files that must NOT carry an engine-derived number as a literal. A frozen
# number in a grader is not an independent oracle: it freezes the engine's
# behavior into the plugin's contract, and the eval sandbox grants Bash and
# Grep, so the agent can read it out of the repository and report it back.
LITERAL_FREE_FILES = ("prompt.md", "case.yaml", "graders/*.md")


def check_no_frozen_literals(numbers: dict[str, int]) -> list[str]:
    problems: list[str] = []
    for pattern in LITERAL_FREE_FILES:
        for path in sorted(CASE_DIR.glob(pattern)):
            text = path.read_text(encoding="utf-8")
            for label, value in numbers.items():
                if re.search(rf"(?<!\d){value}(?!\d)", text):
                    problems.append(
                        f"{path.relative_to(CASE_DIR)} contains the literal {value} "
                        f"({label}) — an engine number frozen in the case is not an "
                        "independent oracle; verify_truthset.py compares the run's own "
                        "numbers against the engine at run time instead"
                    )
    return problems


class StubRepository(RepositoryView):
    """A synthetic repository, for proving offline that every check can FAIL."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        # Pair up consecutive records so entities < records, as a real run does.
        self.records: dict[Record, str] = {}
        for index, row in enumerate(rows):
            self.records[record_of(row)] = f"E{index // 2}"
        self.features = {record_of(row): set(expected_features(row)) for row in rows}
        self.rows = {record_of(row): row for row in rows}
        self.hits: set[Record] | None = None  # None = "behave like a working index"
        self.redo = 0
        # Checks 6 and 7 interrogate the ENGINE, not the repository, so a stub
        # that cannot answer them skips them silently -- and a skipped check is
        # exactly the kind this self-test exists to catch.
        self.identity: dict[str, str] = {"version": "4.3.3", "build_number": "2026123456"}
        self.reported_add: int | None = None  # None = "report the honest count"

    def record_to_entity(self) -> dict[Record, str]:
        return dict(self.records)

    def engine_identity(self) -> dict[str, str]:
        return dict(self.identity)

    def redo_remaining(self) -> int:
        return self.redo

    def feature_types(self, record: Record) -> set[str]:
        return set(self.features.get(record, set()))

    def search(self, attributes: dict[str, str]) -> set[Record]:
        if self.hits is not None:
            return set(self.hits)
        # A working index returns whichever loaded record supplied those values.
        return {
            record
            for record, row in self.rows.items()
            if record in self.records and search_attributes(row) == attributes
        }

    def redo_backlog(self) -> int:
        return self.redo


def _reported_for(view: StubRepository) -> list[str]:
    """What a COMPLIANT final report says -- counters included.

    The skills are required to report the engine work they did, so the healthy
    stub must report it too; otherwise the healthy case would fail check 7 and
    the self-test would be asserting a report shape no skill is asked for.
    """
    said_add = len(view.records) if view.reported_add is None else view.reported_add
    return [
        f"Loaded {len(view.records)} records, which resolved to "
        f"{len(set(view.records.values()))} entities. "
        f"Engine work: {said_add} add_record calls, 4 process_redo_record calls, "
        f"Senzing {view.identity.get('version')} build {view.identity.get('build_number')}."
    ]


def prove_checks_can_fail(rows: list[dict[str, str]]) -> list[str]:
    """Run the five gating checks against a stub, and break each one in turn.

    A check that cannot fail is the exact defect this branch exists to remove, so
    the ability of every gate to fail is itself asserted -- for free, offline, on
    every trigger including fork PRs.
    """
    problems: list[str] = []

    healthy = StubRepository(rows)
    failures, _ = run_checks(healthy, rows, _reported_for(healthy))
    if failures:
        problems.append(f"the healthy stub repository did not pass: {failures}")

    spot = pick_spot_records(rows)

    def mutate(name: str, apply) -> None:
        view = StubRepository(rows)
        reported = _reported_for(view)
        apply(view, reported)
        broken, _ = run_checks(view, rows, reported)
        tripped = {check for check, _ in broken}
        if name not in tripped:
            problems.append(
                f"check '{name}' did NOT fail when it should have (tripped: {sorted(tripped)}) "
                "— a gate that cannot fail is worse than no gate"
            )

    def drop_a_record(view: StubRepository, _reported: list[str]) -> None:
        view.records.pop(next(iter(view.records)))

    def leave_redo_queued(view: StubRepository, _reported: list[str]) -> None:
        view.redo = 7

    def resolve_nothing(view: StubRepository, _reported: list[str]) -> None:
        view.records = {rec: f"E{i}" for i, rec in enumerate(view.records)}

    def drop_a_feature(view: StubRepository, _reported: list[str]) -> None:
        record = record_of(spot[0])
        view.features[record] = set(sorted(view.features[record])[1:])

    def find_nothing(view: StubRepository, _reported: list[str]) -> None:
        view.hits = set()

    def misreport(view: StubRepository, reported: list[str]) -> None:
        reported[0] = f"Loaded {len(view.records)} records into 1 entity."

    def report_nothing(view: StubRepository, reported: list[str]) -> None:
        reported.clear()

    def hide_the_engine(view: StubRepository, _reported: list[str]) -> None:
        # A repository whose STATE is perfect but whose engine will not say what
        # it is -- the case check 6 exists for, and the one every other check
        # passes.
        view.identity = {}

    def understate_the_work(view: StubRepository, reported: list[str]) -> None:
        # The fabrication shape: a plausible narrative over a counter that was
        # never incremented far enough to account for the records that are there.
        view.reported_add = max(len(view.records) - 1, 0)
        reported[:] = _reported_for(view)

    def report_no_counters(view: StubRepository, reported: list[str]) -> None:
        # SILENCE. The earlier draft of check 7 passed this, because it guarded
        # on `if said_add` -- so the run that reported nothing was the one run
        # the check could not catch.
        reported[:] = [
            f"Loaded {len(view.records)} records, which resolved to "
            f"{len(set(view.records.values()))} entities."
        ]

    # The shape that shipped a FALSE FAIL (run 35730635947): the repository holds
    # 159 records, the run reported 159, and the SDK read comes back EMPTY because
    # the export was asked for no entity classes. A populated repository must read
    # as populated; when it does not, the verdict must name the READ, not the
    # plugin. Both directions are asserted, because a guard that always fires is
    # as useless as one that never does.
    populated = StubRepository(rows)
    # Verbatim shape of the real run's final message (run 35730635947).
    said_loaded = [f"## {len(rows)} records -> **85 distinct entities**"]
    healthy_detail = run_checks(populated, rows, _reported_for(populated))[1]
    cases = [
        ("populated repo reads as populated", healthy_detail["engine_record_count"],
         len(rows), _reported_for(populated), healthy_detail["feature_spot_check"], False),
        ("populated repo reads as EMPTY (the CI false fail)", 0, len(rows), said_loaded, [], True),
        ("empty read, empty table, but the run said it loaded", 0, 0, said_loaded, [], True),
        ("nothing loaded and nothing claimed", 0, 0, [], [], False),
        ("every spot entity has no features", len(rows), len(rows), _reported_for(populated),
         [{"record": ["X", "1"], "expected": ["NAME"], "present": []}], True),
    ]
    for label, engine_records, sqlite_records, said, spot_features, want_fault in cases:
        got = read_fault(engine_records, sqlite_records, said, spot_features)
        if bool(got) != want_fault:
            problems.append(
                f"read-fault guard, '{label}': expected "
                f"{'a read fault' if want_fault else 'no read fault'}, got {got!r}"
            )

    mutate("data_went_in", drop_a_record)
    mutate("data_went_in", leave_redo_queued)
    mutate("er_ran", resolve_nothing)
    mutate("features_present", drop_a_feature)
    mutate("searchable", find_nothing)
    mutate("reported_matches_engine", misreport)
    mutate("reported_matches_engine", report_nothing)
    mutate("engine_identified", hide_the_engine)
    mutate("engine_work_reported", understate_the_work)
    mutate("engine_work_reported", report_no_counters)
    return problems


def self_test(out_path: Path | None) -> int:
    rows = read_fixture_rows(FIXTURE_DIR)
    key = read_key(KEY_FILE)
    fixture_records = {record_of(row) for row in rows}
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

    spot = pick_spot_records(rows)
    if len(spot) < 2:
        failures.append(f"only {len(spot)} spot-check record(s) could be selected — need 2 or 3")
    for row in spot:
        if not expected_features(row):
            failures.append(
                f"spot-check record {record_of(row)} supplies no mapped feature type — "
                "check 3 would assert nothing about it"
            )

    failures.extend(
        check_no_frozen_literals(
            {"record count": len(fixture_records), "entity count": len(clusters)}
        )
    )
    failures.extend(prove_checks_can_fail(rows))

    verdict = {
        "mode": "self-test",
        "verdict": "FAIL" if failures else "PASS",
        "headline": (
            f"{len(fixture_records)} fixture records agree with the key; every gating check "
            "was proven able to fail against a stub repository"
        ),
        "failures": failures,
        "ground_truth_key": str(KEY_FILE.relative_to(HERE)),
        "submitted_record_count": len(fixture_records),
        "truthset_key_entity_count": len(clusters),
        "spot_check_records": [
            {"record": list(record_of(row)), "expected_features": sorted(expected_features(row))}
            for row in spot
        ],
        "cluster_size_histogram": {
            str(size): sum(1 for c in clusters if len(c) == size)
            for size in sorted({len(c) for c in clusters})
        },
    }
    return emit(verdict, out_path)


# --------------------------------------------------------------------------
# Verify
# --------------------------------------------------------------------------
def verify(
    repo_db: Path,
    out_path: Path | None,
    reported_from: Path | None,
    sqlite_records: int,
) -> int:
    submitted = read_fixture_rows(FIXTURE_DIR)
    reported = final_messages(reported_from) if reported_from is not None else []
    if reported_from is not None and not reported:
        print(
            f"::warning::no final agent message found under {reported_from} — check 5 will "
            "fail, because the run's own numbers cannot be compared to the engine's"
        )

    view = SdkRepository(repo_db)
    failures, detail = run_checks(view, submitted, reported)
    signal = truthset_signal(view.record_to_entity())

    # Before any of the above is printed as a statement about the PLUGIN, ask
    # whether the read itself is the suspect. See read_fault().
    fault = read_fault(
        detail["engine_record_count"], sqlite_records, reported, detail["feature_spot_check"]
    )

    verdict = {
        "mode": "verify",
        "verdict": "ENVIRONMENTAL" if fault else ("FAIL" if failures else "PASS"),
        "headline": (
            f"{detail['engine_record_count']} records resolved to "
            f"{detail['engine_entity_count']} entities, the mapped features are queryable, "
            "and the run reported the engine's own numbers"
        ),
        # A read fault REPLACES the failure list rather than joining it: those
        # failures are all downstream of the bad read, and printing them as
        # co-equal is how the wrong first line gets believed.
        "failures": [fault] if fault else [message for _, message in failures],
        "failed_checks": [] if fault else sorted({check for check, _ in failures}),
        "suppressed_by_read_fault": (
            [message for _, message in failures] if fault else []
        ),
        "repository": str(repo_db),
        "repository_dsrc_record_rows": sqlite_records,
        "gating_checks": detail,
        "informational_truthset_signal": signal,
    }
    rc = emit(verdict, out_path)
    print_truthset_signal(signal)
    return rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true", help="offline consistency + ability-to-fail")
    group.add_argument("--repo-db", type=Path, help="path to the Senzing SQLite repository")
    group.add_argument(
        "--search-root",
        type=Path,
        help=f"directory to search for the {MARKER_NAME} marker (the repository is then "
        "looked for beside it, never anywhere else)",
    )
    parser.add_argument("--out", type=Path, help="also write the verdict JSON here")
    parser.add_argument(
        "--reported-from",
        type=Path,
        help="collected CLI trace file or directory; the run's own reported counts are read "
        "from the final agent message and compared against the engine (check 5)",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test(args.out)

    try:
        if args.search_root is not None:
            repo_db, sqlite_records = locate_repository(args.search_root)
        else:
            repo_db = args.repo_db
            if not repo_db.is_file():
                raise Environmental(f"no repository at {repo_db}")
            # The same SQLite oracle locate_repository() uses, so --repo-db gets
            # the read-fault guard too.
            sqlite_records = looks_like_senzing_repo(repo_db) or 0
        return verify(repo_db, args.out, args.reported_from, sqlite_records)
    except Environmental as exc:
        print(
            "::error::ENVIRONMENTAL FAILURE (not a plugin verdict) — "
            f"{exc} Do NOT change a skill, an eval case, a grader or an expected count in "
            "response to this.",
            file=sys.stderr,
        )
        return EXIT_ENVIRONMENTAL


if __name__ == "__main__":
    sys.exit(main())
