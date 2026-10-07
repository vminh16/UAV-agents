"""Validate thông điệp theo JSON Schema đọc trực tiếp từ ``docs/interfaces/schemas/``.

Không chép schema vào module (CONTRIBUTING §2.3). Thư mục schema tìm theo thứ tự:
biến môi trường ``UAV_SCHEMA_DIR``, rồi đi ngược từ file này lên tới gốc repo.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

_SCHEMA_SUBDIR = Path("docs") / "interfaces" / "schemas"


class ContractError(ValueError):
    def __init__(self, schema: str, errors: list[str]):
        self.schema = schema
        self.errors = errors
        super().__init__(f"thông điệp không khớp schema '{schema}':\n  " + "\n  ".join(errors))


def find_schema_dir() -> Path:
    override = os.environ.get("UAV_SCHEMA_DIR")
    if override:
        path = Path(override)
        if not path.is_dir():
            raise FileNotFoundError(f"UAV_SCHEMA_DIR={override} không phải thư mục")
        return path
    for parent in Path(__file__).resolve().parents:
        candidate = parent / _SCHEMA_SUBDIR
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f"không tìm thấy {_SCHEMA_SUBDIR}; đặt biến môi trường UAV_SCHEMA_DIR")


@lru_cache(maxsize=None)
def _load(schema_dir: Path) -> tuple[dict[str, dict], Registry]:
    schemas = {p.name.removesuffix(".schema.json"): json.loads(p.read_text(encoding="utf-8"))
               for p in sorted(schema_dir.glob("*.schema.json"))}
    resources = []
    for name, schema in schemas.items():
        resource = Resource.from_contents(schema)
        resources.append((schema["$id"], resource))
        resources.append((f"{name}.schema.json", resource))
    return schemas, Registry().with_resources(resources)


@lru_cache(maxsize=None)
def validator(name: str, schema_dir: Path | None = None) -> Draft202012Validator:
    schemas, registry = _load(schema_dir or find_schema_dir())
    if name not in schemas:
        raise KeyError(f"không có schema '{name}'. Có: {', '.join(schemas)}")
    return Draft202012Validator(schemas[name], registry=registry, format_checker=FormatChecker())


def errors(name: str, instance: Any) -> list[str]:
    out = []
    for err in sorted(validator(name).iter_errors(instance), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"{path}: {err.message}")
    return out


def validate(name: str, instance: Any) -> None:
    """Ném ``ContractError`` nếu ``instance`` không khớp schema ``name``."""
    found = errors(name, instance)
    if found:
        raise ContractError(name, found)
