"""Round-trip qua broker thật: publish clip_ready -> fake_perception -> nhận observation.

Bỏ qua nếu không có broker. Đổi broker bằng biến môi trường MQTT_HOST / MQTT_PORT.
"""
from __future__ import annotations

import json
import os
import queue
import socket
import subprocess
import sys
import uuid

import pytest
from conftest import TESTS_DIR

from uav_cv.contracts import errors
from uav_cv.messages import TOPIC_CLIP_READY, TOPIC_OBSERVATION

HOST = os.environ.get("MQTT_HOST", "localhost")
PORT = int(os.environ.get("MQTT_PORT", "1883"))


def _broker_up() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=1.0):
            return True
    except OSError:
        return False


pytestmark = [
    pytest.mark.mqtt,
    pytest.mark.skipif(not _broker_up(), reason=f"không có MQTT broker ở {HOST}:{PORT}"),
]


def test_roundtrip(clip_ready):
    import paho.mqtt.client as mqtt

    uav_id = f"uav-test-{uuid.uuid4().hex[:6]}"
    clip_ready["header"]["uav_id"] = uav_id
    received: queue.Queue[dict] = queue.Queue()

    stub = subprocess.Popen(
        [sys.executable, str(TESTS_DIR / "fake_perception.py"), "--host", HOST, "--port", str(PORT),
         "--uav-id", uav_id, "--sequence", "smoke,invalid", "--delay", "0.3", "--seed", "1"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
    )
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = lambda _c, _u, msg: received.put(json.loads(msg.payload))
    try:
        # Chờ stub đăng ký topic xong rồi mới phát.
        for line in stub.stdout:
            if "đã kết nối" in line:
                break
        else:
            pytest.fail("fake_perception thoát trước khi kết nối broker")

        client.connect(HOST, PORT)
        client.subscribe(TOPIC_OBSERVATION.format(uav_id=uav_id), qos=1)
        client.loop_start()
        topic_in = TOPIC_CLIP_READY.format(uav_id=uav_id)
        client.publish(topic_in, b"{not json", qos=1)                 # phải bị bỏ, không làm sập stub
        for _ in range(2):
            client.publish(topic_in, json.dumps(clip_ready), qos=1).wait_for_publish(5)

        first, second = received.get(timeout=10), received.get(timeout=10)
    finally:
        client.loop_stop()
        client.disconnect()
        stub.terminate()
        stub.wait(timeout=10)

    for obs in (first, second):
        assert errors("observation", obs) == []
        assert obs["header"]["uav_id"] == uav_id
        assert obs["latency_ms"]["total"] >= 300
    assert first["valid"] and first["llr"] > 0
    assert not second["valid"] and second["llr"] is None
