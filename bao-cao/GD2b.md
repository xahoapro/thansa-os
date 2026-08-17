# BÁO CÁO GĐ2b — Rebrand triệt để hiển thị + chat, P007–P010 (trạm #2, VPS)

Ngày: 2026-08-17. Thi hành theo `nhiem-vu/GD2b.md`. Khảo sát bằng 3 subagent song song
(server / dashboard / test-coupling) theo chỉ đạo của chủ, trạm chính tổng hợp + thi công.

## Việc đã làm — 4 commit `[me]`, so_patch 4 → 8

| Patch | Phạm vi thật (rộng hơn bản đồ nhiệm vụ nhờ sweep) |
|---|---|
| P007 | 42 file: persona `CORE_CONTRACT` ("Bạn là Thansa"), khối context (channel_context, compaction, learn, tasks, self_improve), tin bot Zalo/Telegram/STT, thông báo write-gate + lỗi các *_path_runtime + **readonly_orchestrator.py** (subagent quét sót, bắt lại bằng AST), antigravity/connect_health/cred_exchange/mcp_hub…, 2 tiêu đề cửa sổ Windows (claude_cli). Cặp marker `# === NĂNG LỰC THANSA` đổi đồng bộ main.py + context_runtime.py. Kèm fixture test + 7 file test bám chuỗi bot nói (cùng lớp ngoại lệ #1). |
| P008 | 22 file: FastAPI title (/docs), OAuth client_name, codex clientInfo title, nhãn Authenticator (totp default + issuer), X-Title OpenRouter, template ghi vào vault (Memory index, Javis/README, AGENTS.md seed, Vault Schema meta_tools, .gitignore header), ~117 chuỗi UI dashboard (console/usage/branding/chatbots/code-term/mobile-chat/studio/index/voice-test/style.css) + subdomain ví dụ. Kèm 3 file test bám nhãn UI (engine_ngang_quyen, muc_dung_moi, trang_chatbot.js). |
| P009 | `BRAND_SOFTWARE="Thansa OS"`; **bỏ chunk Source** (chưa có tên miền Thansa — không bịa); docstring; câu mô tả console.js; 3 assertion `test_image_gen.py` (ngoại lệ #2). |
| P010 | app.js đúng 2 dòng fallback, sửa bằng THAO TÁC BYTE (giữ nguyên encoding hỗn hợp), `git diff` = 2 dòng, `node --check` OK. |

## Danh sách GIỮ (đúng LUẬT phân loại — trạm #1 đối chiếu khi nghiệm thu)

- Kỹ thuật: `JAVIS_*`, tool `javis_*`, header `X-Javis-*`, enum `source='javis'`,
  path `Javis/`, tên container/service `javis`, `stop-javis.bat`/`start-javis.vbs`,
  lệnh `javis login`, localStorage `javis.*`, định danh JS `Javis*`, sentinel
  `JAVIS-STDIN-OK-7413`, User-Agent `javis-os/0.3`, tiền tố file `javis-img`,
  contract id `javis-core-contract-v1`.
- **Tên kỹ thuật hiển thị TRONG HƯỚNG DẪN giữ nguyên có chủ đích** (đổi là hướng dẫn
  thành sai): "container javis", "docker compose logs javis", `JAVIS_ADMIN_*`…
- `"# Javis adaptive source contract"` (main.py:471): `test_adaptive_context_phase8:251`
  bám chuỗi này; xếp là CONTRACT ID kỹ thuật, không đổi — tránh ngoại lệ test thứ ba.
- Git author "Javis Learn"/"Javis Sync" (git_brain): tên committer trong repo backup
  brain — máy đọc là chính; đổi sẽ lệch lịch sử backup. Giữ, chờ chủ quyết.
- Link `javisos.com` + 2 link GitHub `blogminhquy/javis-os` trong index.html (tài liệu
  tham khảo upstream) và `dashboard/docs/`, `CLAUDE.md`, `README*`: ngoài phạm vi vòng
  này theo nhiệm vụ. LƯU Ý cho trạm #1: CLAUDE.md dòng đầu vẫn "Bạn là **Javis**" —
  nó là prompt cho engine CLI đọc repo; persona runtime đã đổi ở CORE_CONTRACT, nhưng
  nếu muốn triệt để thì cần quyết rebrand CLAUDE.md (file churn cao) ở vòng sau.

## Kết quả tiêu chí ĐẠT

1. `tu-kiem-chung` XANH cả 4 luật: 8 commit `[me]` = 8 mục mapping = `so_patch: 8`. ✓
2. Test: full suite **241/241 XANH** (243 giây — kể cả `test_chat_disconnect` qua được
   ngưỡng vì máy nhẹ tải). Trước đó lần chạy đầu sau P007–P010 lộ **10 test đỏ** do bám
   chuỗi bot nói/UI (lớp coupling subagent test đã quét sót) — tất cả được đồng bộ
   Javis→Thansa (CHỈ chuỗi kỳ vọng, không đổi logic test) và gộp vào đúng patch
   tương ứng: 7 file vào P007, 3 file vào P008. Danh sách đủ trong sổ trộn + mapping.
3. Sweep: AST scan string-literal server (loại docstring) chỉ còn đúng danh sách GIỮ;
   HTML trả về client: 0 chuỗi "javis" hiển thị (12 mục còn lại đều kỹ thuật: định danh
   JS, key localStorage, tên file thật, env, link tham khảo). ✓
4. App chạy thật: `<title>Thansa OS</title>`, `/docs` = "Thansa OS - Swagger UI",
   `/settings` khởi động sạch = "Thansa OS". Persona: fixture + CORE_CONTRACT khớp
   "Bạn là Thansa" (test phase4 xanh); trạm #1 nghiệm thu bằng cách hỏi bot thật. ✓
5. Sổ trộn khối GĐ2b (ghi 2 ngoại lệ test + bài học AST) + báo cáo này + push. ✓

## Bài học vận hành (đã ghi sổ trộn)

- Subagent quét grep bỏ sót `readonly_orchestrator.py` và lệch số dòng vài file →
  lưới cuối phải là quét AST string-literal, không tin grep đơn thuần.
- Chuỗi ghép nhiều dòng (adjacent string concat) làm whitelist theo dòng hụt —
  AST bắt được vì nó thấy cả hằng gộp.
- Sự cố suýt mất patch (đã khắc phục, minh bạch để trạm #1 soát): trong một vòng
  amend, lấy SHA bằng `grep "P010"` khớp nhầm cả commit nhiệm vụ (subject chứa
  "P007-P010") → cherry-pick gãy âm thầm, P009+P010 rơi khỏi nhánh; tự kiểm chứng
  vẫn XANH vì mapping cùng trạng thái cũ (luật 1 không phát hiện được "patch chưa
  từng vào nhánh"). Phát hiện nhờ SOÁT LOG trước khi kết thúc, khôi phục từ reflog,
  suite 241/241 chạy lại trên cây hoàn chỉnh. Bài học: sau mọi thao tác viết lại
  lịch sử phải `git log main..me` đối chiếu ĐẾM patch bằng mắt, và lấy SHA bằng
  match đầu-chuỗi subject chứ không grep tự do.

## Đề xuất

- GĐ3 (chờ trạm #1 nghiệm thu + chủ ra lệnh): release `thansa-v1.0`.
- Chủ quyết vòng sau: rebrand CLAUDE.md + dashboard/docs/ + README (churn cao);
  đổi git author "Javis Learn/Sync"; domain Thansa cho BRAND_SOURCE.
