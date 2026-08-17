# BÁO CÁO GĐ2 — Rebrand hiển thị P001/P003/P004/P005 (trạm #2, VPS)

Ngày: 2026-08-17. Thi hành theo `nhiem-vu/GD2.md` + DAC-TA mục 6, 7 (GĐ2).
P002 hoãn theo quyết định chủ (dùng tạm logo upstream).

## Việc đã làm — 4 commit `[me]`, mỗi patch 1 commit + 1 mục mapping đủ 7 trường

| Patch | Commit | Nội dung |
|---|---|---|
| P001 | `[me] P001: fallback ten hien thi Thansa OS` | `env.example`, 3 fallback `server/main.py` (getenv /settings, 2FA issuer, settings general), 4 fallback `console.js`, và `server/config.py` `_DEFAULT["workspace_name"]` (xem mục Phát hiện) |
| P003 | `[me] P003: chrome san pham - ...` | `<title>`, brand topbar `THANSA OS`, alt logo sidebar, đăng nhập, wizard chào mừng (6 chuỗi), noti-sub, thẻ Cập nhật/Tổng quan (console.js), khung thông báo trống (notifications.js), thông báo release (main.py) |
| P004 | `[me] P004: i18n vi/en - ...` | 4 giá trị vi.json + 4 giá trị en.json (tổng 9 lần xuất hiện "Javis"), giữ nguyên key |
| P005 | `[me] P005: compose image ...` | 3 file compose → `ghcr.io/xahoapro/thansa-os:latest` |

`so_patch = 4`. Lịch sử `me` được dựng lại một lần bằng amend + cherry-pick (trước khi
push) để giữ đúng kỷ luật 1 patch = 1 commit sau 2 phát hiện muộn bên dưới.

## Phát hiện trong lúc thi công (nhờ smoke test thật, không chỉ grep)

1. **`server/config.py:_DEFAULT`** — bản đồ chuỗi của nhiệm vụ không có chỗ này, nhưng
   nó mới là nguồn `workspace_name` mặc định GHI VÀO `settings.json` lần khởi động đầu,
   nên thắng mọi fallback đã sửa: `/settings` vẫn trả "Javis OS" dù grep sạch. Bắt được
   vì khởi động server thật và gọi `/settings`. Đã gộp vào P001 + khai mapping.
2. **`<span class="brand-text">JAVIS OS</span>`** (index.html) — viết HOA nên grep
   "Javis OS" không bắt. Đã sửa thành `THANSA OS`, gộp vào P003; kiem_chung của P003
   đổi thành grep KHÔNG phân biệt hoa thường.

## Kết quả tiêu chí ĐẠT

1. `python3 ops/tu-kiem-chung.py` → XANH cả 4 luật (4 commit `[me]` = 4 mục mapping = so_patch). ✓
2. `tests/run.py` trên cây `me` (venv goc, có pytest): **240/241** — đỏ duy nhất
   `test_chat_disconnect.py` (chuẩn VPS đã được chủ chấp nhận 17/08, ghi sổ trộn).
   Không test nào đỏ thêm. Ghi chú: một lần chạy trung gian thấy `test_brains_dem.py`
   đỏ — nguyên nhân là tôi để server smoke-test chạy SONG SONG với suite trên cùng cây;
   tắt server chạy lại thì xanh (chạy riêng cũng xanh). Bài học vận hành đã ghi. ✓
3. `kiem_chung` 4 patch: grep P001 `|| "Javis OS"` = 0; P003 grep -i "javis os" trong
   index.html + notifications.js = 0; P004 grep -i javis 2 file i18n = 0, JSON hợp lệ;
   P005 grep image javis-os = 0. ✓
4. App chạy thật (uvicorn từ cây `me`, khởi động sạch): HTTP 200,
   `<title>Thansa OS</title>`, HTML trả về client 0 chuỗi "javis os" (mọi casing),
   `GET /settings` → `"workspace_name": "Thansa OS"`. ✓
5. Sổ trộn khối GĐ2 + báo cáo này + push `me`. ✓

## Chuỗi "Javis" để lại CÓ CHỦ ĐÍCH (chờ chủ quyết vòng sau)

- Tên TRỢ LÝ ở bề mặt cài đặt/chat: "giọng Javis", "Nói với Javis", "Cài đặt Javis",
  option engine "MCP Javis", ghi chú Telegram/mật khẩu, vault-banner, dom-intro
  (index.html), 2 chuỗi autostart Windows (console.js), FastAPI title, vault template,
  thông điệp skill hệ thống (main.py). Đổi hết tức là đổi TÊN trợ lý (đụng cả persona
  trong CLAUDE.md/system prompt của app) — vượt phạm vi rebrand hiển thị, cần chủ chốt.
- KỸ THUẬT không bao giờ đụng: `JavisBackground/JavisEditorCmds/JavisSessions`,
  `javis_*` tool, `JAVIS_*` env, watermark `image_gen.py` ("Javis OS"/javisos.com —
  `test_image_gen` bám chuỗi này, đổi là test đỏ), X-Title OpenRouter, OAuth
  client_name, clientInfo codex (định danh gửi dịch vụ ngoài — đổi cần cân nhắc riêng).

## Việc để lại + đề xuất

- P002: chờ ảnh logo/favicon Thansa từ chủ (không tự chế).
- Vòng sau cân nhắc: (a) quyết tên trợ lý (Javis giữ hay thành Thansa?); (b) GĐ3 tạo
  release `thansa-v1.0` khi trạm #1 nghiệm thu GĐ2 đạt; (c) workflow docker-publish
  của upstream sẽ tự đẩy `ghcr.io/xahoapro/thansa-os` khi push — cần bật GHCR cho repo.
