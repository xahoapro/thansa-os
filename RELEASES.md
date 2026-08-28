# Sổ phát hành Thansa OS (neo với Javis)

Thansa OS đánh version RIÊNG (semver: `MAJOR.MINOR.PATCH`), độc lập với số của Javis OS
(nền upstream). Mỗi bản Thansa vẫn dựng trên một bản Javis cụ thể — đó là **điểm neo**.

- **Nguồn sự thật của neo:** file `VERSION` mang dạng `<semver-thansa>-javis-<nền-javis>`
  (vd `1.2.0-javis-0.40.0`). Phần `-javis-...` là NEO nội bộ, **ẩn khỏi mọi chỗ người dùng
  thấy** (UI chỉ hiện `v1.2.0`, tag ảnh chỉ là `1.2.0`). `ops/moc-goc.json` giữ neo chính
  thức (`thansa_version` + `goc_version` + `goc_commit`).
- **So bản mới** dùng semver Thansa (hàm `ver_tuple` tự bỏ đuôi neo). **So "đã cài" trên trang
  Nhật ký** dùng phần nền Javis (changelog đánh số theo Javis).
- Mỗi lần phát hành: thêm một dòng vào bảng dưới, và cập nhật `VERSION` + `moc-goc.json` khớp nhau.

| Thansa | Nền Javis | Commit gốc | Ngày | Ghi chú |
|--------|-----------|------------|------|---------|
| 1.4.0  | 0.50.2    | `60830fa`  | 2026-08-28 | Trộn Javis 0.47→0.50.2: **bộ não Grok Build** (gói SuperGrok/X Premium+) thay Gemini CLI (Google đã ngắt hạng cá nhân), **hòm thư + thông báo đẩy trình duyệt**, ChatGPT tạo ảnh, đấu Hostinger, agent chọn đúng model mọi nhà cung cấp, Telegram giữ ngữ cảnh qua restart. System prompt sang tiếng Anh (tiết kiệm ~2.000 token/lượt, vẫn nói tiếng Việt với user). Rebrand chuỗi hiển thị mới. Còn 248 chuỗi UI chờ dịch EN (suy biến về tiếng Việt). |
| 1.3.0  | 0.47.2    | `78dff14`  | 2026-08-27 (đã phát hành) | Trộn Javis 0.43→0.47.2 (tự-học ra Agent/Workflow không đè, sync cả ảnh, banner Model + PWA cài desktop, trần tool 8→30 + phanh kẹt-vòng, gọn Vault). Dịch UI mới; vá test timing (dứt điểm ws-disconnect) + trần prompt. Phát hành qua **snapshot main** (ff cho user cũ). |
| 1.2.0  | 0.43.2    | `fac4746`  | 2026-08-25 (đã phát hành) | Trộn Javis 0.40→0.43.2 (YouTube phụ đề, đổi model giữ mạch, Antigravity MCP hub, Telegram sidebar); changelog song ngữ; dịch plugin/chatbot/UI mới; version Thansa riêng + neo; rebrand bản quyền/link/tác giả → Duy Quang. Đẩy `main`, image `:1.2.0`. |
| 1.1    | 0.35.10   | (nhánh `release`) | 2026-08 | Bản Thansa OS đầu tiên phát hành (rebrand + EN). |
