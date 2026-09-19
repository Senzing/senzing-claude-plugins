#!/usr/bin/env python3
"""Prove this container can actually run Senzing — before any API budget is spent.

Builds a throwaway SQLite repository exactly the way the `analyze` skill does on a
user's machine (sdk_guide topic='install'/'configure'/'load', platform='linux_apt'),
loads three records that must resolve into two entities, drains the redo queue and
reads the result back through the engine.

If this fails, the job fails here — loudly, cheaply, and with "Senzing cannot run
on this host" rather than a plugin-quality verdict. It never degrades to a
simulated result.

No license is involved: three records, and Senzing's no-license ceiling is 500
Distinct Source Records.

Usage: preflight.py [workdir]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = "/etc/opt/senzing"
RESOURCE_PATH = "/opt/senzing/er/resources"
SUPPORT_PATH = "/opt/senzing/data"
SCHEMA_SQL = f"{RESOURCE_PATH}/schema/szcore-schema-sqlite-create.sql"

DATA_SOURCE = "PREFLIGHT"
# Two of these three are the same person with a different name form and the same
# address and phone; the third is unrelated. Expect 2 entities from 3 records.
RECORDS = [
    (
        "1",
        {
            "DATA_SOURCE": DATA_SOURCE,
            "RECORD_ID": "1",
            "PRIMARY_NAME_FULL": "Robert Smith",
            "DATE_OF_BIRTH": "12/11/1978",
            "ADDR_FULL": "123 Main Street, Las Vegas NV 89132",
            "PHONE_NUMBER": "702-919-1300",
        },
    ),
    (
        "2",
        {
            "DATA_SOURCE": DATA_SOURCE,
            "RECORD_ID": "2",
            "PRIMARY_NAME_FULL": "Bob Smith",
            "DATE_OF_BIRTH": "12/11/1978",
            "ADDR_FULL": "123 Main Street, Las Vegas NV 89132",
            "PHONE_NUMBER": "702-919-1300",
        },
    ),
    (
        "3",
        {
            "DATA_SOURCE": DATA_SOURCE,
            "RECORD_ID": "3",
            "PRIMARY_NAME_FULL": "Maria Gonzalez",
            "DATE_OF_BIRTH": "3/2/1991",
            "ADDR_FULL": "44 Oak Avenue, Portland OR 97205",
            "PHONE_NUMBER": "503-555-0142",
        },
    ),
]


def die(message: str) -> None:
    print(f"::error::Senzing preflight FAILED — {message}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    workdir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/sz-preflight")
    workdir.mkdir(parents=True, exist_ok=True)
    repo_db = workdir / "G2C.db"
    if repo_db.exists():
        repo_db.unlink()

    # The DB file is NOT auto-created: make the schema first (sdk_guide).
    if not Path(SCHEMA_SQL).is_file():
        die(f"the SQLite schema {SCHEMA_SQL} is missing — the SDK install is incomplete")
    with Path(SCHEMA_SQL).open(encoding="utf-8") as schema:
        result = subprocess.run(  # noqa: S603
            ["sqlite3", str(repo_db)], stdin=schema, capture_output=True, text=True, check=False
        )
    if result.returncode != 0:
        die(f"creating the SQLite schema failed: {result.stderr.strip()}")

    try:
        from senzing import SzError
        from senzing_core import SzAbstractFactoryCore
    except ImportError as exc:
        die(
            f"the Senzing Python SDK is not importable ({exc}). "
            "PYTHONPATH=/opt/senzing/er/sdk/python, LD_LIBRARY_PATH=/opt/senzing/er/lib"
        )
        return 1

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

    try:
        factory = SzAbstractFactoryCore("preflight", settings, verbose_logging=False)

        product = factory.create_product()
        print("Senzing version:", json.loads(product.get_version()).get("VERSION"))
        license_info = json.loads(product.get_license())
        print(
            "license:",
            license_info.get("licenseType") or "evaluation (no license file)",
            "| record limit:",
            license_info.get("recordLimit"),
        )

        config_manager = factory.create_configmanager()
        config = config_manager.create_config_from_template()
        config.register_data_source(DATA_SOURCE)
        config_id = config_manager.set_default_config(config.export(), "preflight")
        # Required: without this the engine keeps using the previous config.
        factory.reinitialize(config_id)

        engine = factory.create_engine()
        for record_id, record in RECORDS:
            engine.add_record(DATA_SOURCE, record_id, json.dumps(record))

        processed = 0
        while engine.count_redo_records():
            redo_record = engine.get_redo_record()
            if not redo_record:
                break
            engine.process_redo_record(redo_record)
            processed += 1
        print(f"redo records processed: {processed}; queue now {engine.count_redo_records()}")

        entity_ids = set()
        for record_id, _ in RECORDS:
            blob = engine.get_entity_by_record_id(DATA_SOURCE, record_id)
            entity_ids.add(json.loads(blob)["RESOLVED_ENTITY"]["ENTITY_ID"])
    except SzError as err:
        die(f"{err.__class__.__name__}: {err}")
        return 1

    print(f"3 records -> {len(entity_ids)} entities")
    if len(entity_ids) != 2:
        die(
            f"expected 3 records to resolve to 2 entities, got {len(entity_ids)}. "
            "The engine runs but is not resolving as this Senzing version should; "
            "the end-to-end ground-truth check downstream would be meaningless."
        )
    print("Senzing preflight OK — this host can map, load, resolve and read back.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
