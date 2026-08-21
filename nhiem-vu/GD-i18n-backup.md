# NHIỆM VỤ (patch lẻ) — i18n hoá dòng cảnh báo backup (trang Sao lưu / Self-learning)

Trạm #1 soạn · 2026-08-21 · cho trạm #2 (VPS). Queue vào vòng patch kế (KHÔNG chặn phát hành v1.1).
Bối cảnh: dòng cảnh báo ở `dashboard/console.js:2170` đang **hardcode tiếng Việt** → user giao diện tiếng Anh vẫn thấy tiếng Việt. Đưa vào i18n để hiển thị đúng ngôn ngữ.

## Việc (1 commit `[me]` P<kế tiếp, vd P024> + mục mapping 7 trường)
1. Thêm key i18n vào `dashboard/i18n/vi.json` **và** `en.json` (giữ đúng cơ chế i18n hiện có — xem `dashboard/i18n/index.js` + cách các chuỗi khác gọi):
   - key gợi ý: `backup.warn.brain_private`
   - **vi**: `Brain có thể chứa số liệu/thông tin cá nhân — CHỈ dùng repo Private. Token lưu nội bộ (không đẩy lên repo).`
   - **en**: `Your brain may contain personal data — use a PRIVATE repo ONLY. The token is stored locally and never pushed to the repo.`
2. Ở `dashboard/console.js:2170`, thay chuỗi hardcode bằng lời gọi i18n (`t("backup.warn.brain_private")` hoặc đúng hàm dịch mà file này đang dùng).
   - Nếu scope chỗ đó KHÔNG gọi được hàm dịch (ngoài phạm vi i18n runtime) → DỪNG, báo trạm #1 để chọn cách khác (đừng ép).

## Ràng buộc
- Chỉ đụng `dashboard/i18n/vi.json`, `en.json`, `dashboard/console.js` (đúng 1 dòng warn). KHÔNG đụng logic backup, KHÔNG đổi key i18n có sẵn.
- Giữ nguyên nghĩa; đây là chuỗi HIỂN THỊ (đã theo tinh thần Thansa — không có "Javis").

## kiem_chung (mapping)
- Đổi UI sang **English** → dòng cảnh báo hiện tiếng Anh; đổi **Tiếng Việt** → hiện tiếng Việt.
- `grep -n "Brain có thể chứa" dashboard/console.js` = 0 (đã rời sang i18n); key `backup.warn.brain_private` có trong cả vi.json + en.json.

## Tiêu chí ĐẠT
- `tu-kiem-chung.py` XANH (so_patch +1). `tests/run.py` vẫn XANH (không đụng test).
- Ghi `ops/so-tron.md` + cập nhật `bao-cao` vòng đó. Push `me`. Báo trạm #1 nghiệm thu → gộp vào bản phát hành kế (v1.2 hoặc bundle).
