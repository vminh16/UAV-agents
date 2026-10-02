# Nhật ký quyết định kiến trúc (ADR)

Mỗi quyết định ghi: bối cảnh → quyết định → hệ quả → phương án đã cân nhắc. Muốn đổi một quyết định, thêm ADR mới với trạng thái "Thay thế ADR-xxx". **Không sửa nội dung ADR cũ.**

| Mã | Tiêu đề | Trạng thái |
|---|---|---|
| ADR-001 | ArduPilot trên Pixhawk 2.4.8, MAVLink qua UART | Chấp nhận |
| ADR-002 | Tách giả thuyết: onboard chỉ kết luận về khói | Chấp nhận |
| ADR-003 | MQTT + JSON Schema làm bus và hợp đồng | Chấp nhận (xem lại ở V1) |
| ADR-004 | Phương pháp cắm được, chọn bằng config; không hardcode | Chấp nhận |
| ADR-005 | Vị trí chạy CV cấu hình được | Chấp nhận |
| ADR-006 | Chỉ camera RGB, chỉ ban ngày | Chấp nhận |
| ADR-007 | CV xuất LLR đã hiệu chỉnh; một nguồn prior duy nhất | Chấp nhận |
| ADR-008 | Thẩm quyền an toàn thuộc embedded; từ chối chứ không sửa lệnh | Chấp nhận |
| ADR-009 | Phương pháp mặc định của agent cho MVP; hoãn RL | Chấp nhận |
| ADR-010 | VMOKED chỉ là baseline | Chấp nhận |
| ADR-011 | MVP: phi công cất cánh thủ công, không trạm sạc | Chấp nhận |

---

## ADR-001 — ArduPilot trên Pixhawk 2.4.8, MAVLink qua UART

**Bối cảnh.** FC dự kiến là Pixhawk 2.4.8 (clone FMUv2, STM32F427, 1 MB flash). PX4 phát hành bản cuối cho fmu-v2 ở v1.15 và không chạy uXRCE-DDS trên bo 1 MB. ArduPilot có target `Pixhawk1-1M` với tính năng rút gọn. Bản v2 của đặc tả ghi "PX4 trên STM32H7 + Micro-XRCE-DDS", không khớp phần cứng.

**Quyết định.** Dùng **ArduPilot Copter `Pixhawk1-1M`**. Máy tính đồng hành nối **TELEM2 (MAVLink2)**, thư viện mặc định `pymavlink`. Điều khiển bằng chế độ **GUIDED** với mục tiêu vị trí. Gimbal và kiểm tra địa hình làm trên máy tính đồng hành.

**Hệ quả.**
- Không cần bộ phát lại setpoint 10–20 Hz như PX4 Offboard (GUIDED giữ mục tiêu vị trí).
- Không phụ thuộc tính năng có thể bị lược trên bản 1 MB.
- `fc_bridge` là nơi duy nhất biết MAVLink. Đổi sang PX4 hay bo H743 chỉ ảnh hưởng module này.

**Đã cân nhắc.**
- PX4 v1.15 qua MAVLink: khả thi, nhưng cần luồng setpoint ≥ 2 Hz và là nhánh không còn cập nhật.
- ROS 2 + MAVROS: nặng hơn cho MVP 4 người làm độc lập (xem ADR-003).

---

## ADR-002 — Tách giả thuyết: onboard chỉ kết luận về khói

**Bối cảnh.** Bản v2 đặt H₁ = "cần báo động", trộn hiện tượng vật lý (có khói) với quyết định chính sách (điều động). Camera RGB chỉ mang thông tin về hiện tượng. Bản v2 còn có luật "GIS mâu thuẫn với onboard thì không kết luận được", tạo hai cơ chế abstain chồng nhau. Ngoài ra, khoảng 65% vụ cháy rừng ở Việt Nam bắt nguồn từ đốt nương / đốt đồng cỏ cháy lan, nên "khói trên đất nương" không thể coi là vô hại.

**Quyết định.**
- Onboard: H₁ = `SMOKE`, H₀ = `NO_SMOKE`; kết luận `SMOKE_CONFIRMED` / `NO_SMOKE` / `UNDETERMINED`.
- Backend (`adjudicator`) diễn giải thành 4 kết quả vận hành. Khói trên đất canh tác được **xếp hạng rủi ro cháy lan**.
- Mâu thuẫn GIS ↔ onboard chỉ tạo **cờ cần xem**, không đổi kết luận agent.

**Hệ quả.** Mỗi thành phần có một thước đo riêng (đúng tinh thần PRD: quy trách nhiệm theo nhóm báo giả). Agent không cần biết GIS.

---

## ADR-003 — MQTT + JSON Schema làm bus và hợp đồng

**Bối cảnh.** Bốn người làm độc lập trên bốn module, ngôn ngữ có thể khác nhau. Liên kết UAV ↔ mặt đất chập chờn. FC không chạy uXRCE-DDS.

**Quyết định.** MQTT (mosquitto onboard + mặt đất, có cầu nối), payload JSON, hợp đồng bằng **JSON Schema 2020-12** trong `docs/interfaces/`. CI validate các ví dụ trên mọi PR.

**Hệ quả.** Không cần gói thông điệp dùng chung (tránh phụ thuộc code chéo). Ghi log và phát lại đơn giản (JSONL). Hiệu năng đủ cho tần số quyết định thấp. Clip không đi qua MQTT.

**Đã cân nhắc.** ROS 2 (chuẩn robotics, rosbag tốt, nhưng cần gói `.msg` dùng chung và học nhiều hơn); ZeroMQ (nhanh, nhưng tự xây cầu và lưu-rồi-gửi). **Xem lại ở V1**: nếu chuyển ROS 2 thì schema vẫn là nguồn sự thật.

---

## ADR-004 — Phương pháp cắm được, chọn bằng config; không hardcode

**Bối cảnh.** Rà soát bản v2 và mã VMOKED cho thấy nhiều ngưỡng, luật và hằng số bị viết cứng (ngưỡng chuyển động 0,02, prior tra bảng, nhãn "nghi đốt nương" bằng luật, hằng số phạt chọn tay). Không truy vết hay so sánh được.

**Quyết định.**
- Mọi khe thuật toán là interface + **registry tên**, chọn trong config.
- Ba loại tham số tách bạch: thiết kế (config) / ước lượng từ dữ liệu (artifact có phiên bản) / rủi ro sản phẩm (PRD → `mission_request`).
- Mọi đầu ra quan trọng mang `provenance` (`config_hash`, phiên bản phương pháp, artifact).
- Giá trị dự phòng phải ghi cảnh báo vào vết, không im lặng.

**Hệ quả.** Baseline và phương pháp mới chạy trên cùng hạ tầng. Benchmark là chuyện đổi config. Tài liệu từng module có **bảng ứng viên + mặc định MVP**.

---

## ADR-005 — Vị trí chạy CV cấu hình được

**Bối cảnh.** Máy tính đồng hành chưa chốt (RPi 5 hay Jetson). Ngân sách hạn chế.

**Quyết định.** `perception_service` là một mã nguồn, chạy **onboard hoặc mặt đất**. Khác biệt chỉ ở config (`runtime`, cách lấy clip qua `clip_ready.uri`). **Agent luôn onboard.**

**Hệ quả.** Có thể bắt đầu MVP với RPi 5 + CV mặt đất, nâng lên Jetson mà không đổi code. Khi CV ở mặt đất, mất liên kết dẫn tới `UNDETERMINED` / `OBSERVATION_TIMEOUT`, đã có trong bảng ngoại lệ.

---

## ADR-006 — Chỉ camera RGB, chỉ ban ngày

**Bối cảnh.** Phần cứng hạn chế, không có camera nhiệt.

**Quyết định.** MVP và V1 chỉ RGB, chỉ hoạt động ban ngày. Chế độ đêm nằm ngoài phạm vi (formulation giữ trong RRD). Cảnh báo ban đêm được backend xếp hàng chờ sáng (V1).

**Hệ quả.** Nhóm báo giả 1 (sương/mây/bụi/hơi nước) được giải bằng đặc trưng chuyển động sau ổn định ảnh + ngữ cảnh góc nhìn. Phản biện "vì sao không dùng nhiệt" được trả lời bằng chi phí. Kiến trúc cho phép thêm modality sau mà agent không đổi.

---

## ADR-007 — CV xuất LLR đã hiệu chỉnh; một nguồn prior duy nhất

**Bối cảnh.** Nếu CV gửi xác suất hậu nghiệm và agent cập nhật Bayes thêm lần nữa, prior bị đếm hai lần.

**Quyết định.** `observation.llr` = ln p(z|H₁,c) − ln p(z|H₀,c), đã hiệu chỉnh, đã trừ logit của tỷ lệ dương trong tập hiệu chỉnh. Prior chỉ đến từ `mission_request.prior.b0`. Quan sát không hợp lệ: `valid=false`, `llr=null`.

**Hệ quả.** Agent cộng bằng chứng một cách nhất quán. CV phải sinh artifact A-01 để agent lập kế hoạch.

---

## ADR-008 — Thẩm quyền an toàn thuộc embedded; từ chối chứ không sửa lệnh

**Bối cảnh.** Agent không biết địa hình, geofence, pin.

**Quyết định.** Phân tầng: phi công > failsafe FC > `safety_supervisor` > `mission_executor` > agent. Lệnh không an toàn bị **từ chối kèm `reject_reason`**, không bao giờ bị sửa ngầm. Agent gửi góc nhìn **tương đối mục tiêu**. Embedded quy đổi toạ độ và kiểm tra địa hình dọc đường bay.

**Hệ quả.** Mô hình quan sát của agent luôn đúng với góc thực sự được nhìn. Kiểm định an toàn gói gọn trong một module.

---

## ADR-009 — Phương pháp mặc định của agent cho MVP; hoãn RL

**Bối cảnh.** Với giả thuyết nhị phân, LLR vô hướng và lưới góc nhỏ, bài toán có lời giải cổ điển: SPRT (dừng), Chernoff (chọn phép đo), và quy hoạch động khi biết mô hình. RL chỉ đáng dùng khi vượt được các baseline này.

**Quyết định.** Mặc định MVP:
- `belief.fusion = tempered_bayes` (τ từ A-01).
- `planner = chernoff_kl_per_cost`.
- `stopping = sprt_wald` (α, β từ `mission_request`).
- `cost_model = flight_time`.

Baseline B1–B4, B7 luôn chạy được. RL (`ppo`) và POMCP thuộc V1/nghiên cứu, chỉ được bật khi benchmark L0 cho thấy lợi ích.

**Hệ quả.** Tính tác tử (3 quyết định không lập trình sẵn) có ngay ở MVP với phương pháp giải thích được. Phần nghiên cứu (RRD) có hạ tầng sẵn để so sánh.

---

## ADR-010 — VMOKED chỉ là baseline

**Bối cảnh.** Rà soát mã công khai `GloryVu/VSMOKED` ([báo cáo](../research/2026-10-02-danh-gia-dac-ta-v2.md) §3):
- Module chuyển động là trừ khung hình với ngưỡng cố định.
- 64,89 "GFLOPs" là GMACs của YOLO-NAS-L.
- Độ trễ công bố không tính detector và SGS.
- Bộ lọc "trên trời" cắt mảng sai.
- Script đánh giá bỏ qua mẫu âm.
- Trọng số YOLO-NAS chỉ dùng phi thương mại.
- Thiết kế cho camera cố định có preset.

**Quyết định.** Không dùng VMOKED làm xương sống. Giữ làm **baseline** chạy lại bằng bộ đánh giá của dự án. Liên hệ nhóm tác giả để xác minh.

---

## ADR-011 — MVP: phi công cất cánh thủ công, không trạm sạc

**Bối cảnh.** FC bản clone, chưa có dữ liệu tin cậy về hành vi cất cánh tự động; bay thử phải VLOS theo quy định.

**Quyết định.** Phi công an toàn cất cánh và chuyển GUIDED. Hệ thống tự động từ điểm đó tới khi RTL. Không trạm sạc ở MVP. Tham số `executor.takeoff_mode` cho phép `auto` sau khi HITL ổn định.

**Hệ quả.** Tính tác tử (mục tiêu MVP) không bị ảnh hưởng. Rủi ro an toàn giảm.
