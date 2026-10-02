# `backend/` — Máy chủ trạm / Chi cục

**Owner:** BE — *Lê Sỹ Long Nhật* · **Đọc trước:** [`docs/03-architecture/40-backend.md`](../docs/03-architecture/40-backend.md), [`docs/01-PRD.md`](../docs/01-PRD.md) §6–7, [`00-overview.md`](../docs/03-architecture/00-overview.md) §1–8, 13–14, [`50-interfaces.md`](../docs/03-architecture/50-interfaces.md)

> Nơi **con người** ra quyết định: tiếp nhận cảnh báo, tính prior b₀, phê duyệt bay, giám sát, lưu bằng chứng chỉ-thêm, **diễn giải kết luận onboard thành kết quả vận hành**.

## Làm / không làm

| Làm | Không làm |
|---|---|
| `alert_intake`, `prior_model`, `mission_planner`, `mission_manager`, `adjudicator`, `dashboard`, `evidence_store`, `audit_log`, `notifier`, broker mặt đất | Không gửi lệnh bay chi tiết hay góc nhìn |
| Kết quả vận hành: `FOREST_FIRE_URGENT`, `SMOKE_ON_CULTIVATED_LAND_REVIEW`, `FALSE_ALARM_NO_SMOKE`, `UNDETERMINED_HUMAN_REVIEW` | Không sửa kết luận agent, không sửa/xoá bằng chứng |
| Đóng nhiệm vụ với **nhãn kết quả thực tế** (nhãn vàng) | Không tự động điều động |

## Hợp đồng

Phát: I-01 `mission_request`, I-11 `mission_control`.
Nhận: I-02, I-03, I-07, I-08, I-09, I-10, I-12.

## Thư mục

```
backend/
├── configs/   # backend.default.yaml: prior_model, luật phân xử (có ID), notifier, mặc định nhiệm vụ
├── src/       # uav_backend/: api/, alerts/, prior/, missions/, gateway/, adjudicator/, evidence/, audit/, notify/, ui/
└── tests/     # contract, luồng nhiệm vụ, luật phân xử, chỉ-thêm, fake_uav (stub)
```

## Định nghĩa hoàn thành MVP (tóm tắt)

- [ ] Luồng: cảnh báo → b₀ (có giải thích) → phê duyệt → `mission_request` → dashboard trực tiếp → kết quả vận hành → đóng với nhãn vàng
- [ ] Validate mọi thông điệp vào/ra theo schema
- [ ] Mỗi luật phân xử có test; kết quả ghi ID luật
- [ ] Không có API sửa/xoá bằng chứng; `audit_log` có chuỗi băm
- [ ] Stub `fake_uav` và `fake_backend`
