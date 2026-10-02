# `embedded/` — Nhúng: bay, an toàn, camera, nền tảng onboard

**Owner:** EMB — *(điền tên)* · **Đọc trước:** [`docs/03-architecture/30-embedded.md`](../docs/03-architecture/30-embedded.md), [`60-hardware.md`](../docs/03-architecture/60-hardware.md), [`00-overview.md`](../docs/03-architecture/00-overview.md) §1–8, 13–14, [`50-interfaces.md`](../docs/03-architecture/50-interfaces.md)

> Đưa camera tới **đúng góc nhìn được yêu cầu một cách an toàn**, rồi quay một **clip ổn định có đủ siêu dữ liệu**. Module này **giữ thẩm quyền an toàn**: lệnh không an toàn bị **từ chối kèm lý do**, không bao giờ bị sửa ngầm.

Phần cứng đã chốt: **Pixhawk 2.4.8** (ArduPilot Copter `Pixhawk1-1M`, MAVLink2 qua TELEM2), **camera RGB** (khuyến nghị SIYI A8 mini), **không camera nhiệt**.

## Làm / không làm

| Làm | Không làm |
|---|---|
| Tham số firmware, `fc_bridge`, `mission_executor`, `safety_supervisor`, `gimbal_driver`, `camera_recorder`, `link_bridge` | Không đánh giá có khói hay không, không chọn góc nhìn |
| Quy đổi `view_spec` → toạ độ tuyệt đối (một chỗ duy nhất), kiểm tra geofence + địa hình DEM + pin | Không "sửa nhẹ" lệnh không an toàn |
| Nền tảng onboard (OS, mosquitto, systemd template, chrony) cho các module khác | Không sửa code dịch vụ của `agents/` hay `cv/` |
| SITL/HITL, camera phát lại clip; sơ đồ đấu nối | — |

## Hợp đồng

Nhận: I-01 `mission_request`, I-04 `view_command`, I-08 `agent_decision`, I-11 `mission_control`.
Phát: I-02 `mission_status`, I-03 `vehicle_state`, I-05 `view_result`, I-06 `clip_ready`, I-09 `evidence_package`, I-10 `safety_event`.

## Thư mục

```
embedded/
├── configs/    # embedded.default.yaml (dịch vụ companion)
├── firmware/   # params/*.param ĐÃ kiểm chứng HITL + checklist tiền bay
├── companion/  # fc_bridge/, mission_executor/, safety_supervisor/, gimbal/, camera/, link_bridge/, deploy/
├── hardware/   # đấu nối, BOM, ảnh lắp ráp
├── sim/        # ArduPilot SITL, camera replay, kịch bản kiểm thử, fake_vehicle (stub)
└── tests/
```

## Định nghĩa hoàn thành MVP (tóm tắt)

- [ ] SITL: `view_command` → bay → settle → clip (replay) → `view_result` + `clip_ready`
- [ ] 100% lệnh ngoài geofence / thiếu khoảng cách địa hình / thiếu pin bị từ chối (K-MVP-2)
- [ ] Mọi failsafe trong 30-embedded §6 kiểm thử đạt trong SITL và HITL
- [ ] Test quy đổi toạ độ (sai số < 0,5 m; đúng phía theo `bearing_from_target_deg`)
- [ ] `message_log.jsonl` + `evidence_package` đầy đủ cho mọi nhiệm vụ
- [ ] File tham số Pixhawk 2.4.8 đã kiểm chứng lưu trong `firmware/params/`
