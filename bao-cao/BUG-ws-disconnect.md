# Báo cáo điều tra: BUG ws-disconnect (test_chat_disconnect)

Trạm #2 (VPS) · 2026-08-21 · trả lời `nhiem-vu/BUG-ws-disconnect.md` của trạm #1.

## Kết luận ngắn

**KHÔNG tái hiện được lỗi trên trạm #2 (VPS).** Test `test_chat_disconnect.py` XANH ổn định
qua **45+ lần** chạy (pytest, kiểu CI `__main__`, có nén 4 tiến trình CPU, `PYTHONASYNCIODEBUG=1`),
và full suite **250/250** (hai lần). Đường code mà test chạy **byte-identical** giữa v1.0
(`a68882d`, nơi trạm #1 xác nhận XANH) và `me` hiện tại → **không có hồi quy code trong đường
test đi qua.** Khác biệt đỏ/xanh gần như chắc chắn do **môi trường** trạm #1, không phải defect
tái hiện trên đích triển khai.

## Đã kiểm gì

1. **Tái hiện:** 10× pytest + 5× CI-style + 30× dưới tải CPU/asyncio-debug = **45/45 PASS**.
   Không thấy một lần flake nào. (Trạm #1 báo 3/3 ĐỎ, load 0.30.)
2. **Đường disconnect đúng theo thiết kế:**
   - `chat_runtime.remove_client()` chỉ pop subscriber, **KHÔNG** huỷ job (`main.py:9753`).
   - Không có `.cancel()` nào chạy trên đường disconnect (chỉ action `stop` mới cancel).
   - Turn chạy ở `asyncio.create_task(run_turn(...))` riêng (`main.py:9742`); `except
     WebSocketDisconnect` chỉ `pass` rồi `remove_client` (`main.py:9749-9753`).
   - Persist assistant **vô điều kiện theo final_text**: `if final_text: await _persist_turn`
     (`main.py:9636`), độc lập với client còn kết nối hay không.
3. **Provider resolve** (nghi patch chết): `_do_turn` dùng `_chat_provider_for_session`
   (`main.py:8792`) còn test patch `_chat_provider`. Truy ra: phiên test không có key trong
   `mcfg` rỗng nên `_chat_provider_for_session` **rơi về** `_chat_provider` (đã patch) → vẫn tới
   đúng nhánh api + `_api_stream_mcp` (fake_stream). Patch KHÔNG chết. Không phải nguyên nhân.
4. **Diff v1.0 (`a68882d`) → `me`** (đúng yêu cầu bisect của trạm #1):
   - `run_turn` + vòng nhận tin + `except WebSocketDisconnect`: **GIỐNG HỆT** (95/95 dòng).
   - `_persist_turn`: **GIỐNG HỆT**.
   - `_do_turn`: thay đổi DUY NHẤT là nhánh **CLI/claude** (0.37.1 `a1ad69a`: mồi mạch từ SQLite,
     `if _cli_xoay_mach` → `if not cli.session_id`). Test dùng **openrouter/api**, KHÔNG vào nhánh
     CLI này. → không dính.
   - Test file: **giống hệt** v1.0 ↔ me (113 dòng).
5. **Môi trường trạm #2:** Python 3.12.3, fastapi 0.115.0, starlette 0.38.6.

## Vì sao khả năng cao là môi trường

Đường code test đi qua KHÔNG đổi từ v1.0. Nếu v1.0 xanh và me đỏ trên CÙNG máy trạm #1, mà code
đường đó y hệt, thì biến số còn lại là runtime: **phiên bản fastapi/starlette/anyio** hoặc lịch
biểu asyncio của OS trạm #1 (timing giữa `receive_text()` ném `WebSocketDisconnect` và task
`run_turn` kịp stream 0.03s + persist trong cửa sổ chờ 0.08s của test).

## Đề xuất (chờ trạm #1 quyết)

1. Trạm #1 chạy lại test trên `me` hiện tại (`f487ad7`) và **gửi version** `python -c "import
   fastapi,starlette,anyio,sys; print(sys.version, fastapi.__version__, starlette.__version__)"`
   + `pip freeze | grep -i "anyio\|starlette\|fastapi\|uvicorn"` để đối chiếu.
2. Nếu là race timing theo môi trường: **nới cửa sổ chờ** của test (0.08s → ~0.3s) cho tất định
   trên máy chậm — NHƯNG trạm #1 dặn KHÔNG tự sửa test, nên để trạm #1 duyệt trước.
3. KHÔNG sửa code disconnect (đang đúng + không đổi từ v1.0) — sửa mù code đúng theo một lỗi
   không tái hiện là rủi ro thuần.

## Cổng release

Theo tiêu chí trạm #1: "test xanh khi chạy riêng" — trên trạm #2 **đang XANH ổn định**. Nhưng vì
trạm #1 quan sát ĐỎ, để trạm #1 nghiệm thu lại trước khi mở cổng `thansa-v1.1/v1.2`.
