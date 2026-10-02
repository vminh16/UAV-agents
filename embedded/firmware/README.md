# Firmware — Pixhawk 2.4.8 (ArduPilot Copter, target `Pixhawk1-1M`)

- Danh mục tham số cần cấu hình và lý do: [`docs/03-architecture/30-embedded.md` §7](../../docs/03-architecture/30-embedded.md).
- Chỉ lưu vào `params/` các file **đã kiểm chứng HITL**, đặt tên `pixhawk248-YYYYMMDD.param`, kèm ghi chú phiên bản firmware và kết quả kiểm thử failsafe.
- Trước khi nạp: kiểm tra [danh sách tính năng bị lược theo bo](https://ardupilot.org/copter/docs/binary-features.html) cho `Pixhawk1-1M`. Gimbal và kiểm tra địa hình làm trên máy tính đồng hành, không phụ thuộc FC.
- Phương án thay thế: PX4 v1.15 (`px4_fmu-v2`) qua MAVLink — cần luồng setpoint ≥ 2 Hz cho Offboard.
