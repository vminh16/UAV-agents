#!/usr/bin/env python3
"""Validate interface contracts.

1. Every schema in ../schemas is a valid JSON Schema (draft 2020-12).
2. Every example in ../examples validates against its schema. The schema is
   chosen by the file-name prefix: ``<schema>.<anything>.json``.
3. Every schema except ``common`` has at least one example.
4. Every file in ../examples/invalid FAILS validation (guards against
   accidentally loosened rules).

Usage:  python docs/interfaces/tools/validate.py
Requires: jsonschema>=4.18 (pip install -r docs/interfaces/tools/requirements.txt)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = ROOT / "examples"


def load_schemas() -> dict[str, dict]:
    return {p.name.removesuffix(".schema.json"): json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(SCHEMA_DIR.glob("*.schema.json"))}


def build_registry(schemas: dict[str, dict]) -> Registry:
    resources = []
    for name, schema in schemas.items():
        resource = Resource.from_contents(schema)
        resources.append((schema["$id"], resource))
        resources.append((f"{name}.schema.json", resource))
    return Registry().with_resources(resources)


def main() -> int:
    schemas = load_schemas()
    registry = build_registry(schemas)
    errors: list[str] = []

    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - report every broken schema
            errors.append(f"[schema] {name}: {exc}")

    covered: set[str] = set()
    for example in sorted(EXAMPLE_DIR.glob("*.json")):
        name = example.name.split(".")[0]
        if name not in schemas:
            errors.append(f"[example] {example.name}: no schema named '{name}'")
            continue
        covered.add(name)
        validator = Draft202012Validator(schemas[name], registry=registry, format_checker=FormatChecker())
        instance = json.loads(example.read_text(encoding="utf-8"))
        for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
            path = "/".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append(f"[example] {example.name} @ {path}: {err.message}")

    for name in schemas:
        if name != "common" and name not in covered:
            errors.append(f"[coverage] schema '{name}' has no example in {EXAMPLE_DIR.name}/")

    # Negative examples: each must violate the contract. If one validates,
    # a schema rule has been loosened by accident.
    for example in sorted((EXAMPLE_DIR / "invalid").glob("*.json")):
        name = example.name.split(".")[0]
        if name not in schemas:
            errors.append(f"[invalid] {example.name}: no schema named '{name}'")
            continue
        validator = Draft202012Validator(schemas[name], registry=registry, format_checker=FormatChecker())
        if validator.is_valid(json.loads(example.read_text(encoding="utf-8"))):
            errors.append(f"[invalid] {example.name}: expected to FAIL but validated")

    if errors:
        print("\n".join(errors))
        print(f"\nFAILED: {len(errors)} problem(s)")
        return 1
    n_valid = len(list(EXAMPLE_DIR.glob("*.json")))
    n_invalid = len(list((EXAMPLE_DIR / "invalid").glob("*.json")))
    print(f"OK: {len(schemas)} schemas, {n_valid} valid examples, {n_invalid} invalid examples rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
