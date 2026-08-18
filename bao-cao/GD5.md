# BÁO CÁO GĐ4 + GĐ5 — Cron/kênh KHẨN + diễn tập vòng trộn thật (trạm #2, VPS)

Ngày: 2026-08-18. GĐ4-GĐ5 theo lệnh trực tiếp của chủ (chưa có nhiem-vu/GD4-5.md).

## GĐ4 — HOÀN THÀNH (một tiêu chí cần thời gian)

- Cron: `0 23 * * * UTC` (= 06:00 giờ VN) chạy `ops/cron-do-hang-ngay.sh` → bộ dò +
  log `ops/ban-tin/cron.log`. Exit 2 (CỜ KHẨN) → `ops/bao-khan.sh` gửi **Telegram**
  (kênh chủ chốt 18/08). Secret ở `/home/thansa/.thansa-alert.env` (chmod 600,
  NGOÀI git); thiếu secret thì cảnh báo ghi `khan-chua-gui.log`, không mất.
- Đã bắn thử Telegram thật: chủ nhận được tin. Pipeline chạy tay 1 lần ra bản tin
  chuẩn. Tiêu chí "bản tin tự sinh 3 ngày liên tiếp" sẽ tự tích luỹ (kiểm sau 3 ngày).

## GĐ5 — vòng trộn thật 0.35.10 → 0.37.1 (+13 commit, 42 file, +1618/-62)

Đúng 8 bước mục 4 của đặc tả:

| Bước | Kết quả |
|---|---|
| 1 Tự kiểm chứng | XANH trước trộn |
| 2 main ← upstream | `a1ad69a` (0.37.1); bản tin dò: 9 patch dính vùng theo dõi, ảnh gốc KHÔNG lệch, không cờ bảo mật |
| 3 Rebase me | 35 commit, **2 xung đột** (P003, P012), rerere đã ghi cách giải |
| 4 Phân ô | Ô (i): P004/P005/P006-chore. Ô (ii): P001/P007–P011/P013 — replay sạch, kiem_chung XANH. Ô (iii)-nhẹ: P003 + P012 — neo còn nguyên nhưng phải hoà với thay đổi cạnh bên + NEO LẠI 2 bề mặt mới (chi tiết dưới) |
| 5 Duyệt | Diễn tập theo lệnh chủ; các quyết định ô (iii) liệt kê dưới đây để chủ/trạm #1 soát lại — có gì không ưng tôi làm lại được (me chưa phát hành) |
| 6 Thi hành | Xong trong rebase + 2 lần amend P003 |
| 7 Nghiệm thu | `tests/run.py` **247/247 XANH** (upstream thêm 6 test); tu-kiem-chung XANH; kiem_chung 11 patch XANH |
| 8 Sổ trộn | Khối "Vòng 2026-08-18" đã ghi. CHƯA phát hành — chờ chủ chạy thử + bấm |

### Các quyết định ô (iii) cần chủ/trạm #1 soát

1. **P003 × meta viewport**: upstream thêm meta chặn zoom mobile ngay cạnh `<title>`
   → lấy tính năng upstream + giữ title "Thansa OS" (hiển thị → Thansa thắng, luật 4.1#2).
2. **P012 × catalog issue #112**: upstream thêm trường `needs_local_browser` cạnh mô tả
   đã rebrand → lấy nguyên bản catalog mới rồi CHẠY LẠI transform P012 (replay theo ý
   định) — text mới của upstream cũng thành Thansa luôn.
3. **NEO LẠI P003** (2 bề mặt tên app upstream 0.36.x mới thêm): meta
   `apple-mobile-web-app-title` (iOS màn hình chính) + `dashboard/manifest.json`
   (PWA Android) → "Thansa OS"/"Thansa". Mapping đã khai bổ sung anh_goc.
4. **test_ignore_files** (test mới upstream) bắt 2 log bộ dò → thêm `ops/ban-tin/*.log`
   vào `.git/info/exclude` cục bộ (không đụng .gitignore upstream).

### Ghi nhận cho vòng sau

- **Upstream thêm LICENSE MIT** → mục rủi ro cuối trong DAC-TA mục 8 đã được gỡ.
- File launcher mới `JAVIS OS.bat/.app`, `Start/Stop JAVIS OS.command`, `bin/javis-*`:
  CHƯA đụng (giai đoạn máy Windows/macOS theo spec 5.2). Khi triển khai các máy đó
  cần chủ quyết có đổi tên file hiển thị không (đổi tên file = patch nặng hơn đổi chuỗi).
- Đo thời gian thật của vòng trộn (mục 10.2 spec): ~40 phút gồm 2 xung đột + 2 lần
  neo lại + 3 lượt chạy suite; công sức người cần: duyệt các quyết định ở trên.

## Trạng thái + việc chờ

- Máy thử (100.122.173.30:7777) đang chạy nhánh `me` bản trộn — chủ nghiệm thu thực tế
  (spec khuyến nghị 1–3 ngày cho bản nền nhảy 2 minor).
- Đạt → chủ bấm phát hành **thansa-v1.2** (nền 0.37.1 + 11 patch).
- P002 logo: vẫn chờ ảnh.
