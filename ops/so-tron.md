# Sổ trộn — thansa-os

Trả lời: "tôi đã đi qua những gì và vì sao quyết như vậy?" (DAC-TA mục 2.3).
Chỉ ghi thêm (append-only), KHÔNG sửa dòng cũ. Mỗi vòng trộn một khối, mới nhất dưới cùng.

## Khởi lập 2026-08-17 (chưa phải vòng trộn)

- GĐ0: dựng khung trên nền upstream `0b8f2c0` (VERSION 0.35.10), 0 patch. 3 nhánh
  main/me/release, 2 worktree goc/thansa, repo private `xahoapro/thansa-os`.
  Chuẩn xanh = CÓ pytest → 241/241. Không pytest → 240/241
  (`test_workflow_graph_phase10.py` lỗi `import pytest`). `test_chat_disconnect.py`
  nhạy timing (bản ghi sửa theo nhiem-vu/GD1-bosung.md; chi tiết ở mục "Đã biết").
- GĐ1: lập bộ hồ sơ ops/ (mốc gốc, mapping rỗng, sổ trộn) + bộ dò hằng ngày
  (`ops/do-hang-ngay.sh`) + tự kiểm chứng (`ops/tu-kiem-chung.sh`). Mapping sẽ có
  mục đầu tiên ở GĐ2 (P001–P006, rebrand).
- Chưa có vòng trộn nào. Vòng đầu tiên ghi khối kế tiếp theo mẫu DAC-TA mục 2.3.

## Đã biết (không phải lỗi của bản Thansa)

- `pytest` là DEV-DEPENDENCY BẮT BUỘC (chốt 17/08, nhiem-vu/GD1.md bản sửa sau nghiệm thu
  độc lập của trạm #1): 5 test Python `import pytest` ngay đầu file, thiếu là lỗi cứng
  `ModuleNotFoundError` chứ KHÔNG self-skip. Chuẩn "xanh" chính thức = CÓ pytest → 241/241.
  pytest ghi ở `ops/requirements-dev.txt` (upstream không khai vì requirements.txt của họ
  chỉ dành cho runtime). Đáng đề xuất upstream: bọc import bằng self-skip thật hoặc thêm
  file requirements dev.
- `test_chat_disconnect.py` NHẠY TIMING: chờ cứng `asyncio.sleep(0.08)` rồi đòi tin nhắn
  assistant đã ghi xong — chạy song song tải nặng có thể đỏ dù mã đúng (kiểm chứng 17/08:
  chạy riêng thì xanh; nâng chờ 2s ở bản nháp cũng xanh). Flaky thì chạy riêng để xác nhận.
  Không vá trong thansa-os (ngoài phạm vi rebrand); nếu muốn thì đề xuất upstream đổi
  sleep cứng thành poll.

## Quyết định của chủ 2026-08-17 (nghiệm thu GĐ1)

- CHẤP NHẬN chuẩn xanh GĐ1, gồm chuẩn riêng cho VPS: 240/241 + `test_chat_disconnect.py`
  đỏ do ngưỡng 80ms (số đo trong bao-cao/GD1.md). Máy nghiệm thu Windows vẫn kỳ vọng 241/241.
- P002 (logo + favicon): DÙNG TẠM ảnh mặc định của upstream, chưa thay. Patch P002 để
  lại đến khi chủ cung cấp ảnh Thansa; GĐ2 làm các patch còn lại.
