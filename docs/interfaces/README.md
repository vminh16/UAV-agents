# Hợp đồng giao tiếp (machine-readable)

Đây là **nguồn sự thật duy nhất** về thông điệp giữa `agents/`, `cv/`, `embedded/`, `backend/`. Giải thích ngữ nghĩa: [`../03-architecture/50-interfaces.md`](../03-architecture/50-interfaces.md).

| Thư mục | Nội dung |
|---|---|
| `schemas/` | JSON Schema 2020-12, mỗi thông điệp một file; `common.schema.json` chứa kiểu dùng chung |
| `examples/` | Ít nhất một ví dụ **hợp lệ** cho mỗi schema, dùng làm dữ liệu test và stub |
| `examples/invalid/` | Ví dụ **cố ý sai**, mỗi file vi phạm đúng một quy tắc; phải bị từ chối |
| `tools/validate.py` | Kiểm tra schema, ví dụ hợp lệ, ví dụ sai. CI chạy trên mọi PR |

```bash
pip install -r docs/interfaces/tools/requirements.txt
python docs/interfaces/tools/validate.py
```

**Cách dùng trong module:** mỗi module viết test hợp đồng riêng, đọc schema từ thư mục này (đường dẫn tương đối từ gốc repo) và validate mọi thông điệp mình phát ra/nhận vào. **Không** chép schema vào thư mục module.

**Thay đổi hợp đồng:** theo [00-overview §15](../03-architecture/00-overview.md). Tóm tắt: PR sửa `schemas/` + `examples/` + `50-interfaces.md`; tăng `schema_version` (patch / minor / major); mọi owner bị ảnh hưởng duyệt.
