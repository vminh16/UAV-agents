#!/usr/bin/env python3
"""fake_perception — stub của ``perception_service`` cho AGT/EMB/BE kiểm thử độc lập.

Nghe I-06 ``uav/{uav_id}/embedded/clip_ready``, chờ ``processing_delay_s`` rồi phát I-07
``uav/{uav_id}/cv/observation`` hợp lệ theo schema. LLR là số giả lập theo kịch bản
(cấu hình trong ``cv/configs/fake_perception.yaml``); ``context`` tính thật từ tư thế
trong ``clip_ready``.

Chạy với MQTT broker::

    python cv/tests/fake_perception.py --scenario random --seed 42
    python cv/tests/fake_perception.py --sequence no_smoke,invalid,smoke,smoke

Không cần broker (in observation ra stdout)::

    python cv/tests/fake_perception.py --once docs/interfaces/examples/clip_ready.example.json --scenario smoke
"""
from __future__ import annotations

import argparse
import itertools
import json
import logging
import queue
import random
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

CV_DIR = Path(__file__).resolve().parents[1]
try:
    import uav_cv  # noqa: F401
except ImportError:
    sys.path.insert(0, str(CV_DIR / "src"))

from uav_cv import __version__  # noqa: E402
from uav_cv.config import config_hash, load_config  # noqa: E402
from uav_cv.context import compute_view_geometry  # noqa: E402
from uav_cv.contracts import ContractError, validate  # noqa: E402
from uav_cv.messages import (  # noqa: E402
    MQTT_QOS, TOPIC_CLIP_READY, TOPIC_OBSERVATION, major, make_header,
)

COMPONENT = "cv/fake_perception"
PRODUCER = f"{COMPONENT}@{__version__}"
DEFAULT_CONFIG = CV_DIR / "configs" / "fake_perception.yaml"
SCENARIOS = ("smoke", "no_smoke", "invalid", "random")
STUB_WARNING = "STUB fake_perception: quan sát giả lập, không đến từ mô hình thật"

# Đặc trưng minh hoạ (agent không dùng). Khoảng giá trị phỏng theo bảng vật lý ở 20-cv §3.
_FEATURE_RANGES = {
    True: {"flow_vertical_mps": (0.8, 2.0), "flow_divergence": (0.10, 0.40),
           "flow_coherence": (0.60, 0.90), "source_point_score": (0.50, 0.90)},
    False: {"flow_vertical_mps": (-0.2, 0.3), "flow_divergence": (-0.05, 0.05),
            "flow_coherence": (0.10, 0.50), "source_point_score": (0.00, 0.30)},
}

log = logging.getLogger("fake_perception")


def git_sha() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=CV_DIR,
                             capture_output=True, text=True, timeout=5, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    sha = out.stdout.strip()
    return sha or None


class FakePerception:
    """Sinh observation từ clip_ready. Không chứa MQTT để test được trực tiếp."""

    def __init__(self, cfg: dict[str, Any], config_hash: str, seed: int | None = None):
        self.cfg = cfg
        self.config_hash = config_hash
        self.rng = random.Random(seed)
        self.git_sha = git_sha()
        sequence = cfg.get("sequence") or []
        for name in [cfg.get("scenario"), *sequence]:
            if name not in SCENARIOS:
                raise ValueError(f"kịch bản không hợp lệ: {name!r}. Hợp lệ: {SCENARIOS}")
        self._sequence = itertools.cycle(sequence) if sequence else None

    def next_scenario(self) -> str:
        return next(self._sequence) if self._sequence else self.cfg["scenario"]

    def _draw(self, scenario: str) -> tuple[bool, list[str]]:
        """Bốc (H thật, lý do hỏng do kịch bản)."""
        p_smoke = self.cfg["random"]["p_smoke"]
        if scenario == "smoke":
            return True, []
        if scenario == "no_smoke":
            return False, []
        if scenario == "invalid":
            return self.rng.random() < p_smoke, list(self.cfg["invalid"]["reasons"])
        is_smoke = self.rng.random() < p_smoke
        if self.rng.random() < self.cfg["random"]["p_invalid"]:
            return is_smoke, [self.rng.choice(self.cfg["invalid"]["random_reasons"])]
        return is_smoke, []

    def _geometry_reasons(self, geometry) -> list[str]:
        gate = self.cfg["geometry_gate"]
        if not gate["enabled"]:
            return []
        reasons = []
        if geometry.sun_rel_azimuth_deg < gate["sun_glare_rel_azimuth_deg"]:
            reasons.append("SUN_GLARE")
        if gate["target_out_of_fov"] and not geometry.target_in_fov:
            reasons.append("TARGET_OUT_OF_FOV")
        return reasons

    def _smoke_block(self, is_smoke: bool, valid: bool, target_norm) -> dict[str, Any]:
        fires = valid and (is_smoke or self.rng.random() < 0.3)
        if not fires:
            return {"detected": False, "max_score": round(self.rng.uniform(0.0, 0.15), 3), "regions": []}
        score = self.rng.uniform(0.5, 0.9) if is_smoke else self.rng.uniform(0.15, 0.45)
        cx, base_y = target_norm if target_norm else (0.5, 0.6)
        w, h = self.rng.uniform(0.08, 0.25), self.rng.uniform(0.15, 0.45)
        x0, x1 = max(0.0, cx - w / 2), min(1.0, cx + w / 2)
        y0, y1 = max(0.0, base_y - h), min(1.0, base_y)
        region = {"bbox_norm": [round(v, 4) for v in (x0, y0, x1, y1)],
                  "score": round(score, 3),
                  "area_frac": round((x1 - x0) * (y1 - y0), 4)}
        return {"detected": True, "max_score": region["score"], "regions": [region]}

    def observe(self, clip_ready: dict[str, Any], scenario: str | None = None,
                latency_s: float | None = None) -> dict[str, Any]:
        """Trả observation đã validate theo schema."""
        scenario = scenario or self.next_scenario()
        geometry = compute_view_geometry(clip_ready)
        is_smoke, reasons = self._draw(scenario)
        for reason in self._geometry_reasons(geometry):
            if reason not in reasons:
                reasons.append(reason)
        valid = not reasons

        llr = None
        if valid:
            lo, hi = self.cfg["llr_range"]["smoke" if is_smoke else "no_smoke"]
            clip = self.cfg["llr_clip"]
            llr = round(max(-clip, min(clip, self.rng.uniform(lo, hi))), 3)

        features: dict[str, float | None] = {"stub_truth_smoke": 1.0 if is_smoke else 0.0}
        if valid:
            features.update({k: round(self.rng.uniform(*r), 3)
                             for k, r in _FEATURE_RANGES[is_smoke].items()})
        if "SUN_GLARE" in reasons:
            features["glare_fraction"] = round(self.rng.uniform(0.25, 0.6), 3)

        header_in = clip_ready["header"]
        latency_s = self.cfg["processing_delay_s"] if latency_s is None else latency_s
        observation = {
            "header": make_header("observation", self.cfg["schema_version"], header_in["uav_id"],
                                  header_in["mission_id"], PRODUCER),
            "view_id": clip_ready["view_id"],
            "clip_id": clip_ready["clip_id"],
            "valid": valid,
            "invalid_reasons": reasons,
            "llr": llr,
            "observation_model_version": self.cfg["observation_model_version"],
            "context": geometry.to_context(),
            "smoke": self._smoke_block(is_smoke, valid, geometry.target_norm),
            "features": features,
            "landcover_at_base": None,
            "latency_ms": {"total": round(latency_s * 1000.0, 1)},
            "provenance": {
                "component": COMPONENT,
                "version": __version__,
                "config_hash": self.config_hash,
                "git_sha": self.git_sha,
                "methods": {"stub": "fake_perception", "scenario": scenario},
                "artifacts": [{"name": "observation_model",
                               "version": self.cfg["observation_model_version"]}],
                "warnings": [STUB_WARNING, *geometry.warnings],
            },
        }
        validate("observation", observation)
        return observation


def check_clip_ready(clip_ready: Any, expected_schema_version: str) -> None:
    """Ném ContractError/ValueError nếu clip_ready sai schema hoặc khác major version."""
    validate("clip_ready", clip_ready)
    theirs = clip_ready["header"]["schema_version"]
    if major(theirs) != major(expected_schema_version):
        raise ValueError(f"schema_version {theirs} khác major với {expected_schema_version}")


def run_mqtt(fp: FakePerception, host: str, port: int, uav_id: str, delay_s: float) -> None:
    import paho.mqtt.client as mqtt

    topic_in = TOPIC_CLIP_READY.format(uav_id=uav_id)
    jobs: queue.Queue[tuple[float, str, bytes]] = queue.Queue()

    def on_connect(client, _userdata, _flags, reason_code, _properties):
        if reason_code.is_failure:
            log.error("kết nối broker thất bại: %s", reason_code)
            return
        client.subscribe(topic_in, qos=MQTT_QOS)
        log.info("đã kết nối %s:%d, nghe %s", host, port, topic_in)

    def on_message(_client, _userdata, msg):
        jobs.put((time.monotonic(), msg.topic, msg.payload))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=f"cv-fake-perception-{uuid.uuid4().hex[:8]}")
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(host, port, keepalive=30)
    except OSError as exc:
        raise SystemExit(f"không kết nối được MQTT broker {host}:{port}: {exc}") from exc
    client.loop_start()
    try:
        while True:
            received, topic, payload = jobs.get()
            try:
                clip_ready = json.loads(payload)
                check_clip_ready(clip_ready, fp.cfg["schema_version"])
            except (json.JSONDecodeError, ContractError, ValueError) as exc:
                log.error("bỏ clip_ready trên %s: %s", topic, exc)
                continue
            remaining = delay_s - (time.monotonic() - received)
            if remaining > 0:
                time.sleep(remaining)
            observation = fp.observe(clip_ready, latency_s=time.monotonic() - received)
            topic_out = TOPIC_OBSERVATION.format(uav_id=observation["header"]["uav_id"])
            client.publish(topic_out, json.dumps(observation, ensure_ascii=False), qos=MQTT_QOS)
            log.info("%s -> %s valid=%s llr=%s reasons=%s", observation["clip_id"], topic_out,
                     observation["valid"], observation["llr"], observation["invalid_reasons"])
    except KeyboardInterrupt:
        log.info("dừng")
    finally:
        client.loop_stop()
        client.disconnect()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--host", help="MQTT host (ghi đè io.mqtt_host)")
    p.add_argument("--port", type=int, help="MQTT port (ghi đè io.mqtt_port)")
    p.add_argument("--uav-id", help='uav_id để nghe; "+" = mọi UAV (ghi đè io.uav_id)')
    p.add_argument("--scenario", choices=SCENARIOS)
    p.add_argument("--sequence", help="danh sách kịch bản cách nhau bởi dấu phẩy, lặp vòng")
    p.add_argument("--p-smoke", type=float)
    p.add_argument("--p-invalid", type=float)
    p.add_argument("--delay", type=float, help="giây giả lập xử lý (ghi đè processing_delay_s)")
    p.add_argument("--seed", type=int)
    p.add_argument("--no-geometry-gate", action="store_true",
                   help="tắt đánh dấu SUN_GLARE/TARGET_OUT_OF_FOV theo hình học")
    p.add_argument("--once", type=Path, metavar="CLIP_READY_JSON",
                   help="xử lý một file clip_ready, in observation ra stdout, không dùng MQTT")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def apply_overrides(cfg: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if args.host:
        cfg["io"]["mqtt_host"] = args.host
    if args.port:
        cfg["io"]["mqtt_port"] = args.port
    if args.uav_id:
        cfg["io"]["uav_id"] = args.uav_id
    if args.scenario:
        cfg["scenario"] = args.scenario
        cfg["sequence"] = []
    if args.sequence:
        cfg["sequence"] = [s.strip() for s in args.sequence.split(",") if s.strip()]
    if args.p_smoke is not None:
        cfg["random"]["p_smoke"] = args.p_smoke
    if args.p_invalid is not None:
        cfg["random"]["p_invalid"] = args.p_invalid
    if args.delay is not None:
        cfg["processing_delay_s"] = args.delay
    if args.seed is not None:
        cfg["seed"] = args.seed
    if args.no_geometry_gate:
        cfg["geometry_gate"]["enabled"] = False
    return cfg


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = apply_overrides(load_config(args.config).data, args)
    fp = FakePerception(cfg, config_hash(cfg), seed=cfg.get("seed"))

    if args.once:
        clip_ready = json.loads(args.once.read_text(encoding="utf-8"))
        check_clip_ready(clip_ready, cfg["schema_version"])
        print(json.dumps(fp.observe(clip_ready), ensure_ascii=False, indent=2))
        return 0

    io = cfg["io"]
    run_mqtt(fp, io["mqtt_host"], int(io["mqtt_port"]), io["uav_id"], cfg["processing_delay_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
