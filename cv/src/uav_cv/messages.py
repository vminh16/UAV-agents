"""Header chung, topic MQTT và mốc thời gian theo 50-interfaces §1–2."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

TOPIC_CLIP_READY = "uav/{uav_id}/embedded/clip_ready"
TOPIC_OBSERVATION = "uav/{uav_id}/cv/observation"
MQTT_QOS = 1


def utc_now() -> str:
    """RFC 3339 UTC có mili-giây, ví dụ ``2026-10-02T03:15:22.123Z``."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def make_header(schema: str, schema_version: str, uav_id: str,
                mission_id: str | None, producer: str) -> dict[str, Any]:
    return {
        "schema": schema,
        "schema_version": schema_version,
        "msg_id": str(uuid.uuid4()),
        "uav_id": uav_id,
        "mission_id": mission_id,
        "stamp_utc": utc_now(),
        "producer": producer,
    }


def major(version: str) -> str:
    return version.split(".", 1)[0]
