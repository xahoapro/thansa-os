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
| 1.2.0  | 0.40.0    | `5bcc6f4`  | (chưa phát hành) | YouTube read, Shopify, Terminal đa tab; changelog song ngữ; dịch plugin + trang Chatbot; tách version Thansa + neo. Chờ gỡ chốt ws-disconnect. |
| 1.1    | 0.35.10   | (nhánh `release`) | 2026-08 | Bản Thansa OS đầu tiên phát hành (rebrand + EN). |
