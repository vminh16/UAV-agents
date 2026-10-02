# `cv/` — Thị giác máy tính

**Owner:** CV — *Nguyễn Văn Đạt* · **Đọc trước:** [`docs/03-architecture/20-cv.md`](../docs/03-architecture/20-cv.md) (đặc biệt **§5 định nghĩa LLR**), [`00-overview.md`](../docs/03-architecture/00-overview.md) §1–8, 13–14, [`50-interfaces.md`](../docs/03-architecture/50-interfaces.md)

> Biến **một clip** thành **một quan sát đã hiệu chỉnh**: `llr` = ln p(z|SMOKE,c) − ln p(z|NO_SMOKE,c), cộng cờ chất lượng và ngữ cảnh. Sinh artifact **A-01 `observation_model`** cho agent. Chỉ RGB.

## Làm / không làm

| Làm | Không làm |
|---|---|
| `perception_service` (onboard **hoặc** mặt đất, chọn bằng config) | Không kết luận nhiệm vụ, không bắn cảnh báo |
| Pipeline dữ liệu: đăng ký nguồn + giấy phép, khử trùng lặp **trước** khi chia, chia theo nhóm | **Không gửi posterior/sigmoid vào `llr`**; không cộng prior |
| Huấn luyện, hiệu chỉnh, xuất NCNN/TensorRT, A-01, model card | Không đọc/ghi MAVLink |
| Stub `fake_perception` | Không commit dữ liệu hay trọng số vào git |

## Hợp đồng

Nhận: I-06 `clip_ready`. Phát: I-07 `observation`, artifact A-01 `observation_model`.

## Thư mục

```
cv/
├── configs/    # pipeline.default.yaml (profile mvp_rpi5 / mvp_jetson)
├── data/       # README.md: đăng ký nguồn dữ liệu + giấy phép (KHÔNG chứa dữ liệu)
├── src/        # uav_cv/: service/, quality/, stabilize/, detect/, track/, motion/, classify/, calibrate/, registry.py
├── training/   # khử trùng lặp, chia tập, huấn luyện, đánh giá, sinh A-01, xuất mô hình
└── tests/      # contract, LLR không phụ thuộc tỷ lệ dương, valid=false, latency, fake_perception
```

## Định nghĩa hoàn thành MVP (tóm tắt)

- [ ] `perception_service` trả `observation` hợp lệ trong ≤ 5 s/clip onboard (≤ 15 s mặt đất)
- [ ] Test chứng minh LLR = logit(q) − logit(π_cal) (không phụ thuộc tỷ lệ dương tập hiệu chỉnh)
- [ ] Mỗi `invalid_reason` có clip test
- [ ] A-01 v0.1 + model card; báo cáo FPR theo từng loại giả khói + zero-shot chéo dataset
- [ ] VMOKED chạy lại làm baseline bằng bộ đánh giá của dự án
- [ ] Stub `fake_perception` cho AGT/EMB/BE
