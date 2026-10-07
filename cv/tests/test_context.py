from __future__ import annotations

import math

import pytest

from uav_cv.context import compute_view_geometry, sun_relative_azimuth_deg, wrap_deg_180


@pytest.mark.parametrize("cam, sun, expected", [
    (315.0, 148.3, 166.7),
    (350.0, 10.0, 20.0),     # qua Bắc: không được ra 340
    (10.0, 350.0, 20.0),
    (90.0, 90.0, 0.0),
    (0.0, 180.0, 180.0),
])
def test_sun_relative_azimuth(cam, sun, expected):
    assert sun_relative_azimuth_deg(cam, sun) == pytest.approx(expected)


def test_wrap():
    assert wrap_deg_180(190.0) == pytest.approx(-170.0)
    assert wrap_deg_180(-190.0) == pytest.approx(170.0)


def test_example_clip_geometry(clip_ready):
    g = compute_view_geometry(clip_ready)
    # Ví dụ: UAV cách mục tiêu ~150 m ngang, cao hơn mặt đất mục tiêu 104,2 m.
    assert g.range_m == pytest.approx(math.hypot(150.0, 104.2), abs=3.0)
    assert g.height_above_target_m == 100.0
    assert g.sun_rel_azimuth_deg == pytest.approx(166.7, abs=0.01)
    assert g.target_in_fov
    u, v = g.target_norm
    assert abs(u - 0.5) < 0.05          # gimbal yaw nhìn đúng phương vị mục tiêu
    assert 0.5 < v < 1.0                # mục tiêu dưới tâm ảnh (pitch_offset +5° ngẩng lên)
    assert g.warnings == ()

    ctx = g.to_context()
    assert set(ctx) == {"range_m", "height_above_target_m", "sun_rel_azimuth_deg",
                        "sun_elevation_deg", "target_in_fov", "base_occlusion_ratio"}
    assert ctx["base_occlusion_ratio"] is None


def test_target_behind_camera_is_out_of_fov(clip_ready):
    clip_ready["pose_mean"]["gimbal_yaw_deg"] = 135.0
    g = compute_view_geometry(clip_ready)
    assert not g.target_in_fov
    assert g.target_px is None


def test_target_beside_camera_is_out_of_fov(clip_ready):
    clip_ready["pose_mean"]["gimbal_yaw_deg"] = 15.0   # lệch 60° > hfov/2 = 40.5°
    assert not compute_view_geometry(clip_ready).target_in_fov


def test_null_gimbal_falls_back_with_warnings(clip_ready):
    clip_ready["pose_mean"]["gimbal_yaw_deg"] = None
    clip_ready["pose_mean"]["gimbal_pitch_deg"] = None
    g = compute_view_geometry(clip_ready)
    assert g.target_in_fov
    assert len(g.warnings) == 2


def test_intrinsics_used_when_given(clip_ready):
    clip_ready["camera"]["intrinsics"] = {"fx": 1000.0, "fy": 1000.0, "cx": 100.0, "cy": 540.0}
    g = compute_view_geometry(clip_ready)
    assert g.target_px[0] == pytest.approx(100.0, abs=60.0)
