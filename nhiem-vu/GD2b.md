# NHIỆM VỤ GĐ2b — Rebrand triệt để phần HIỂN THỊ + CHAT (P007–P010)

Trạm #1 soạn · 2026-08-17 · cho trạm #2 (VPS)
Quyết định của chủ (17/08): **đổi cả tên OS — BẤT CỨ chỗ nào HIỂN THỊ hoặc CHAT nói/hiện ra đều phải là "Thansa"** (sản phẩm = "Thansa OS", trợ lý tự xưng = "Thansa"). GIỮ NGUYÊN phần internal.
Nền: `me` @ `a78e898` (sau GĐ2, so_patch=4), `tu-kiem-chung.py` XANH, test 240/241 (chỉ `test_chat_disconnect` flaky).

## LUẬT phân loại (áp cho MỌI chuỗi "Javis"/"Javis OS")
- **REBRAND** nếu người dùng THẤY nó, hoặc CHAT nói/ghi nó ra: chuỗi UI, persona/hệ prompt, tin nhắn bot gửi (Zalo/Telegram/voice), tiêu đề/nhãn/tooltip/thông báo/lỗi hiển thị, tên client OAuth, nhãn Authenticator, brand nhúng vào ảnh, template ghi vào vault người dùng.
- **GIỮ** nếu chỉ máy đọc: biến `JAVIS_*` (49 file), tên thư mục, `javis.service`, tool `javis_*`, enum dữ liệu `source='javis'`, comment/docstring KHÔNG hiển thị, header kỹ thuật (tuỳ chọn — xem P008).
- Nghi ngờ một chuỗi có hiển thị không → mở app/đọc luồng để xác định, KHÔNG đoán.

## Bốn patch (mỗi patch 1 commit `[me]` + mục mapping 7 trường). P006 bỏ trống (ops đã là chore).

### P007 — Danh tính trợ lý → "Thansa" (CHAT nói)
- **`server/context_compiler.py:111`**: `Bạn là Javis, trợ lý agentic…` → `Bạn là Thansa, …` — **quan trọng nhất**, đây là persona khiến bot tự xưng.
- `server/stt.py:30,51,69,72,74`: chuỗi chèn vào chat khi xử lý voice ("Javis chưa nghe được…") → "Thansa …".
- `server/zalo_bot.py:377,387,419,426,617`: tin nhắn bot gửi người dùng Zalo ("… Javis không …", "bot Javis này") → "Thansa".
- **SWEEP đủ**: rà mọi chuỗi CHAT-facing còn lại chứa "Javis" (engine.py, context_runtime.py, aux_engine.py, telegram, các bộ prompt). Chỉ đổi chuỗi runtime bot NÓI/GHI; bỏ qua comment/docstring.
- kiem_chung: bot tự xưng "Thansa" (mở chat hỏi "bạn là ai"); `grep -rn "Javis" server/ --include=*.py | (lọc comment)` không còn chuỗi chat-facing.

### P008 — Chuỗi sản phẩm HIỂN THỊ ở server + UI còn sót → "Thansa OS"
- `server/oauth_mcp.py:245` `client_name` (màn OAuth MCP người dùng thấy).
- `server/codex_models.py:121` `"title"`.
- `server/main.py:114` `FastAPI(title="Javis OS")` (hiện ở /docs).
- `server/main.py:3837,3859` template ghi vào vault người dùng; `:4476` thông báo lỗi hiển thị ("Skill hệ thống của Javis OS").
- `server/totp.py:96` default `ten_workspace="Javis OS"` + `server/main.py:806` (nhãn Authenticator) → "Thansa OS".
- `dashboard/studio.js:639` tooltip badge "Skill hệ thống Javis OS".
- (TUỲ CHỌN, khuyến nghị) `server/engine.py:779,827,1659` header `X-Title: "Javis OS"` → "Thansa OS" (không test ràng buộc; đổi cho nhất quán).
- kiem_chung: các grep trên = 0; app khởi động; /docs hiện "Thansa OS".

### P009 — Brand nhúng ảnh (COUPLED TEST — phải sửa test kèm)
- `server/image_gen.py:114` `BRAND_SOFTWARE="Javis OS"` → `"Thansa OS"`; dòng 178 docstring + chuỗi domain `javisos.com`.
- **Giả định trạm #1 (báo nếu khác):** CHƯA có tên miền Thansa → **bỏ chuỗi `javisos.com`** khỏi metadata (hoặc để trống), KHÔNG bịa domain. Nếu bạn có domain Thansa, cấp để dùng.
- **BẮT BUỘC cập nhật `tests/python/test_image_gen.py:74`**: đang assert `b"javisos.com"` và `b"Javis OS"` trong ảnh → đổi theo brand mới (bỏ javisos.com, đổi "Thansa OS"). Đây là ngoại lệ được phép chạm test (luật ưu tiên #1: sửa test cho khớp thay đổi brand có chủ đích, ghi rõ ở `so-tron.md`).
- kiem_chung: `tests/run.py test_image_gen.py` XANH với brand "Thansa OS".

### P010 — app.js fallback (NGOẠI LỆ có kiểm soát — file "sửa dễ hỏng")
- `dashboard/app.js:80` và `:2100`: `… || "Javis OS"` (fallback workspaceName người dùng thấy) → "Thansa OS".
- ⚠️ **CẢNH BÁO**: app.js là file spec dặn "hạn chế đụng" + **bẫy encoding hỗn hợp** (grep báo "binary file matches"). CHỈ đổi đúng 2 string literal, giữ nguyên phần còn lại **byte-for-byte** (đừng để editor đổi encoding/EOL). Kiểm `git diff` chỉ có 2 dòng đổi.
- kiem_chung: app.js tải được (mở dashboard không lỗi console), workspaceName hiện "Thansa OS"; `git diff --stat` app.js đúng 2 dòng.

## GIỮ NGUYÊN (khẳng định lại)
- Biến `JAVIS_*`, thư mục, `javis.service`, tool `javis_*`, enum `source='javis'`, comment/docstring không hiển thị.
- `VERSION`, `CHANGELOG*`, `README*`. Không phát hành.
- **`dashboard/docs/`**: giả định KHÔNG rebrand vòng này (churn cao, ngoài luồng hiển thị chính). Báo nếu bạn muốn gồm docs.

## Kỷ luật + Tiêu chí ĐẠT
1. Mỗi patch 1 commit `[me]` + mapping đủ 7 trường (`anh_goc` chụp đoạn upstream trước sửa; `diem_neo` ký hiệu). `so_patch` 4 → 8. `tu-kiem-chung.py` XANH.
2. `tests/run.py` **241/241 với pytest** (test_image_gen đã cập nhật; `test_chat_disconnect` flaky-timing chấp nhận khi tải nặng — chạy riêng phải XANH). Không làm đỏ test nào khác.
3. **Sweep nghiệm thu**: `grep -rniE "javis os|bạn là javis|Javis (chưa|đã|không|nghe)" server/ dashboard/ --include=*.py --include=*.js --include=*.html` (lọc comment/docstring/vars) = 0 chuỗi hiển thị/chat.
4. Mở app: tab/sidebar/login/welcome/workspace/thông báo/thẻ cập nhật = "Thansa OS"; hỏi bot "bạn là ai" → tự xưng "Thansa".
5. Cập nhật `ops/so-tron.md` (khối GĐ2b, ghi rõ ngoại lệ test_image_gen + app.js) + `bao-cao/GD2b.md`. Push `me`.

## Hạn chót
Không gấp. Xong báo trạm #1 nghiệm thu (diff + kiem_chung + mở app + hỏi danh tính bot) trước khi phát hành `thansa-v1.0`.
