# Quy tắc làm việc nhóm

Mục tiêu: **4 người làm song song mà không đụng code của nhau**, và không hiểu sai phần của nhau.

## 1. Quyền sở hữu

| Thư mục | Owner | Ai được sửa |
|---|---|---|
| `agents/` | AGT | Chỉ AGT. Người khác mở issue hoặc PR có AGT duyệt |
| `cv/` | CV | Chỉ CV |
| `embedded/` | EMB | Chỉ EMB |
| `backend/` | BE | Chỉ BE |
| `docs/01-PRD.md`, `docs/02-RRD.md` | Trưởng nhóm | PR + trưởng nhóm duyệt |
| `docs/03-architecture/00-overview.md`, `50-interfaces.md`, `90-decisions.md` | Trưởng nhóm | PR + **mọi owner bị ảnh hưởng** duyệt |
| `docs/03-architecture/<module>.md` | Owner module tương ứng | PR + trưởng nhóm duyệt |
| `docs/interfaces/**` | Trưởng nhóm | PR + **mọi owner bị ảnh hưởng** duyệt; CI xanh |

Điền tên GitHub vào [`.github/CODEOWNERS`](.github/CODEOWNERS) để GitHub tự yêu cầu duyệt.

## 2. Quy tắc kỹ thuật bắt buộc

1. **Không import chéo module.** Giao tiếp chỉ qua MQTT theo schema và artifact có phiên bản.
2. **Không hardcode** phương pháp hay ngưỡng. Chọn phương pháp bằng tên trong config. Ngưỡng nằm trong config/artifact, có nguồn gốc. Mọi đầu ra quan trọng mang `provenance.config_hash`.
3. **Validate theo schema** trong test, cả thông điệp phát ra lẫn nhận vào. Đọc schema trực tiếp từ `docs/interfaces/schemas/`, không chép.
4. **Mỗi module cung cấp stub** phát thông điệp hợp lệ (`fake_perception`, `scripted_agent`, `fake_vehicle`, `fake_backend`, `fake_uav`) để người khác test độc lập.
5. **Quy ước chung** (UTC, SI, độ, hệ quy chiếu độ cao, `view_spec` tương đối mục tiêu, LLR không phải posterior): [00-overview §8](docs/03-architecture/00-overview.md). Đọc thêm bảng **sai lệch tích hợp** ở §14.
6. **Không commit** dữ liệu, video, trọng số mô hình, log bay, bí mật. Dùng kho artifact chung và biến môi trường.

## 3. Nhánh và PR

- Nhánh: `<module>/<mô-tả-ngắn>`, ví dụ `agents/chernoff-planner`, `embedded/geofence-check`, `docs/interfaces-v0.2`.
- Một PR chỉ chạm **một** thư mục module (cộng `docs/` nếu cần). PR chạm hai module phải tách đôi.
- Mô tả PR ghi rõ yêu cầu PRD (FR-xx / NFR-xx) và mốc (M0–M4) liên quan.

## 4. Thay đổi hợp đồng giao tiếp

Theo [00-overview §15](docs/03-architecture/00-overview.md):
1. Mở issue.
2. PR sửa `docs/interfaces/schemas/` + `examples/` + `50-interfaces.md`, tăng `schema_version`.
3. CI `contracts` xanh.
4. Mọi owner bị ảnh hưởng duyệt.
5. Mỗi module cập nhật code của **chính mình** trong PR riêng.

## 5. Đổi một quyết định kiến trúc

Thêm ADR mới vào [`90-decisions.md`](docs/03-architecture/90-decisions.md) ("Thay thế ADR-xxx"). Không sửa ADR cũ.
