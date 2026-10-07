"""Nạp config YAML và tính ``config_hash`` cho provenance."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_ENV_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass(frozen=True)
class LoadedConfig:
    data: dict[str, Any]
    config_hash: str
    path: Path | None = None
    unresolved_env: tuple[str, ...] = field(default_factory=tuple)


def config_hash(data: Mapping[str, Any]) -> str:
    """``sha256:<hex>`` của JSON chuẩn hoá (khoá sắp xếp, không khoảng trắng)."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _expand(value: Any, env: Mapping[str, str], missing: set[str]) -> Any:
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            name = match.group(1)
            if name in env:
                return env[name]
            missing.add(name)
            return match.group(0)

        return _ENV_VAR.sub(repl, value)
    if isinstance(value, Mapping):
        return {k: _expand(v, env, missing) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(v, env, missing) for v in value]
    return value


def load_config(
    path: str | Path,
    env: Mapping[str, str] | None = None,
    strict_env: bool = False,
) -> LoadedConfig:
    """Đọc YAML, thay ``${VAR}`` bằng biến môi trường.

    ``config_hash`` tính trên nội dung **trước** khi thay biến môi trường, để mọi UAV
    chạy cùng một file config có cùng hash.
    """
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: config phải là một mapping YAML")
    missing: set[str] = set()
    data = _expand(copy.deepcopy(raw), os.environ if env is None else env, missing)
    if strict_env and missing:
        raise KeyError(f"{path}: thiếu biến môi trường {sorted(missing)}")
    return LoadedConfig(data=data, config_hash=config_hash(raw), path=path,
                        unresolved_env=tuple(sorted(missing)))
