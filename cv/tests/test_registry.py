from __future__ import annotations

from pathlib import Path

import pytest

from uav_cv import registry
from uav_cv.config import config_hash, load_config

PIPELINE_CONFIG = Path(__file__).resolve().parents[1] / "configs" / "pipeline.default.yaml"


@pytest.fixture
def clean_registry():
    saved = {slot: dict(methods) for slot, methods in registry._REGISTRY.items()}
    yield
    registry._REGISTRY.clear()
    registry._REGISTRY.update(saved)


def test_register_and_build(clean_registry):
    @registry.register("detector", "dummy_det")
    class DummyDetector:
        def __init__(self, min_score, input_size=640, extra=None):
            self.min_score, self.input_size, self.extra = min_score, input_size, extra

    config = {"detector": {"method": "dummy_det", "min_score": 0.2, "input_size": 320,
                           "dummy_det": {"extra": "x"}, "other_method": {"ignored": True}}}
    det = registry.build(config, "detector")
    assert isinstance(det, DummyDetector)
    assert (det.min_score, det.input_size, det.extra) == (0.2, 320, "x")
    assert "dummy_det" in registry.available("detector")


def test_runtime_slot_uses_backend_key(clean_registry):
    registry.register("runtime", "dummy_rt")(lambda **kw: kw)
    assert registry.build({"runtime": {"backend": "dummy_rt", "max_latency_s": 5.0}}, "runtime") == \
        {"max_latency_s": 5.0}


def test_disabled_slot_builds_none():
    assert registry.build({"landcover": {"method": None}}, "landcover") is None
    assert registry.build({}, "landcover") is None


def test_unknown_method_and_slot_raise():
    with pytest.raises(registry.RegistryError, match="chưa đăng ký"):
        registry.get("detector", "no_such_method")
    with pytest.raises(registry.RegistryError, match="khe không tồn tại"):
        registry.register("no_such_slot", "x")


def test_duplicate_registration_rejected(clean_registry):
    registry.register("calibrator", "dup")(lambda: 1)
    with pytest.raises(registry.RegistryError, match="đã được đăng ký"):
        registry.register("calibrator", "dup")(lambda: 2)


def test_selected_methods_from_default_pipeline():
    cfg = load_config(PIPELINE_CONFIG, env={"UAV_ID": "uav-01", "UAV_ARTIFACT_DIR": "/opt/a"}).data
    assert registry.selected_methods(cfg) == {
        "quality_gate": "heuristic_gate",
        "stabilization": "ecc_affine",
        "detector": "yolo11n",
        "plume_tracker": "iou_tracker",
        "motion_features": "dis_flow",
        "clip_classifier": "gbdt",
        "calibrator": "isotonic_binned",
        "runtime": "ncnn",
    }
    assert registry.params_for(cfg, "quality_gate")["min_laplacian_var"] == 60.0
    assert cfg["io"]["uav_id"] == "uav-01"


def test_config_hash_independent_of_env():
    a = load_config(PIPELINE_CONFIG, env={"UAV_ID": "uav-01", "UAV_ARTIFACT_DIR": "/a"})
    b = load_config(PIPELINE_CONFIG, env={"UAV_ID": "uav-02", "UAV_ARTIFACT_DIR": "/b"})
    assert a.config_hash == b.config_hash
    assert a.config_hash.startswith("sha256:") and len(a.config_hash) == 7 + 64


def test_missing_env_reported_or_strict():
    loaded = load_config(PIPELINE_CONFIG, env={})
    assert loaded.unresolved_env == ("UAV_ARTIFACT_DIR", "UAV_ID")
    with pytest.raises(KeyError):
        load_config(PIPELINE_CONFIG, env={}, strict_env=True)


def test_config_hash_is_key_order_independent():
    assert config_hash({"a": 1, "b": [1, 2]}) == config_hash({"b": [1, 2], "a": 1})
