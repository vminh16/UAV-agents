# `agents/` — Tác tử onboard

**Owner:** AGT — *Nguyễn Văn Minh* · **Đọc trước:** [`docs/03-architecture/10-agents.md`](../docs/03-architecture/10-agents.md), [`00-overview.md`](../docs/03-architecture/00-overview.md) §1–8, 13–14, [`50-interfaces.md`](../docs/03-architecture/50-interfaces.md)

> Module mang **tính tác tử — mốc MVP**: tự quyết **nhìn ở đâu tiếp**, **nhìn tiếp hay dừng**, **kết luận gì** (`SMOKE_CONFIRMED` / `NO_SMOKE` / `UNDETERMINED`).

## Làm / không làm

| Làm | Không làm |
|---|---|
| Niềm tin, fusion, planner, luật dừng, mô hình chi phí — **cắm được qua registry** | Không đọc pixel, không chạy mô hình thị giác |
| Xử lý REJECTED / timeout / quan sát kém / `safety_event` | Không gửi MAVLink, toạ độ GPS, độ cao tuyệt đối — chỉ `view_spec` tương đối mục tiêu |
| Vết quyết định (`agent_step`, `agent_decision`) | Không tự đặt prior, không cộng b₀ hai lần |
| Bộ mô phỏng L0 + benchmark baseline | Không diễn giải vận hành (việc của backend) |

## Hợp đồng

Nhận: I-01 `mission_request`, I-03 `vehicle_state`, I-05 `view_result`, I-07 `observation`, I-10 `safety_event`, A-01 `observation_model`.
Phát: I-04 `view_command`, I-12 `agent_step`, I-08 `agent_decision`.
Schema: [`docs/interfaces/schemas/`](../docs/interfaces/schemas/).

## Thư mục

```
agents/
├── configs/   # agent.default.yaml (profile mvp_default) — chọn phương pháp bằng tên
├── src/       # uav_agent/: runtime, belief/, planners/, stopping/, cost/, registry.py, trace.py, io_mqtt.py
├── sim/       # ActiveVerificationEnv (L0), sinh kịch bản, benchmark, scripted_agent (stub)
└── tests/     # unit, contract (validate theo schema), replay, nhánh ngoại lệ
```

## Định nghĩa hoàn thành MVP (tóm tắt)

- [ ] Mặc định MVP chạy: `tempered_bayes` + `chernoff_kl_per_cost` + `sprt_wald` + `flight_time`
- [ ] Baseline B1–B4, B7 chạy được bằng đổi config
- [ ] 100% thông điệp phát ra validate theo schema
- [ ] Mọi nhánh ngoại lệ (10-agents §4.4, 00-overview §6) có test
- [ ] Phát lại `message_log.jsonl` cho ra đúng chuỗi quyết định
- [ ] Benchmark L0 đạt K-MVP-1 ([PRD §8](../docs/01-PRD.md))
- [ ] Stub `scripted_agent` cho EMB/BE test độc lập
