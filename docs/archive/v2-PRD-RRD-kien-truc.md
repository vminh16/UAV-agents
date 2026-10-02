# HỆ THỐNG UAV XÁC MINH CẢNH BÁO CHÁY RỪNG — BỘ TÀI LIỆU v2

**Wildfire Active Smoke Verifier**

*Bản v2, cập nhật 20/09/2026. Thay đổi so với v1: phân loại lại báo động giả thành ba nhóm; bổ sung hành động kết thúc `a_abstain`; bổ sung module phân đoạn lớp phủ đất vào mô hình quan sát; sửa KPI tỷ lệ bỏ sót; bổ sung mục Tính tự chủ của tác tử; chuyển chế độ ban đêm xuống mục mở rộng; sửa trích dẫn VMOKED.*

---

# PHẦN I — PRD (PRODUCT REQUIREMENTS DOCUMENT)

## 1\. Bối cảnh và vấn đề cần giải quyết

**Thực tế vận hành.** Camera chòi canh kiểm lâm và cảnh báo điểm nóng từ vệ tinh thường xuyên báo nhầm. Địa hình đồi núi dốc khiến kiểm lâm mất từ 1 đến 2 giờ đi bộ luồn rừng chỉ để kiểm tra một toạ độ nghi vấn. Nếu là báo động giả, lực lượng bị kiệt sức và mất niềm tin vào hệ thống; nếu là cháy thật, sau 2 giờ ngọn lửa đã vượt tầm khống chế.

Mức độ cấp thiết có số liệu: riêng khu vực miền Bắc, đầu năm 2025 ghi nhận 129 vụ cháy rừng làm thiệt hại hơn 150 ha, gấp đôi cùng kỳ năm trước, tập trung tại Tuyên Quang, Quảng Ninh, Vĩnh Phúc, Cao Bằng, Lạng Sơn \[17\].

**Ba nhóm báo động giả — phân biệt rõ vì chúng cần ba cách xử lý khác nhau.** Đây là thay đổi quan trọng nhất của bản v2: bản v1 gộp chung tất cả thành "báo động giả", khiến không quy được trách nhiệm cho thành phần nào của hệ thống.

**Nhóm 1 — Không có khói.** Sương mù, mây tầng thấp sà xuống tán rừng, bụi đường đất, hơi nước bốc lên sau mưa. Đặc điểm phân biệt nằm trong ảnh: sương lan ngang, tan dần, không có nguồn điểm; khói bốc lên, nở rộng, xuất phát từ một điểm. *Giải bằng thị giác và chính sách quan sát chủ động — thuộc phạm vi nghiên cứu (Phần II).*

**Nhóm 2 — Có khói thật nhưng hợp pháp.** Đốt nương rẫy, đốt thực bì có phép, đốt rác. Đây gần như chắc chắn là nhóm báo giả đông nhất ở Việt Nam. Đốt rơm rạ vùng Đồng bằng sông Hồng đã được lập kiểm kê phát thải riêng bằng dữ liệu vệ tinh \[14\], và canh tác nương rẫy ở vùng núi phía Bắc là hiện tượng thường niên đã được lập bản đồ bằng viễn thám \[15\].

Điểm mấu chốt: **bản thân cột khói không mang thông tin phân biệt** — khói đốt nương và khói cháy rừng giống nhau. Toàn bộ văn liệu viễn thám tách hai loại này bằng cách chồng điểm cháy lên lớp che phủ đất, không bằng đặc trưng của lửa \[7\]\[8\].

Nhưng UAV có lợi thế mà vệ tinh và chòi canh không có: **ở độ cao 80–120 m và cự ly 100–200 m, lớp che phủ đất ngay tại chân cột khói nằm trong khung hình.** Vệ tinh với pixel 375 m buộc phải tra bản đồ; chòi canh nhìn ngang từ xa bị địa hình che. Drone nhìn thấy trực tiếp. *Giải bằng phân đoạn lớp phủ đất tại chân cột khói (onboard) đối chiếu với lớp dữ liệu GIS (máy chủ).*

**Nhóm 3 — Cháy thật nhưng không cần điều động.** Đám nhỏ đã được kiểm soát, cháy bãi rác, cháy ngoài ranh giới quản lý. *Giải bằng tầng phán xét ở máy chủ: kết hợp ảnh, gió, độ ẩm, khoảng cách tới thảm thực vật dễ cháy và ranh giới quản lý để xếp mức khẩn.*

**Giải pháp.** Một drone túc trực tại trạm kiểm lâm, tự động bay tới toạ độ nghi vấn trong 5–10 phút, **tự quyết định quan sát từ những góc nào và quan sát bao nhiêu lần** để khẳng định cháy thật hay báo động giả, rồi gửi gói bằng chứng kèm lý do về máy tính chỉ huy trước khi điều động người.

## 2\. Phạm vi sản phẩm

**Trong phạm vi bản v1:**

- Xác minh cảnh báo đã có tại một toạ độ được chỉ định.  
- Hoạt động ban ngày, trong điều kiện ánh sáng tự nhiên đủ để camera RGB phân biệt khói.  
- Phân biệt nhóm 1 (có khói / không khói) bằng thị giác onboard.  
- Gắn cờ nhóm 2 (nghi đốt nương) bằng lớp phủ đất onboard kết hợp GIS máy chủ.  
- Xếp mức khẩn nhóm 3 tại máy chủ.

**Ngoài phạm vi bản v1:**

- Hoạt động ban đêm. Camera RGB không nhìn thấy khói trong bóng tối. Chế độ ban đêm dựa trên phát hiện quầng sáng được viết formulation tại Phần II mục 6, triển khai sau khi bản v1 hoàn tất.  
- Tuần tra phát hiện chủ động trên diện rộng. Hệ thống chỉ phản ứng với cảnh báo có sẵn, không thay thế chuỗi phát hiện hiện có.  
- Chữa cháy hoặc can thiệp vật lý.

## 3\. Kịch bản vận hành thực tế

**Bước 1 — Tiếp nhận cảnh báo.** Máy chủ nhận toạ độ nghi vấn từ camera chòi canh, điểm nóng vệ tinh, hoặc phản ánh của người dân. Máy chủ tra lớp GIS và khởi tạo niềm tin ban đầu: toạ độ nằm trên rừng tự nhiên hay trên đất nông nghiệp / nương rẫy.

**Bước 2 — Tự động xuất kích.** Trạm sạc tự động mở nắp; drone cất cánh bay tới khu vực nghi vấn theo trần bay an toàn đã thiết lập.

**Bước 3 — Quan sát chủ động.** Đến cách tâm nghi vấn 100–200 m, drone dừng và giữ vị trí trên không (hover) khoảng 2 giây tại mỗi điểm quan sát để camera ghi một đoạn video ngắn. Sau mỗi lần quan sát, hệ thống tự quyết định: quan sát tiếp ở góc nào, hay đã đủ để kết luận. Số lần quan sát **không cố định** — đây là điểm khác biệt cốt lõi so với quỹ đạo tròn lập sẵn.

**Bước 4 — Kết luận.** Bốn kết quả có thể xảy ra:

| Kết quả | Hành động hệ thống |
| :---- | :---- |
| Cháy rừng — khẩn cấp | Gửi toạ độ GPS, video, ảnh cận cảnh về màn hình kiểm lâm; kích hoạt còi báo động; gửi SMS/Zalo cho tổ tuần tra |
| Có khói — nghi đốt nương, cần đối chiếu | Gửi bằng chứng kèm cờ "chân khói nằm trên đất đã phát dọn"; không kích hoạt còi; chuyển cán bộ trực xác nhận |
| Không có khói — do sương hoặc mây | Ghi nhận báo động giả, tự động bay về trạm sạc |
| Không kết luận được | Gửi toàn bộ khung hình đã thu kèm mức tin cậy cuối; chuyển người trực quyết định |

Kết quả thứ tư là bắt buộc. Nếu chỉ có hai kết quả khẳng định, hệ thống buộc phải đoán trong đúng những tình huống mơ hồ — và đó chính là nơi mọi lần bỏ sót sẽ xảy ra.

## 4\. Bảng yêu cầu tính năng

**Trạm đỗ và phương tiện bay**

- Trạm sạc tự động đặt tại trạm kiểm lâm có điện hoặc pin mặt trời; vỏ chống mưa bão; sạc tiếp xúc.  
- Bay theo trần cố định 80–120 m trên tán rừng, bảo đảm cự ly an toàn bức xạ nhiệt và tránh địa hình.  
- Cơ chế failsafe: pin xuống 25% hoặc mất tín hiệu quá 15 giây thì huỷ nhiệm vụ, tự bay về trạm. Failsafe có quyền ghi đè mọi quyết định của tầng tự chủ.

**Xử lý trên phương tiện bay**

- Chế độ Dừng–Nhìn (Hover-and-Stare): dừng tĩnh khoảng 2 giây tại mỗi điểm quan sát để triệt tiêu rung lắc, cho phép phân tích động học khói. *Con số 2 giây là giá trị khởi điểm cần kiểm chứng thực nghiệm, không khoá cứng.*  
- Phát hiện và đo động học khói.  
- **Phân đoạn lớp phủ đất tại chân cột khói** — phân biệt tán rừng kín / đất đã phát dọn hoặc nương rẫy / mặt nước / công trình.  
- Chọn góc quan sát tiếp theo: tự động đổi vị trí và góc camera nếu mức tin cậy chưa vượt ngưỡng.  
- Quyết định dừng: tự chọn một trong ba hành động kết thúc.

**Hệ thống máy chủ**

- Bảng điều khiển kiểm lâm: bản đồ số đồi rừng, vị trí drone thời gian thực, khung hình video, nút phê duyệt và huỷ lệnh bay.  
- **Lớp dữ liệu ngữ cảnh (phân hệ mới).** Ba nguồn, xếp theo sức mạnh: ranh giới sử dụng đất phân biệt rừng tự nhiên và rừng phòng hộ với đất nông nghiệp \[12\]\[13\]; lịch đăng ký đốt thực bì của kiểm lâm nếu số hoá được; prior theo mùa vụ và giờ trong ngày. Lớp này khởi tạo niềm tin ban đầu trước khi bay và đối chiếu chéo với kết quả phân đoạn onboard sau khi bay.  
- Cơ chế đồng thuận: hai nguồn (onboard và GIS) đồng thuận thì tin cậy cao; mâu thuẫn thì kích hoạt kết quả "không kết luận được".  
- Xếp mức khẩn cho nhóm 3 và sinh báo cáo.  
- Cơ chế báo động đa kênh: SMS/Zalo kèm link ảnh hiện trường.  
- Nhật ký chỉ-thêm: lưu toàn bộ chuỗi quyết định của mỗi nhiệm vụ để truy vết.

## 5\. Chỉ số thành công

**Thời gian phản ứng.** Có mặt tại hiện trường và đưa ra kết luận trong vòng dưới 10 phút, bán kính 5 km.

**Độ chính xác xác minh — tách theo nhóm báo giả.** Gộp chung thì khi kết quả không đạt sẽ không biết thành phần nào hỏng.

- Nhóm 1: giảm ≥ X% số lần điều động do sương mù và mây bị nhận nhầm. Đo bằng thị giác và chính sách quan sát.  
- Nhóm 2: giảm ≥ Y% số lần điều động do đốt nương rẫy. Đo bằng lớp phủ đất và GIS.

**Tỷ lệ bỏ sót.** Không quá Z% trên tập kiểm thử, với ngưỡng quyết định hiệu chỉnh thiên về recall.

> **Ghi chú bắt buộc trong mọi tài liệu đối ngoại:** hệ thống này **không thay thế** chuỗi cảnh báo hiện có và không phải người gác cuối cùng. Nó lọc bớt số lần điều động không cần thiết. Mọi cảnh báo mà hệ thống không kết luận được đều chuyển cho người.

> *Lý do sửa so với bản v1:* bản v1 đặt tỷ lệ bỏ sót bằng 0%. Không hệ thống nhận dạng nào đạt được điều đó, và nó tự mâu thuẫn với hàm phần thưởng ở Phần II, nơi chi phí bỏ sót C\_MD là một giá trị hữu hạn — nếu bỏ sót thực sự không được phép thì C\_MD phải vô hạn và chính sách tối ưu sẽ báo động trong mọi trường hợp, phá luôn mục tiêu giảm điều động thừa.

**Tỷ lệ tự chủ.** Tỷ lệ nhiệm vụ hoàn thành và đưa ra kết luận khẳng định mà không cần can thiệp của người, trên tổng số nhiệm vụ. Đây là KPI đo trực tiếp tính tự chủ và được giải thích ở Phần III.

**Các con số X, Y, Z cần xác định bằng khảo sát thực địa trước khi khoá.** Cụ thể: một trạm kiểm lâm nhận bao nhiêu cảnh báo mỗi ngày trong mùa khô, và bao nhiêu phần trăm trong số đó thuộc mỗi nhóm. Không có mẫu số này thì mọi tỷ lệ phần trăm đều không kiểm chứng được, và cũng không biết sản phẩm có đủ tần suất sử dụng để đáng đầu tư hay không. Việc này giải quyết được bằng một buổi làm việc với Chi cục Kiểm lâm.

---

# PHẦN II — RRD (RESEARCH REQUIREMENTS DOCUMENT)

**Tên đề tài:** Kiểm định giả thuyết tuần tự chủ động cho UAV sử dụng thị giác RGB trong xác thực khói cháy rừng, với quan sát kết hợp động học khói và lớp phủ đất tại nguồn.

## 1\. Định hình bài toán khoa học

**Câu hỏi nghiên cứu cốt lõi.** Làm thế nào để một UAV chỉ mang camera quang học RGB phân biệt chính xác khói cháy rừng với các hiện tượng giả khói, với số lần dừng quan sát ít nhất dưới giới hạn pin ngặt nghèo?

**Phạm vi nghiên cứu.** Đề tài nhận trách nhiệm giải **nhóm 1** — phân biệt có khói thật với không có khói. Việc phân biệt **nhóm 2** (khói hợp pháp) được giải bằng lớp phủ đất và dữ liệu GIS, là bài toán dữ liệu và quy trình, thuộc Phần I. Tuyên bố phạm vi này là cần thiết: nếu đề tài hứa giải cả nhóm 2 bằng thị giác thuần tuý thì nó đang hứa điều mà camera RGB không làm được, và đó là lỗ hổng phản biện sẽ tìm ra ngay.

**Mô hình toán học.** Bài toán được mô hình hoá dưới dạng POMDP.

Trạng thái ẩn nhị phân: H ∈ {H₁: cần báo động, H₀: không cần báo động}.

Trạng thái niềm tin: b\_t \= P(H₁ | z\_{1:t}) ∈ \[0,1\], cập nhật theo Bayes sau mỗi quan sát:

b\_{t+1} \= \\frac{P(z\_{t+1} \\mid H\_1, v\_{t+1}) \\cdot b\_t}{P(z\_{t+1} \\mid H\_1, v\_{t+1}) \\cdot b\_t \+ P(z\_{t+1} \\mid H\_0, v\_{t+1}) \\cdot (1 \- b\_t)}

trong đó v\_{t+1} là toạ độ và góc nhìn camera được tác tử chọn tại bước t+1.

Niềm tin ban đầu b₀ **không phải 0.5** mà được khởi tạo từ lớp GIS máy chủ theo loại đất tại toạ độ cảnh báo.

**Mô hình quan sát mở rộng (thay đổi so với bản v1).** Quan sát z\_t giờ gồm hai thành phần:

z\_t \= (z\_t^khói, z\_t^nền)

- z\_t^khói: vector đặc trưng động học khói — có nguồn điểm hay không, hướng bốc, tốc độ nở rộng.  
- z\_t^nền: phân bố lớp phủ đất tại vùng chân cột khói.

Đây là thay đổi làm bài toán lấy mẫu chủ động **giàu hơn chứ không phức tạp hơn một cách vô ích**: góc nhìn tốt nhất đôi khi không phải góc nhìn rõ cột khói nhất, mà là góc nhìn thấy được **thứ nằm dưới cột khói** — dịch chuyển để chân khói không bị tán cây che, hoặc nâng độ cao để lộ ranh giới thửa đất. Tác tử phải học đánh đổi giữa "nhìn khói" và "nhìn chân khói".

Đây cũng là lập luận mạnh nhất giải thích vì sao cần quan sát chủ động thay vì chụp một ảnh: **một ảnh đơn không thể đổi vị trí để lộ nền đất ra.**

Hai tín hiệu phụ có sẵn trong ảnh với chi phí gần bằng không: hình học ranh giới (đốt nương có biên thẳng, thửa vuông hoặc ruộng bậc thang, nhiều vệt đốt song song; cháy rừng có mặt lửa bất quy tắc, không biên), và sự hiện diện của người, xe, dụng cụ gần đám cháy — dùng bộ phát hiện tiền huấn luyện trên COCO, không cần gắn nhãn mới.

## 2\. Thiết kế bài toán cho Học tăng cường

**Không gian trạng thái S**

- Vector đặc trưng động học khói trích xuất từ mô hình thị giác.  
- **Phân bố lớp phủ đất tại vùng chân cột khói.**  
- Mức độ tin cậy hiện tại b\_t.  
- Toạ độ tương đối của UAV so với tâm cột khói: Δp \= (Δx, Δy, Δz).  
- Góc chiếu sáng của mặt trời so với trục camera, để tác tử học được hiện tượng loá sáng khi ngược nắng.  
- **Tỷ lệ vùng chân khói bị che khuất trong khung hình hiện tại.** Biến này cần thiết để tác tử biết khi nào nên dịch chuyển nhằm nhìn rõ nền đất.  
- Ngân sách số lần dừng đo còn lại: K\_remain.

**Không gian hành động A**

- Tập các vị trí góc nhìn tiếp theo: quay vòng 45°, đổi cự ly ±20 m, chỉnh góc nghiêng camera.  
- **Ba hành động kết thúc:**  
  - a\_alarm — khẳng định cần báo động.  
  - a\_dismiss — khẳng định không cần báo động.  
  - a\_abstain — **không kết luận được, chuyển người xem (bổ sung ở bản v2).**

> *Lý do bổ sung a\_abstain:* với hai hành động, khi hết ngân sách quan sát mà b\_t vẫn lửng lơ quanh 0.5, tác tử **buộc phải đoán** — và đó chính xác là nơi mọi lần bỏ sót sẽ xảy ra. Về sản phẩm, kiểm lâm tin một hệ thống biết nói "tôi không chắc" hơn một hệ thống luôn khẳng định. Về nghiên cứu, abstention trong kiểm định giả thuyết tuần tự là chuẩn mực, và nó cho thêm một trục để báo cáo: đường đánh đổi giữa tỷ lệ tự quyết và độ chính xác trên phần tự quyết.

**Hàm phần thưởng R**

R \= − c\_hover − C\_FA · 𝟙(a\_alarm | H₀) − C\_MD · 𝟙(a\_dismiss | H₁) − C\_AB · 𝟙(a\_abstain) \+ R\_correct

- c\_hover: chi phí cố định cho mỗi lần dừng quan sát, ép tác tử quyết định nhanh và tiết kiệm pin.  
- C\_FA: phạt báo động nhầm.  
- C\_MD: phạt bỏ sót đám cháy, với C\_MD ≫ C\_FA.  
- C\_AB: phạt vừa phải cho việc không kết luận được, thoả C\_FA \> C\_AB \> 0 và C\_MD ≫ C\_AB. Ràng buộc này bảo đảm abstain là lựa chọn tốt hơn đoán sai nhưng tệ hơn quyết đúng, nếu không tác tử sẽ abstain mọi lúc.  
- R\_correct: thưởng khi kết luận chính xác.

**Thuật toán khuyến nghị.** PPO hoặc SAC cho không gian hành động liên tục, kết hợp mạng trích xuất đặc trưng không gian để xử lý bản đồ quan sát.

## 3\. Phương pháp đánh giá và baseline đối chứng

**Baseline 1 — Single-shot Static.** Drone bay đến một điểm cố định duy nhất, chụp một ảnh, phụ thuộc hoàn toàn vào mô hình phát hiện đối tượng thông thường.

**Baseline 2 — Fixed Circular Orbit.** Drone bay đủ một vòng tròn 360° quanh điểm nghi vấn, thu ảnh đều đặn rồi lấy trung bình xác suất. Đây là phương án cơ học tốn pin, và là phép so sánh trực tiếp cho tính tự chủ: nó có cùng thông tin nhưng không tự quyết dừng.

**Baseline 3 — Greedy một bước.** Chọn góc nhìn tối đa hoá mức giảm entropy kỳ vọng ở bước kế tiếp, không nhìn xa hơn một bước. Baseline này là bắt buộc: chính sách greedy tối đa hoá thông tin tương hỗ có bảo đảm gần tối ưu (1 − 1/e) theo Krause et al. \[19\], nên trần cải thiện phía trên greedy bị chặn về mặt lý thuyết. Thiếu baseline này thì kết quả không thuyết phục.

**Thước đo.**

- F1-score và accuracy trên tập dữ liệu video thực địa.  
- **N\_hover** — số điểm dừng trung bình. Kỳ vọng 1 đến 3 thay vì bay hết vòng tròn. Đây là chỉ số đo trực tiếp sự thông minh của chính sách.  
- **T\_decision** — tổng thời gian từ khi tiếp cận đến khi ra kết luận.  
- **Đường cong coverage–accuracy** — tỷ lệ nhiệm vụ tác tử tự quyết (không abstain) so với độ chính xác trên phần đó. Vẽ bằng cách quét tham số C\_AB.

> **Cảnh báo về chỉ số.** Không được báo cáo thành công chỉ bằng mức giảm entropy hay mức giảm phương sai. Bickford Smith et al. \[18\] chứng minh bất định tham số có thể giảm mạnh mà bất định dự đoán trên các đầu vào quan tâm không giảm tương ứng. Chỉ số công bố phải là sai số trên tập kiểm thử giữ lại, không phải mức giảm entropy.

## 4\. Dữ liệu

**Đã có.** WSDataset trên Kaggle \[2\]: 11.539 khung hình khói cháy rừng thực tế và 12.481 khung hình môi trường không khói.

**Cần bổ sung cho nhánh lớp phủ đất.** Không gắn nhãn trực tiếp hai lớp "đốt nương" và "cháy rừng" — dữ liệu ảnh cặp của cả hai từ độ cao UAV ở địa hình Việt Nam gần như không tồn tại, và lớp "cháy rừng" hiếm theo đúng định nghĩa. Thay vào đó **phân đoạn lớp phủ đất**, rồi nhãn "nghi đốt nương" suy ra bằng luật.

Dữ liệu sẵn có cho hướng này rất dồi dào: LoveDA \[9\] (NeurIPS 2021, dữ liệu nông thôn và đô thị, miền khá gần Việt Nam), OpenEarthMap \[10\] (toàn cầu, 97 vùng), LandCover.ai \[11\]. Bổ sung dữ liệu riêng Việt Nam: bộ LULC thường niên 1990–2020 cho toàn lục địa Việt Nam \[12\] và Land Cover 2020 trên OD Mekong Datahub \[13\].

Ước tính công sức bổ sung: fine-tune trên LoveDA hoặc OpenEarthMap, rồi một đợt fine-tune nhỏ cho địa hình Việt Nam, khoảng 500–2.000 khung hình gắn nhãn vùng. Gắn nhãn đa giác lớp phủ rẻ hơn nhiều so với đi săn ảnh cháy rừng thật, và làm được quanh năm.

**Cảnh báo về rò rỉ tập kiểm thử.** Nghiên cứu kiểm chéo dataset cho phát hiện lửa và khói từ UAV \[3\] phát hiện 46,0% ảnh test của D-Fire và 90,7% của FASDD\_UAV có ảnh gần-trùng trong tập huấn luyện; loại bỏ trùng lặp làm điểm mAP rơi thêm 2,8 đến 12,4 điểm. Cùng nghiên cứu đó đo YOLOv8m đạt 92,71% mAP@0.5 in-domain trên FASDD\_UAV nhưng chỉ 14,32% khi kiểm thử zero-shot trên D-Fire. **Bắt buộc khử trùng lặp trước khi chia tập, và bắt buộc báo cáo kết quả zero-shot chéo dataset**, nếu không mọi con số đều vô nghĩa.

## 5\. Hướng mở rộng — chế độ ban đêm (ngoài phạm vi v1)

Triển khai sau khi bản v1 hoàn tất. Ghi formulation ở đây để đề tài có đường phát triển rõ ràng.

**Quan sát then chốt: ban đêm không phải bài toán khó hơn, mà là bài toán khác.** Ban ngày, khói nhìn thấy được từ xa còn ngọn lửa bị tán rừng che, nên dò khói. Ban đêm thì ngược lại: khói tan vào bóng tối và gần như vô hình, nhưng **ngọn lửa tự phát sáng** và nhìn thấy được từ rất xa. Tập báo giả cũng đổi: ban ngày là sương và mây, ban đêm là đèn nhà, đèn xe trên đường lâm nghiệp, lửa trại, ánh trăng phản chiếu trên mặt nước.

**Formulation:** cùng POMDP, cùng ba hành động kết thúc, đổi mô hình quan sát z^khói thành z^sáng — phát hiện nguồn sáng bất thường trên ảnh phơi sáng dài. Tác tử phải học một chính sách quan sát khác cho chế độ này. Đóng góp khoa học tương ứng: *cùng một POMDP, hai mô hình quan sát theo điều kiện ánh sáng.*

**Hệ quả bắt buộc:** ban đêm **không nhìn thấy nền đất**, nên thành phần z^nền biến mất. Chế độ ban đêm do đó **phụ thuộc hoàn toàn vào lớp GIS máy chủ** để biết nguồn sáng nằm trên rừng hay trên nương. Đây là lý do lớp GIS phải được xây ngay từ v1 chứ không phải để sau.

**Rào cản đã biết:** WSDataset không có dữ liệu ban đêm; rủi ro va chạm khi bay đêm trên rừng cao hơn hẳn; thủ tục xin phép bay đêm khó hơn.

**Ghi chú giảm nhẹ để đưa vào phần biện luận:** cháy rừng ở Việt Nam phần lớn khởi phát ban ngày vì nguyên nhân chủ yếu là hoạt động con người — đốt nương, tàn thuốc, đốt rác, khách tham quan. Ban đêm gió lặng hơn, nhiệt độ giảm, độ ẩm tăng, tốc độ lan chậm lại. Việc chưa hỗ trợ ban đêm mất ít hơn cảm giác ban đầu.

**Hành vi hệ thống ban đêm trong bản v1:** cảnh báo ban đêm không bị bỏ. Máy chủ giữ lại, chấm điểm ưu tiên theo gió, độ ẩm, khoảng cách tới khu dân cư và lịch sử điểm đó; drone xuất kích theo thứ tự ưu tiên đó ngay khi trời sáng. Cảnh báo mức nghiêm trọng cao chuyển thẳng cho người trực ngay trong đêm.

---

# PHẦN III — TÍNH TỰ CHỦ CỦA TÁC TỬ

*Mục mới ở bản v2. Trả lời trực tiếp câu hỏi: UAV này là tác tử ở chỗ nào, và nó tự hành ra sao.*

## 1\. Phân biệt hai nghĩa của từ "tác tử"

Sự bùng nổ của các mô hình nền tảng gần đây tạo ra nhầm lẫn khái niệm giữa hai thứ khác hẳn nhau:

**Tác tử mô hình ngôn ngữ / thị giác lớn (LLM/VLM Agent)** vận hành bằng suy luận tuần tự qua chuỗi tư duy, phân tích ngữ cảnh ngữ nghĩa và gọi công cụ bên ngoài. Độ trễ tính bằng giây.

**Tác tử tự trị cổ điển** trong lý thuyết điều khiển và robot học được định nghĩa theo Quá trình Quyết định Markov: một chính sách ánh xạ từ không gian trạng thái sang không gian hành động nhằm tối đa hoá phần thưởng tích luỹ. Độ trễ tính bằng mili-giây.

Hệ thống này dùng **cả hai, ở hai tầng khác nhau**, và đó là lý do kiến trúc phân tầng Biên–Máy chủ là bắt buộc chứ không phải tuỳ chọn.

## 2\. Vì sao không đặt LLM/VLM Agent lên phương tiện bay

Số liệu đo thực tế: một tác tử LLM chạy cục bộ với mô hình Gemma-3 4B mất 1,48 ± 0,58 giây cho mỗi quyết định, và qua GPT-4 API là 4,95 ± 1,15 giây — đo trên máy trạm RTX 4070, chưa phải phần cứng nhúng \[5\]. Một pipeline tác tử đa vai dùng VLM cho giám sát cháy rừng đo được 19,8 giây mỗi ảnh so với 0,15 giây của YOLOv8n, và chính tác giả kết luận nó không phù hợp để sàng lọc thời gian thực mà chỉ dùng để rà soát cảnh báo \[4\].

Trong khi đó vòng điều khiển tư thế của phương tiện bay nhiều cánh quạt hoạt động ở chu kỳ khoảng 1 mili-giây, vòng điều khiển vị trí khoảng 10 mili-giây. Khoảng cách là hai đến ba bậc độ lớn, và không kỹ thuật nén nào đóng được.

Cùng nghiên cứu \[5\] cũng cho thấy giá trị thật của tác tử nằm ở đâu: tầng luật cứng đưa ra khuyến nghị hành động trong 0% tình huống, còn tác tử cục bộ là 79% và GPT-4 là 92%. Tác tử không mua thêm tốc độ — nó mua khả năng diễn giải và ra quyết định.

**Kết luận thiết kế:** tác tử theo nghĩa ngữ nghĩa cư trú hoàn toàn tại máy chủ. Trên phương tiện bay chỉ có tác tử theo nghĩa MDP.

## 3\. Ba quyết định mà không ai chỉ định — tác tử ở chỗ này

Đây là câu trả lời ngắn nhất cho câu hỏi "UAV này là tác tử ở đâu":

**Quyết định 1 — Nhìn ở đâu tiếp theo.** Chính sách chọn góc nhìn v\_{t+1} từ trạng thái niềm tin hiện tại. Không người nào, và không đoạn mã lập sẵn nào, chỉ định góc này.

**Quyết định 2 — Nhìn bao nhiêu lần.** Không có số lần cố định. Tác tử tự quyết khi nào đã đủ thông tin để dừng.

**Quyết định 3 — Kết luận gì, hoặc thừa nhận không kết luận được.** Ba hành động kết thúc, tự chọn.

**Đối chiếu để thấy rõ ranh giới.** Baseline 2 — quỹ đạo tròn cố định — có cùng phần cứng, cùng mô hình thị giác, cùng thông tin. Nhưng người lập trình đã quyết trước rằng bay đủ 360°, chụp N ảnh, lấy trung bình. Đó là **tự động hoá**, không phải **tự chủ**. Sự khác biệt giữa hai thứ đo được bằng một con số duy nhất: N\_hover.

## 4\. Ranh giới tự chủ — những gì tác tử không được quyết

Một hệ thống tự chủ triển khai trong không phận dân dụng phải nêu rõ giới hạn của nó. Bốn điều tác tử không có quyền:

- **Không tự quyết bay ra ngoài vùng đã được phép bay.** Geofence do bộ điều khiển bay cưỡng chế, tầng tự chủ không ghi đè được.  
- **Không tự điều khiển động cơ.** Bộ điều khiển bay PX4 xử lý toàn bộ động học, tiền định, có thể chứng minh ổn định. Tác tử chỉ phát ra điểm bay đã qua kiểm tra hợp lệ.  
- **Không tự quyết điều động lực lượng chữa cháy.** Nó phát cảnh báo kèm bằng chứng; con người ra lệnh điều động.  
- **Không ghi đè failsafe.** Ngưỡng pin và mất tín hiệu có quyền huỷ nhiệm vụ bất kể tác tử đang ở bước nào.

## 5\. Vòng lặp tự hành, năm bước

1. **Kích hoạt.** Máy chủ nhận toạ độ, tra lớp GIS, khởi tạo niềm tin b₀ theo loại đất. Gửi nhiệm vụ xuống phương tiện bay.  
2. **Di chuyển.** Bộ điều khiển bay đưa drone tới điểm quan sát đầu tiên. *Bước này không phải tác tử — đó là điều hướng theo điểm bay, bài toán đã giải xong.*  
3. **Quan sát.** Hover khoảng 2 giây; mô hình thị giác trả về xác suất khói và phân bố lớp phủ tại chân cột khói.  
4. **Cập nhật và quyết định.** Cập nhật Bayes cho b\_t; chính sách chọn: tiếp tục quan sát tại góc nào, hay kết thúc bằng alarm, dismiss, abstain. **Đây là bước duy nhất mang tính tác tử, và nó lặp lại.**  
5. **Kết thúc.** Gửi gói bằng chứng về máy chủ. Tác tử máy chủ đối chiếu GIS, xếp mức khẩn, sinh báo cáo và kích hoạt kênh cảnh báo.

Chu kỳ của bước 4 là khoảng 0,2 đến 2 Hz — đủ chậm để một chính sách học được chạy thoải mái, đủ nhanh so với quy mô thời gian của việc bay giữa hai điểm quan sát.

## 6\. Tính giải trình

Một tác tử tự chủ phải giải thích được, nếu không kiểm lâm sẽ không dùng và hội đồng sẽ không duyệt. Mỗi nhiệm vụ trả về một hồ sơ gồm:

- Chuỗi góc nhìn đã chọn, kèm lý do chọn từng góc (mức bất định trước và sau).  
- Quỹ đạo niềm tin b₀ → b₁ → … → b\_T.  
- Hành động kết thúc kèm b\_T tại thời điểm quyết định.  
- Kết quả đối chiếu giữa lớp phủ onboard và GIS máy chủ: đồng thuận hay mâu thuẫn.

Hồ sơ này lưu vào nhật ký chỉ-thêm. Nó biến quyết định của tác tử thành thứ đọc được và truy vết được, không phải hộp đen.

## 7\. Bảng phân định quyền quyết định

| Quyết định | Ai quyết | Chu kỳ | Hệ quả nếu sai |
| :---- | :---- | :---- | :---- |
| Cân bằng, giữ độ cao, giữ hover | Bộ điều khiển bay PX4 | 1–10 ms | Rơi phương tiện |
| Huỷ nhiệm vụ do pin / mất sóng | Failsafe cứng | Liên tục | Mất phương tiện |
| Bay tới điểm quan sát đã chọn | Điều hướng điểm bay | 10–100 ms | Lệch vị trí |
| **Chọn góc quan sát tiếp theo** | **Chính sách RL onboard** | **0,2–2 Hz** | **Tốn pin, kết luận chậm** |
| **Dừng hay quan sát tiếp** | **Chính sách RL onboard** | **0,2–2 Hz** | **Kết luận sai hoặc bỏ lỡ** |
| **Kết luận: alarm / dismiss / abstain** | **Chính sách RL onboard** | **1 lần/nhiệm vụ** | **Báo nhầm hoặc bỏ sót** |
| Đối chiếu GIS, xếp mức khẩn | Tác tử máy chủ | Giây | Xếp sai ưu tiên |
| Xếp hàng ưu tiên cảnh báo ban đêm | Tác tử máy chủ | Phút | Chậm phản ứng |
| Điều động lực lượng | **Con người** | — | — |

## 8\. Đo tính tự chủ bằng số

Một tuyên bố về tự chủ cần bằng chứng. Bốn chỉ số:

- **N\_hover** so với Baseline 2 cố định. Đo việc tác tử có học được cách dừng sớm hay không.  
- **Tỷ lệ tự quyết** \= 1 − tỷ lệ abstain. Đo việc tác tử đủ tự tin bao nhiêu phần.  
- **Độ chính xác trên phần tự quyết.** Cặp với chỉ số trên tạo thành đường cong coverage–accuracy.  
- **Tỷ lệ nhiệm vụ hoàn thành không cần can thiệp người.** KPI tự chủ ở cấp sản phẩm, đã đưa vào Phần I mục 5\.

---

# PHẦN IV — KIẾN TRÚC KỸ THUẬT THAM KHẢO

## 1\. Xương sống thị giác

**Mô hình nền: VMOKED.** Chọn làm bộ trích xuất đặc trưng thị giác cốt lõi nhờ ba cơ chế chuyên biệt cho khói:

1. **Sky-Ground Segmentation (SGS)** — dùng MobileNetV3 kết hợp Feature Pyramid Network để nhận diện đường chân trời, tách vùng trời khỏi tán rừng. Cơ chế này loại bỏ ngay các đám mây trên cao vốn hay gây nhầm lẫn.  
2. **Motion Measurement Module (MMM)** — phân tích chuỗi khung hình liên tiếp thay vì một ảnh tĩnh, phát hiện luồng chuyển động nở rộng và bốc lên của khói.  
3. **Thiết kế hướng tới thiết bị tài nguyên thấp.**

> **Sửa trích dẫn so với bản v1.** VMOKED là **bản tiền ấn phẩm (preprint) trên SSRN**, đăng ngày 15/06/2025, tiêu đề đầy đủ *"A Low-Resource System for Rapid and Accurate Forest Fire Smoke Detection Using Video-Based Multiple Object Kinetic Emission Detection"*, tác giả Vinh Vu và Cong Tran (Học viện Công nghệ Bưu chính Viễn thông) cùng Dat Tran-Anh (Đại học Thuỷ lợi) \[1\]. **Không phải** bài đã xuất bản trên Elsevier *Array* 2026 như bản v1 ghi.

> **Hai con số cần xác minh trước khi đặt cược.** Bản v1 dẫn 64,89 GFLOPs và thời gian suy luận 7,5 mili-giây, nhưng không nêu phần cứng đo. Hai con số này không có trong phần công khai của bản tiền ấn phẩm. 64,89 GFLOPs trong 7,5 ms tương đương duy trì khoảng 8,6 TFLOPS — hợp lý trên GPU máy bàn nhưng đáng ngờ trên Jetson Orin Nano. **Phải hỏi tác giả đo trên máy nào trước khi khoá lựa chọn phần cứng.**

> **Cơ hội:** nhóm tác giả ở Hà Nội. Liên hệ trực tiếp khả thi và có giá trị hơn bất cứ kho mã nguồn nào.

**Mở rộng ở bản v2: đầu phân đoạn lớp phủ đất.** Không thêm mô hình mới — **mở rộng số lớp đầu ra của module SGS đang có**, từ hai lớp trời/đất thành: trời / tán rừng kín / đất đã phát dọn hoặc nương rẫy / mặt nước / công trình. Vì dùng chung backbone MobileNetV3, chi phí tính toán tăng thêm là biên, không phải gấp đôi.

## 2\. Cơ chế Hover-and-Stare

**Vấn đề.** VMOKED được thiết kế cho camera gắn trên chòi canh cố định. Khi đưa lên UAV đang bay, chuyển động của drone làm phông nền chuyển động theo, gây sai lệch cho module đo chuyển động khói.

**Giải pháp.** Drone di chuyển tới toạ độ chỉ định bằng bộ điều khiển bay PX4. Khi đến điểm quan sát, hệ thống kích hoạt trạng thái treo ổn định khoảng 2 giây. Trong khoảng đó, cụm gimbal ba trục triệt tiêu rung lắc do gió và camera ghi một đoạn video ngắn 30–60 khung hình. Phông nền rừng núi trở về trạng thái tĩnh, cho phép module đo chuyển động chạy chính xác.

## 3\. Bảng phân tầng kiến trúc

**Tầng 1 — Phản xạ biên (trên phương tiện bay)** Phần cứng: bộ điều khiển bay PX4 trên STM32H7, gimbal camera RGB. Công nghệ: MAVLink, PX4 Offboard Mode, ROS 2, Micro-XRCE-DDS. Trách nhiệm: điều khiển cân bằng, giữ hover, ổn định đường chân trời camera, tự quay về khi pin yếu. Tiền định, không có thành phần học máy. *Lưu ý triển khai: chế độ Offboard của PX4 yêu cầu luồng điểm đặt liên tục trên 2 Hz nếu không sẽ tự thoát chế độ \[16\]. Chính sách chạy ở 0,2 Hz do đó cần một bộ nội suy phát lại điểm đặt ở 10–20 Hz.*

**Tầng 2 — Trích xuất thị giác biên** Phần cứng: máy tính nhúng NVIDIA Jetson Orin Nano. Công nghệ: PyTorch / TensorRT, pipeline VMOKED mở rộng. Trách nhiệm: chạy SGS đa lớp tách nền trời và phân loại lớp phủ, chạy MMM đo chuyển động khói trên clip 2 giây, xuất ra xác suất khói và phân bố lớp phủ tại chân cột khói.

**Tầng 3 — Tác tử chiến thuật** Phần cứng: chạy trên cùng bo mạch biên ở Tầng 2\. Công nghệ: Gymnasium, Stable-Baselines3, bộ cập nhật niềm tin Bayes. Trách nhiệm: nhận đầu ra Tầng 2, cập nhật b\_t, chọn góc nhìn kế tiếp hoặc phát hành động kết thúc. Đây là tầng mang tính tác tử theo nghĩa MDP.

**Tầng 4 — Phán xét trung tâm** Phần cứng: máy chủ tại Chi cục Kiểm lâm hoặc trạm chỉ huy. Công nghệ: FastAPI, WebRTC/RTSP, dashboard GIS, GeoPandas. Trách nhiệm: lớp dữ liệu ngữ cảnh và đối chiếu GIS, khởi tạo b₀, xếp mức khẩn, xếp hàng ưu tiên cảnh báo ban đêm, phát cảnh báo đa kênh, nhật ký chỉ-thêm. Đây là tầng mang tính tác tử theo nghĩa nghị luận.

## 4\. Tài nguyên mã nguồn và dữ liệu

- **Mô hình thị giác:** kho mã nguồn VMOKED của nhóm tác giả \[1\].  
- **Tập dữ liệu khói:** WSDataset trên Kaggle \[2\] — 11.539 khung hình có khói, 12.481 khung hình không khói.  
- **Dữ liệu lớp phủ đất:** LoveDA \[9\], OpenEarthMap \[10\], LandCover.ai \[11\]; dữ liệu Việt Nam \[12\]\[13\].  
- **Môi trường mô phỏng:** PX4 SITL kết hợp Gazebo Garden để kiểm chứng tích hợp.

---

# TÀI LIỆU TRÍCH DẪN

\[1\] Vu, V., Tran-Anh, D., Tran, C. *A Low-Resource System for Rapid and Accurate Forest Fire Smoke Detection Using Video-Based Multiple Object Kinetic Emission Detection.* SSRN preprint, 15/06/2025. [https\://papers.ssrn.com/sol3/papers.cfm?abstract\_id=5295846](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5295846)

\[2\] WSDataset — wildfire-smoke-detection. Kaggle. [https\://www\.kaggle.com/datasets/gloryvu/wildfire-smoke-detection/data](https://www.kaggle.com/datasets/gloryvu/wildfire-smoke-detection/data)

\[3\] *Cross-Dataset Evaluation of YOLOv8 for UAV Fire and Smoke Detection: Benchmark Contamination, Zero-Shot Transfer, and Onboard Deployment on a Low-Cost Airframe.* Drones 10(8):635. [https\://www\.mdpi.com/2504-446X/10/8/635](https://www.mdpi.com/2504-446X/10/8/635)

\[4\] *ContextFireAgent: A Multi-Role Consensus Agent for RGB Wildfire Monitoring.* Remote Sensing 18(18):3066. [https\://www\.mdpi.com/2072-4292/18/18/3066](https://www.mdpi.com/2072-4292/18/18/3066)

\[5\] *Agentic UAVs: LLM-Driven Autonomy with Integrated Tool-Calling and Cognitive Reasoning.* arXiv:2509.13352. [https\://arxiv.org/abs/2509.13352](https://arxiv.org/abs/2509.13352)

\[6\] Nghị định 288/2025/NĐ-CP về quản lý tàu bay không người lái và phương tiện bay khác. Hiệu lực 05/11/2025. [https\://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Nghi-dinh-288-2025-ND-CP-quan-ly-tau-bay-khong-nguoi-lai-va-phuong-tien-bay-khac-679996.aspx](https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Nghi-dinh-288-2025-ND-CP-quan-ly-tau-bay-khong-nguoi-lai-va-phuong-tien-bay-khac-679996.aspx)

\[7\] *Use of Remote Sensing to Identify Forest Fire and Crop Residue Burning.* [https\://www\.researchgate.net/publication/363134581\_Use\_of\_Remote\_Sensing\_to\_Identify\_Forest\_Fire\_and\_Crop\_Residue\_Burning](https://www.researchgate.net/publication/363134581_Use_of_Remote_Sensing_to_Identify_Forest_Fire_and_Crop_Residue_Burning)

\[8\] *Overcoming Common Pitfalls to Improve the Accuracy of Crop Residue Burning Measurement Based on Remote Sensing Data.* Remote Sensing 16(2):342. [https\://doi.org/10.3390/rs16020342](https://doi.org/10.3390/rs16020342)

\[9\] Wang, J. et al. *LoveDA: A Remote Sensing Land-Cover Dataset for Domain Adaptive Semantic Segmentation.* NeurIPS 2021\. [https\://github.com/Junjue-Wang/LoveDA](https://github.com/Junjue-Wang/LoveDA)

\[10\] *OpenEarthMap: A Benchmark Dataset for Global High-Resolution Land Cover Mapping.* [https\://open-earth-map.org/overview\_oem.html](https://open-earth-map.org/overview_oem.html)

\[11\] Boguszewski, A. et al. *LandCover.ai: Dataset for Automatic Mapping of Buildings, Woodlands, Water and Roads.* CVPRW 2021\. [https\://openaccess.thecvf.com/content/CVPR2021W/EarthVision/papers/Boguszewski\_LandCover.ai\_Dataset\_for\_Automatic\_Mapping\_of\_Buildings\_Woodlands\_Water\_and\_CVPRW\_2021\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2021W/EarthVision/papers/Boguszewski_LandCover.ai_Dataset_for_Automatic_Mapping_of_Buildings_Woodlands_Water_and_CVPRW_2021_paper.pdf)

\[12\] *First comprehensive quantification of annual land use/cover from 1990 to 2020 across mainland Vietnam.* Scientific Reports. [https\://www\.nature.com/articles/s41598-021-89034-5](https://www.nature.com/articles/s41598-021-89034-5)

\[13\] Land Cover 2020 in Vietnam. OD Mekong Datahub. [https\://data.vietnam.opendevelopmentmekong.net/dataset/land-cover-2020](https://data.vietnam.opendevelopmentmekong.net/dataset/land-cover-2020)

\[14\] *Emission inventories of rice straw open burning in the Red River Delta of Vietnam: Evaluation of the potential of satellite data.* [https\://www\.sciencedirect.com/science/article/abs/pii/S0269749119335420](https://www.sciencedirect.com/science/article/abs/pii/S0269749119335420)

\[15\] *From pixels to patterns: review of remote sensing techniques for mapping shifting cultivation systems.* Spatial Information Research. [https\://link.springer.com/article/10.1007/s41324-023-00547-9](https://link.springer.com/article/10.1007/s41324-023-00547-9)

\[16\] PX4 Offboard Control with ROS 2\. [https\://docs.px4.io/main/en/ros2/offboard\_control](https://docs.px4.io/main/en/ros2/offboard_control)

\[17\] *Northern region sees sharp rise in forest fires in early 2025\.* Việt Nam News. [https\://vietnamnews.vn/environment/1716190/northern-region-sees-sharp-rise-in-forest-fires-in-early-2025.html](https://vietnamnews.vn/environment/1716190/northern-region-sees-sharp-rise-in-forest-fires-in-early-2025.html)

\[18\] Bickford Smith, F. et al. *Prediction-Oriented Bayesian Active Learning.* AISTATS 2023\. [https\://proceedings.mlr.press/v206/bickfordsmith23a/bickfordsmith23a.pdf](https://proceedings.mlr.press/v206/bickfordsmith23a/bickfordsmith23a.pdf)

\[19\] Krause, A., Singh, A., Guestrin, C. *Near-Optimal Sensor Placements in Gaussian Processes.* JMLR 9, 2008\. [https\://jmlr.org/papers/v9/krause08a.html](https://jmlr.org/papers/v9/krause08a.html)

---

# PHỤ LỤC — DANH MỤC CẦN XÁC MINH

Các mục dưới đây chưa được xác minh và cần giải quyết trước khi khoá tài liệu:

1. **Số cảnh báo mỗi ngày trên một trạm kiểm lâm trong mùa khô, và tỷ lệ phân bố giữa ba nhóm báo giả.** Đây là mẫu số của mọi KPI phần trăm. Giải quyết bằng một buổi làm việc với Chi cục Kiểm lâm.  
2. **Phần cứng đo hai con số hiệu năng của VMOKED.** Hỏi trực tiếp nhóm tác giả.  
3. **Tính khả thi của KPI 10 phút với bán kính 5 km.** Bay 5 km một chiều ở tốc độ hành trình multirotor thực tế mất khoảng 6–8 phút, khứ hồi 12–16 phút, chưa tính thời gian quan sát. Cần đo thực tế hoặc điều chỉnh một trong hai con số. *Mục này chưa được chủ nhiệm đề tài duyệt sửa, giữ nguyên để rà lại.*  
4. **Thủ tục cấp phép bay theo Nghị định 288/2025/NĐ-CP** \[6\]: thời hạn nộp hồ sơ trước, thời gian xử lý, và khả năng xin phép theo một hộp không gian cố định gắn với vị trí trạm thay vì theo từng chuyến. Gọi Bộ Chỉ huy Quân sự tỉnh nơi dự kiến triển khai. *Mục này chưa được chủ nhiệm đề tài duyệt đưa vào phần chính, giữ ở phụ lục.*  
5. **Con số 2 giây cho mỗi lần hover** — giá trị khởi điểm, cần kiểm chứng xem có đủ để module đo chuyển động bắt được động học nở rộng của khói trong điều kiện gió nhẹ hay không.

