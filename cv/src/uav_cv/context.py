"""Ngữ cảnh góc nhìn ``observation.context`` tính từ ``clip_ready`` (20-cv §5.3).

Hệ toạ độ cục bộ ENU (Đông, Bắc, Lên) đặt tại UAV, xấp xỉ phẳng: sai số không đáng kể
ở cự ly vài trăm mét.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

EARTH_RADIUS_M = 6_371_008.8


def wrap_deg_180(angle_deg: float) -> float:
    """Đưa góc về [-180, 180)."""
    return (angle_deg + 180.0) % 360.0 - 180.0


def sun_relative_azimuth_deg(camera_yaw_deg: float, sun_azimuth_deg: float) -> float:
    """|wrap(yaw camera − phương vị mặt trời)| ∈ [0, 180]; 0 = nhìn thẳng vào mặt trời."""
    return abs(wrap_deg_180(camera_yaw_deg - sun_azimuth_deg))


def enu_offset_m(lat0_deg: float, lon0_deg: float, alt0_m: float,
                 lat1_deg: float, lon1_deg: float, alt1_m: float) -> np.ndarray:
    """Véc-tơ (E, N, U) từ điểm 0 tới điểm 1, đơn vị mét."""
    lat_mid = math.radians((lat0_deg + lat1_deg) / 2.0)
    d_north = math.radians(lat1_deg - lat0_deg) * EARTH_RADIUS_M
    d_east = math.radians(wrap_deg_180(lon1_deg - lon0_deg)) * EARTH_RADIUS_M * math.cos(lat_mid)
    return np.array([d_east, d_north, alt1_m - alt0_m])


def camera_axes(yaw_deg: float, pitch_deg: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Trục (phải, lên, trước) của camera trong ENU. Pitch: 0 = ngang, âm = chúc xuống."""
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    forward = np.array([math.cos(p) * math.sin(y), math.cos(p) * math.cos(y), math.sin(p)])
    right = np.array([math.cos(y), -math.sin(y), 0.0])
    up = np.array([-math.sin(p) * math.sin(y), -math.sin(p) * math.cos(y), math.cos(p)])
    return right, up, forward


@dataclass(frozen=True)
class ViewGeometry:
    range_m: float
    height_above_target_m: float
    camera_yaw_deg: float
    camera_pitch_deg: float
    sun_rel_azimuth_deg: float
    sun_elevation_deg: float
    target_in_fov: bool
    target_px: tuple[float, float] | None
    image_size: tuple[int, int]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def target_norm(self) -> tuple[float, float] | None:
        if self.target_px is None:
            return None
        width, height = self.image_size
        return self.target_px[0] / width, self.target_px[1] / height

    def to_context(self) -> dict[str, Any]:
        return {
            "range_m": round(self.range_m, 2),
            "height_above_target_m": round(self.height_above_target_m, 2),
            "sun_rel_azimuth_deg": round(self.sun_rel_azimuth_deg, 2),
            "sun_elevation_deg": round(self.sun_elevation_deg, 2),
            "target_in_fov": self.target_in_fov,
            "base_occlusion_ratio": None,
        }


def _intrinsics(clip_ready: Mapping[str, Any]) -> tuple[float, float, float, float]:
    media, camera = clip_ready["media"], clip_ready["camera"]
    width, height = media["width"], media["height"]
    k = camera.get("intrinsics")
    if k:
        return k["fx"], k["fy"], k["cx"], k["cy"]
    fx = (width / 2.0) / math.tan(math.radians(camera["hfov_deg"]) / 2.0)
    fy = (height / 2.0) / math.tan(math.radians(camera["vfov_deg"]) / 2.0)
    return fx, fy, width / 2.0, height / 2.0


def compute_view_geometry(clip_ready: Mapping[str, Any]) -> ViewGeometry:
    pose, target, media = clip_ready["pose_mean"], clip_ready["target"], clip_ready["media"]
    view, sun = clip_ready["view"], clip_ready["sun"]
    warnings: list[str] = []

    to_target = enu_offset_m(pose["lat_deg"], pose["lon_deg"], pose["alt_amsl_m"],
                             target["lat_deg"], target["lon_deg"], clip_ready["target_ground_amsl_m"])
    horizontal = float(math.hypot(to_target[0], to_target[1]))
    range_m = float(np.linalg.norm(to_target))

    camera_yaw = pose.get("gimbal_yaw_deg")
    if camera_yaw is None:
        camera_yaw = pose["yaw_deg"]
        warnings.append("gimbal_yaw_deg=null: dùng yaw thân máy bay làm yaw camera")

    camera_pitch = pose.get("gimbal_pitch_deg")
    if camera_pitch is None:
        look_at_pitch = math.degrees(math.atan2(to_target[2], horizontal))
        camera_pitch = look_at_pitch + view["gimbal"].get("pitch_offset_deg", 0.0)
        warnings.append("gimbal_pitch_deg=null: giả định gimbal nhìn vào mục tiêu + pitch_offset_deg")

    right, up, forward = camera_axes(camera_yaw, camera_pitch)
    depth = float(to_target @ forward)
    width, height = media["width"], media["height"]
    target_px = None
    in_fov = False
    if depth > 0:
        fx, fy, cx, cy = _intrinsics(clip_ready)
        # Mô hình pinhole, bỏ qua méo ống kính.
        u = cx + fx * float(to_target @ right) / depth
        v = cy - fy * float(to_target @ up) / depth
        target_px = (u, v)
        in_fov = 0.0 <= u <= width and 0.0 <= v <= height

    return ViewGeometry(
        range_m=range_m,
        height_above_target_m=float(view["height_above_target_m"]),
        camera_yaw_deg=float(camera_yaw),
        camera_pitch_deg=float(camera_pitch),
        sun_rel_azimuth_deg=sun_relative_azimuth_deg(camera_yaw, sun["azimuth_deg"]),
        sun_elevation_deg=float(sun["elevation_deg"]),
        target_in_fov=in_fov,
        target_px=target_px,
        image_size=(width, height),
        warnings=tuple(warnings),
    )
