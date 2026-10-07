from __future__ import annotations

import copy
import json
import subprocess
import sys

import pytest
from conftest import EXAMPLES_DIR, TESTS_DIR

import fake_perception as fpmod
from uav_cv.config import config_hash, load_config
from uav_cv.contracts import ContractError, errors


@pytest.fixture
def cfg() -> dict:
    return load_config(fpmod.DEFAULT_CONFIG).data


def make(cfg, seed=0, **overrides):
    cfg = copy.deepcopy(cfg)
    cfg.update(overrides)
    return fpmod.FakePerception(cfg, config_hash(cfg), seed=seed)


@pytest.mark.parametrize("scenario", fpmod.SCENARIOS)
def test_every_scenario_emits_valid_schema(cfg, clip_ready, scenario):
    fp = make(cfg)
    for _ in range(50):
        assert errors("observation", fp.observe(clip_ready, scenario=scenario)) == []


def test_smoke_llr_range(cfg, clip_ready):
    fp = make(cfg)
    for _ in range(100):
        obs = fp.observe(clip_ready, scenario="smoke")
        assert obs["valid"] and 1.5 <= obs["llr"] <= 3.5
        assert obs["smoke"]["detected"]


def test_no_smoke_llr_range(cfg, clip_ready):
    fp = make(cfg)
    for _ in range(100):
        obs = fp.observe(clip_ready, scenario="no_smoke")
        assert obs["valid"] and -3.0 <= obs["llr"] <= -1.0


def test_invalid_scenario(cfg, clip_ready):
    obs = make(cfg).observe(clip_ready, scenario="invalid")
    assert obs["valid"] is False
    assert obs["llr"] is None
    assert obs["invalid_reasons"] == ["SUN_GLARE"]
    assert obs["smoke"]["regions"] == []


def test_random_scenario_mixes_outcomes(cfg, clip_ready):
    fp = make(cfg, seed=1)
    obs = [fp.observe(clip_ready, scenario="random") for _ in range(400)]
    valid = [o for o in obs if o["valid"]]
    n_invalid = len(obs) - len(valid)
    n_pos = sum(o["llr"] > 0 for o in valid)
    assert 15 <= n_invalid <= 70                    # p_invalid = 0.1
    assert 0.35 < n_pos / len(valid) < 0.65         # p_smoke = 0.5
    for o in valid:                                 # nhãn thật khớp dấu LLR
        assert (o["llr"] > 0) == (o["features"]["stub_truth_smoke"] == 1.0)


def test_sequence_cycles(cfg, clip_ready):
    fp = make(cfg, sequence=["no_smoke", "invalid", "smoke"])
    got = [fp.observe(clip_ready) for _ in range(6)]
    kinds = ["invalid" if not o["valid"] else ("smoke" if o["llr"] > 0 else "no_smoke") for o in got]
    assert kinds == ["no_smoke", "invalid", "smoke"] * 2


def test_seed_reproducible(cfg, clip_ready):
    fa, fb = make(cfg, seed=7), make(cfg, seed=7)
    assert [fa.observe(clip_ready)["llr"] for _ in range(20)] == \
           [fb.observe(clip_ready)["llr"] for _ in range(20)]


def test_ids_copied_from_clip_ready(cfg, clip_ready):
    obs = make(cfg).observe(clip_ready, scenario="smoke")
    assert obs["view_id"] == clip_ready["view_id"]
    assert obs["clip_id"] == clip_ready["clip_id"]
    assert obs["header"]["mission_id"] == clip_ready["header"]["mission_id"]
    assert obs["header"]["uav_id"] == clip_ready["header"]["uav_id"]
    assert obs["header"]["producer"].startswith("cv/fake_perception@")
    assert obs["provenance"]["config_hash"].startswith("sha256:")
    assert fpmod.STUB_WARNING in obs["provenance"]["warnings"]


def test_geometry_gate_sun_glare(cfg, clip_ready):
    clip_ready["sun"]["azimuth_deg"] = 320.0          # camera yaw 315 → lệch 5°
    obs = make(cfg).observe(clip_ready, scenario="smoke")
    assert not obs["valid"] and obs["invalid_reasons"] == ["SUN_GLARE"]
    assert obs["context"]["sun_rel_azimuth_deg"] == pytest.approx(5.0)
    assert "glare_fraction" in obs["features"]


def test_geometry_gate_target_out_of_fov(cfg, clip_ready):
    clip_ready["pose_mean"]["gimbal_yaw_deg"] = 135.0
    obs = make(cfg).observe(clip_ready, scenario="no_smoke")
    assert not obs["valid"] and "TARGET_OUT_OF_FOV" in obs["invalid_reasons"]
    assert obs["context"]["target_in_fov"] is False


def test_geometry_gate_can_be_disabled(cfg, clip_ready):
    clip_ready["sun"]["azimuth_deg"] = 320.0
    cfg["geometry_gate"]["enabled"] = False
    assert make(cfg).observe(clip_ready, scenario="smoke")["valid"]


def test_rejects_bad_clip_ready(clip_ready):
    broken = copy.deepcopy(clip_ready)
    del broken["media"]["sha256"]
    with pytest.raises(ContractError):
        fpmod.check_clip_ready(broken, "0.1.0")
    other_major = copy.deepcopy(clip_ready)
    other_major["header"]["schema_version"] = "1.0.0"
    with pytest.raises(ValueError, match="major"):
        fpmod.check_clip_ready(other_major, "0.1.0")


def test_unknown_scenario_rejected(cfg):
    with pytest.raises(ValueError, match="kịch bản"):
        make(cfg, sequence=["smoke", "fire"])


def test_cli_once():
    out = subprocess.run(
        [sys.executable, str(TESTS_DIR / "fake_perception.py"),
         "--once", str(EXAMPLES_DIR / "clip_ready.example.json"), "--scenario", "smoke", "--seed", "3"],
        capture_output=True, text=True, encoding="utf-8", check=True, timeout=60,
    )
    obs = json.loads(out.stdout)
    assert errors("observation", obs) == []
    assert obs["valid"] and obs["llr"] > 0
    assert obs["provenance"]["methods"]["scenario"] == "smoke"
