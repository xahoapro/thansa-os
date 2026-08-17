# BỔ SUNG GĐ1 — sửa bản ghi "chuẩn xanh" (sau nghiệm thu độc lập của trạm #1)

Trạm #1 chạy lại `tests/run.py` độc lập và phát hiện bản ghi trong `ops/so-tron.md` (kế thừa từ báo cáo GĐ0) SAI. Ghi lại sự thật đã kiểm (chạy riêng 2 lần):

## Sự thật
- **`pytest` là DEV-DEPENDENCY BẮT BUỘC.** Thiếu pytest → `test_workflow_graph_phase10.py` (và phase8/11/12) **lỗi cứng** `ModuleNotFoundError: No module named 'pytest'` ở dòng `import pytest` — **KHÔNG self-skip**.
- **Không pytest → 240/241** (phase10 đỏ thật, ~1s), KHÔNG phải "241/241" như GĐ0/so-tron đang ghi.
- **Có pytest** (trạm #1 đã cài `pytest 9.1.1` vào `goc/.venv`) → phase10 XANH (39s), suite **241/241**.
- `test_chat_disconnect.py` **nhạy timing**: chạy riêng = XANH; flaky khi chạy song song tải nặng (lần full 861s nó đỏ, chạy riêng lại xanh).

## Việc cần làm (GĐ1 bổ sung)
1. **Sửa `ops/so-tron.md`**: thay câu "tests/run.py XANH 241/241 theo cấu hình upstream" bằng bản ghi đúng:
   > Chuẩn xanh = CÓ pytest → 241/241. Không pytest → 240/241 (`test_workflow_graph_phase10.py` lỗi `import pytest`). `test_chat_disconnect.py` nhạy timing (chạy riêng xanh).
2. **Thêm `pytest` vào tài liệu môi trường** để không biến mất khi dựng lại `.venv`: tạo `ops/requirements-dev.txt` (nội dung tối thiểu: `pytest`) + 1 dòng trong checklist cấp máy / `env.thansa.example`.
3. (Tuỳ chọn, đề xuất upstream — KHÔNG vá trong thansa-os): bọc `import pytest` bằng self-skip thật, hoặc đưa pytest vào requirements dev của upstream.

## Ràng buộc
- Nếu thêm `ops/requirements-dev.txt` vào phạm vi patch P006 thì **cập nhật `diem_neo`/`vung_theo_doi` trong mapping.yaml cho khớp** để `tu-kiem-chung.py` vẫn XANH. Nếu coi là chore riêng thì commit thường (không `[me]`), giữ số `[me]` == số mục mapping.
- Không đụng mã nguồn app. Không phát hành.

## Nghiệm thu bổ sung (đo được)
- `ops/tu-kiem-chung.py` vẫn XANH (exit 0).
- `goc/.venv/bin/python -c "import pytest"` OK.
- `ops/so-tron.md` phản ánh đúng chuẩn xanh (có pytest).
- Chạy riêng `test_workflow_graph_phase10.py` = XANH.

Xong thì báo trạm #1 nghiệm thu lại trước khi sang GĐ2 (rebrand P001–P005).
