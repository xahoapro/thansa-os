# NHIỆM VỤ (BUG — CHẶN phát hành v1.1) — Sửa hồi quy test_chat_disconnect

Trạm #1 soạn · 2026-08-21 · cho trạm #2 (VPS). **Ưu tiên cao — v1.1 KHÔNG được phát hành đến khi test này XANH.**

## Triệu chứng (trạm #1 xác minh độc lập)
- `tests/python/test_chat_disconnect.py::test_websocket_disconnect_does_not_cancel_turn` **ĐỎ cố định** (chạy riêng 3/3 lần đỏ, máy KHÔNG tải — load 0.30, 1.44s). KHÔNG phải flaky timing.
- Lỗi: `AssertionError` tại **line 95**:
  ```
  assert [m["role"] for m in messages] == ["user", "assistant"]
  # pytest: "Right contains one more item: 'assistant'"
  ```
  → sau khi websocket ngắt, danh sách role KHÔNG khớp `["user","assistant"]` — bản chất: **turn bị huỷ / message assistant không được ghi (hoặc ghi sai số lượng) khi ws disconnect.** Đây chính là bất biến mà test bảo vệ ("disconnect KHÔNG được huỷ turn").

## Đây là HỒI QUY CODE (không phải test)
- Test **y hệt** ở v1.0 (`a68882d`) và me (đều 113 dòng). Ở **v1.0 test này XANH** (chạy riêng). Bây giờ ĐỎ.
- Nguyên nhân nằm ở **`server/main.py`** đường xử lý websocket-disconnect / hoàn tất turn (quanh `except asyncio.CancelledError` ~9645 và `except WebSocketDisconnect` ~9721). Nghi vấn: **merge 0.37.x giải xung đột sai** làm mất/thừa bước ghi message assistant khi client rời sớm, hoặc turn bị cancel thay vì chạy tiếp nền.
- GĐ5 báo 247/247 nhưng sau đó có thêm merge (test 247→250) — hồi quy nhiều khả năng lọt trong đợt merge sau GĐ5.

## Việc cần làm
1. Chạy `.venv/bin/python tests/run.py test_chat_disconnect.py -v` đọc diff đầy đủ (role sequence thực tế + content).
2. Bisect: kiểm tại commit v1.0 (`a68882d`) test còn xanh → tìm commit/merge giữa `a68882d..me` làm nó đỏ (`git log a68882d..me -- server/main.py`; xem các đoạn quanh 9645/9721 và nơi persist message assistant khi turn kết thúc/disconnect).
3. Sửa **code** để giữ đúng bất biến: ws disconnect → turn VẪN chạy nền tới khi xong, message assistant ghi **đúng 1 lần** (`["user","assistant"]`, content = "ket qua nen"), job dọn xong (`get_job(...) is None`). **KHÔNG sửa test** (test mã hoá hành vi đúng). Nếu buộc phải điều chỉnh test vì upstream đổi hợp đồng → DỪNG, báo trạm #1.
4. Nếu là lỗi giải-xung-đột-merge (đoạn code bị nhân đôi hoặc thiếu `nonlocal`/`await`) → sửa đúng chỗ, ghi rõ trong báo cáo.

## Kỷ luật
- Đây là sửa hồi quy trên vùng LOGIC (không phải rebrand) → theo luật ưu tiên #3: nếu thay đổi hành vi nghiệp vụ, mô tả rõ và để trạm #1/chủ soát. Commit gợi ý `[me] fix: ws-disconnect khong huy turn (hoi quy 0.37.x)` — hoặc nếu chỉ sửa cách hoà merge thì nói rõ.
- Cập nhật mapping/so_patch nếu tạo patch `[me]` mới; giữ `tu-kiem-chung.py` XANH.

## Tiêu chí ĐẠT (mở lại cổng release)
1. `tests/run.py test_chat_disconnect.py` (chạy riêng) → **1/1 XANH**, ổn định.
2. `tests/run.py` full → tất cả XANH (chỉ chấp nhận flaky nếu chứng minh được là timing, chạy riêng xanh).
3. `tu-kiem-chung.py` XANH. Ghi `bao-cao/` + `so-tron.md`. Push `me`. Báo trạm #1 nghiệm thu lại → khi đó mới phát hành `thansa-v1.1`.
