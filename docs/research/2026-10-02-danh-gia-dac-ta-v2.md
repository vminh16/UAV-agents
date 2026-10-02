# Đánh giá bộ đặc tả v2 — UAV xác minh cảnh báo cháy rừng

*Ngày rà soát: 02/10/2026. Đối tượng: `UAV Xác minh Cháy rừng — PRD _ RRD _ Kiến trúc (v2).md`.*
*Phạm vi: khả thi phần cứng (bao gồm Pixhawk 2.4.8), mức độ "hardcode" của phương pháp, kiểm chứng trích dẫn, ứng viên thay thế, chiến lược viết paper.*

> Quy ước: **[Đã kiểm chứng]** = đã đọc nguồn/mã gốc; **[Ước tính]** = tính toán xấp xỉ, cần đo lại; **[Chưa xác minh]** = không truy cập được nguồn gốc trong phiên này.

---

## 0. Tóm tắt nhanh

1. **Phần sản phẩm (PRD) viết tốt**: tách 3 nhóm báo giả, có `a_abstain`, tách bạch tự chủ và tự động hoá, có ranh giới quyền quyết định, có cảnh báo về rò rỉ tập test. Đây là nền tốt.
2. **Mô hình thị giác VMOKED không cung cấp được thứ mà POMDP cần.** Đọc mã nguồn công khai ([GloryVu/VSMOKED](https://github.com/GloryVu/VSMOKED)) cho thấy:
   - "Motion Measurement Module" chỉ là **trừ khung hình** với **ngưỡng cố định**, không đo được hướng bốc hay tốc độ nở rộng.
   - Con số **64,89 "GFLOPs" thực ra là GMACs của YOLO-NAS-L**. Độ trễ đo được **không tính** thời gian chạy detector và SGS.
   - Notebook đánh giá **tắt module chuyển động** và **bỏ qua toàn bộ mẫu không khói**.
   - Có lỗi cắt mảng trong bộ lọc "trên trời".
   - Trọng số YOLO-NAS **chỉ được dùng phi thương mại**.
3. **Formulation RL chưa bảo vệ được trước phản biện.** Giả thuyết nhị phân với niềm tin Bayes vô hướng và tập góc nhìn rời rạc nhỏ có thể giải **chính xác bằng quy hoạch động**, và chính sách dừng tối ưu có **dạng ngưỡng (SPRT)**. Nếu không so với SPRT, Chernoff hay DP thì kết quả "RL giảm N_hover" không chứng minh được gì. Thêm vào đó, cập nhật Bayes giả định các góc nhìn **độc lập có điều kiện**, điều này sai trong thực tế và sẽ làm niềm tin quá tự tin.
4. **Có 2 trích dẫn lý thuyết bị dùng sai.** Krause 2008 \[19\] áp dụng cho bố trí cảm biến không thích ứng trên GP. Trong bài toán thích ứng có nhiễu, greedy theo information gain **có thể rất tệ** ([Golovin, Krause, Ray 2010](https://las.inf.ethz.ch/files/golovin10near.pdf)). Bickford Smith \[18\] cũng không áp đúng ngữ cảnh.
5. **Phần cứng: Pixhawk 2.4.8 không khớp với đặc tả "PX4 trên STM32H7 + Micro-XRCE-DDS".** Bo 2.4.8 là bản clone FMUv2 (STM32F427, giới hạn 1 MB flash). PX4 phát hành bản cuối cho fmu-v2 ở **v1.15**, và **không chạy được uXRCE-DDS**. Dùng tạm được cho bàn thử và SITL/HITL, nhưng nên thay bằng bo H743 (≈40–150 USD) trước khi bay thật.
6. **Năng lực tính toán biên không phải nút thắt.** Vòng quyết định chạy ở 0,2–2 Hz, thời gian bay giữa các điểm quan sát cỡ hàng chục giây, còn suy luận chỉ cỡ mili-giây. Nút thắt thật là **dữ liệu đa góc nhìn** và **môi trường huấn luyện**.
7. **"3 mảng độc lập" là cách nhìn dễ dẫn tới paper yếu.** Mỗi mảng tách riêng chỉ là ứng dụng (YOLO, PPO, TensorRT). Đóng góp khoa học nằm ở **chỗ ghép nối**: likelihood có hiệu chỉnh theo góc nhìn (CV → tác tử), dừng có kiểm soát rủi ro bỏ sót (tác tử → KPI), chi phí tính toán/bay như một hành động (biên → tác tử).
8. **Khuyến nghị lộ trình paper khi phần cứng hạn chế**: Paper 1 là benchmark *active sequential hypothesis testing* bán mô phỏng từ dữ liệu thật, không cần bay. Paper 2 là bộ dữ liệu UAV khói/giả khói Việt Nam, thu bằng drone rẻ. Paper 3 là hệ thống hoàn chỉnh.

---

## 1. Những điểm đặc tả đang làm đúng (nên giữ)

- Tách 3 nhóm báo giả và quy trách nhiệm cho từng thành phần. Đây là cách viết đúng của một bài báo đánh giá.
- Có `a_abstain` và đường cong coverage–accuracy. Đây là chuẩn mực của selective classification.
- Sửa KPI bỏ sót 0% thành Z%, kèm lập luận về C_MD hữu hạn. Lập luận đúng.
- Ranh giới tự chủ: geofence, failsafe và quyết định điều động thuộc về con người.
- Không đặt LLM/VLM lên phương tiện bay, và lý do về độ trễ là hợp lý.
- Bắt buộc khử trùng lặp và báo cáo zero-shot chéo dataset. Điểm này rất đúng, đã kiểm chứng số liệu 46,0% / 90,7% ở mục 2.
- Ghi chú PX4 Offboard cần luồng setpoint >2 Hz. Đúng theo [tài liệu PX4](https://docs.px4.io/main/en/ros2/offboard_control).

---

## 2. Kiểm chứng trích dẫn và con số

| # | Nội dung trong đặc tả | Kết quả kiểm chứng | Việc cần làm |
|---|---|---|---|
| \[1\] VMOKED | "64,89 GFLOPs, 7,5 ms … **không có** trong phần công khai" | **Sai một phần.** Hai con số này **có** trong abstract SSRN (còn bản SSRN thứ hai cùng tiêu đề: [abstract_id=5005161](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5005161), ngoài 5295846). Tên trong repo là **VSMOKED**. Xem mục 3 về ý nghĩa thật của hai con số. | Sửa câu và dẫn cả hai mã SSRN cùng repo |
| \[1\] mã nguồn | "kho mã nguồn VMOKED của nhóm tác giả" | Repo [GloryVu/VSMOKED](https://github.com/GloryVu/VSMOKED): README ghi *"The source code will availability soon"*. Có mã suy luận, notebook train/eval, commit cuối 15/09/2025. **Không có trọng số**, link WSDataset trong README trống. | Hỏi tác giả về trọng số, dataset, script đánh giá dùng cho paper |
| \[2\] WSDataset | 11.539 / 12.481 khung hình | **[Chưa xác minh]** Tìm kiếm không ra link Kaggle `gloryvu/wildfire-smoke-detection`. Theo mã, dữ liệu gồm các **video từ camera cố định (PTZ có preset)**, không phải từ UAV. | Kiểm tra giấy phép, tốc độ khung hình và nguồn camera |
| \[3\] Drones 10(8):635 | 46,0% D-Fire, 90,7% FASDD_UAV gần-trùng | **[Đã kiểm chứng]** Abstract còn nêu AP@0.5 lớp fire rơi từ 89,1→39,4 (D-Fire→FASDD_UAV) và 72,8→6,0 (chiều ngược lại). Chưa đối chiếu được con số 92,71 / 14,32. | Đối chiếu lại bảng trong bài |
| \[4\] ContextFireAgent | 19,8 s/ảnh so với 0,15 s | Bài tồn tại; acc 0,983 trên N=410 và chỉ gọi YOLO ở 10% ảnh **[Đã kiểm chứng]**. Con số độ trễ **[Chưa xác minh]**. | — |
| \[5\] Agentic UAVs | luật cứng 0%, cục bộ 79%, GPT-4 92% | **Lệch.** Abstract ghi **92% so với 4,5%**, không phải 0% ([arXiv:2509.13352](https://arxiv.org/abs/2509.13352)). Bối cảnh là tìm kiếm cứu nạn trong Gazebo, không phải cháy rừng. | Sửa 0% thành 4,5%, nêu rõ là mô phỏng |
| \[16\] PX4 offboard >2 Hz | — | **Đúng.** | — |
| \[18\] Bickford Smith (EPIG) | Lý do không báo cáo mức giảm entropy | **Dùng lệch ngữ cảnh.** EPIG nói về bất định *tham số mô hình* trong active learning. Ở đây b_t *chính là* bất định dự đoán về H. Lý do đúng để không tin vào entropy là: cập nhật Bayes ngây thơ với các quan sát tương quan làm niềm tin quá tự tin (mục 5.2). | Thay lập luận |
| \[19\] Krause 2008 | "greedy có bảo đảm (1−1/e) nên trần cải thiện bị chặn" | **Dùng sai.** (a) Bảo đảm này dành cho bài toán **không thích ứng**, GP, ngân sách cố định. (b) Bài toán ở đây là **thích ứng và có nhiễu**: greedy information gain có thể rất tệ ([Golovin et al. 2010](https://las.inf.ethz.ch/files/golovin10near.pdf)), và EC² mới có bảo đảm. (c) Mục tiêu "ít lần quan sát nhất để đạt ngưỡng tin cậy" là bài toán *cover*, không phải *maximization*. | Thay bằng Chernoff 1959, [Naghshvar & Javidi 2013](https://projecteuclid.org/euclid.aos/1387313387), Golovin & Krause 2011 (adaptive submodularity), Golovin et al. 2010 (EC²) |
| Phần IV | "PPO hoặc SAC cho không gian hành động liên tục" | **Mâu thuẫn nội bộ.** Không gian hành động mô tả ở Phần II là **rời rạc** (quay 45°, ±20 m, 3 hành động kết thúc). SAC không phù hợp. | Đổi thành PPO rời rạc / DQN / masked PPO |
| Tầng 1 | "PX4 trên STM32H7, ROS 2, Micro-XRCE-DDS" | **Không khớp phần cứng dự kiến** (Pixhawk 2.4.8 = STM32F427). Xem mục 6. | Sửa |
| Phụ lục mục 3 | KPI 10 phút tính cả khứ hồi | KPI chỉ yêu cầu **có mặt và kết luận**. Khứ hồi chỉ ảnh hưởng ngân sách pin. Xem tính toán ở mục 6.3. | Tách KPI thời gian và ngân sách pin |

---

## 3. VMOKED/VSMOKED nhìn từ mã nguồn — các phát hiện quan trọng

Repo đã đọc: `GloryVu/VSMOKED`, commit `2025-09-15 "add test func"`. **Lưu ý công bằng:** đây là repo công khai, README ghi mã chưa đầy đủ. Mã dùng để ra số liệu trong paper có thể khác. Các điểm dưới đây cần **hỏi lại tác giả** trước khi kết luận về bài báo. Dù vậy, chúng đủ để thấy **không nên đặt VMOKED làm "xương sống" cho UAV**.

### 3.1 Kiến trúc thật

| Thành phần | Đặc tả mô tả | Mã thực tế |
|---|---|---|
| Detector | "mô hình phát hiện thời gian thực" | **YOLO-NAS-L** (super-gradients), fine-tune từ trọng số COCO (`pretrained_weights="coco"`), 15–20 epoch |
| SGS | MobileNetV3 + FPN tách trời/đất, "loại mây trên cao" | `smp.FPN(timm-mobilenetv3_small_minimal_100)` ở 320×320, 1 lớp `sky`, khoảng 3,2 GMACs. Dùng như **bộ lọc cứng**: bỏ box nếu ≥80% diện tích nằm trên trời |
| MMM | "phát hiện luồng chuyển động nở rộng và bốc lên" | `motion_measure` = 1 − độ tương đồng xám trung bình giữa các crop 75×75 liên tiếp (**trừ khung hình**). **Không có hướng, không có độ nở, không có optical flow** |

### 3.2 Các ngưỡng hardcode (`vsmoked/object_detection.py`)

`windowsize=7`, `step=3`, `preset_similarity=0.9`, `curbbox_motion_threshold=0.02`, `bboxes_motion_threshold=0.02`, `on_sky threshold=0.8`, `conf=0.4`, `score≥0.1`, `IoU≥0.1` khi ghép box, crop `75×75`.

- `preset_similarity`: nếu khung đầu và khung cuối của cửa sổ lệch nhau hơn 10% thì **xoá mọi phát hiện**. Ngưỡng này sinh ra cho camera PTZ chuyển preset. **Trên UAV**, chỉ cần drift khi hover hoặc gimbal chỉnh là có thể xoá trắng kết quả.

### 3.3 Lỗi đã tái hiện được bằng script

1. **Bộ lọc "trên trời" cắt mảng sai** (`on_sky`, dòng 99–101): viết `mask[y0:y1][x0:x1]` thay vì `mask[y0:y1, x0:x1]`. Với box `[500,100,600,200]` nằm hoàn toàn trên trời, lát cắt sai có shape `(0, 640)` và tổng bằng 0, trong khi lát cắt đúng có tổng 10.000. Hệ quả: bộ lọc SGS **hầu như không bao giờ kích hoạt**. Lợi ích "loại mây" vì thế chưa được chứng minh bằng mã này.
2. **Điểm chuyển động bị chia cho diện tích box** (dòng 76): `score × (75·75)/(h·w)`. Cùng một mức thay đổi 5% điểm ảnh cho điểm 0,05 với box 75×75, nhưng chỉ 0,0125 với box 150×150 và 0,003 với box 300×300 (ngưỡng là 0,02). Từ UAV ở 100–200 m, cột khói **chiếm vùng lớn trong khung hình** nên sẽ bị loại là "không chuyển động".
3. **Độ trễ không tính detector và SGS.** Comment trong code ghi *"We measure latency from here because in product we cache previous predict"*, và lời gọi SGS nằm ngoài vùng đo thời gian. Notebook `test.ipynb` đo riêng detector được 1000 lần chạy trong 12,02 s, tức **khoảng 12 ms mỗi lần**. Máy đo có CPU AVX-512, tức máy bàn/máy chủ, không phải Jetson.
4. **64,89 "GFLOPs" là GMACs của YOLO-NAS-L.** `flops_eval.ipynb` dùng `torchprofile.profile_macs(yolo_nas_l)` rồi in ra "Our Framework: … GFlOPs". Số phép tính thực tế khoảng **130 GFLOPs**. Câu hỏi "8,6 TFLOPS duy trì" trong đặc tả vì vậy đặt sai cơ sở.
5. **Đánh giá bỏ qua mẫu âm tính.** Trong `test.ipynb` có `if len(y)!=0: ... else: continue`, tức **mọi clip không khói đều bị bỏ qua**. Trong `eval_testset_ourmodel.py`, điều kiện `gt==0 & pred==0` bị tính theo độ ưu tiên toán tử thành `gt==0`, nên khi ảnh không có GT thì luôn cộng TN=1, **không bao giờ đếm FP**. Với một dự án mà mục tiêu chính là giảm báo giả, đây là lỗ hổng nghiêm trọng.
6. **Module chuyển động bị tắt khi đánh giá.** `test.ipynb` gọi `set_params(7,2,0.7,-1,-1)` (ngưỡng −1), còn script eval gọi `set_params(2,1,0.9,0.0,0.0)` (ngưỡng 0). Cả hai đều không lọc gì.

### 3.4 Hệ quả cho dự án

- **Giấy phép**: trọng số YOLO-NAS dùng phi thương mại, Deci đã được NVIDIA mua lại và repo không còn được bảo trì ([YOLONAS.md](https://github.com/Deci-AI/super-gradients/blob/master/YOLONAS.md), [NVIDIA forum](https://forums.developer.nvidia.com/t/licensing-and-usage-terms-for-yolo-nas-model/326342)). Cho bài báo thì được, nhưng **không dùng được cho sản phẩm** trong PRD.
- **Hiệu năng trên Orin Nano**: YOLO-NAS-L chạy FP16 mất 7,87 ms trên T4 ([model zoo](https://github.com/Deci-AI/super-gradients/blob/master/documentation/source/model_zoo.md)). Orin Nano Super có năng lực FP16 tensor khoảng ¼ và băng thông khoảng ⅓ so với T4, nên **[Ước tính]** cỡ 25–40 ms/khung FP16. **Vẫn đủ** cho vòng quyết định 0,2–2 Hz, vì 20 khung (2 s ở 30 fps, step 3) chỉ mất khoảng 0,5–0,8 s.
- **Kết luận**: giữ VMOKED làm **baseline** (chạy lại với bộ đánh giá đã sửa), **không** làm xương sống. Cũng không nên chỉ "mở rộng số lớp của SGS": SGS hiện chỉ là bộ lọc nhị phân, và lớp phủ đất ở góc xiên UAV là một bài toán khác.

---

## 4. Phương pháp trong đặc tả có đang "hardcode" không?

Câu trả lời ngắn: **có, ở nhiều chỗ quan trọng hơn người đọc tưởng**. Ngoài ra, phần được gọi là "học" có nguy cơ hội tụ về một quy tắc ngưỡng cổ điển.

| Thành phần | Hiện trạng trong đặc tả | Vì sao là vấn đề | Đề xuất |
|---|---|---|---|
| Đặc trưng khói z^khói | "nguồn điểm, hướng bốc, tốc độ nở" từ VMOKED | VMOKED **không xuất** các đặc trưng này (mục 3). Nếu tự viết luật để tính thì lại là hardcode | Optical flow sau khi ổn định ảnh (homography/ECC), rồi đặc trưng vật lý (thành phần thẳng đứng, divergence, điểm hội tụ ngược) **+** đầu phân loại thời gian học được |
| **Likelihood P(z\|H,v)** | Không nói lấy từ đâu | Đây là **trái tim** của cập nhật Bayes. Tự đặt bảng độ chính xác theo góc thì là hardcode. Nếu dùng xác suất softmax của CNN thì sai, vì đó là posterior chưa hiệu chỉnh | Học từ dữ liệu: histogram/mật độ điểm detector theo nhóm (khoảng cách, góc mặt trời, tỷ lệ che khuất); hiệu chỉnh bằng temperature/isotonic; kiểm tra bằng reliability diagram |
| Cập nhật Bayes | Nhân likelihood qua các góc nhìn | Giả định **độc lập có điều kiện** bị vi phạm: cùng một cột khói, cùng một detector, cùng một lỗi hệ thống (ví dụ detector luôn nhầm mây trắng). Hệ quả là niềm tin quá tự tin, dừng sớm và **sai** | Likelihood "tempered" (lũy thừa τ<1, fit trên tập validation), hoặc bộ tổng hợp học được (RNN/Transformer nhỏ trên embedding của các góc nhìn). So sánh cả hai |
| b₀ từ GIS | Tra bảng theo loại đất | Prior viết tay | Ước lượng từ nhật ký cảnh báo lịch sử của Chi cục, cụ thể là tỷ lệ cảnh báo đúng theo loại đất × mùa × giờ |
| Nhãn "nghi đốt nương" | "suy ra bằng luật" | Hardcode. Quan trọng hơn: **khoảng 65% số vụ cháy rừng ở VN do đốt nương làm rẫy hoặc đốt đồng cỏ cháy lan** (số liệu Bộ NN&PTNT được báo chí dẫn lại: [moitruong.net.vn](https://moitruong.net.vn/bo-nn-ptnt-chi-ra-nguyen-nhan-chay-rung-lien-tuc-dien-ra-trong-4-thang-dau-nam-74272.html), [CAND](https://cand.vn/Xa-hoi/chay-rung-gia-tang--vi-sao--i730402/); **cần số liệu gốc**). Khói trên đất nương **không đồng nghĩa với vô hại** mà là nguồn cháy lan số 1 | Đổi khung: nhóm 2 = "nguồn khói trên đất canh tác". Mức khẩn = f(khoảng cách tới bìa rừng, hướng và tốc độ gió, độ ẩm, giấy phép đốt). Đây là bài toán xếp hạng rủi ro, không phải "hợp pháp / không" |
| Cơ chế đồng thuận onboard–GIS | Mâu thuẫn thì abstain | **Có hai cơ chế abstain chồng nhau**: một do tác tử học, một do luật ở máy chủ ghi đè. Trục coverage–accuracy vì vậy không còn đo riêng chính sách | Đưa độ mâu thuẫn GIS vào trạng thái (hoặc vào likelihood), để abstain chỉ đến từ một nguồn |
| Hằng số phần thưởng | C_FA, C_MD, C_AB, c_hover chọn tay | Phạt C_MD **không bảo đảm** tỷ lệ bỏ sót ≤ Z% (KPI của chính PRD) | Đổi thành **ràng buộc**: Lagrangian PPO (CMDP), hoặc chọn ngưỡng dừng bằng **conformal risk control** để bảo đảm E\[FNR\] ≤ α ([Angelopoulos et al., ICLR 2024](https://github.com/aangelopoulos/conformal-risk)) |
| Không gian hành động | Lưới cố định: quay 45°, ±20 m, nghiêng | Chấp nhận được. Đây là thiết kế, không phải lỗi, nhưng cần nói rõ | Giữ lưới. Thêm action mask cho geofence/địa hình |
| Hover 2 s, cự ly 100–200 m, độ cao 80–120 m | Cố định | Đặc tả đã ghi chú. **[Ước tính]** Ở 150 m với HFOV 80° và ảnh 1920 px thì khoảng 0,13 m/px. Khói bốc 1–2 m/s cho 15–30 px trong 2 s, đủ đo. Nhưng **sương trôi theo gió 1–3 m/s cũng cho độ lớn tương tự**, nên cần **hướng** chuyển động chứ không chỉ "có chuyển động" | Biến thời gian hover thành tham số của hành động (1/2/4 s) để tác tử tự học |
| Tác tử máy chủ "nghị luận" | Xếp mức khẩn, đối chiếu GIS | Thực chất là **bộ luật chấm điểm** cộng phần sinh báo cáo. Chưa có thiết kế nào cho thấy cần LLM | Viết rõ: luật chấm điểm (minh bạch) cộng VLM/LLM chỉ để rà soát bằng chứng và sinh báo cáo, theo kiểu ContextFireAgent |
| **Chính sách RL** | "3 quyết định không ai chỉ định" | Xem mục 5.1: với cấu trúc bài toán này, **chính sách tối ưu đã biết dạng** (ngưỡng trên b_t, phụ thuộc vị trí và ngân sách còn lại) và **tính chính xác được bằng DP** | RL chỉ đáng dùng khi trạng thái có đặc trưng nhiều chiều (ảnh, vị trí nguồn khói chưa biết). Phải thắng SPRT/Chernoff/DP mới được tính là đóng góp |

> Hardcode **không xấu** trong hệ thống an toàn: ngưỡng minh bạch dễ kiểm định hơn mạng nơ-ron. Vấn đề là đặc tả **gọi nó là học** và lấy đó làm đóng góp khoa học. Bài báo cần nói rõ phần nào học, phần nào thiết kế, và vì sao phần học là cần thiết.

---

## 5. Các vấn đề lý thuyết của formulation

### 5.1 RL có thực sự cần không?

- Trạng thái của belief-MDP gồm (b_t, vị trí, K_remain). Với b_t lưới 201 điểm, khoảng 48 vị trí (8 phương vị × 3 cự ly × 2 góc nghiêng) và K ≤ 6, ta có **khoảng 58 nghìn trạng thái × khoảng 51 hành động**. **Value iteration giải trong vài giây trên laptop.** Nếu đã có mô hình quan sát thì DP cho chính sách **tối ưu**, RL không thể vượt.
- Lý thuyết dừng tối ưu (Wald–Wolfowitz; Chernoff 1959; [Naghshvar & Javidi 2013](https://projecteuclid.org/euclid.aos/1387313387)) cho biết phần dừng có **dạng ngưỡng** trên posterior. Do đó "Quyết định 2 — nhìn bao nhiêu lần" chính là **SPRT** (1948). Giảm N_hover so với quỹ đạo tròn là do **dừng tuần tự**, không phải do học.
- **RL có giá trị thật khi**: (i) mô hình quan sát không có dạng đóng, phải học từ ảnh; (ii) trạng thái có thêm **vị trí nguồn khói chưa biết** (điểm nóng VIIRS có sai số vị trí cỡ một pixel 375 m, có thể tới khoảng 1,5 km; camera chòi canh chỉ cho phương vị), tức bài toán **tìm kiếm + xác minh**; (iii) chính sách phải tổng quát hoá qua nhiều địa hình mà không giải lại DP. Đã có tiền lệ dùng deep RL cho active hypothesis testing ([Kartik et al. 2018](https://arxiv.org/abs/1810.04859)), và RL end-to-end cho nhận dạng chủ động ([Jayaraman & Grauman, ECCV 2016](https://arxiv.org/pdf/1605.00164)).
- **Baseline bắt buộc nên thêm** (ngoài 3 baseline hiện có):
  - B4: góc cố định + **SPRT**.
  - B5: **greedy-IG + SPRT**.
  - B6: **Chernoff test** hoặc **EC²**.
  - B7: **DP-tối ưu** với mô hình quan sát đã biết. Đây là trần lý thuyết.
  - B8: **POMCP/DESPOT** (lập kế hoạch online).

### 5.2 Quan sát tương quan

Hai lần nhìn cùng một cột khói không phải hai phép đo độc lập. Nếu nhân likelihood ngây thơ, b_t vượt ngưỡng sau 1–2 lần nhìn, kể cả khi detector đang nhầm hệ thống (ví dụ mây trắng sát tán rừng). Đây vừa là **rủi ro an toàn** vừa là **câu hỏi nghiên cứu đáng viết**: *đo mức tương quan giữa các góc nhìn, và so sánh fusion tempered với fusion học được về độ hiệu chỉnh và tỷ lệ bỏ sót*.

### 5.3 Định nghĩa giả thuyết

H₁ "cần báo động" đang trộn **hiện tượng vật lý** (có khói/cháy) với **quyết định chính sách** (có điều động không). Camera chỉ có thông tin về cái thứ nhất. Đề xuất: H_smoke ∈ {khói, không khói} cho tác tử onboard, còn quyết định báo động = g(b(H_smoke), lớp phủ tại chân khói, GIS, thời tiết). Nhờ vậy mỗi nhóm báo giả có một thước đo riêng, đúng tinh thần PRD.

---

## 6. Phần cứng — đặc tả có ổn với phần cứng hạn chế không?

### 6.1 Pixhawk 2.4.8 (bộ điều khiển bay dự kiến)

| Hạng mục | Thực tế | Nguồn |
|---|---|---|
| Vi điều khiển | STM32F427 168 MHz, 192 KB RAM, **1 MB flash** (bản clone FMUv2; nhiều bo dính lỗi silicon giới hạn 1 MB) | [ArduPilot Pixhawk overview](https://ardupilot.org/copter/docs/common-pixhawk-overview.html) |
| PX4 | fmu-v2 **phát hành lần cuối ở v1.15**, nhiều module bị tắt để vừa 1 MB | [PX4 v1.16 – Pixhawk 1](https://docs.px4.io/v1.16/en/flight_controller/pixhawk), [Discontinued](https://docs.px4.io/main/en/flight_controller/autopilot_discontinued) |
| ROS 2 qua uXRCE-DDS | **Không dùng được** bản build tiêu chuẩn trên bo 1 MB. Phải dùng MAVLink (MAVROS/MAVSDK/pymavlink) | [PX4 uXRCE-DDS](https://docs.px4.io/main/en/middleware/uxrce_dds), [diễn đàn PX4](https://discuss.px4.io/t/is-pixhawk-2-4-8-fully-supported-by-px4/27180) |
| ArduPilot | Có firmware `Pixhawk1-1M` (tính năng rút gọn); diễn đàn khuyên giữ ở phiên bản cũ | [ArduPilot Discourse](https://discuss.ardupilot.org/t/which-firmware-should-be-used-on-a-pixhawk-2-4-8/142386) |
| Chất lượng | Bản clone thường kém về chống rung IMU, ổn áp, barometer. **Không nên** dùng cho bay ngoài tầm nhìn (BVLOS) trên rừng | Kinh nghiệm cộng đồng |

**Khuyến nghị**:
- **Giai đoạn bàn thử, SITL/HITL và bay thử trong tầm nhìn**: dùng Pixhawk 2.4.8 được. Chọn **ArduPilot Pixhawk1-1M** hoặc **PX4 v1.15 fmu-v2**, nối companion qua **MAVLink**.
  - ArduPilot Guided nhận **mục tiêu vị trí** và tự giữ vị trí đó, không cần stream liên tục. Lệnh vận tốc hết hạn sau `GUID_TIMEOUT` (mặc định 3 s) ([Guided mode](https://ardupilot.org/copter/docs/ac2_guidedmode.html)). Như vậy **bỏ được bộ nội suy 10–20 Hz** mà Tầng 1 yêu cầu cho PX4 Offboard.
- **Trước khi bay thật**: đổi sang bo **STM32H743**: [Pixhawk 6C Mini](https://holybro.com/products/pixhawk-6c-mini) khoảng 130–150 USD, hoặc bo H743 giá rẻ như [MicoAir H743](https://robofusion.net/products/micoair-h743-flight-controller) khoảng 40–50 USD, đều hỗ trợ PX4/ArduPilot. Cả hai đường đều có ROS 2 native: PX4 qua uXRCE-DDS, ArduPilot ≥4.5 qua AP_DDS ([ArduPilot ROS 2](https://ardupilot.org/dev/docs/ros2.html)).
- **Sửa Tầng 1 trong đặc tả** cho khớp phần cứng thật.

### 6.2 Các thành phần khác

| Thành phần | Đặc tả | Đánh giá | Ghi chú |
|---|---|---|---|
| Máy tính biên | Jetson Orin Nano | **Ổn.** Bản Super: 67 TOPS INT8, 8 GB LPDDR5 102 GB/s, 7–25 W, 249 USD ([NVIDIA](https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/)). YOLO26n TensorRT FP16 khoảng 4,6 ms ([Ultralytics](https://docs.ultralytics.com/guides/nvidia-jetson)) | Nút thắt là **khối lượng và tản nhiệt** (mùa khô 35–40 °C), không phải TOPS. **[Ước tính]** 15 W chỉ bằng vài % công suất hover của một quad 2–3 kg |
| Phương án rẻ hơn | — | RPi 5 + AI HAT+ (Hailo-8, 26 TOPS): YOLOv8m khoảng 140 FPS theo datasheet ([so sánh](https://www.electromaker.io/blog/article/hailo-8-vs-hailo-8l-vs-hailo-10h-which-ai-accelerator-should-you-buy)) | Hỗ trợ kém cho mô hình video và optical flow. Hợp với detector, không hợp với nhánh thời gian |
| Camera + gimbal | RGB 3 trục | [SIYI A8 mini](https://shop.siyi.biz/collections/gimbal-camera): khoảng 260–330 USD, 95 g, điều khiển qua MAVLink | **Thermal**: [SIYI ZT6](https://siyi.biz/en/product/tri-axis-multi-sensor-gimbal-pod/zt6/) (640×512 radiometric + 4K) tương thích PX4/ArduPilot. Phản biện chắc chắn sẽ hỏi "vì sao không dùng thermal?" — cần biện luận bằng chi phí hoặc đưa thermal vào làm biến thể |
| Đường truyền | Mất sóng 15 s thì về trạm | Vùng núi Việt Nam phủ 4G chập chờn | Cần radio tầm xa và **băng thông video** nếu muốn rà soát ở máy chủ |
| Trạm sạc tự động | Có trong PRD | **Ngoài phạm vi nghiên cứu.** Phương án thương mại: [DJI Dock 3](https://www.dronefly.com/products/dji-dock-3-matrice-4td-with-care-enterprise-plus) (khoảng 15,9 nghìn USD) + [M4TD](https://advexure.com/products/dji-matrice-4td-for-dock-3) (khoảng 7,6 nghìn USD, có thermal), chạy mô hình riêng qua FlightHub 2 / [Manifold 3](https://www.dronefly.com/products/dji-manifold-3) (100 TOPS) | Tự làm dock là một dự án cơ khí riêng |
| Thu dữ liệu giá rẻ | — | **DJI Mini 4 Pro + MSDK v5** (Android; hỗ trợ từ 17/03/2025; có waypoint và virtual stick) ([Dronelink](https://support.dronelink.com/hc/en-us/community/posts/39483696617363-Mini-4-Pro-MSDK-support-released-March-17th-2025), [MSDK v5](https://github.com/dji-sdk/Mobile-SDK-Android-V5)) | Đủ để quay **video đa góc nhìn** cho bộ dữ liệu và thử chính sách, với suy luận ở mặt đất |

### 6.3 Ngân sách thời gian cho KPI "dưới 10 phút trong bán kính 5 km" [Ước tính]

| Cruise | Bay 5 km | Cất cánh và lên độ cao | 3 lần quan sát (dịch chuyển khoảng 20–30 s + hover 2 s) | Tổng |
|---|---|---|---|---|
| 10 m/s | 8,3 phút | khoảng 1 phút | khoảng 1,5 phút | **khoảng 10,8 phút (trượt KPI)** |
| 15 m/s | 5,6 phút | khoảng 1 phút | khoảng 1,5 phút | **khoảng 8,1 phút (đạt)** |

Như vậy KPI đòi **cruise ≥ 12–15 m/s** khi có gió, khả thi với drone thương mại nhưng nặng với quad tự chế mang gimbal + Jetson. Chú ý **thời gian bay giữa các góc nhìn chiếm áp đảo** so với suy luận. Hệ quả là c_hover nên được mô hình hoá theo **quãng đường dịch chuyển**, không phải hằng số.

---

## 7. "Ba mảng độc lập"? — Đóng góp nằm ở chỗ ghép nối

| Mảng | Nếu làm tách rời | Đóng góp khi ghép nối |
|---|---|---|
| Computer vision | Fine-tune YOLO trên dữ liệu khói, rất nhiều bài đã làm | Phải xuất ra **likelihood hiệu chỉnh, phụ thuộc góc nhìn** P(z\|H,v) và **đo được tương quan giữa các góc** để tác tử dùng |
| Tác tử tự hành | Chạy PPO trên môi trường tự viết | **Dừng tuần tự có kiểm soát rủi ro bỏ sót** (Z%) và có abstain, chứng minh khi nào học vượt được SPRT/Chernoff/DP |
| Thiết bị biên | Đo FPS trên Jetson | **Chi phí tính toán và chi phí bay là hành động**: chạy model rẻ hay đắt, xử lý onboard hay gửi về máy chủ, bay thêm hay dừng |

Viết thành ba bài "ứng dụng" riêng thì mỗi bài đều mỏng. Viết **một câu hỏi khoa học cắt ngang cả ba** thì có bài tốt.

---

## 8. Chiến lược viết paper

### 8.1 Các lựa chọn

| Lựa chọn | Câu hỏi nghiên cứu | Cần phần cứng? | Độ mới | Venue phù hợp (tham khảo) |
|---|---|---|---|---|
| **A. Active verification benchmark** *(khuyến nghị làm trước)* | Khi nào chọn góc nhìn chủ động, và khi nào việc học, thực sự giúp xác minh khói, dưới quan sát tương quan và ràng buộc tỷ lệ bỏ sót? | **Không**: bán mô phỏng từ dữ liệu thật + GPU | Trung bình–cao nếu có kết quả âm/dương rõ ràng so với baseline cổ điển | RA-L / IROS / ICRA (khó); *Drones*, *Remote Sensing*, *Fire*, *IEEE Access*; workshop CVPR EarthVision, WACV CV4EO (nơi [FIRE-VLM](https://arxiv.org/html/2601.03449v1) xuất hiện), NeurIPS CCAI |
| **B. Bộ dữ liệu UAV khói/giả khói Việt Nam** | Thiếu dữ liệu UAV đa góc cho smoke vs sương/mây thấp/bụi/hơi nước, kèm lớp phủ tại chân khói; phải có protocol khử trùng lặp và zero-shot chéo | Drone rẻ (Mini 4 Pro) + phối hợp kiểm lâm khi đốt thực bì có phép | **Cao** vì hiện chưa có bộ tương tự cho Đông Nam Á | *Scientific Data*, *Data in Brief*, ESSD, *Remote Sensing*, *Drones* |
| **C. Compute-aware active verification** | Tác tử chọn cả **nhìn ở đâu** lẫn **chạy mô hình nào / xử lý ở đâu** (YOLO-n onboard, mô hình video onboard, VLM ở mặt đất), với chi phí thời gian + năng lượng + băng thông | 1 Orin Nano đo profile trên bàn | **Cao**: ghép thật sự ba mảng; tiền lệ ContextFireAgent chỉ gọi YOLO ở 10% ảnh | Như A; *IEEE IoT Journal*, *JRTIP* |
| D. Hệ thống hoàn chỉnh + bay thực địa | Hệ thống có giảm điều động thừa ngoài thực tế không? | Đầy đủ | Thấp về thuật toán, cao về thực tiễn | *Journal of Field Robotics*, *Drones*, *Fire* |

**Lộ trình khuyến nghị khi phần cứng hạn chế**: **A** (3–4 tháng, chỉ cần máy tính) → **B** (chạy song song việc thu dữ liệu, dùng lại cho A) → **C** hoặc **D** khi đã có drone H743 + Orin.

### 8.2 Khung bài cho lựa chọn A

- **Tên tạm**: *"Look Again or Decide? Risk-Controlled Active Sequential Hypothesis Testing for UAV Wildfire Smoke Verification"*.
- **Đóng góp (3 ý)**:
  1. Formulation xác minh khói như **active SHT có abstain và ràng buộc tỷ lệ bỏ sót**, kèm **mô hình quan sát phụ thuộc góc nhìn học từ dữ liệu thật** và mô hình tương quan giữa các góc.
  2. **Benchmark bán mô phỏng** công khai, dựng từ clip thật: FIgLib, PyroNear, Boreal Forest Fire, FLAME, FASDD_UAV và dữ liệu tự thu, kèm protocol khử trùng lặp.
  3. So sánh có hệ thống: SPRT, Chernoff/EC², DP-tối ưu, POMCP, PPO/Recurrent PPO. Phân tích **khi nào học có ích**, ví dụ khi vị trí nguồn khói bất định hoặc khi quan sát tương quan mạnh, và **khi nào không**. Ngưỡng dừng hiệu chỉnh bằng conformal risk control để bảo đảm FNR ≤ α.
- **Thí nghiệm cốt lõi**:
  - Đường cong coverage–accuracy.
  - N_hover và thời gian ra quyết định có tính quãng bay.
  - FNR thực tế so với α mục tiêu.
  - Độ nhạy theo mức tương quan ρ và mức hiệu chỉnh sai của detector.
  - Zero-shot chéo dataset.
  - Phụ lục: độ trễ và năng lượng trên Orin Nano.
- **Thí nghiệm nên chạy ngay, khoảng 1 ngày**: cài DP trên mô hình quan sát đồ chơi rồi so với PPO. Nếu PPO chỉ hội tụ về DP thì **đóng góp không thể là "RL"**. Phải chuyển trọng tâm sang mô hình quan sát, quan sát tương quan và kiểm soát rủi ro, hoặc mở rộng bài toán sang tìm kiếm + xác minh.

---

## 9. Các ứng viên nên thử

### 9.1 Thị giác

| Vai trò | Ứng viên | Lý do / lưu ý |
|---|---|---|
| Detector khói | YOLO26 / YOLO11 n–s (Ultralytics, **AGPL-3.0**); RT-DETRv2 / D-FINE / DEIM (Apache-2.0) | Thay YOLO-NAS (vướng giấy phép). Bản n/s chạy vài ms trên Orin Nano |
| Nhánh thời gian (thay MMM) | Ổn định ảnh (ECC/homography) → optical flow (Farnebäck; RAFT-small / NeuFlow trên GPU) → đặc trưng vật lý: thành phần thẳng đứng, divergence, điểm nguồn | Cho ra đúng z^khói mà đặc tả cần, và giải thích được |
| Phân loại video nhẹ | TSM-MobileNetV2, X3D-XS, MoViNet-A0; STCNet và CNN-LSTM (đã có trong repo VSMOKED, dùng làm baseline); SmokeyNet ([FIgLib](https://arxiv.org/pdf/2112.08598)) | Lưu ý: dữ liệu chòi canh (FIgLib) **khoảng 1 khung/phút**. Động học học từ đó khác hẳn clip hover 2 s ở 30 fps |
| Zero-shot / mở từ vựng | [YOLOE](https://docs.ultralytics.com/models/yoloe), YOLO-World, Grounding DINO + SAM/MobileSAM ([ví dụ cho khói](https://github.com/sidkudupudi/zero-shot-wildfire-smoke-segmentation)), [EdgeTAM](https://github.com/facebookresearch/EdgeTAM) để bám vùng khói qua khung | Baseline không cần gắn nhãn; EdgeTAM giúp đo độ nở của vùng khói theo thời gian |
| Lớp phủ tại chân khói | Huấn luyện trên **ảnh drone xiên**: [VDD](https://arxiv.org/abs/2305.13608) (30°/60°/90°, 50–120 m), [UAVid](https://www.sciencedirect.com/science/article/abs/pii/S0924271620301295), IDD, cộng 500–2.000 ảnh VN. Mô hình SegFormer-B0, PIDNet-S, DDRNet-slim, hoặc DINOv2/v3-small đóng băng + đầu tuyến tính | LoveDA, OpenEarthMap, LandCover.ai là **ảnh nadir/ortho**. Lệch miền lớn với góc xiên UAV, chỉ nên dùng để pre-train |
| Hiệu chỉnh xác suất | Temperature/isotonic theo nhóm góc nhìn; conformal | Bắt buộc nếu muốn dùng làm likelihood |
| Rà soát ở máy chủ | VLM nhỏ/vừa theo kiểu [ContextFireAgent](https://www.mdpi.com/2072-4292/18/18/3066) | Chỉ dùng để rà soát và sinh báo cáo, không nằm trong vòng bay |
| Thermal (tuỳ chọn) | [FLAME 3](https://arxiv.org/html/2412.02831v1) (RGB + thermal radiometric từ UAV) | Gần như giải luôn nhóm 1 và chế độ đêm. Cân nhắc làm biến thể "RGB-only vs RGB-T" |

### 9.2 Ra quyết định (tác tử)

| Ứng viên | Khi nào dùng |
|---|---|
| SPRT + góc cố định; greedy-IG + SPRT; Chernoff test; EC² | **Baseline bắt buộc** |
| DP / value iteration trên belief rời rạc | Trần tối ưu khi mô hình quan sát đã biết. Rẻ |
| POMCP / DESPOT | Khi có mô hình sinh nhưng không gian trạng thái lớn (ví dụ thêm vị trí nguồn khói) |
| PPO rời rạc / Recurrent PPO / masked PPO; imitation từ DP oracle | Khi trạng thái có đặc trưng ảnh nhiều chiều hoặc bài toán tìm kiếm + xác minh |
| Lagrangian PPO (CMDP) / conformal risk control | Bảo đảm KPI bỏ sót Z% thay cho chỉnh tay C_MD |
| Fusion học được (RNN/Transformer trên embedding các góc) | Thay Bayes ngây thơ khi quan sát tương quan |
| Mở rộng bài toán: belief trên lưới vị trí nguồn (kiểu [PyroTrack](https://arxiv.org/pdf/2403.11095)) | Biện minh mạnh nhất cho RL |

### 9.3 Dữ liệu

| Bộ dữ liệu | Góc nhìn | Dùng cho |
|---|---|---|
| [FIgLib](https://arxiv.org/pdf/2112.08598) (khoảng 25 nghìn ảnh, 315 chuỗi, camera HPWREN) | Chòi canh | Khói xa, có lưu trữ ngày sương/mây làm mẫu âm khó |
| [PyroNear-2024/2025](https://arxiv.org/pdf/2402.05349) (khoảng 50 nghìn ảnh, 150 nghìn nhãn, có video), [pyro-sdis](https://huggingface.co/datasets/pyronear/pyro-sdis) | Chòi canh/web | Huấn luyện detector, mô hình chuỗi |
| [Boreal Forest Fire](https://www.nature.com/articles/s41597-025-05634-0) (4.954 ảnh + 292 clip UAV, mask khói) | **UAV** | Khói từ UAV, video |
| [FLAME 1/2/3](https://arxiv.org/html/2412.02831v1) | **UAV**, RGB + thermal | Lửa/khói khi đốt có kiểm soát |
| [FASDD](https://essd.copernicus.org/preprints/essd-2022-394/essd-2022-394.pdf) (subset UAV) | Hỗn hợp | Chú ý 90,7% ảnh test gần-trùng |
| VDD / UAVid / IDD | **UAV xiên** | Lớp phủ đất |
| Tự thu tại VN | **UAV đa góc** | Mẫu âm khó (sương sáng sớm, mây thấp), khói đốt thực bì có phép. Đây là chính nhóm 2 |

### 9.4 Mô phỏng (bậc thang)

1. **Mức 0**: bộ giả lập quan sát dựng từ dữ liệu thật. Mỗi lần "nhìn" lấy một clip thật theo nhóm góc/cự ly/ánh sáng, hoặc lấy mẫu từ phân phối điểm detector đã fit. Đủ cho paper A.
2. **Mức 1**: SITL (ArduPilot/PX4) + Gazebo để kiểm thử tích hợp bay. Không dùng để học thị giác vì Gazebo không dựng khói thực tế.
3. **Mức 2**: Unreal Engine 5 (Niagara smoke) qua Cosys-AirSim, hoặc Isaac Sim + Pegasus. Tiền lệ: [WildfireX-SLAM](https://arxiv.org/pdf/2510.27133) dùng UE5 + Niagara; [FIRE-VLM](https://arxiv.org/html/2601.03449v1) dùng digital twin có che khuất bởi khói.
4. **Mức 3**: bay thật.

---

## 10. Đề xuất chỉnh sửa đặc tả (v3)

1. **Phần II §1**: tách H_smoke (onboard) khỏi quyết định báo động (máy chủ). Nhóm 2 đổi thành "nguồn khói trên đất canh tác", xếp rủi ro cháy lan thay vì "hợp pháp".
2. **Phần II §1**: viết rõ cách có **P(z\|H,v)** (học + hiệu chỉnh) và cách xử lý **tương quan** (tempered hoặc học được).
3. **Phần II §2**: đổi "PPO hoặc SAC liên tục" thành PPO rời rạc / DQN; thêm hover-duration vào hành động; c_hover tỷ lệ với quãng bay.
4. **Phần II §2**: KPI bỏ sót Z% thành **ràng buộc** (CMDP hoặc conformal risk control), không phải hằng số phạt.
5. **Phần II §3**: thêm baseline B4–B8 (mục 5.1); thay trích dẫn \[19\] và chỉnh lập luận \[18\].
6. **Phần II §4**: thêm dữ liệu UAV (Boreal, FLAME, FASDD_UAV) và dữ liệu xiên cho lớp phủ (VDD/UAVid); ghi tốc độ khung hình của từng nguồn.
7. **Phần IV §1**: hạ VMOKED từ "mô hình nền" xuống "baseline". Cập nhật: 64,89 là GMACs của YOLO-NAS-L, độ trễ không gồm detector, vướng giấy phép. Thay MMM bằng optical flow sau ổn định ảnh + đầu thời gian học được.
8. **Phần IV §3 Tầng 1**: sửa theo phần cứng thật (Pixhawk 2.4.8 / ArduPilot hoặc PX4 1.15 qua MAVLink), hoặc ghi lộ trình nâng lên H743.
9. **Phần III**: thừa nhận "nhìn bao nhiêu lần" có lời giải cổ điển (SPRT). Tính tự chủ cần được chứng minh bằng việc thắng baseline cổ điển, không chỉ thắng quỹ đạo tròn.
10. **Phụ lục**: thêm mục cần xác minh: (a) mã, trọng số và script đánh giá VMOKED; (b) giấy phép WSDataset; (c) số liệu gốc về tỷ lệ nguyên nhân cháy từ Cục Lâm nghiệp và Kiểm lâm.

---

## 11. Việc nên làm trong 2–4 tuần tới

1. **Liên hệ nhóm VMOKED**, hỏi các câu sau:
   - Phần cứng đo 7,5 ms là gì?
   - Script đánh giá trong paper có tính mẫu âm không?
   - Ngưỡng MMM dùng trong paper là bao nhiêu?
   - Có chia sẻ được trọng số và WSDataset không, theo giấy phép nào?
2. **Thí nghiệm 1 ngày**: DP và SPRT so với PPO trên mô hình quan sát đồ chơi (mục 8.2). Dùng kết quả để quyết định trọng tâm của paper.
3. **Đo tương quan giữa các góc nhìn** trên dữ liệu đa khung có sẵn (Boreal, FLAME), dùng detector đã hiệu chỉnh.
4. **Phần cứng**: giữ Pixhawk 2.4.8 cho SITL/HITL với ArduPilot Pixhawk1-1M hoặc PX4 1.15 qua MAVLink; đặt mua bo H743 cho giai đoạn bay. Không mua Jetson trước khi có pipeline chạy trên PC.
5. **Làm việc với Chi cục Kiểm lâm**: lấy mẫu số cảnh báo (X, Y, Z trong PRD) và xin quay video các đợt đốt thực bì có phép (dữ liệu nhóm 2 hợp pháp, an toàn).

---

## 12. Câu hỏi mở cần chủ nhiệm đề tài quyết định

- Mục tiêu trước mắt là **paper** hay **nguyên mẫu sản phẩm**? Hai mục tiêu này kéo phần cứng và giấy phép theo hai hướng khác nhau.
- Có chấp nhận **thermal** không? Nếu có, nhóm 1 và chế độ đêm gần như được giải, và trọng tâm nghiên cứu nên chuyển sang tìm kiếm + xác minh và kiểm soát rủi ro.
- Cảnh báo đầu vào chủ yếu đến từ đâu: vệ tinh (sai số vị trí lớn) hay chòi canh (chỉ có phương vị)? Câu trả lời quyết định có cần mở rộng POMDP sang **tìm vị trí nguồn khói** hay không. Đây là phần biện minh mạnh nhất cho RL.

---

### Nguồn chính đã dùng

- VMOKED/VSMOKED: [SSRN 5295846](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5295846), [SSRN 5005161](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5005161), [GitHub GloryVu/VSMOKED](https://github.com/GloryVu/VSMOKED)
- [Cross-Dataset Evaluation of YOLOv8 for UAV Fire and Smoke Detection (Drones 2026)](https://www.mdpi.com/2504-446X/10/8/635) · [ContextFireAgent (Remote Sensing 2026)](https://www.mdpi.com/2072-4292/18/18/3066) · [Agentic UAVs (arXiv:2509.13352)](https://arxiv.org/abs/2509.13352)
- Lý thuyết: [Golovin, Krause, Ray 2010 – EC²](https://las.inf.ethz.ch/files/golovin10near.pdf) · [Naghshvar & Javidi 2013](https://projecteuclid.org/euclid.aos/1387313387) · [Kartik et al. 2018](https://arxiv.org/abs/1810.04859) · [Jayaraman & Grauman 2016](https://arxiv.org/pdf/1605.00164) · [Conformal Risk Control](https://github.com/aangelopoulos/conformal-risk)
- UAV + cháy rừng: [PyroTrack](https://arxiv.org/pdf/2403.11095) · [FIRE-VLM](https://arxiv.org/html/2601.03449v1) · [WildfireX-SLAM](https://arxiv.org/pdf/2510.27133)
- Dữ liệu: [FIgLib](https://arxiv.org/pdf/2112.08598) · [PyroNear](https://arxiv.org/pdf/2402.05349) · [FLAME 3](https://arxiv.org/html/2412.02831v1) · [Boreal Forest Fire](https://www.nature.com/articles/s41597-025-05634-0) · [FASDD](https://essd.copernicus.org/preprints/essd-2022-394/essd-2022-394.pdf) · [VDD](https://arxiv.org/abs/2305.13608) · [UAVid](https://www.sciencedirect.com/science/article/abs/pii/S0924271620301295)
- Phần cứng: [PX4 Pixhawk 1 (v1.16 docs)](https://docs.px4.io/v1.16/en/flight_controller/pixhawk) · [PX4 uXRCE-DDS](https://docs.px4.io/main/en/middleware/uxrce_dds) · [ArduPilot Pixhawk](https://ardupilot.org/copter/docs/common-pixhawk-overview.html) · [ArduPilot Guided](https://ardupilot.org/copter/docs/ac2_guidedmode.html) · [Jetson Orin Nano Super](https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/) · [Ultralytics Jetson benchmarks](https://docs.ultralytics.com/guides/nvidia-jetson) · [SIYI ZT6](https://siyi.biz/en/product/tri-axis-multi-sensor-gimbal-pod/zt6/) · [DJI MSDK v5](https://github.com/dji-sdk/Mobile-SDK-Android-V5)
- Giấy phép YOLO-NAS: [YOLONAS.md](https://github.com/Deci-AI/super-gradients/blob/master/YOLONAS.md) · [NVIDIA forum](https://forums.developer.nvidia.com/t/licensing-and-usage-terms-for-yolo-nas-model/326342)
- Nguyên nhân cháy rừng VN: [moitruong.net.vn – Bộ NN&PTNT chỉ ra nguyên nhân cháy rừng](https://moitruong.net.vn/bo-nn-ptnt-chi-ra-nguyen-nhan-chay-rung-lien-tuc-dien-ra-trong-4-thang-dau-nam-74272.html) · [CAND – Cháy rừng gia tăng](https://cand.vn/Xa-hoi/chay-rung-gia-tang--vi-sao--i730402/) *(số liệu báo chí, cần đối chiếu số liệu gốc)*
- VIIRS: [NASA FIRMS FAQ](https://www.earthdata.nasa.gov/data/tools/firms/faq)
