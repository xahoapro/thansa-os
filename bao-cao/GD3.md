# BÁO CÁO GĐ3 — Phát hành thansa-v1.0 (trạm #2, VPS)

Ngày: 2026-08-17. Thi hành theo `nhiem-vu/GD3.md`. Người bấm phát hành: quang
(lệnh trực tiếp "ok làm gđ 3" sau khi trạm #1 nghiệm thu GĐ2b đạt).

## Việc đã làm

1. Ghi chú về `nhiem-vu/HANH-DONG-NGAY.md`: file đó viết lúc trạm #1 chưa thấy GĐ2b
   trên origin (khoảng trống giữa lúc tôi làm xong và force-push). Thực tế GĐ2b đã
   push đủ từ trước — chính GD3.md xác nhận ĐẠT. Đã xoá file theo cho phép của GD3.
2. Chore chốt phiên bản (commit `a68882d`): khối "Phát hành thansa-v1.0" trong
   `ops/so-tron.md` (`moc-goc.json` đã đúng `thansa_version: "1.0"` từ GĐ1).
3. Phát hành:
   - `release` ← `me` fast-forward (dùng `git push . me:release` — tương đương
     `merge --ff-only`, không tạo merge commit, không phải checkout đổi worktree).
   - Tag `thansa-v1.0` (annotated) + tag mốc nền `thansa-v1.0-goc-0b8f2c0` (tuỳ chọn
     trong spec 1.3).
   - Push `origin release --tags`.

## Nghiệm thu (tiêu chí GD3 mục 4 + spec mục 7 GĐ3)

- `release` == `thansa-v1.0^{}` == `me` == `a68882d` (3 sha trùng). ✓
- Máy Linux "thứ hai" (clone mới từ GitHub, nhánh release, thư mục riêng):
  - `git log -1` = `a68882d`; `git describe --tags` = **thansa-v1.0**. ✓
  - `git pull --ff-only` → "Already up to date" (cơ chế update.sh dùng đúng lệnh này;
    phần restart docker/systemd của update.sh không chạy được trên máy thử vì không
    có container/service — đúng thiết kế, không phải lỗi). ✓
  - Venv mới + `pip install -r requirements.txt` sạch; server khởi động từ clone:
    `<title>Thansa OS</title>`, `/settings` → `"workspace_name": "Thansa OS"`. ✓

## Trạng thái sau v1.0

- `main` = gương upstream `0b8f2c0` · `me` = main + 8 patch [me] + hồ sơ ops/nhiem-vu/
  bao-cao · `release` = `me` tại thời điểm phát hành, chỉ tiến tới.
- Mọi máy chạy từ nay: clone `release`, cập nhật `git pull --ff-only` / `update.sh`.
  Lùi bản: checkout tag `thansa-v1.0`.

## Việc kế tiếp (theo GD3 mục 5)

- **v1.1**: chờ chủ cấp `logo.png` + `favicon.png` → patch `[me] P002`.
- **GĐ4**: cron chạy `ops/do-hang-ngay.sh` hằng ngày + chốt kênh báo cờ KHẨN
  (Telegram/email — điểm để ngỏ số 1 của spec mục 10).
- **GĐ5**: diễn tập vòng trộn thật với bản cập nhật kế tiếp của upstream (nhịp
  hiện tại 9–23 commit/ngày — sẽ không phải chờ lâu).
