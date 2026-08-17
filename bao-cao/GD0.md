# BÁO CÁO GĐ0 — Dựng khung (trạm #2, VPS)

Ngày: 2026-08-17. Tham chiếu: DAC-TA-THANSA-OS.md mục 7 (GĐ0) + START-HERE.md bước 2.

## Việc đã làm

1. Clone upstream `blogminhquy/javis-os` → `/home/thansa/thansa/goc`, remote đặt tên `upstream`.
   - Commit nền: `0b8f2c0` — khớp nền khảo sát của đặc tả (v0.35.10).
2. Ba nhánh cùng đứng tại `0b8f2c0`:
   - `main` (track `upstream/main`, không commit)
   - `me` (worktree `/home/thansa/thansa/thansa` — file báo cáo này nằm ở đây)
   - `release`
3. Hai worktree chung một kho `.git`: `goc/` (main) và `thansa/` (me).
4. `rerere.enabled=true` (global, đã bật sẵn từ trạm Windows).
5. Repo private `origin = https://github.com/xahoapro/thansa-os` (repo do người tạo qua `gh repo create`, tài khoản `xahoapro`).
6. `.venv` tạo trong `goc/` + cài `requirements.txt` + cài thêm `pytest` (xem mục Vấn đề).

## Kết quả test (`python tests/run.py` trên bản gốc sạch)

- **Lần 1 (đúng cấu hình upstream, chưa có pytest): 241/241 XANH** — nhưng 5 test Python
  dạng pytest tự BỎ QUA khi thiếu pytest (in "bỏ qua: chưa cài pytest", exit 0).
- Sau khi cài pytest (để 5 test đó chạy thật): 240/241 — 4 test phase8/10/11/12 XANH thật,
  còn `test_chat_disconnect.py` ĐỎ ổn định.
- Điều tra `test_chat_disconnect.py`: test chờ `asyncio.sleep(0.08)` rồi đòi tin nhắn
  assistant đã ghi xong. Trên VPS này 0.08s không đủ. Thử bản sao (ngoài goc, không sửa
  goc) nâng chờ lên 2.0s → **XANH (1 passed)**. Kết luận: test nhạy timing, KHÔNG phải
  lỗi mã nguồn upstream.

## Vấn đề gặp và cách xử lý

- `pytest` không nằm trong `requirements.txt` upstream (dev dependency). Đã cài vào `.venv`
  để tăng độ phủ thật (4 test phase chạy thật thay vì tự bỏ qua). Đánh đổi: từ nay
  `test_chat_disconnect.py` sẽ đỏ chập chờn trên máy chậm/tải cao.
- Hai lệnh `gh repo create` và `git push` lần đầu bị bộ phân quyền của Claude Code chặn
  (đưa dữ liệu ra ngoài) → người vận hành tự bấm. Các push nhánh `me` về sau dự kiến bình thường.

## Việc để lại + lý do

- Push 3 nhánh lên `origin` lần đầu: chờ người vận hành bấm (đang chờ tại thời điểm viết).
- Chưa tạo `nhiem-vu/` (trạm #1 soạn) và `ops/` (việc của GĐ1).

## Đề xuất cho vòng sau

- GĐ1 nên đưa vào script tự kiểm chứng một quy ước về pytest: hoặc khai `pytest` trong
  tài liệu môi trường (env.thansa.example / checklist cấp máy), hoặc chấp nhận chuẩn
  "xanh" theo cấu hình upstream (không pytest). Trạm #1 + người quyết.
- `test_chat_disconnect.py` đáng báo lên upstream (nâng ngưỡng chờ hoặc poll thay vì
  sleep cứng) — không vá trong thansa-os vì ngoài phạm vi rebrand.
