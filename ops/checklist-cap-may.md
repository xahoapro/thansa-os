# Checklist cấp máy PHÁT TRIỂN / NGHIỆM THU Thansa

(Máy CHẠY app xem DAC-TA mục 5.2 — checklist này chỉ cho máy làm việc trên repo.)

1. Cài: git, python3.12+, node 22+, gh (đăng nhập), Claude Code CLI nếu là trạm AI.
2. Clone `xahoapro/thansa-os`, thêm remote `upstream` → `blogminhquy/javis-os`.
3. Dựng 2 worktree `goc` (main) / `thansa` (me); bật `git config rerere.enabled true`.
4. Trong `goc/`: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
5. **`goc/.venv/bin/pip install -r ../thansa/ops/requirements-dev.txt`** — pytest BẮT BUỘC
   để chạy đủ bộ test (thiếu là phase8/10/11/12 đỏ cứng `ModuleNotFoundError`).
6. Chạy `python3 tests/run.py` trong `goc/` → chuẩn xanh 241/241 (máy chậm: xem mục
   "Đã biết" trong `ops/so-tron.md` về `test_chat_disconnect.py`).
7. Bí mật (`.env`, `server/.secret_key`) theo từng máy, KHÔNG vào git; backup
   `.secret_key` ngoài git (mất là mất khoá API đã mã hoá).
