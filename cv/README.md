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

## Cài đặt và chạy test

```powershell
cd cv
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest            # test MQTT tự bỏ qua nếu không có broker ở localhost:1883
```

## Stub `fake_perception` (cho AGT / EMB / BE)

Tiến trình độc lập: nghe `uav/{uav_id}/embedded/clip_ready`, chờ 1,5 s, phát `uav/{uav_id}/cv/observation` hợp lệ theo schema. `context` tính thật từ tư thế trong `clip_ready`; LLR giả lập theo kịch bản trong [`configs/fake_perception.yaml`](configs/fake_perception.yaml).

| Kịch bản | Kết quả |
|---|---|
| `smoke` | `valid=true`, LLR ∈ [+1,5, +3,5] |
| `no_smoke` | `valid=true`, LLR ∈ [−3,0, −1,0] |
| `invalid` | `valid=false`, `llr=null`, `invalid_reasons=["SUN_GLARE"]` |
| `random` (mặc định) | H ~ Bernoulli(`p_smoke`), hỏng ngẫu nhiên theo `p_invalid` |

Ngoài ra, ở mọi kịch bản: camera nhìn trong ±20° quanh mặt trời → `SUN_GLARE`; mục tiêu ngoài khung hình → `TARGET_OUT_OF_FOV` (tắt bằng `--no-geometry-gate`). Nhãn thật nằm ở `features.stub_truth_smoke` để chấm điểm agent.

```powershell
# Cần mosquitto (hoặc broker MQTT bất kỳ) đang chạy
python cv/tests/fake_perception.py                                   # random, nghe mọi UAV
python cv/tests/fake_perception.py --scenario smoke --seed 42
python cv/tests/fake_perception.py --sequence no_smoke,invalid,smoke,smoke --uav-id uav-01
python cv/tests/fake_perception.py --host 192.168.1.10 --delay 3

# Không cần broker: in observation cho một clip_ready
python cv/tests/fake_perception.py --once docs/interfaces/examples/clip_ready.example.json --scenario invalid
```

## Định nghĩa hoàn thành MVP (tóm tắt)

- [ ] `perception_service` trả `observation` hợp lệ trong ≤ 5 s/clip onboard (≤ 15 s mặt đất)
- [ ] Test chứng minh LLR = logit(q) − logit(π_cal) (không phụ thuộc tỷ lệ dương tập hiệu chỉnh)
- [ ] Mỗi `invalid_reason` có clip test
- [ ] A-01 v0.1 + model card; báo cáo FPR theo từng loại giả khói + zero-shot chéo dataset
- [ ] VMOKED chạy lại làm baseline bằng bộ đánh giá của dự án
- [ ] Stub `fake_perception` cho AGT/EMB/BE
