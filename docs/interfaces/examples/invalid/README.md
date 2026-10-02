# Ví dụ SAI (phải bị từ chối)

Mỗi file ở đây cố ý vi phạm **đúng một** quy tắc của hợp đồng. `tools/validate.py` yêu cầu mỗi file phải **thất bại** khi validate; nếu một file bỗng hợp lệ, nghĩa là schema đã bị nới lỏng ngoài ý muốn.

| File | Lỗi cố ý |
|---|---|
| `agent_decision.undetermined_threshold.json` | UNDETERMINED với reason THRESHOLD_REACHED |
| `mission_request.b0_one.json` | b0 phải nằm trong (0, 1) |
| `observation.invalid_with_llr.json` | valid=false nhưng vẫn gửi llr |
| `observation.local_time.json` | dùng giờ địa phương thay vì UTC |
| `observation.valid_without_llr.json` | valid=true nhưng llr=null |
| `observation.wrong_header_schema.json` | header.schema không khớp tên schema |
| `view_command.absolute_coordinates.json` | agent gửi toạ độ tuyệt đối trong view_spec |
| `view_command.bearing_360.json` | phương vị phải trong [0, 360) |
| `view_result.reached_without_clip.json` | REACHED nhưng thiếu clip_id |
| `view_result.rejected_without_reason.json` | REJECTED nhưng thiếu reject_reason |
