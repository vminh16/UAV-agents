"""Hợp đồng I-06/I-07: validator của cv/ khớp schema trong docs/interfaces và stub luôn phát đúng schema."""
from __future__ import annotations

import pytest
from conftest import EXAMPLES_DIR, load_json

from uav_cv.contracts import ContractError, errors, validate


@pytest.mark.parametrize("name", ["observation.example.json", "observation.invalid.example.json",
                                  "clip_ready.example.json"])
def test_official_examples_validate(name):
    schema = name.split(".")[0]
    assert errors(schema, load_json(EXAMPLES_DIR / name)) == []


@pytest.mark.parametrize("path", sorted((EXAMPLES_DIR / "invalid").glob("observation.*.json")),
                         ids=lambda p: p.name)
def test_official_negative_examples_rejected(path):
    with pytest.raises(ContractError):
        validate("observation", load_json(path))


@pytest.mark.parametrize("field, value", [
    ("llr", None),            # valid=true mà thiếu llr
    ("invalid_reasons", ["BLUR"]),
])
def test_valid_observation_rules(field, value):
    obs = load_json(EXAMPLES_DIR / "observation.example.json")
    obs[field] = value
    with pytest.raises(ContractError):
        validate("observation", obs)


def test_invalid_observation_requires_null_llr():
    obs = load_json(EXAMPLES_DIR / "observation.invalid.example.json")
    obs["llr"] = -1.0
    with pytest.raises(ContractError):
        validate("observation", obs)
