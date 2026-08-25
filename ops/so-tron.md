# Sổ trộn — thansa-os

Trả lời: "tôi đã đi qua những gì và vì sao quyết như vậy?" (DAC-TA mục 2.3).
Chỉ ghi thêm (append-only), KHÔNG sửa dòng cũ. Mỗi vòng trộn một khối, mới nhất dưới cùng.

## Khởi lập 2026-08-17 (chưa phải vòng trộn)

- GĐ0: dựng khung trên nền upstream `0b8f2c0` (VERSION 0.35.10), 0 patch. 3 nhánh
  main/me/release, 2 worktree goc/thansa, repo private `xahoapro/thansa-os`.
  Chuẩn xanh = CÓ pytest → 241/241. Không pytest → 240/241
  (`test_workflow_graph_phase10.py` lỗi `import pytest`). `test_chat_disconnect.py`
  nhạy timing (bản ghi sửa theo nhiem-vu/GD1-bosung.md; chi tiết ở mục "Đã biết").
- GĐ1: lập bộ hồ sơ ops/ (mốc gốc, mapping rỗng, sổ trộn) + bộ dò hằng ngày
  (`ops/do-hang-ngay.sh`) + tự kiểm chứng (`ops/tu-kiem-chung.sh`). Mapping sẽ có
  mục đầu tiên ở GĐ2 (P001–P006, rebrand).
- Chưa có vòng trộn nào. Vòng đầu tiên ghi khối kế tiếp theo mẫu DAC-TA mục 2.3.

## Đã biết (không phải lỗi của bản Thansa)

- `pytest` là DEV-DEPENDENCY BẮT BUỘC (chốt 17/08, nhiem-vu/GD1.md bản sửa sau nghiệm thu
  độc lập của trạm #1): 5 test Python `import pytest` ngay đầu file, thiếu là lỗi cứng
  `ModuleNotFoundError` chứ KHÔNG self-skip. Chuẩn "xanh" chính thức = CÓ pytest → 241/241.
  pytest ghi ở `ops/requirements-dev.txt` (upstream không khai vì requirements.txt của họ
  chỉ dành cho runtime). Đáng đề xuất upstream: bọc import bằng self-skip thật hoặc thêm
  file requirements dev.
- `test_chat_disconnect.py` NHẠY TIMING: chờ cứng `asyncio.sleep(0.08)` rồi đòi tin nhắn
  assistant đã ghi xong — chạy song song tải nặng có thể đỏ dù mã đúng (kiểm chứng 17/08:
  chạy riêng thì xanh; nâng chờ 2s ở bản nháp cũng xanh). Flaky thì chạy riêng để xác nhận.
  Không vá trong thansa-os (ngoài phạm vi rebrand); nếu muốn thì đề xuất upstream đổi
  sleep cứng thành poll.

## Quyết định của chủ 2026-08-17 (nghiệm thu GĐ1)

- CHẤP NHẬN chuẩn xanh GĐ1, gồm chuẩn riêng cho VPS: 240/241 + `test_chat_disconnect.py`
  đỏ do ngưỡng 80ms (số đo trong bao-cao/GD1.md). Máy nghiệm thu Windows vẫn kỳ vọng 241/241.
- P002 (logo + favicon): DÙNG TẠM ảnh mặc định của upstream, chưa thay. Patch P002 để
  lại đến khi chủ cung cấp ảnh Thansa; GĐ2 làm các patch còn lại.

## Vòng GĐ2 2026-08-17 — rebrand hiển thị (không phải vòng trộn upstream)

- 4 patch [me] trên nền `0b8f2c0`: P001 (fallback tên + mặc định settings.json trong
  server/config.py), P003 (chrome: title, brand topbar "THANSA OS", login, welcome/wizard,
  thẻ cập nhật, thông báo, release-noti), P004 (i18n vi/en, 9 giá trị), P005 (3 compose
  → ghcr.io/xahoapro/thansa-os:latest). so_patch = 4, tu-kiem-chung XANH cả 4 luật.
- P002 (logo/favicon) HOÃN theo quyết định chủ 17/08 — dùng tạm ảnh upstream.
- Hai chỗ suýt sót, bắt được nhờ smoke test + quét không phân biệt hoa thường:
  `server/config.py` `_DEFAULT["workspace_name"]` (thắng mọi fallback vì ghi vào
  settings.json) và `<span class="brand-text">JAVIS OS</span>` (viết HOA).
- Chuỗi "Javis" ĐỂ LẠI có chủ đích (tên trợ lý ở bề mặt cài đặt/chat + kỹ thuật):
  danh sách đầy đủ khai trong y_dinh của P003. Chờ chủ quyết vòng sau có đổi tên
  trợ lý hay không. TUYỆT ĐỐI không đụng watermark image_gen (test bám chuỗi).

## Vòng GĐ2b 2026-08-17 — rebrand triệt để hiển thị + chat (P007–P010)

- Quyết định chủ: BẤT CỨ chỗ nào hiển thị hoặc chat nói ra đều là "Thansa"; giữ internal.
- P007 (42 file): persona CORE_CONTRACT "Bạn là Thansa", mọi tin bot nói (Zalo/Telegram/
  STT/write-gate/lỗi runtime+orchestrator), cặp marker "# === NĂNG LỰC THANSA" đổi ĐỒNG BỘ
  main.py + context_runtime.py, 2 tiêu đề cửa sổ Windows.
- P008 (22 file): FastAPI title, OAuth client_name, codex title, nhãn Authenticator,
  X-Title, template vault, ~117 chuỗi UI dashboard. GIỮ: tên kỹ thuật hiển thị trong
  hướng dẫn (JAVIS_*, container javis, stop-javis.bat, lệnh javis login, path Javis/),
  "# Javis adaptive source contract" (contract id — test phase8 bám, không đổi).
- P009: BRAND_SOFTWARE="Thansa OS"; BỎ chunk Source (chưa có domain Thansa, không bịa).
- P010: app.js đúng 2 dòng fallback, sửa bằng thao tác byte (bẫy encoding), diff 2 dòng.
- NGOẠI LỆ TEST được phép (luật ưu tiên: test đồng bộ theo thay đổi brand có chủ đích,
  KHÔNG sửa logic test nào — chỉ chuỗi kỳ vọng Javis→Thansa), khai đủ trong mapping:
  fixture context_compiler_contract.json + test_image_gen (3 assertion) + 10 file test
  bám chuỗi bot nói/UI: bao_viec_ve_chat_web, bot_noi_nhu_nguoi, cli_kenh, codex_context,
  connect_health, engine_ngang_quyen, loi_ket_noi_google, muc_dung_moi, terminal_cmd_goc,
  trang_chatbot.js.
- Bài học quét: subagent grep bỏ sót readonly_orchestrator.py + chuỗi ghép nhiều dòng +
  test coupling kiểu "máy chạy Javis" — lưới cuối phải là quét AST string-literal và
  CHẠY full suite, đừng tin bản đồ grep.

## Phát hành thansa-v1.0 (người bấm: quang, 2026-08-17)

- Nền upstream `0b8f2c0` (VERSION 0.35.10) + 8 patch [me] rebrand P001–P010
  (P002 logo HOÃN sang v1.1, dùng tạm ảnh upstream; P006 = hồ sơ ops dạng chore).
- Nghiệm thu trước phát hành: tests 241/241 (pytest), tu-kiem-chung XANH cả 4 luật,
  sweep hiển thị/chat sạch, persona "Bạn là Thansa" — trạm #1 đã nghiệm thu độc lập
  (nhiem-vu/GD3.md mục tiền đề).
- release ← me (ff-only), tag thansa-v1.0.

## Vòng sau-v1.0 2026-08-17 — P011 + P012 (lệnh trực tiếp của chủ, chờ gộp phát hành v1.1)

- P011: footer "by Tradingauto.org" (link tradingauto.org) + 2 gợi ý lùi bản Docker
  trỏ đúng ghcr.io/xahoapro/thansa-os.
- P012: mô tả hiển thị còn sót → Thansa: CLAUDE.md (persona system prompt đầy đủ),
  SKILL.md 6 skill hệ thống, description/author plugin bundled, mcp-catalog.json,
  substack.html in-app. Ruột kỹ thuật giữ nguyên theo chốt của chủ ("giữ nhưng ẩn").
- Sự cố bắt được nhờ test: transform lỡ đổi literal đường dẫn "Javis" trong
  javis-schedule/plugin.py (Path(vault)/"Javis"/"loops") → đã trả lại; bài học:
  literal path một-từ không có dấu / cạnh nó, regex không tự phân biệt được —
  phải chạy full suite sau MỌI đợt đổi chuỗi, và soi diff từng dòng file logic.
- tests 241/241; tu-kiem-chung XANH; so_patch = 10; máy thử (/home/thansa/thansa-chay,
  nhánh me) đã chạy bản này cho chủ nghiệm thu bằng mắt.

## Phát hành thansa-v1.1 (người bấm: quang, 2026-08-18)

- v1.0 + P011 (footer Tradingauto.org, gợi ý image), P012 (mô tả hiển thị: system
  prompt/skill/plugin/catalog/docs in-app), P013 (BRAND_SOURCE = tradingauto.org).
- P002 (logo/favicon) VẪN hoãn — chưa có ảnh Thansa.
- Cổng phát hành: tests 241/241 + tu-kiem-chung XANH (so_patch=11) + chủ đã nghiệm thu
  bằng mắt trên máy thử.

## Vòng 2026-08-18 (goc 0b8f2c0 → a1ad69a, upstream +13 commit, VERSION 0.35.10 → 0.37.1)

- Giao với mapping: 9 patch dính vùng theo dõi (P001/P003/P007/P008/P009/P010/P011/
  P012/P013); ẢNH GỐC không lệch; không cờ bảo mật.
- Rebase 35 commit lên nền mới: 2 xung đột — P003 (upstream thêm meta viewport chặn
  zoom cạnh <title> → lấy tính năng upstream + giữ title Thansa), P012 (catalog thêm
  trường issue #112 → lấy nền upstream rồi chạy lại transform P012). rerere đã ghi.
- NEO LẠI P003 (2 lần, amend + cherry-pick range): upstream 0.36.x thêm 2 bề mặt tên
  app mới — meta apple-mobile-web-app-title (iOS) + dashboard/manifest.json (PWA
  Android) → "Thansa OS"/"Thansa". Khai bổ sung anh_goc trong mapping.
- Upstream thêm LICENSE MIT (74b14b4) → GỠ mục rủi ro "repo gốc không LICENSE" ở
  DAC-TA mục 8.
- File launcher mới "JAVIS OS.bat/.app", "Start/Stop JAVIS OS.command", bin/javis-*
  (Windows/macOS): CHƯA đụng — thuộc giai đoạn máy Windows/macOS (spec 5.2), ghi nhận
  chờ chủ quyết khi triển khai các máy đó.
- Test mới upstream test_ignore_files bắt 2 log bộ dò chưa ignore → thêm
  ops/ban-tin/*.log vào .git/info/exclude cục bộ.
- tests/run.py: XANH 247/247 (upstream thêm 6 test). tu-kiem-chung XANH. kiem_chung
  11 patch: XANH. so_patch = 11, mốc gốc a1ad69a (0.37.1).
- CHƯA phát hành — chờ chủ chạy thử bản me trên máy thử rồi bấm (dự kiến v1.2).

## Đã biết (bổ sung 18/08) — restart máy thử phải kiểm PID giữ cổng

Sự cố: sau khi cập nhật code máy thử, `pkill` theo pattern không khớp dòng lệnh thật
(tiến trình cũ chạy bằng đường dẫn tương đối `../.venv/...`) → server CŨ vẫn chiếm
cổng 7777, server mới bind thất bại âm thầm, curl vẫn HTTP 200 (vào server cũ) →
chủ nghiệm thu trên CODE CŨ mà không ai biết (18/08, vụ changelog "vẫn còn Javis").

Luật từ nay cho mọi lần cập nhật bản chạy thử/chạy tay (máy chạy thật dùng
update.sh + systemd/docker thì không dính):
1. Khởi động bằng ĐƯỜNG DẪN TUYỆT ĐỐI của venv.
2. Kill bằng pattern đầy đủ "uvicorn main:app --host ... --port ...".
3. Sau restart BẮT BUỘC xác minh: `ss -tlnp | grep <cổng>` — PID phải là tiến trình
   mới; đừng tin HTTP 200 (server cũ cũng trả 200).
4. Máy thử VPS: dùng sẵn `/home/thansa/thansa-chay/restart-thu.sh` (đã làm đủ 3 bước).

## Vòng ngôn ngữ Anh 2026-08-18 — P015 UI + docs EN (28/28)

- Chủ báo mục tiếng Anh thiếu (i18n gốc chỉ phủ 76 key, ~1130 chuỗi hiển thị còn
  cứng trong code). Không i18n-hoá từng chuỗi (diff diện rộng, xung đột mỗi vòng
  trộn) mà làm LỚP PHỦ dịch lúc hiển thị: P015 = dashboard/i18n/dich-en.js (đọc
  text node + attribute, thay khi khớp nguyên chuỗi, chỉ chạy ui_lang=en) +
  en-goi.json (1130 cặp việt→anh). Diff: 1 file JS + 1 file JSON + 1 dòng <script>.
- Tài liệu: docs/*.en.md cho cả 28 file (27 doc + README), commit dạng chore (file
  mới, 0 xung đột như ops/). Header song ngữ mỗi file.
- Cách làm: fan-out subagent HAIKU (rẻ, đúng ý chủ tiết kiệm token) — 6 lô UI + 7 lô
  docs. Sự cố: đợt 1 (13 subagent) chết đồng loạt do GIỚI HẠN PHIÊN tài khoản (reset
  5:10 UTC), nhưng 6 lô UI + 8 docs kịp ghi trước khi chết. Gộp UI (dich-1.json hỏng
  JSON do haiku thoát chuỗi sai ở mảnh regex → phục hồi bằng regex chịu lỗi, giữ
  190/191 cặp). Đợt 2 (quota mở lại) 5 subagent haiku dịch nốt 20 docs.
- Bài học: (1) subagent dịch dùng haiku tiết kiệm; (2) haiku dễ tạo JSON hỏng với
  chuỗi chứa code/regex — luôn có bước phục hồi khoan dung + validate; (3) giới hạn
  phiên tài khoản làm chết cả loạt subagent, nên commit phần xong sớm kẻo mất.
- so_patch = 13 (P015 là patch [me] thứ 13). Docs không cần mapping (additive).

## Vòng quét vét cạn ngôn ngữ Anh 2026-08-18 (chủ báo còn nhiều tiếng Việt)

- Vấn đề: lớp phủ P015 chỉ phủ chuỗi đã trích thủ công (~1130), còn sót nhiều chuỗi
  ghép động/template mà regex bỏ qua → trang Kết nối và nhiều nơi còn tiếng Việt.
- Cách làm (đúng đề xuất chủ "1 bot kiểm tra + 1 bot vá"): thả 11 bot HAIKU đọc thẳng
  source dashboard (console.js chia 4, app.js, chatbots/index.html, usage/chat-render,
  studio/dataview, sessions/voice/graph, editor/term/file/marks, các file nhỏ), mỗi bot
  VỪA nhận diện chuỗi hiển thị (LLM phân biệt câu hiển thị vs code tốt hơn regex) VỪA
  dịch, tách chuỗi ghép biến theo ${..}. Cộng 6 bot trước (catalog + UI sót).
- Từ điển en-goi.json: 1130 → 1833 (catalog+UI sót) → 2457 cặp (quét vét cạn). Phục hồi
  JSON khoan dung cho lô haiku hỏng; sửa Javis→Thansa trong mọi bản dịch; bỏ 19 key
  nghi là mảnh code.
- P016: vá app.js — P010 cố ý chỉ đụng 2 dòng nên còn 10 chuỗi hiển thị "Javis"
  (marker file-open, "Bắt đầu dùng Javis", "Javis đang suy nghĩ"...). Sửa byte-an-toàn;
  marker giờ khớp CLAUDE.md ("của Thansa:"). so_patch = 14.
- Bài học: overlay khớp-nguyên-text-node hợp cho chuỗi hoàn chỉnh; chuỗi ghép biến phải
  tách segment. Bot đọc source hiệu quả hơn regex để lọc code vs hiển thị.

## Vòng Option B 2026-08-18 — dịch sẵn source thay overlay (P017, chốt của chủ)

- Chủ chốt: dịch sẵn toàn bộ (rẻ + bảo trì đơn giản) thay overlay DOM. Nguyên nhân overlay
  sót đã chẩn đoán: (1) hộp thoại native alert/confirm/prompt ngoài DOM; (2) chuỗi ghép
  biến/nhiều dòng khó khớp text node; (3) attribute ngoài danh sách. Overlay đã vá 3 cái
  đó nhưng vẫn có trần → chuyển kiến trúc.
- P017: ops/build-en.py áp từ điển vào string literal (JS) + text node/attr (HTML), sinh
  dashboard/en/. AN TOÀN: kiểm "khung code y hệt" (bỏ mọi literal rồi so byte) + node --check
  mỗi file → chứng minh không đụng code. Server sinh en/ lúc khởi động (gitignore cục bộ,
  KHÔNG commit, mọi máy tự có), phục vụ theo cookie thansa_lang=en; file chưa dịch rơi về
  gốc + overlay. Client (dich-en.js + handler console.js) đặt cookie + reload khi đổi ngôn ngữ.
- Bảo trì: mỗi vòng trộn build-en chạy lại lúc khởi động, chỉ chuỗi MỚI cần dịch.
- 2 lỗi P017 đã vá: root() nhận request tùy chọn (test gọi trực tiếp); subprocess thêm
  winproc.kwargs_no_window() theo quy ước test_windows_no_console.
- Từ điển 2.474 → 2.580 cặp. tests 246/247 (chỉ chat_disconnect flaky). so_patch = 15.
- Overlay (P015) GIỮ làm lưới cho file/chuỗi chưa migrate; hai lớp cùng chạy không xung đột
  (overlay khớp key tiếng Việt, bản en/ đã là tiếng Anh nên overlay no-op).

## Vòng 2026-08-20 (goc a1ad69a → 41cd1ab, upstream +3 commit, VERSION 0.37.1 → 0.39.0)

- 3 commit: connector Shopify (MCP chuẩn UCP) + inject_args catalog; Terminal nhiều tab;
  fork nền trần wall-clock 1 giờ (env chỉnh).
- Rebase 69 commit lên nền mới: KHÔNG xung đột (rerere + thay đổi khác vùng). Mọi patch
  [me] sống, kiem_chung nhanh XANH (title/persona/brand).
- NEO LẠI (P020): Shopify catalog + ucp-agent-profile.json mang chuỗi hiển thị "Javis"
  mới (P012 chỉ đổi nội dung cũ) → rebrand Javis→Thansa các chuỗi mới.
- Dịch EN chuỗi mới: 3 client (terminal tabs) + 12 catalog (Shopify guide/risk). Dict
  2934 → 2949. Phần lớn chuỗi terminal tái dùng chuỗi cũ đã có.
- Test upstream mới: test_shopify_mcp, test_tran_wall_clock_nen, test_code_terminal.
- so_patch = 17 (thêm P020), mốc gốc 41cd1ab (0.39.0).
- Docs upstream đổi docs/09, docs/27 (+Shopify MCP, +terminal tabs) — docs/*.en.md
  tương ứng cần cập nhật phần mới (để lại, ưu tiên thấp).

## Vòng 2026-08 fork-only (P022–P027) — song ngữ, version riêng, rebrand bản quyền/tên

Không trộn upstream (giữ nền 0.40.0). Loạt patch [me] thêm, so_patch 19 → 24:

- **P022–P024 (song ngữ + i18n vét cạn):** Nhật ký cập nhật TỰ VIẾT song ngữ
  (`dashboard/changelog-thansa.json`, render theo `rel[lang]` — hợp luật lang_bat_bien);
  dịch trọn 471 version cũ sang EN + bake rebrand hiển thị; bổ sung từ điển EN cho 11
  plugin bundled + 9 cảnh báo mức quyền chatbot + 49 mẩu text-node `chatbots.js`
  (build-en tách theo `<b>`). en-goi.json 2949 → 3027.
- **P025 (version Thansa riêng + neo):** `VERSION` = `1.2.0-javis-0.40.0` — semver Thansa
  lái update + HIỂN THỊ (`1.2.0`), đuôi `-javis-<nền>` là NEO nội bộ (ẩn khỏi UI/tag ảnh).
  `_ver_thansa`/`_ver_javis`; changelog "đã cài" so theo NỀN javis. `GITHUB_REPO` →
  `xahoapro/thansa-os` (env `THANSA_UPDATE_REPO`). `moc-goc.thansa_version` = 1.2.0.
  Thêm `RELEASES.md` (sổ neo) + **tu-kiem-chung luật 5** (neo VERSION == goc_version).
- **P026 (bản quyền + link + tác giả):** LICENSE GIỮ copyright Nguyễn Minh Quý (MIT) +
  THÊM Duy Quang (thansa.org). javisos.com→thansa.org, minhquy.vn→tradingauto.org,
  Minh Quý→Duy Quang, blogminhquy/javis-os→xahoapro/thansa-os. `_rebrand_hien_thi` +
  changelog-thansa.json + website + link tài liệu. Giữ dữ liệu test/comment ví dụ.
- **P027 (tên sản phẩm docs):** Javis OS→Thansa OS trong README*/docs bằng regex
  `Javis(?![/A-Za-z_])` (giữ JAVIS_*/javis_*/Javis/ path). ~1261 chỗ, 37 file.
- **ws-disconnect:** `bao-cao/BUG-ws-disconnect.md` — KHÔNG tái hiện trên VPS (45+ lần xanh,
  đường code test giống hệt v1.0). Chờ trạm #1 gửi version thư viện + nghiệm thu.
- **Repo đã PUBLIC** → kênh update/CHANGELOG/ANNOUNCEMENTS chạy qua fork được.
- Suite 250/250 sau mỗi patch. so_patch = 24, mốc gốc 5bcc6f4 (0.40.0), thansa_version 1.2.0.

## Vòng 2026-08-25 (goc 5bcc6f4 → fac4746, upstream +7 commit, VERSION nền 0.40.0 → 0.43.2)

- 7 commit upstream: YouTube phụ đề (6 client InnerTube + yt-dlp, 0.41-0.42), vá tự-tin-sai +
  lệnh tự kiểm (0.42.0), đổi model giữa chừng KHÔNG mất mạch (0.42.1), Antigravity đấu MCP hub
  Javis vào `agy` (0.43.0), Telegram hiện ở thanh bên + file dán đọc mọi engine (0.43.1),
  dải việc nền + đồng hồ chờ phút/giờ (0.43.2).
- Rebase 88 commit (24 patch [me] + ghi chú) lên nền mới. Xung đột giải 3 chỗ (rerere ghi lại):
  P021 (youtube-read: giữ version/mô tả mới upstream + author Thansa), P025 (VERSION → neo
  `1.2.0-javis-0.43.2`), P027 (4 docs 02/10/16/20: lấy bản upstream mới + áp lại regex rebrand).
- NEO LẠI (P028): Antigravity 0.43.0 thêm nhãn trạng thái "tool của Javis" → "tool của Thansa"
  (console.js) + dịch EN. Các "Javis" khác của vòng là comment/định danh kỹ thuật (X-Javis-Vault,
  MCP key `javis`) — giữ.
- VERSION neo `1.2.0-javis-0.43.2` (thansa_version giữ 1.2.0 vì 1.2.0 chưa phát hành, chỉ đổi nền).
  moc-goc goc_commit fac4746, goc_version 0.43.2, so_patch 25. tu-kiem-chung 5/5 XANH.
- Test upstream mới: test_doc_file_dinh_kem, test_doi_model_lien_mach, test_phien_telegram_hien_o_thanh_ben.
  Suite 253/253 xanh (chat_disconnect xanh lần này).
- CÒN LẠI: 199 mẩu UI mới (upstream refactor dashboard nhiều) chờ dịch EN — build-en suy biến
  về tiếng Việt cho tới khi dịch, không vỡ.

## Đổi quy trình 2026-08-25 — MỘT MÁY, bỏ hai trạm

Chủ (Duy Quang) bỏ mô hình hai trạm. Nay một máy này làm trọn: giữ bản rebuild → trộn upstream
Javis → rebrand Thansa → tự đẩy `main` cho user. KHÔNG còn "trạm #1 nghiệm thu" → chốt ws-disconnect
kiểu chờ trạm #1 duyệt VÔ HIỆU (suite xanh trên chính máy phát hành là đủ). Cổng phát hành:
build/suite xanh → `push origin me:main` (ff) → CI build image → user cập nhật.

**Đã phát hành thansa 1.2.0 / nền Javis 0.43.2** (main = 03937f4, VERSION 1.2.0-javis-0.43.2,
image GHCR :1.2.0). Xem RELEASES.md.
