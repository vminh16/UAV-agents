from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
CV_DIR = TESTS_DIR.parent
REPO_ROOT = CV_DIR.parent
EXAMPLES_DIR = REPO_ROOT / "docs" / "interfaces" / "examples"

for path in (CV_DIR / "src", TESTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def clip_ready_example() -> dict:
    return load_json(EXAMPLES_DIR / "clip_ready.example.json")


@pytest.fixture
def clip_ready(clip_ready_example) -> dict:
    """Bản sao sửa được của ví dụ clip_ready chính thức."""
    return copy.deepcopy(clip_ready_example)
