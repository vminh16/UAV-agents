# Đăng ký nguồn dữ liệu (data registry)

**Không commit dữ liệu, ảnh, video hay trọng số vào git.** Thư mục này chỉ chứa *mô tả* nguồn. Dữ liệu lưu ở kho chung (ổ mạng / object storage), đường dẫn trong biến môi trường `UAV_DATA_DIR`.

Mỗi nguồn một dòng; cập nhật khi thêm nguồn. Cột **Giấy phép** bắt buộc trước khi dùng cho sản phẩm (NFR-09).

| ID | Tên | Góc nhìn | fps / tần suất | Quy mô | Nhãn | Giấy phép | Dùng cho | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| D01 | FIgLib (HPWREN) | Chòi canh | ~1 khung/phút | ~25k ảnh, 315 chuỗi | Mức ảnh/chuỗi | *(kiểm tra)* | Detector, mẫu âm khó | Động học theo phút |
| D02 | PyroNear-2024/2025, pyro-sdis | Chòi canh/web | Có video | ~50k ảnh | bbox | *(kiểm tra)* | Detector | — |
| D03 | Boreal Forest Fire | UAV | Video | 4.954 ảnh + 292 clip | bbox + mask | *(kiểm tra)* | Detector, chuyển động UAV | Rừng phương Bắc |
| D04 | FLAME 1/2/3 | UAV | — | FLAME 3 ~14k | mask/nhãn | *(kiểm tra)* | Khói/lửa đốt kiểm soát | Chỉ dùng RGB |
| D05 | FASDD (UAV) | UAV | — | — | bbox | *(kiểm tra)* | Detector | 90,7% test gần-trùng: khử lại |
| D06 | D-Fire | Hỗn hợp | — | — | bbox | *(kiểm tra)* | Detector | 46,0% test gần-trùng |
| D07 | WSDataset (VMOKED) | Camera cố định | — | 11.539 / 12.481 khung | — | **chưa rõ** | Baseline VMOKED | Chưa xác minh link |
| D08 | VDD / UAVid / IDD | UAV xiên | — | 400 / 300 / 811 | Phân đoạn | *(kiểm tra)* | Lớp phủ (V1) | — |
| D09 | **VN field (tự thu)** | **UAV đa góc, hover 1–4 s** | 30 fps | Khởi điểm ≥ 30 sự kiện × ≥ 8 góc | Mức sự kiện + loại giả khói | Của dự án | A-01, test chính | Quy trình: PRD §10 |

**Quy tắc chia tập:** khử trùng lặp gần (pHash / embedding) **trên toàn bộ** dữ liệu trước, rồi chia theo **nhóm** (sự kiện / địa điểm / video). Lưu danh sách chia tập có phiên bản cùng gói phát hành.
