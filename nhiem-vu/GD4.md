# NHIỆM VỤ GĐ4 — Cron DÒ hằng ngày + báo Telegram (KHÔNG auto-update)

Trạm #1 soạn · 2026-08-21 · cho trạm #2 (VPS). Tham chiếu: spec mục 3 (bộ dò hằng ngày), mục 10.1 (kênh báo).
**Chốt của chủ (21/08):** cron **CHỈ kiểm tra + báo**. KHÔNG tự trộn / update / đồng bộ / phát hành. Có bản mới → báo Telegram; việc trộn vẫn làm THỦ CÔNG qua quy trình 2 trạm (kiểm tra + đấu nối như GĐ2/2b/3). Lý do: rủi ro lệch cao, khó kiểm soát.

## Phạm vi (chỉ 2 việc)
1. **Gắn lịch** chạy `ops/do-hang-ngay.py` mỗi ngày 1 lần.
2. **Báo Telegram** khi bản tin ngày đó có upstream commit mới (>0) HOẶC cờ KHẨN bảo mật.

## RANH GIỚI CỨNG — cron TUYỆT ĐỐI KHÔNG
- `git merge` / `rebase` / `checkout release` / `pull` vào nhánh làm việc / cập nhật code / đồng bộ / tag / phát hành.
- Cron chỉ: `git fetch upstream` (không đụng worktree) → so `anh_goc`/`vung_theo_doi` → quét từ khoá bảo mật → ghi `ops/ban-tin/YYYY-MM-DD.md` → (nếu có gì) báo Telegram. Hết.

## 1. Lịch (login-independent — KHUYẾN NGHỊ crontab)
- `crontab -e` của user `thansa`, thêm 1 dòng chạy hằng ngày (vd 07:30):
  ```
  30 7 * * *  cd /home/thansa/thansa/thansa && /usr/bin/python3 ops/do-hang-ngay.py >> /home/thansa/thansa/thansa/ops/cron.log 2>&1
  ```
  (crontab chạy bất kể đăng nhập; systemd --user timer thì phải `loginctl enable-linger thansa` — nếu chọn timer thì nhớ bật linger.)

## 2. Báo Telegram
- **Bí mật KHÔNG vào git** (mục 5.3): tạo `ops/.telegram` chứa `BOT_TOKEN=...` và `CHAT_ID=...`. THÊM `ops/.telegram` vào `.gitignore`.
- Chủ cấp token+chat_id (tạo bot qua @BotFather; chat_id qua @userinfobot), HOẶC tái dùng bot Telegram sẵn có của app nếu tiện.
- Viết `ops/bao-telegram.py` (hoặc hàm trong do-hang-ngay): đọc `ops/.telegram`, gửi qua `https://api.telegram.org/bot<TOKEN>/sendMessage`.
  - Gọi ở CUỐI do-hang-ngay: nếu (commit mới > 0) hoặc (cờ KHẨN) → gửi. Nếu +0 commit → **im lặng** (không gửi).
  - Nội dung tin: `Thansa OS — upstream +<n> commit (<sha cũ>→<mới>), VERSION <cũ>→<mới nếu đổi>. Cờ KHẨN: <có/không>. Bản tin: <tên file>.`
  - Thiếu `ops/.telegram` → log cảnh báo, VẪN ghi bản tin (không crash).

## Tiêu chí ĐẠT
1. `crontab -l` (thansa) thấy job daily; chạy tay `python3 ops/do-hang-ngay.py` → bản tin sinh đúng định dạng, cron.log ghi được.
2. **Test Telegram sống**: chạy `python3 ops/bao-telegram.py "test GD4"` (hoặc giả lập bản tin có commit) → **chủ nhận được tin trên Telegram**.
3. Xác nhận cron KHÔNG đụng nhánh nào: sau khi chạy, `git status` sạch, `git rev-parse me/release` không đổi. `ops/tu-kiem-chung.py` vẫn XANH.
4. `ops/.telegram` KHÔNG bị commit (`git status` + `.gitignore` có nó). Ghi `ops/so-tron.md` + `bao-cao/GD4.md`.

## Quy trình khi CÓ bản mới (thủ công — KHÔNG đổi)
Chủ nhận báo Telegram → tự quyết trộn hay không → nếu trộn thì ra lệnh cho trạm #2 theo đúng quy trình 2 trạm: `nhiem-vu/` → thi công (rebase + neo lại) → `bao-cao/` → trạm #1 nghiệm thu độc lập → **chủ bấm** phát hành. Không có bước tự động.

## Cần chủ cấp
- **Telegram bot token + chat_id** (hoặc xác nhận tái dùng bot của app). Trạm #1 sẽ chuyển vào `ops/.telegram` trên VPS (không qua git).
