# Hợp đồng giao tiếp giữa các module

| | |
|---|---|
| Phiên bản hợp đồng | `0.1.0` (MVP) |
| Nguồn sự thật | `docs/interfaces/schemas/*.schema.json` (JSON Schema 2020-12). Tài liệu này giải thích **ngữ nghĩa**; khi mâu thuẫn, **schema thắng**, và phải mở PR sửa tài liệu |
| Ví dụ hợp lệ | `docs/interfaces/examples/*.example.json` |
| Kiểm tra | `python docs/interfaces/tools/validate.py` (CI chạy trên mọi PR) |
| Quy trình thay đổi | [00-overview §15](00-overview.md) |

---

## 1. Vận chuyển

| Hạng mục | Quy ước |
|---|---|
| Giao thức | MQTT 3.1.1/5, payload **JSON UTF-8** ([ADR-003](90-decisions.md)) |
| Broker | Onboard: mosquitto trên máy tính đồng hành. Mặt đất: mosquitto của backend. Cầu nối do `link_bridge` (EMB) |
| QoS | 1 cho mọi thông điệp. `retain` chỉ dùng cho `vehicle_state` và `mission_status` |
| Clip, video | **Không** đi qua MQTT. Chỉ gửi URI (`file://` onboard, `https://` mặt đất) + `sha256` |
| Validate | Bên phát **phải** validate trước khi gửi (trong test). Bên nhận **phải** validate khi nhận; sai schema thì bỏ thông điệp + log lỗi, **không** đoán ý |

### 1.1 Topic

`{uav_id}` ví dụ `uav-01`.

| Mã | Topic | Bên phát | Bên nhận | Cầu lên/xuống mặt đất |
|---|---|---|---|---|
| I-01 | `uav/{uav_id}/mission/request` | BE | EMB, AGT | Xuống |
| I-02 | `uav/{uav_id}/mission/status` | EMB | BE | Lên |
| I-03 | `uav/{uav_id}/vehicle/state` | EMB | AGT (BE) | Lên, đã hạ tần số |
| I-04 | `uav/{uav_id}/agent/view_command` | AGT | EMB | Không (onboard) |
| I-05 | `uav/{uav_id}/embedded/view_result` | EMB | AGT | Không |
| I-06 | `uav/{uav_id}/embedded/clip_ready` | EMB | CV | Lên **chỉ khi** CV chạy mặt đất |
| I-07 | `uav/{uav_id}/cv/observation` | CV | AGT (BE) | Lên (hoặc xuống khi CV chạy mặt đất) |
| I-08 | `uav/{uav_id}/agent/decision` | AGT | EMB, BE | Lên |
| I-09 | `uav/{uav_id}/mission/evidence` | EMB | BE | Lên |
| I-10 | `uav/{uav_id}/safety/event` | EMB | AGT, BE | Lên |
| I-11 | `uav/{uav_id}/mission/control` | BE | EMB | Xuống |
| I-12 | `uav/{uav_id}/agent/step` | AGT | BE | Lên |
| — | `uav/{uav_id}/health/{module}` | mọi dịch vụ | EMB, BE | Lên |

---

## 2. Phần đầu chung `header` (mọi thông điệp)

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `schema` | string | Tên schema, ví dụ `"observation"`. Phải khớp file schema |
| `schema_version` | string semver | Phiên bản hợp đồng bên phát dùng, ví dụ `"0.1.0"` |
| `msg_id` | UUID v4 | Duy nhất cho mỗi thông điệp |
| `uav_id` | string | Ví dụ `"uav-01"` |
| `mission_id` | string \| null | `M-YYYYMMDD-NNN`; null với thông điệp ngoài nhiệm vụ |
| `stamp_utc` | RFC 3339 | Thời điểm **tạo** thông điệp, UTC |
| `producer` | string | `"<module>/<service>@<version>"`, ví dụ `"cv/perception_service@0.1.0"` |

**Tương thích phiên bản:** bên nhận chấp nhận cùng **major**. Khác major thì từ chối và log.

---

## 3. Kiểu dùng chung (`common.schema.json`)

| Kiểu | Trường chính | Ghi chú |
|---|---|---|
| `geo_point` | `lat_deg`, `lon_deg`, `alt_amsl_m?` | WGS84 |
| `view_spec` | `bearing_from_target_deg`, `horizontal_range_m`, `height_above_target_m`, `gimbal{mode, pitch_offset_deg, yaw_offset_deg}`, `hover_s` | **Tương đối mục tiêu** — xem [00-overview §8.3](00-overview.md) |
| `pose` | `lat_deg`, `lon_deg`, `alt_amsl_m`, `height_agl_m?`, `yaw_deg`, `gimbal_pitch_deg?`, `gimbal_yaw_deg?` | Tư thế thực tế |
| `belief` | `p_smoke`, `log_odds`, `sum_llr_effective` | `p_smoke = σ(log_odds)` |
| `provenance` | `component`, `version`, `config_hash`, `git_sha?`, `methods{}`, `artifacts[]` | Truy vết (P3, P7) |

---

## 4. Ngữ nghĩa từng thông điệp

### I-01 `mission_request` (BE → EMB, AGT)
- `alert`: nguồn, thời điểm, `target` (`geo_point`), `location_uncertainty_m`. **MVP giả định** sai số ≤ ngưỡng PRD A-1.
- `prior.b0` ∈ (0, 1) + `model` + `explanation`. **Nguồn prior duy nhất** của hệ thống.
- `risk_targets.alpha_false_alarm`, `risk_targets.beta_miss`: mục tiêu rủi ro (PRD §8) cho luật dừng của agent.
- `budget.max_views`, `budget.max_on_station_s`.
- `geofence`: đa giác + `min_height_agl_m`, `max_height_agl_m`. `home`: vị trí trạm.
- `profiles.agent`, `profiles.cv`: tên profile config (không gửi config tự do).
- `approval`: ai phê duyệt, lúc nào.

### I-02 `mission_status` (EMB → BE)
- `phase` ∈ `RECEIVED, PREFLIGHT, WAITING_TAKEOFF, TRANSIT, ON_STATION, MOVING, SETTLING, RECORDING, RETURNING, LANDED, UPLOADING, COMPLETED, ABORTED`.
- `pose`, `battery_pct`, `current_view_id`, `detail`.

### I-03 `vehicle_state` (EMB → AGT, BE)
- `pose`, `velocity_ned_mps`, `battery{pct, voltage_v}`, `fc{mode, armed, gps_fix, satellites}`, `link{ground_connected}`, `mission_phase`.
- **`on_station_margin_s`**: thời gian còn được ở trên trạm trước khi bắt buộc về (EMB tính, đã trừ năng lượng về nhà + dự trữ). Agent dùng con số này, không tự tính pin.

### I-04 `view_command` (AGT → EMB)
- `view_id` (agent cấp, tăng dần), `view` (`view_spec`), `intent{rationale, expected_score?, expected_cost_s?}`.
- Embedded **có thể từ chối**; không bao giờ tự thay thế bằng góc khác.

### I-05 `view_result` (EMB → AGT)
- `status` ∈ `REACHED, REJECTED, ABORTED, TIMEOUT`.
- `reject_reason` (khi REJECTED) ∈ `INVALID_SPEC, OUTSIDE_GEOFENCE, TERRAIN_CLEARANCE, BATTERY_RESERVE, ON_STATION_TIME, NOT_READY, OTHER`.
- `achieved_pose`, `clip_id` (khi REACHED).

### I-06 `clip_ready` (EMB → CV)
- `uri`, `media{container, width, height, fps, n_frames, duration_s, sha256}`.
- `camera{model, hfov_deg, vfov_deg, intrinsics?}`.
- `frames_meta_uri`: JSONL tư thế UAV + gimbal **theo từng khung**.
- `view` (lệnh), `pose_mean` (thực tế), `target`, `sun{azimuth_deg, elevation_deg}`, `settle{pos_rms_m, gimbal_rms_deg}`.

### I-07 `observation` (CV → AGT)
- `valid`, `invalid_reasons[]`, **`llr`** (null khi không hợp lệ) — định nghĩa trong [20-cv §5](20-cv.md).
- `observation_model_version` (phải khớp A-01 agent đang dùng).
- `context{range_m, height_above_target_m, sun_rel_azimuth_deg, sun_elevation_deg, target_in_fov, base_occlusion_ratio}`.
- `smoke{detected, max_score, regions[]}` (minh hoạ, hiển thị); `features{}` (đặc trưng có tên, phục vụ debug); `landcover_at_base` (V1, null ở MVP); `latency_ms`; `provenance`.
- **Agent chỉ dùng `valid`, `llr`, `context`, `view_id`.** Các trường khác để giải trình. Agent **không** dùng `smoke.max_score` để ra quyết định.

### I-08 `agent_decision` (AGT → EMB, BE)
- `decision` ∈ `SMOKE_CONFIRMED, NO_SMOKE, UNDETERMINED`.
- `reason` ∈ `THRESHOLD_REACHED, BUDGET_EXHAUSTED, LOW_QUALITY, VIEW_INFEASIBLE, OBSERVATION_TIMEOUT, SAFETY_ABORT, MISSION_CANCELLED, LINK_LOSS, POLICY_ABSTAIN`.
- `final_belief`, `thresholds{method, upper, lower, space, derivation}`, các bộ đếm, `steps[]` (toàn bộ `agent_step`), `observation_model_version`, `provenance`.

### I-09 `evidence_package` (EMB → BE)
- `summary{started_utc, ended_utc, final_phase}`, `decision` (bản sao I-08), `observations[]` (bản sao I-07).
- `files[]`: mỗi file có `kind` (`CLIP, THUMBNAIL, FLIGHT_LOG, MESSAGE_LOG, CONFIG, FRAMES_META`), `uri`, `sha256`, `size_bytes`.
- `upload_status` ∈ `COMPLETE, PARTIAL` + `missing[]`.

### I-10 `safety_event` (EMB → AGT, BE)
- `event` ∈ `BATTERY_LOW, BATTERY_CRITICAL, LINK_LOST, LINK_RESTORED, GEOFENCE_BREACH, FC_FAILSAFE, PILOT_OVERRIDE, MISSION_CANCELLED, MISSION_TIMEOUT, COMPANION_FAULT`.
- `severity` ∈ `INFO, WARNING, ABORT`. **`ABORT` ⇒ agent kết thúc ngay** với `UNDETERMINED`.
- `action_taken` ∈ `NONE, HOLD, RTL, LAND`.

### I-11 `mission_control` (BE → EMB)
- `command` ∈ `CANCEL_RTL` (MVP). `issued_by`, `reason`.

### I-12 `agent_step` (AGT → BE)
- `step`, `view_id`, `observation_ref{clip_id, valid, llr, llr_effective}`, `belief_before`, `belief_after`, `candidates[]` (top-k: `view`, `score`, `cost_s`, `feasible`), `chosen{action, view_id?, view?, decision?}`, `rationale`, `warnings[]`, `provenance`.

### A-01 `observation_model` (CV → AGT, file)
- `version`, `created_utc`, `provenance`.
- `llr_definition`, `llr_clip`.
- `context_bins[]{name, edges[]}`, `bins[]{index[], n{SMOKE, NO_SMOKE}, p_invalid, llr_given{SMOKE, NO_SMOKE}}`, `fallback`.
- `inter_view_correlation{method, tempering_tau, kernel?, notes}`, `validation{ece?, auroc?, notes}`.

---

## 5. Thời hạn và tần số (giá trị khởi điểm — đặt trong config các module)

| Đại lượng | Khởi điểm | Ai đặt |
|---|---|---|
| `vehicle_state` onboard | 2 Hz | EMB |
| `vehicle_state` lên mặt đất | 0,5 Hz | EMB |
| `mission_status` | 1 Hz + khi đổi pha | EMB |
| Agent chờ `view_result` | 180 s | AGT |
| Agent chờ `observation` sau REACHED | 20 s onboard / 45 s mặt đất | AGT |
| CV xử lý một clip | ≤ 5 s onboard / ≤ 15 s mặt đất | CV (NFR-07) |

---

## 6. Stub bắt buộc cho kiểm thử độc lập

| Module | Stub | Phát |
|---|---|---|
| CV | `fake_perception` | `observation` theo kịch bản (H, cự ly, góc mặt trời, tỷ lệ hỏng) |
| AGT | `scripted_agent` | Chuỗi `view_command` cố định + `agent_decision` |
| EMB | `fake_vehicle` | `vehicle_state`, `view_result`, `clip_ready` (clip mẫu), `safety_event` theo kịch bản |
| BE | `fake_backend` | `mission_request`, `mission_control` |

Mỗi stub là tiến trình độc lập nói chuyện qua MQTT, nằm trong thư mục module của owner.
