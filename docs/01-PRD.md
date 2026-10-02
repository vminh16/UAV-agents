# PRD — Hệ thống UAV xác minh cảnh báo cháy rừng

**Wildfire Active Smoke Verifier — Product Requirements Document**

| | |
|---|---|
| Phiên bản | **v3.0** — 02/10/2026 (thay thế v2 ngày 20/09/2026, lưu tại [archive](archive/v2-PRD-RRD-kien-truc.md)) |
| Trạng thái | Đặc tả cho **MVP**; các con số đánh dấu "đề xuất" cần chốt |
| Tài liệu liên quan | [RRD](02-RRD.md) · [Kiến trúc tổng thể](03-architecture/00-overview.md) · [Phần cứng](03-architecture/60-hardware.md) · [Rà soát v2](research/2026-10-02-danh-gia-dac-ta-v2.md) |

---

## 1. Bối cảnh và vấn đề

**Thực tế vận hành.** Camera chòi canh và điểm nóng vệ tinh thường xuyên báo nhầm. Ở địa hình đồi núi, kiểm lâm có thể mất 1–2 giờ đi bộ chỉ để kiểm tra một toạ độ nghi vấn. Báo nhầm làm lực lượng kiệt sức và mất niềm tin vào hệ thống. Ngược lại, nếu là cháy thật thì sau 2 giờ đám cháy có thể đã vượt tầm khống chế. Riêng miền Bắc, đầu năm 2025 ghi nhận 129 vụ cháy rừng, thiệt hại hơn 150 ha, gấp đôi cùng kỳ ([Việt Nam News](https://vietnamnews.vn/environment/1716190/northern-region-sees-sharp-rise-in-forest-fires-in-early-2025.html)).

**Ba nhóm báo giả** — mỗi nhóm cần cách xử lý khác nhau và do thành phần khác nhau chịu trách nhiệm:

| Nhóm | Mô tả | Giải bằng | Thành phần chịu trách nhiệm |
|---|---|---|---|
| **1 — Không có khói** | Sương mù, mây thấp sà xuống tán rừng, bụi đường, hơi nước sau mưa | Thị giác (đặc trưng chuyển động: khói bốc lên từ nguồn, sương trôi ngang không nguồn) + **quan sát chủ động** từ nhiều góc | `cv/` + `agents/` (onboard) |
| **2 — Có khói trên đất canh tác** | Đốt nương rẫy, đốt thực bì, đốt rác, đốt rơm rạ | Lớp phủ đất tại mục tiêu (GIS) + (V1) lớp phủ tại chân khói nhìn từ UAV | `backend/` (`adjudicator`) |
| **3 — Cháy thật nhưng mức khẩn khác nhau** | Đám nhỏ đã kiểm soát, ngoài ranh giới quản lý, xa rừng | Xếp mức khẩn theo khoảng cách tới bìa rừng, ranh giới, (V1) gió/độ ẩm | `backend/` (`adjudicator`) |

> **Thay đổi quan trọng so với v2:** nhóm 2 **không còn được coi là "hợp pháp / vô hại"**. Theo số liệu Bộ NN&PTNT được báo chí dẫn lại, khoảng **65% vụ cháy rừng** bắt nguồn từ đốt nương làm rẫy, đốt đồng cỏ cháy lan ([moitruong.net.vn](https://moitruong.net.vn/bo-nn-ptnt-chi-ra-nguyen-nhan-chay-rung-lien-tuc-dien-ra-trong-4-thang-dau-nam-74272.html); cần số liệu gốc từ Cục Lâm nghiệp và Kiểm lâm). Khói trên đất canh tác vì vậy được **xếp hạng rủi ro cháy lan**, không bị bỏ qua.

**Giải pháp.** Một UAV túc trực tại trạm kiểm lâm bay tới toạ độ nghi vấn, **tự quyết định quan sát từ góc nào, bao nhiêu lần, và kết luận gì** về sự hiện diện của khói, rồi gửi gói bằng chứng kèm lý do về máy tính chỉ huy **trước khi** điều động người.

---

## 2. Người dùng và bên liên quan

| Vai trò | Nhu cầu chính |
|---|---|
| **Người trực kiểm lâm** (người dùng chính) | Biết nhanh cảnh báo nào cần điều động; xem bằng chứng; phê duyệt / huỷ chuyến bay |
| Tổ tuần tra / lực lượng chữa cháy | Toạ độ chính xác, ảnh hiện trường, mức khẩn |
| **Phi công an toàn** (MVP) | Kiểm soát được drone mọi lúc; thấy rõ trạng thái tự động |
| Lãnh đạo Chi cục | Số liệu giảm điều động thừa, nhật ký truy vết |
| Nhóm phát triển (4 module) | Ranh giới trách nhiệm rõ, hợp đồng giao tiếp ổn định |

---

## 3. Mục tiêu và nguyên tắc sản phẩm

1. **Lọc bớt điều động không cần thiết.** Không thay thế chuỗi cảnh báo hiện có, không phải người gác cuối cùng.
2. **Con người quyết định điều động.** Hệ thống chỉ khuyến nghị kèm bằng chứng.
3. **Biết nói "không chắc".** Mọi trường hợp không kết luận được đều chuyển cho người.
4. **Giải trình được.** Mỗi kết luận có vết quyết định đọc được.
5. **An toàn bay trên hết.** Tầng tự chủ không ghi đè được geofence, failsafe hay phi công.
6. **Không hardcode.** Phương pháp và ngưỡng nằm trong cấu hình, có nguồn gốc ([ADR-004](03-architecture/90-decisions.md)).

> **Ghi chú bắt buộc trong mọi tài liệu đối ngoại:** hệ thống **không thay thế** chuỗi cảnh báo hiện có và không phải người gác cuối cùng. Mọi cảnh báo mà hệ thống không kết luận được đều chuyển cho người.

---

## 4. Ràng buộc đã chốt

| Ràng buộc | Nội dung |
|---|---|
| Thứ tự mục tiêu | **MVP sản phẩm trước**, paper sau nếu có thể |
| Mốc MVP tối thiểu | **Tính tác tử trên UAV**: vòng quan sát → cập nhật niềm tin → chọn góc kế tiếp hoặc kết luận, chạy onboard |
| Phần cứng | Ngân sách hạn chế. FC **Pixhawk 2.4.8**. **Chỉ camera RGB, không camera nhiệt.** Máy tính đồng hành chưa chốt (RPi 5 hoặc Jetson Orin Nano) — [60-hardware](03-architecture/60-hardware.md) |
| Hoạt động | Ban ngày. MVP bay trong tầm nhìn (VLOS) với phi công an toàn |
| Tổ chức | 4 người, 4 module độc lập: `agents/`, `cv/`, `embedded/`, `backend/` |

---

## 5. Phạm vi theo giai đoạn

| Tính năng | MVP | V1 | V2+ |
|---|---|---|---|
| Nhập cảnh báo thủ công trên bản đồ | ✅ | ✅ | ✅ |
| Nguồn cảnh báo tự động (API chòi canh, FIRMS/VIIRS) | | ✅ | ✅ |
| Prior b₀ từ bảng lớp phủ (chuyên gia) | ✅ | | |
| Prior học từ lịch sử nhiệm vụ | | ✅ | ✅ |
| Người trực phê duyệt / huỷ chuyến bay | ✅ | ✅ | ✅ |
| Phi công cất cánh thủ công, hệ thống tự động từ GUIDED tới RTL | ✅ | | |
| Cất cánh tự động | | ✅ | ✅ |
| **Agent onboard: chọn góc, số lần nhìn, kết luận 3 trạng thái** | ✅ | ✅ | ✅ |
| Phương pháp agent cổ điển có cơ sở lý thuyết (Chernoff + SPRT) | ✅ | ✅ | |
| Chính sách học (RL/POMCP) nếu benchmark chứng minh có lợi | | ✅ | ✅ |
| CV: phát hiện khói + đặc trưng chuyển động + LLR hiệu chỉnh | ✅ | ✅ | ✅ |
| CV: phân đoạn lớp phủ tại chân khói | | ✅ | ✅ |
| Phân xử vận hành bằng luật cấu hình (GIS tại mục tiêu) | ✅ | | |
| Phân xử có gió/độ ẩm, khoảng cách bìa rừng chi tiết | | ✅ | ✅ |
| Dashboard trực tiếp + gói bằng chứng + vết quyết định | ✅ | ✅ | ✅ |
| Thông báo SMS/Zalo | | ✅ | ✅ |
| Xếp hàng cảnh báo ban đêm chờ sáng | | ✅ | ✅ |
| Bay ngoài tầm nhìn (BVLOS), bán kính 5 km | | | ✅ |
| Trạm sạc tự động | | | ✅ |
| Tìm kiếm nguồn khói khi vị trí cảnh báo sai lệch lớn | | | ✅ |
| Camera nhiệt / chế độ đêm | | | Ngoài phạm vi (cần phần cứng mới) |

---

## 6. Kịch bản vận hành MVP

1. **Tiếp nhận.** Người trực nhập cảnh báo trên bản đồ: toạ độ, nguồn, sai số vị trí ước lượng.
2. **Khởi tạo.** Backend tra GIS, tính b₀ kèm giải thích, đề xuất nhiệm vụ (geofence, ngân sách, mục tiêu rủi ro).
3. **Phê duyệt.** Người trực phê duyệt. Phi công an toàn kiểm tra tiền bay, cất cánh, chuyển GUIDED.
4. **Quan sát chủ động.** UAV bay tới góc nhìn đầu tiên do agent chọn, dừng ổn định, quay clip ngắn (hover-and-stare). Sau mỗi clip, agent cập nhật niềm tin và **tự quyết định**: nhìn tiếp ở góc nào, hay đã đủ để kết luận. **Số lần quan sát không cố định.**
5. **Kết luận onboard.** `SMOKE_CONFIRMED`, `NO_SMOKE` hoặc `UNDETERMINED`, kèm vết quyết định. UAV tự về (RTL).
6. **Phân xử và trình bày.** Backend kết hợp kết luận onboard với GIS ra **một trong bốn kết quả vận hành**:

| Kết quả vận hành | Hành động hệ thống | Ai quyết điều động |
|---|---|---|
| `FOREST_FIRE_URGENT` — cháy rừng, khẩn | Báo động trên dashboard, toạ độ, clip, (V1) SMS/Zalo | Người trực |
| `SMOKE_ON_CULTIVATED_LAND_REVIEW` — khói trên đất canh tác, đánh giá cháy lan | Bằng chứng + mức khẩn theo khoảng cách tới bìa rừng; không báo động tự động | Người trực |
| `FALSE_ALARM_NO_SMOKE` — không có khói | Ghi nhận, người trực xác nhận đóng | Người trực |
| `UNDETERMINED_HUMAN_REVIEW` — không kết luận được | Toàn bộ clip + vết quyết định | Người trực |

7. **Đóng nhiệm vụ.** Người trực ghi **kết quả thực tế** (nhãn vàng). Bắt buộc, vì đây là dữ liệu cho mọi KPI và cải tiến sau này.

> Kết quả "không kết luận được" là bắt buộc. Nếu chỉ có hai kết quả khẳng định, hệ thống buộc phải đoán đúng trong những tình huống mơ hồ, và đó là nơi bỏ sót xảy ra.

---

## 7. Yêu cầu

### 7.1 Yêu cầu chức năng

Mỗi yêu cầu có **một module chịu trách nhiệm**. Chi tiết thiết kế ở tài liệu module tương ứng.

**Backend** ([40-backend](03-architecture/40-backend.md))

| ID | Yêu cầu | Giai đoạn |
|---|---|---|
| FR-BE-01 | Nhập cảnh báo thủ công trên bản đồ (toạ độ, nguồn, thời điểm, sai số vị trí) | MVP |
| FR-BE-02 | Tính b₀ bằng mô hình prior cấu hình được, kèm giải thích | MVP |
| FR-BE-03 | Tạo nhiệm vụ: geofence (giao giữa vùng được phép bay và vùng quanh mục tiêu), ngân sách, α/β, profile | MVP |
| FR-BE-04 | Người trực phê duyệt / từ chối; chỉ phát `mission_request` sau phê duyệt | MVP |
| FR-BE-05 | Dashboard trực tiếp: vị trí UAV, pha, pin, quỹ đạo niềm tin, vết quyết định | MVP |
| FR-BE-06 | Huỷ nhiệm vụ (`mission_control` CANCEL_RTL) | MVP |
| FR-BE-07 | Nhận, kiểm tra checksum và lưu gói bằng chứng (chỉ-thêm) | MVP |
| FR-BE-08 | Phân xử vận hành bằng luật cấu hình → 4 kết quả + mức khẩn + ID luật | MVP |
| FR-BE-09 | Đóng nhiệm vụ với nhãn kết quả thực tế bắt buộc | MVP |
| FR-BE-10 | Nhật ký kiểm toán chỉ-thêm (chuỗi băm) | MVP |
| FR-BE-11 | Thông báo SMS/Zalo theo cấu hình | V1 |
| FR-BE-12 | Nguồn cảnh báo tự động; xếp hàng cảnh báo ban đêm | V1 |

**Embedded** ([30-embedded](03-architecture/30-embedded.md))

| ID | Yêu cầu | Giai đoạn |
|---|---|---|
| FR-EMB-01 | Kiểm tra tiền bay: GPS, pin, geofence nạp lên FC, DEM sẵn sàng | MVP |
| FR-EMB-02 | Kiểm tra mọi `view_command` (schema, geofence, địa hình dọc đường bay, pin, thời gian) trước khi thực thi | MVP |
| FR-EMB-03 | Từ chối lệnh không an toàn kèm lý do; **không sửa ngầm** | MVP |
| FR-EMB-04 | Hover-and-stare: ổn định vị trí + gimbal khoá mục tiêu, quay clip độ dài theo lệnh | MVP |
| FR-EMB-05 | Phát `clip_ready` kèm tư thế từng khung, mặt trời, chất lượng ổn định | MVP |
| FR-EMB-06 | Failsafe: pin, mất liên kết, geofence (FC + companion), timeout nhiệm vụ, phi công chiếm quyền | MVP |
| FR-EMB-07 | RTL khi có kết luận / huỷ / sự kiện an toàn | MVP |
| FR-EMB-08 | Phát `vehicle_state` (gồm `on_station_margin_s`) và `mission_status` | MVP |
| FR-EMB-09 | Ghi log bay + log mọi thông điệp; đóng gói và tải `evidence_package` | MVP |
| FR-EMB-10 | Nền tảng onboard cho dịch vụ của module khác (OS, broker, giám sát dịch vụ, đồng bộ giờ) | MVP |
| FR-EMB-11 | Cất cánh tự động; trạm sạc tự động | V1 / V2 |

**CV** ([20-cv](03-architecture/20-cv.md))

| ID | Yêu cầu | Giai đoạn |
|---|---|---|
| FR-CV-01 | Nhận `clip_ready`, trả `observation` trong ngân sách thời gian | MVP |
| FR-CV-02 | Cổng chất lượng → `valid=false` + lý do khi clip không dùng được | MVP |
| FR-CV-03 | Ổn định ảnh clip | MVP |
| FR-CV-04 | Phát hiện vùng khói | MVP |
| FR-CV-05 | Đặc trưng chuyển động (dòng quang học) trong vùng khói | MVP |
| FR-CV-06 | Bộ phân loại clip + hiệu chỉnh → **LLR** theo định nghĩa hợp đồng | MVP |
| FR-CV-07 | Sinh artifact `observation_model` (A-01) có phiên bản | MVP |
| FR-CV-08 | Pipeline dữ liệu: đăng ký nguồn và giấy phép, khử trùng lặp trước khi chia, chia theo nhóm, đánh giá zero-shot chéo + FPR theo loại giả khói | MVP |
| FR-CV-09 | Chạy được onboard và mặt đất chỉ bằng đổi cấu hình | MVP |
| FR-CV-10 | Phân đoạn lớp phủ tại chân khói | V1 |

**Agents** ([10-agents](03-architecture/10-agents.md))

| ID | Yêu cầu | Giai đoạn |
|---|---|---|
| FR-AGT-01 | Khởi tạo niềm tin từ b₀ (một lần, một nguồn) | MVP |
| FR-AGT-02 | Sinh góc nhìn ứng viên từ cấu hình; ghi nhớ góc bị từ chối | MVP |
| FR-AGT-03 | Cập nhật niềm tin từ `observation` bằng phương pháp fusion cấu hình được | MVP |
| FR-AGT-04 | **Chọn góc nhìn kế tiếp** bằng planner cấu hình được | MVP |
| FR-AGT-05 | **Quyết định dừng và kết luận** 3 trạng thái bằng luật dừng cấu hình được, dùng α/β từ nhiệm vụ | MVP |
| FR-AGT-06 | Xử lý từ chối, quá hạn, quan sát kém, sự kiện an toàn | MVP |
| FR-AGT-07 | Vết quyết định giải thích được (`agent_step`, `agent_decision`) | MVP |
| FR-AGT-08 | Bộ mô phỏng L0 + benchmark baseline (B1–B4, B7) và chính sách MVP | MVP |
| FR-AGT-09 | Chính sách học (RL/POMCP), ngưỡng hiệu chỉnh conformal | V1 |
| FR-AGT-10 | Tìm kiếm nguồn khói khi vị trí cảnh báo sai lệch lớn | V2 |

### 7.2 Yêu cầu phi chức năng

| ID | Yêu cầu |
|---|---|
| NFR-01 | **An toàn:** phân tầng thẩm quyền theo [00-overview §7](03-architecture/00-overview.md); agent không thể vượt geofence, failsafe hay phi công |
| NFR-02 | **Không hardcode:** phương pháp chọn qua registry trong config; mọi ngưỡng nằm trong config/artifact có nguồn gốc |
| NFR-03 | **Truy vết:** mỗi nhiệm vụ lưu `config_hash`, phiên bản mô hình/artifact, vết quyết định đầy đủ |
| NFR-04 | **Tái lập:** phát lại log nhiệm vụ cho ra cùng chuỗi quyết định của agent |
| NFR-05 | **Độc lập module:** không import chéo; chỉ giao tiếp qua hợp đồng trong `docs/interfaces/` |
| NFR-06 | **Chịu lỗi liên kết:** lưu-rồi-gửi; mất liên kết không làm mất bằng chứng |
| NFR-07 | **Hiệu năng:** một bước quyết định agent ≤ 50 ms; CV ≤ 5 s/clip onboard, ≤ 15 s/clip mặt đất |
| NFR-08 | **Bảo mật và riêng tư:** TLS + xác thực cho MQTT/HTTP; phân quyền xem clip (có thể có người dân) |
| NFR-09 | **Giấy phép:** thành phần dùng cho sản phẩm phải có giấy phép phù hợp (không dùng trọng số YOLO-NAS; AGPL cần đánh giá) |

---

## 8. Chỉ số thành công

### 8.1 Tiêu chí nghiệm thu MVP (đề xuất, cần chốt)

| ID | Tiêu chí | Đo ở đâu |
|---|---|---|
| K-MVP-1 | **Tính tác tử:** trên bộ kịch bản L0 chuẩn (seed cố định), chính sách MVP có **số góc nhìn thay đổi theo tình huống** và trung bình **≤ 50%** số góc của baseline quỹ đạo tròn 8 điểm (B2), với độ chính xác trên phần tự quyết không thấp hơn B2 quá 1 điểm %, và tỷ lệ bỏ sót ≤ β mục tiêu | Benchmark L0 (`agents/sim`) |
| K-MVP-2 | **An toàn:** 100% lệnh không an toàn trong bộ test bị từ chối; 100% kịch bản failsafe SITL đạt; 0 lần vi phạm geofence khi bay thật | Test EMB, SITL, log bay |
| K-MVP-3 | **Đầu-cuối SITL:** ≥ 10 nhiệm vụ liên tiếp không can thiệp, đủ cả 3 loại kết luận | L1 |
| K-MVP-4 | **Bay thật VLOS:** ≥ 3 nhiệm vụ (≥ 1 có nguồn khói kiểm soát, ≥ 1 không có khói) tự động từ GUIDED tới RTL, có gói bằng chứng đầy đủ; số góc nhìn khác nhau giữa các nhiệm vụ | L3 |
| K-MVP-5 | **Truy vết:** 100% nhiệm vụ có `evidence_package` hợp lệ theo schema; phát lại cho cùng quyết định | BE + AGT |
| K-MVP-6 | **Thời gian:** từ lúc tới góc nhìn đầu tiên đến khi kết luận ≤ 3 phút, bán kính VLOS ≤ 500 m | Log bay |

### 8.2 KPI sản phẩm (V1 trở đi; các số X, Y, Z chốt sau khảo sát thực địa)

- **Thời gian phản ứng:** có mặt và kết luận trong < 10 phút, bán kính 5 km. Đòi hỏi tốc độ hành trình ≥ 12–15 m/s ([60-hardware §6](03-architecture/60-hardware.md)).
- **Nhóm 1:** giảm ≥ X% số lần điều động do sương/mây/bụi bị nhận nhầm.
- **Nhóm 2:** giảm ≥ Y% số lần điều động không cần thiết do khói trên đất canh tác **mà vẫn không bỏ sót cháy lan** (đo trên nhãn vàng).
- **Tỷ lệ bỏ sót:** ≤ Z% trên tập kiểm thử giữ lại. β trong `mission_request.risk_targets` lấy từ Z.
- **Tỷ lệ tự chủ:** tỷ lệ nhiệm vụ kết luận khẳng định không cần can thiệp; báo cáo cùng độ chính xác trên phần tự quyết (đường coverage–accuracy).

> Bản v1 đặt tỷ lệ bỏ sót 0%. Không hệ thống nhận dạng nào đạt được điều đó, và nó buộc hệ thống báo động trong mọi trường hợp. v3 giữ Z% hữu hạn và đưa nó vào **ràng buộc** của luật dừng (α, β), thay vì hằng số phạt chọn tay.

**Mẫu số của mọi KPI phần trăm:** số cảnh báo mỗi ngày của một trạm trong mùa khô và tỷ lệ theo từng nhóm báo giả. Cần một buổi làm việc với Chi cục Kiểm lâm (Q-6).

---

## 9. Giả định

| ID | Giả định | Nếu sai thì |
|---|---|---|
| A-1 | Sai số vị trí cảnh báo ≤ **100 m** (đề xuất) sau khi người trực tinh chỉnh trên bản đồ, đủ để mục tiêu nằm trong khung hình ở cự ly 100–200 m | CV báo `target_in_fov=false`, agent không kết luận được; V2 thêm tìm kiếm |
| A-2 | Cột khói tồn tại đủ lâu (≥ vài phút) để UAV tới nơi | Kết luận "không khói" có thể đúng tại thời điểm bay nhưng sai với thời điểm cảnh báo; ghi rõ thời điểm trong báo cáo |
| A-3 | Có liên kết 4G/WiFi tại trạm và vùng bay thử | Lưu-rồi-gửi; CV phải chạy onboard |
| A-4 | Có thể xin phép bay thử VLOS tại địa điểm thử | Thử trong SITL/HITL lâu hơn |

---

## 10. Chiến dịch thu thập dữ liệu (yêu cầu sản phẩm)

Dữ liệu UAV đa góc ở Việt Nam là **nút thắt lớn nhất** cho cả sản phẩm và nghiên cứu. Owner: CV; hỗ trợ: EMB (bay), BE (lưu trữ).

| Hạng mục | Yêu cầu |
|---|---|
| Thiết bị | UAV dự án khi đã ổn định, hoặc drone thương mại nhỏ có SDK (ví dụ DJI Mini 4 Pro + MSDK v5) để thu sớm |
| Cách quay | Hover 1–4 s tại lưới góc nhìn (phương vị × cự ly × độ cao) quanh mục tiêu; ghi tư thế, gimbal, thời điểm, vị trí mặt trời |
| Kịch bản dương tính | Đốt thực bì / đốt nương **có phép**, phối hợp kiểm lâm; không tự gây cháy |
| Kịch bản âm tính khó | Sương sáng sớm, mây thấp sát tán, bụi đường đất, hơi nước sau mưa, cảnh trống |
| Nhãn | Nhãn mức sự kiện (H₁/H₀), loại giả khói, (V1) đa giác lớp phủ tại chân khói |
| Quy mô khởi điểm (đề xuất) | ≥ 30 sự kiện × ≥ 8 góc nhìn cho A-01 v1; tăng dần theo mùa |
| Quản lý | Đăng ký nguồn và giấy phép trong `cv/data/README.md`; không commit dữ liệu vào git |

---

## 11. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Thiếu dữ liệu UAV đa góc | Cao | Chiến dịch §10 bắt đầu sớm; drone thương mại nhỏ để thu |
| Bo FC clone kém ổn định | Trung bình | Phi công an toàn, HITL kỹ, nâng cấp H743 trước V1 |
| Giấy phép mô hình (AGPL / phi thương mại) | Trung bình | Chốt detector trước khi sản phẩm hoá (Q-4) |
| Quy định bay | Trung bình | Chỉ VLOS ở MVP; làm thủ tục sớm (Q-2) |
| Cảnh báo sai vị trí lớn | Trung bình | Giả định A-1; V2 tìm kiếm |
| Tương quan giữa các góc nhìn làm agent quá tự tin | Trung bình | Tempered fusion; đo tương quan; V1 ngưỡng conformal |

---

## 12. Câu hỏi cần chốt

| ID | Câu hỏi | Người chốt | Ảnh hưởng |
|---|---|---|---|
| Q-1 | Lấy được lớp GIS ranh giới rừng / quy hoạch 3 loại rừng từ Chi cục không? | Trưởng nhóm | `prior_model`, `adjudicator` |
| Q-2 | Thủ tục cấp phép bay thử VLOS theo Nghị định 288/2025/NĐ-CP tại địa điểm thử | Trưởng nhóm | Lịch M4 |
| Q-3 | Luật dừng có dùng b₀ không (`sprt_wald` hay `posterior_thresholds`)? | AGT + Trưởng nhóm | Agent |
| Q-4 | Detector cho sản phẩm: Ultralytics (AGPL-3.0) hay D-FINE/DEIM/RT-DETRv2 (Apache-2.0)? | CV + Trưởng nhóm | CV |
| Q-5 | Máy tính đồng hành: RPi 5 hay Jetson Orin Nano Super? | EMB + Trưởng nhóm | Triển khai CV |
| Q-6 | Mẫu số cảnh báo/ngày và tỷ lệ theo nhóm báo giả → chốt X, Y, Z, α, β | Trưởng nhóm + Chi cục | KPI |
| Q-7 | Cơ cấu nguồn cảnh báo (chòi canh / vệ tinh / người dân) | Trưởng nhóm | Ưu tiên V1/V2 |

---

## 13. Lịch sử thay đổi

| Phiên bản | Thay đổi chính |
|---|---|
| v3.0 (02/10/2026) | Tách PRD / RRD / Kiến trúc. Chốt **MVP trước**, mốc MVP = tính tác tử onboard. Chốt phần cứng: Pixhawk 2.4.8, chỉ RGB, không camera nhiệt. Tách giả thuyết onboard (khói) và kết quả vận hành (backend). Nhóm 2 đổi thành "khói trên đất canh tác — xếp rủi ro cháy lan". Bỏ luật "GIS mâu thuẫn ⇒ không kết luận" ở tầng onboard. KPI bỏ sót đưa vào ràng buộc α/β. Thêm FR/NFR có ID và module chịu trách nhiệm, KPI nghiệm thu MVP, chiến dịch dữ liệu. Nguyên tắc không hardcode |
| v2 (20/09/2026) | Ba nhóm báo giả, `a_abstain`, module lớp phủ, KPI bỏ sót hữu hạn, mục tính tự chủ |
