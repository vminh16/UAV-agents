# RRD — Research Requirements Document

**Đề tài:** Kiểm định giả thuyết tuần tự chủ động có quyền không kết luận cho UAV chỉ dùng camera RGB trong xác minh khói cháy rừng.

| | |
|---|---|
| Phiên bản | **v3.0** — 02/10/2026 (thay thế Phần II của v2, lưu tại [archive](archive/v2-PRD-RRD-kien-truc.md)) |
| Quan hệ với sản phẩm | **MVP trước, nghiên cứu sau.** MVP xây hạ tầng (agent cắm được, benchmark L0, pipeline dữ liệu, log phát lại). Nghiên cứu dùng chính hạ tầng đó, không xây song song |
| Tài liệu liên quan | [PRD](01-PRD.md) · [Kiến trúc](03-architecture/00-overview.md) · [agents](03-architecture/10-agents.md) · [cv](03-architecture/20-cv.md) · [Rà soát v2](research/2026-10-02-danh-gia-dac-ta-v2.md) |

---

## 1. Mục tiêu nghiên cứu

**Câu hỏi cốt lõi.** Một UAV chỉ có camera RGB nên **nhìn từ đâu, nhìn bao nhiêu lần, và khi nào được phép kết luận** để phân biệt khói cháy với các hiện tượng giống khói (sương, mây thấp, bụi, hơi nước), với **rủi ro bỏ sót được kiểm soát** và **chi phí bay nhỏ nhất**?

**Phạm vi.** Đề tài giải **nhóm báo giả 1** (khói hay không khói) ở tầng onboard. Nhóm 2 và 3 được diễn giải ở backend bằng GIS ([ADR-002](03-architecture/90-decisions.md)). Đề tài không hứa phân biệt "đốt nương" với "cháy rừng" bằng hình ảnh cột khói, vì cột khói không mang thông tin đó.

**Đóng góp không nằm ở từng mảng riêng lẻ** (fine-tune detector, chạy PPO, đo FPS). Đóng góp nằm ở **chỗ ghép nối**:
1. Thị giác cho ra **likelihood đã hiệu chỉnh và phụ thuộc góc nhìn**.
2. Tác tử **dừng có kiểm soát rủi ro** dựa trên các likelihood **tương quan** giữa các góc.
3. **Chi phí bay** là một phần của quyết định.

---

## 2. Phát biểu bài toán

### 2.1 Mô hình

- Giả thuyết ẩn H ∈ {H₀ = `NO_SMOKE`, H₁ = `SMOKE`}, prior b₀ = P(H₁) từ backend (GIS).
- Tại bước t, tác tử chọn a_t ∈ 𝒱_khả thi ∪ {`CONFIRM`, `REJECT`, `ABSTAIN`}, trong đó 𝒱 là tập góc nhìn (phương vị, cự ly, độ cao, gimbal, thời gian hover) tương đối mục tiêu.
- Mỗi góc nhìn v cho một clip; CV trả về log-likelihood ratio có hiệu chỉnh

$$L_t = \ln \frac{p(z_t \mid H_1, c(v_t))}{p(z_t \mid H_0, c(v_t))}$$

  với c(v) là ngữ cảnh: cự ly, góc mặt trời tương đối, độ cao, tỷ lệ che khuất.
- Gộp bằng chứng có bù tương quan:

$$\Lambda_t = \sum_{k \le t} w_k L_k, \qquad \ell_t = \operatorname{logit}(b_0) + \Lambda_t, \qquad b_t = \sigma(\ell_t)$$

  với w_k = 1 (Bayes ngây thơ), w_k = τ (tempered), hoặc w học được.
- Chi phí mỗi góc: c(v_t | vị trí hiện tại) = thời gian bay + ổn định + hover. Ràng buộc: số góc ≤ N_max, tổng thời gian trên trạm ≤ T_max, biên năng lượng do embedded cung cấp.

### 2.2 Mục tiêu có ràng buộc

$$\min_\pi \; \mathbb{E}[T_\text{decide}] + C_{AB} \cdot P(\text{ABSTAIN}) \quad \text{s.t.} \quad P(\text{REJECT} \mid H_1) \le \beta, \;\; P(\text{CONFIRM} \mid H_0) \le \alpha$$

- α, β là **mục tiêu rủi ro sản phẩm** (PRD KPI Z%), không phải hằng số phạt chọn tay. Bản v2 dùng phạt C_MD, vốn không bảo đảm được tỷ lệ bỏ sót.
- C_AB (hoặc ngân sách) được **quét** để vẽ đường cong coverage–accuracy.

### 2.3 Những gì đã biết — và vì sao điều này quan trọng

| Trường hợp | Lời giải đã biết | Hệ quả cho đề tài |
|---|---|---|
| Một góc nhìn cố định, quan sát độc lập | **SPRT** tối ưu (Wald 1945; Wald & Wolfowitz 1948) | "Nhìn bao nhiêu lần" đã có lời giải cổ điển. Giảm N_hover so với quỹ đạo tròn **không** tự nó chứng minh được trí tuệ của chính sách |
| Chọn phép đo, mô hình biết trước | **Test chủ động Chernoff** (1959), tối ưu tiệm cận; cận và heuristic của Naghshvar & Javidi (2013) | Baseline bắt buộc |
| Mô hình biết, không gian nhỏ (b rời rạc × lưới góc × ngân sách) | **Quy hoạch động chính xác**, trần tối ưu | Baseline bắt buộc, chi phí tính rất rẻ |
| Greedy theo information gain, quan sát nhiễu | **Có thể rất tệ**; EC² có bảo đảm (Golovin, Krause & Ray 2010) | Không được viện dẫn bảo đảm (1 − 1/e) của Krause 2008 (bài toán không thích ứng, GP, ngân sách cố định) |

**Học (RL/POMCP) chỉ được coi là đóng góp khi vượt các baseline trên**, trong ít nhất một chế độ sau: (a) mô hình quan sát không có dạng đóng (đầu vào là đặc trưng ảnh); (b) quan sát **tương quan mạnh** có cấu trúc; (c) vị trí nguồn khói **bất định** (tìm kiếm + xác minh); (d) cần tổng quát hoá qua địa hình mà không giải lại DP.

---

## 3. Câu hỏi nghiên cứu

| Mã | Câu hỏi | Cần gì | Giai đoạn |
|---|---|---|---|
| **RQ1** | Ngữ cảnh góc nhìn (cự ly, góc mặt trời, độ cao, che khuất) thay đổi **khả năng phân biệt** khói/giả khói (KL giữa p(L\|H₁,c) và p(L\|H₀,c)) đến mức nào trên clip hover 1–4 s? *Nếu không đổi, quan sát chủ động vô nghĩa, chỉ cần nhìn lặp lại* | Dữ liệu UAV đa góc (PRD §10) | Sau MVP, dữ liệu thu song song MVP |
| **RQ2** | Tương quan giữa các góc nhìn của cùng một sự kiện lớn đến đâu, và cách gộp nào (ngây thơ / tempered / học được) giữ được **hiệu chỉnh và tỷ lệ bỏ sót**? | Như RQ1 | Sau MVP |
| **RQ3** | Khi nào lập kế hoạch thích ứng (Chernoff, greedy, EC², DP, POMCP, RL) thắng **SPRT góc cố định** và **quỹ đạo tròn**, về số góc và thời gian quyết định ở cùng mức rủi ro? Khi nào RL thắng DP với mô hình xấp xỉ? | Benchmark L0 (MVP) | Bắt đầu ngay với dữ liệu công khai |
| **RQ4** | Hiệu chỉnh ngưỡng dừng bằng **conformal risk control** có bảo đảm tỷ lệ bỏ sót ≤ β khi **dịch chuyển phân phối** giữa các địa điểm không, và mất bao nhiêu coverage? | L0 + dữ liệu thật | V1 |
| **RQ5** | Đặc trưng chuyển động có cơ sở vật lý (dòng quang học sau ổn định ảnh) so với mô hình video học sâu nhẹ cho phân biệt khói / sương / mây / bụi / hơi nước từ clip hover ngắn, **chỉ RGB**; tổng quát hoá chéo dataset? | Dữ liệu công khai + tự thu | MVP (phiên bản đầu) → V1 |
| **RQ6** | Phân đoạn lớp phủ tại chân khói từ **góc xiên UAV** có thêm giá trị so với GIS cho phân xử nhóm 2 không? | Dữ liệu tự thu có đa giác lớp phủ | V1 |
| **RQ7** | Mở rộng: tìm kiếm nguồn khói khi vị trí bất định; hành động có ý thức chi phí tính toán (chọn mô hình rẻ/đắt, onboard/mặt đất) | — | V2, tuỳ chọn |

---

## 4. Phương pháp ứng viên (không hardcode — mọi phương pháp chạy chung hạ tầng)

Danh mục đầy đủ, mặc định MVP và tên registry nằm trong tài liệu module. Bảng dưới gom theo câu hỏi nghiên cứu.

| RQ | Khe | Ứng viên | Chi tiết |
|---|---|---|---|
| RQ1, RQ2 | Mô hình quan sát, fusion | `global_gaussian`, `binned_gaussian`, `binned_histogram`; `naive_bayes`, `tempered_bayes`, `kernel_tempered`, `learned_gru` | [10-agents §4–5](03-architecture/10-agents.md), [20-cv §5](03-architecture/20-cv.md) |
| RQ3 | Planner | `single_shot`, `fixed_orbit`, `greedy_info_gain`, `fixed_view_sprt`, `chernoff_kl_per_cost`, `ec2`, `dp_belief`, `pomcp`, `ppo` | [10-agents §5](03-architecture/10-agents.md) |
| RQ4 | Luật dừng | `sprt_wald`, `posterior_thresholds`, `conformal_calibrated`, `dp_belief` | [10-agents §4.4](03-architecture/10-agents.md) |
| RQ5 | Thị giác | Detector (YOLO11/26, RT-DETRv2, D-FINE, DEIM, YOLOE zero-shot); ổn định ảnh (ECC, homography); flow (DIS, Farnebäck, RAFT-small, NeuFlow); bộ phân loại clip (logistic, GBDT, TSM, X3D, MoViNet); hiệu chỉnh (Platt, temperature, isotonic theo bin) | [20-cv §6](03-architecture/20-cv.md) |
| RQ6 | Lớp phủ | SegFormer-B0, PIDNet-S, DINOv2-S + đầu tuyến tính, phân đoạn từ vựng mở | [20-cv §6](03-architecture/20-cv.md) |

---

## 5. Baseline và thước đo

### 5.1 Baseline (đều là cấu hình của cùng `agent_runtime`)

| Mã | Baseline | Vai trò |
|---|---|---|
| B1 | `single_shot`: một góc, một clip | Sàn |
| B2 | `fixed_orbit`: 8 góc đều quanh mục tiêu, gộp hết rồi quyết | **Tự động hoá không tự chủ** — cùng phần cứng, cùng mô hình, không tự quyết dừng |
| B3 | `greedy_info_gain`: greedy theo giảm entropy kỳ vọng | Greedy thông tin |
| B4 | `fixed_view_sprt`: một góc tốt nhất cố định + SPRT | Tách đóng góp của "dừng tuần tự" khỏi "chọn góc" |
| B5 | `chernoff_kl_per_cost` + `sprt_wald` | **Mặc định MVP** |
| B6 | `ec2` | Greedy có bảo đảm khi nhiễu |
| B7 | `dp_belief` với mô hình quan sát đúng | **Trần tối ưu** khi biết mô hình |
| B8 | `pomcp` | Lập kế hoạch trực tuyến |
| — | `ppo` (và biến thể hồi quy) | Ứng viên học; phải so với B5–B8 |
| — | VMOKED (chạy lại bằng bộ đánh giá dự án) | Baseline thị giác cho RQ5 |

### 5.2 Thước đo

| Thước đo | Định nghĩa | Ghi chú |
|---|---|---|
| Độ chính xác trên phần tự quyết | Trên các nhiệm vụ không `UNDETERMINED` | Cặp với coverage |
| Coverage | 1 − tỷ lệ `UNDETERMINED` | Đường coverage–accuracy khi quét ngân sách / C_AB |
| **Tỷ lệ bỏ sót** | P(`NO_SMOKE` \| H₁) | So với β mục tiêu; báo cáo khoảng tin cậy |
| Tỷ lệ báo nhầm | P(`SMOKE_CONFIRMED` \| H₀), **theo từng loại giả khói** | Sương, mây, bụi, hơi nước tách riêng |
| N_views | Số góc nhìn mỗi nhiệm vụ, **cả phân phối** | Một hằng số = không tự chủ |
| T_decide | Từ khi tới góc đầu tiên đến khi kết luận, **gồm thời gian bay** | Không chỉ thời gian suy luận |
| Hiệu chỉnh | ECE, reliability diagram của b_T | Phát hiện quá tự tin do tương quan |
| Độ nhạy | Theo ρ (tương quan) và theo độ lệch mô hình quan sát | Bắt buộc với kết quả L0 |

> **Không báo cáo thành công bằng mức giảm entropy của niềm tin.** Khi gộp ngây thơ các quan sát tương quan, entropy giảm nhanh trong khi kết luận vẫn sai. Thước đo công bố phải là sai số trên tập kiểm thử giữ lại cùng tỷ lệ bỏ sót.

---

## 6. Dữ liệu

| Bộ dữ liệu | Góc nhìn | Quy mô | Dùng cho | Lưu ý |
|---|---|---|---|---|
| FIgLib (HPWREN) | Chòi canh | ~25 nghìn ảnh, 315 chuỗi | Detector; mẫu âm khó từ kho HPWREN | ~1 khung/phút: động học khác clip hover |
| PyroNear-2024/2025 | Chòi canh / web | ~50 nghìn ảnh, ~150 nghìn nhãn, có video | Detector, chuỗi | — |
| Boreal Forest Fire | **UAV** | 4.954 ảnh + 292 clip | Detector + chuyển động từ UAV | Thảm thực vật phương Bắc |
| FLAME 1/2/3 | **UAV** | FLAME 3: ~14 nghìn ảnh RGB + nhiệt | Khói/lửa đốt có kiểm soát | Chỉ dùng phần RGB |
| FASDD (phần UAV) | UAV | — | Detector | **90,7%** ảnh test có bản gần-trùng trong train |
| D-Fire | Hỗn hợp | — | Detector | **46,0%** ảnh test gần-trùng |
| VDD, UAVid, IDD | **UAV xiên** | 400 / 300 / 811 ảnh | Lớp phủ (RQ6) | LoveDA, OpenEarthMap, LandCover.ai là ảnh trực giao, chỉ dùng pre-train |
| LULC Việt Nam 1990–2020; Land Cover 2020 (OD Mekong) | Bản đồ | — | GIS backend, prior | — |
| WSDataset (nhóm VMOKED) | Camera cố định | 11.539 / 12.481 khung | Baseline VMOKED | Chưa xác minh link và giấy phép |
| **Tự thu tại Việt Nam** | **UAV đa góc, hover 1–4 s** | Khởi điểm ≥ 30 sự kiện × ≥ 8 góc | **Hiệu chỉnh A-01, RQ1, RQ2, test chính** | Quy trình ở PRD §10 |

---

## 7. Quy trình đánh giá và chống rò rỉ (bắt buộc)

1. **Khử trùng lặp gần trước khi chia tập** (pHash / embedding), rồi chia theo **nhóm**: sự kiện, địa điểm, video. Bằng chứng mức độ nghiêm trọng: nghiên cứu kiểm chéo D-Fire / FASDD_UAV ([Drones 2026](https://www.mdpi.com/2504-446X/10/8/635)) thấy 46,0% và 90,7% ảnh test có bản gần-trùng trong train; AP@0.5 của lớp fire rơi từ 89,1 xuống 39,4 và từ 72,8 xuống 6,0 khi chuyển dataset.
2. **Luôn có mẫu âm**, báo cáo FPR theo từng loại giả khói. (Bộ đánh giá công khai của VMOKED bỏ qua mẫu âm.)
3. **Zero-shot chéo dataset** bên cạnh in-domain.
4. **Hiệu chỉnh** đánh giá trên tập riêng, theo bin ngữ cảnh.
5. **Thí nghiệm agent** trên L0 dùng seed cố định, cùng bộ kịch bản cho mọi chính sách. Báo cáo độ nhạy theo ρ.
6. Tách bạch **dữ liệu hiệu chỉnh A-01** và **dữ liệu kiểm thử chính sách**.

---

## 8. Mô phỏng

| Mức | Mục đích nghiên cứu | Owner |
|---|---|---|
| L0 — bộ mô phỏng quan sát | RQ2, RQ3, RQ4: chạy hàng nghìn kịch bản, quét ρ, quét ngân sách | AGT |
| L0-CV — benchmark offline | RQ1, RQ5, RQ6 | CV |
| L1 — SITL + phát lại clip thật | Kiểm chứng tích hợp, thời gian thực | EMB |
| L2/L3 — HITL, bay thật | Kiểm chứng sim-to-real: so phân phối LLR thực địa với A-01 | Cả nhóm |
| (Tuỳ chọn) UE5 / Isaac Sim + khói Niagara | Sinh dữ liệu tổng hợp cho RQ1 khi thiếu dữ liệu thật; phải báo cáo khoảng cách sim-to-real | CV |

---

## 9. Kế hoạch công bố

Thứ tự gợi ý khi MVP đi trước và phần cứng hạn chế:

| Paper | Nội dung | Phụ thuộc | Venue tham khảo |
|---|---|---|---|
| **A — Benchmark xác minh chủ động** | RQ3 (+RQ4): active SHT có abstain và ràng buộc rủi ro; so sánh B1–B8 + RL trên L0 với mô hình quan sát dựng từ dữ liệu thật; phân tích khi nào học có ích | Benchmark L0 (MVP) + A-01 từ dữ liệu công khai/tự thu | RA-L / IROS / ICRA; *Drones*, *Remote Sensing*, *Fire*, *IEEE Access*; workshop CVPR EarthVision, WACV CV4EO, NeurIPS CCAI |
| **B — Bộ dữ liệu UAV khói / giả khói Việt Nam** | RQ1, RQ5: clip đa góc, mẫu âm khó, ngữ cảnh góc nhìn, protocol khử trùng lặp, baseline | Chiến dịch dữ liệu (PRD §10) | *Scientific Data*, *Data in Brief*, ESSD, *Remote Sensing*, *Drones* |
| **C — Hệ thống MVP và thực địa** | Hệ thống đầu-cuối, kết quả bay thật, bài học tích hợp | Đạt M4 + bay thêm | *Drones*, *Journal of Field Robotics*, *Fire*; hội nghị trong nước (RIVF, KSE, SoICT, ATC) |
| D — Mở rộng | RQ2 sâu (fusion học được), RQ6 (lớp phủ xiên), RQ7 | V1/V2 | Tuỳ kết quả |

**Khung paper A (tên tạm):** *"Look Again or Decide? Risk-Controlled Active Sequential Hypothesis Testing for UAV Wildfire Smoke Verification"*.

**Thí nghiệm nên chạy đầu tiên (≈ 1 ngày, trong L0):** so `dp_belief` với `chernoff_kl_per_cost` và `ppo` trên mô hình quan sát đơn giản. Nếu PPO chỉ hội tụ về DP, đóng góp **không** thể là "dùng RL". Khi đó chuyển trọng tâm sang RQ2/RQ4 hoặc mở rộng sang tìm kiếm (RQ7).

---

## 10. Mối đe doạ tính hợp lệ

| Mối đe doạ | Cách xử lý |
|---|---|
| Đốt có kiểm soát khác cháy rừng thật (quy mô, nhiên liệu, thời điểm) | Nêu rõ giới hạn; bổ sung clip cháy thật khi có; phân tích theo loại sự kiện |
| A-01 dựng từ ít dữ liệu → sim-to-real | So phân phối LLR thực địa với A-01 (L3); quét độ lệch mô hình trong L0 |
| Rò rỉ dữ liệu do gần-trùng | §7.1 |
| Dịch chuyển địa lý (rừng phương Bắc → nhiệt đới) | Zero-shot chéo; dữ liệu Việt Nam làm test chính |
| Số sự kiện thật ít → khoảng tin cậy rộng | Báo cáo khoảng tin cậy; không tuyên bố quá mức |
| Nhãn vàng phụ thuộc người trực | Hướng dẫn gán nhãn khi đóng nhiệm vụ; kiểm tra chéo mẫu |

---

## 11. Ngoài phạm vi: chế độ ban đêm

Không có camera nhiệt ([ADR-006](03-architecture/90-decisions.md)), nên chế độ đêm **ngoài phạm vi** MVP và V1. Formulation vẫn giữ để tham khảo: cùng POMDP, đổi mô hình quan sát z^khói thành z^sáng (nguồn sáng bất thường trên ảnh phơi sáng dài hoặc ảnh nhiệt). Lớp phủ tại chân khói không quan sát được ban đêm, nên phải dựa hoàn toàn vào GIS. Cảnh báo ban đêm được backend xếp hàng chờ sáng (V1).

---

## 12. Ghi chú về công trình liên quan và các sửa đổi so với v2

- **VMOKED** \[1\]: rà soát mã công khai cho thấy:
  - Module chuyển động là trừ khung hình với ngưỡng cố định.
  - 64,89 "GFLOPs" là GMACs của YOLO-NAS-L.
  - Độ trễ 7,5 ms không tính detector/SGS.
  - Bộ lọc "trên trời" có lỗi cắt mảng.
  - Bộ đánh giá bỏ qua mẫu âm.
  - Trọng số chỉ dùng phi thương mại.

  Vì vậy VMOKED chỉ là baseline ([ADR-010](03-architecture/90-decisions.md)). Chi tiết: [báo cáo rà soát](research/2026-10-02-danh-gia-dac-ta-v2.md) §3.
- **Agentic UAVs** \[5\]: abstract báo 92% khuyến nghị hành động đúng so với **4,5%** của baseline (không phải 0% như v2), trong mô phỏng tìm kiếm cứu nạn.
- **Krause 2008** \[35\]: chỉ đúng cho bố trí cảm biến **không thích ứng** trên GP với ngân sách cố định. v3 không dùng nó để chặn trần cải thiện.
- **Bickford Smith 2023**: v2 dùng làm lý do không báo cáo entropy; lý do đó lệch ngữ cảnh. v3 thay bằng lập luận về quan sát tương quan (§5.2).
- **Thuật toán:** v2 đề xuất "PPO hoặc SAC cho không gian hành động liên tục" trong khi hành động là rời rạc. v3: PPO rời rạc / masked, và chỉ sau khi so với baseline cổ điển.

---

## 13. Tài liệu tham khảo

1. Vu, V., Tran-Anh, D., Tran, C. *A Low-Resource System for Rapid and Accurate Forest Fire Smoke Detection Using Video-Based Multiple Object Kinetic Emission Detection.* SSRN preprint [5295846](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5295846); bản liên quan [5005161](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5005161). Mã: [GloryVu/VSMOKED](https://github.com/GloryVu/VSMOKED).
2. WSDataset — wildfire-smoke-detection (Kaggle, chưa xác minh).
3. *Cross-Dataset Evaluation of YOLOv8 for UAV Fire and Smoke Detection…* Drones 10(8):635, 2026. https://www.mdpi.com/2504-446X/10/8/635
4. *ContextFireAgent: A Multi-Role Consensus Agent for RGB Wildfire Monitoring.* Remote Sensing 18(18):3066, 2026. https://www.mdpi.com/2072-4292/18/18/3066
5. Koubaa, A., Gabr, K. *Agentic UAVs: LLM-Driven Autonomy with Integrated Tool-Calling and Cognitive Reasoning.* arXiv:2509.13352.
6. Nghị định 288/2025/NĐ-CP về quản lý tàu bay không người lái và phương tiện bay khác (hiệu lực 05/11/2025).
7. *Use of Remote Sensing to Identify Forest Fire and Crop Residue Burning.* ResearchGate 363134581.
8. *Overcoming Common Pitfalls to Improve the Accuracy of Crop Residue Burning Measurement Based on Remote Sensing Data.* Remote Sensing 16(2):342.
9. Wang, J. et al. *LoveDA.* NeurIPS 2021 Datasets & Benchmarks.
10. *OpenEarthMap.* https://open-earth-map.org
11. Boguszewski, A. et al. *LandCover.ai.* CVPRW 2021.
12. *First comprehensive quantification of annual land use/cover from 1990 to 2020 across mainland Vietnam.* Scientific Reports.
13. *Land Cover 2020 in Vietnam.* OD Mekong Datahub.
14. *Emission inventories of rice straw open burning in the Red River Delta of Vietnam.* Environmental Pollution.
15. *From pixels to patterns: review of remote sensing techniques for mapping shifting cultivation systems.* Spatial Information Research.
16. ArduPilot Copter — Guided mode. https://ardupilot.org/copter/docs/ac2_guidedmode.html ; PX4 Offboard (phương án thay thế). https://docs.px4.io/main/en/ros2/offboard_control
17. *Northern region sees sharp rise in forest fires in early 2025.* Việt Nam News.
18. Wald, A. *Sequential Tests of Statistical Hypotheses.* Annals of Mathematical Statistics, 1945; Wald, A., Wolfowitz, J. *Optimum character of the sequential probability ratio test.* 1948.
19. Chernoff, H. *Sequential Design of Experiments.* Annals of Mathematical Statistics, 1959.
20. Naghshvar, M., Javidi, T. *Active Sequential Hypothesis Testing.* Annals of Statistics 41(6), 2013. https://projecteuclid.org/euclid.aos/1387313387
21. Golovin, D., Krause, A., Ray, D. *Near-Optimal Bayesian Active Learning with Noisy Observations.* NeurIPS 2010. https://las.inf.ethz.ch/files/golovin10near.pdf
22. Golovin, D., Krause, A. *Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization.* JAIR, 2011.
23. Kartik, D., Sabir, E., Mitra, U., Natarajan, P. *Policy Design for Active Sequential Hypothesis Testing using Deep Learning.* Allerton 2018. arXiv:1810.04859
24. Jayaraman, D., Grauman, K. *Look-Ahead Before You Leap: End-to-End Active Recognition by Forecasting the Effect of Motion.* ECCV 2016.
25. Angelopoulos, A. N. et al. *Conformal Risk Control.* ICLR 2024.
26. Geifman, Y., El-Yaniv, R. *Selective Classification for Deep Neural Networks.* NeurIPS 2017.
27. Dewangan, A. et al. *FIgLib & SmokeyNet.* Remote Sensing 14(4):1007, 2022.
28. Lostanlen, M. et al. *Scrapping the Web for Early Wildfire Detection (PyroNear).* arXiv:2402.05349.
29. *FLAME 3 Dataset: Unleashing the Power of Radiometric Thermal UAV Imagery for Wildfire Management.* arXiv:2412.02831.
30. *Boreal Forest Fire: UAV-collected Wildfire Detection and Smoke Segmentation Dataset.* Scientific Data, 2025.
31. *FASDD: An Open-access 100,000-level Flame and Smoke Detection Dataset.* ESSD (preprint essd-2022-394).
32. de Venâncio, P. et al. *D-Fire dataset.* 2022.
33. *VDD: Varied Drone Dataset for Semantic Segmentation.* arXiv:2305.13608 / JVCIR 2025; Lyu, Y. et al. *UAVid.* ISPRS JPRS 2020.
34. *PyroTrack.* arXiv:2403.11095; *FIRE-VLM.* WACV Workshops 2026.
35. Krause, A., Singh, A., Guestrin, C. *Near-Optimal Sensor Placements in Gaussian Processes.* JMLR 9, 2008 (chỉ áp dụng cho bài toán không thích ứng).
36. Silver, D., Veness, J. *Monte-Carlo Planning in Large POMDPs (POMCP).* NeurIPS 2010; Somani, A. et al. *DESPOT.* NeurIPS 2013.
37. Schulman, J. et al. *Proximal Policy Optimization Algorithms.* arXiv:1707.06347, 2017.
