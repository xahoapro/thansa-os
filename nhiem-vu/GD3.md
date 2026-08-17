# NHIỆM VỤ GĐ3 — Phát hành `thansa-v1.0`

Trạm #1 soạn · 2026-08-17 · cho trạm #2 (VPS). Tham chiếu: spec mục 5.1, 7 (GĐ3), 9.3.
Tiền đề (trạm #1 đã nghiệm thu): GĐ0–GĐ2b ĐẠT · `tests/run.py` **241/241** (pytest) · `tu-kiem-chung.py` XANH · sweep hiển thị/chat sạch · persona="Bạn là Thansa" · `so_patch=8`.
**P002 (logo) HOÃN** → v1.0 ship với logo upstream nhưng toàn bộ TEXT + CHAT = Thansa; logo để v1.1.

## 1. (Khuyến nghị) Smoke test sống trước khi tag
- Khởi động app, mở dashboard → tab/sidebar/login = "Thansa OS"; hỏi bot **"bạn là ai"** → tự xưng **"Thansa"**.
- Nếu không tiện chạy app: bỏ qua (đã verify tĩnh: persona + sweep + 241/241).

## 2. Cập nhật phiên bản (commit chore trên `me`)
- `ops/moc-goc.json`: `thansa_version: "1.0"` (nếu đang `1.0-dev`).
- `ops/so-tron.md`: thêm khối "Phát hành thansa-v1.0 (người bấm: quang, 2026-08-17). Rebrand P001–P010. P002 logo hoãn sang v1.1."
- (Tuỳ chọn dọn dẹp) xoá `nhiem-vu/HANH-DONG-NGAY.md` (đã moot).
```
git add -A && git commit -m "ops: chot phien ban thansa-v1.0 (so-tron + moc-goc)"
git push origin me
```

## 3. Phát hành — **NGƯỜI BẤM (chờ chủ duyệt)**
```
cd /home/thansa/thansa/thansa
git checkout release
git merge --ff-only me        # release tiến tới HEAD của me (ff-only, KHÔNG tạo merge commit)
git tag -a thansa-v1.0 -m "Thansa OS v1.0 — rebrand hien thi+chat (P001-P010), logo hoan v1.1"
git push origin release --tags
git checkout me               # quay về nhánh làm việc
```
- Nếu `merge --ff-only` báo lỗi "not fast-forward" → `me` và `release` đã phân kỳ, DỪNG và báo trạm #1 (không được tạo merge commit trên release).
- Nếu `git push` bị chặn quyền → chủ duyệt.

## 4. Nghiệm thu GĐ3 (spec mục 7)
- `git rev-parse origin/release` == `git rev-parse thansa-v1.0` == HEAD của `me`.
- Clone thử nhánh release ở thư mục khác:
```
git clone -b release https://github.com/xahoapro/thansa-os.git /tmp/test-release
cd /tmp/test-release && git log --oneline -1 && git describe --tags
```
  → thấy đúng HEAD + tag `thansa-v1.0`. `git pull --ff-only` chạy được (release chỉ tiến tới).
- Báo trạm #1 để nghiệm thu độc lập (đối chiếu sha + tag).

## 5. Sau v1.0
- **P002 logo**: khi chủ cấp `logo.png`+`favicon.png` Thansa → patch `[me] P002` → phát hành **v1.1**.
- **GĐ4**: gắn lịch cron dò hằng ngày + kênh báo cờ KHẨN.
- **GĐ5**: diễn tập một vòng trộn thật với bản cập nhật kế tiếp của upstream.
