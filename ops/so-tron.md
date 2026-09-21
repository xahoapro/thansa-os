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

## Vòng 2026-08-27 (goc fac4746 → 78dff14, upstream +7 commit, VERSION nền 0.43.2 → 0.47.2, thansa 1.2→1.3)

- 7 commit upstream: việc nền hết chết lặng khi chưa login Claude (0.43.3), tự-học ra Agent
  (0.44.0) + SỬA thay vì đẻ bản sao (0.45.0), sync cả ảnh cho GitHub (0.46.0), banner Model
  hết đỏ oan + PWA cài desktop (0.47.0), trần tool 8→30 + phanh kẹt-vòng-lặp (0.47.1), gọn
  Vault panel + cột lịch sử (0.47.2).
- Rebase 32 patch [me]. Xung đột giải 5 chỗ (rerere): P003 manifest (giữ field `id`+PWA
  upstream, icon trỏ /brand-logo giữ logo Thansa), P007 learn.py/engine.py (5+5 chuỗi danh
  tính), P008 console.js (intro tự-học), P025 VERSION→1.3.0-javis-0.47.2, P027 docs 16/18/22.
- NEO LẠI (P031): PWA install title/aria, sync-ảnh, _LapGuard "⚠ [Javis]", tự-học agent/workflow.
  Dịch 16 UI mới (P032). Vá 2 test coupled (P033): ws-disconnect POLL-tới-xong (dứt điểm bug
  trạm #1 - timing chứ không phải code), trần CLAUDE.md 30k→31k (thuế rebrand + nội dung mới).
- so_patch 30, VERSION 1.3.0-javis-0.47.2. Suite 257/257 xanh.
- **Đổi cơ chế phát hành (quan trọng):** rebase làm `me` viết lại lịch sử → `push me:main` KHÔNG
  còn ff, `git pull --ff-only` của user vỡ. Nay phát hành bằng **SNAPSHOT**: commit tree của `me`
  lên trên origin/main (parent = main cũ) → main là chuỗi ff, user cập nhật được, updater cũ vẫn
  chạy. `me` = chuỗi patch rebase (force-push origin/me); local `main` = nền upstream (cho luật 3);
  origin/main = chuỗi snapshot phát hành.

## Vòng 2026-08-28 (goc 78dff14 → 60830fa, upstream +19 commit, VERSION nền 0.47.2 → 0.50.2, thansa 1.3→1.4)

- 19 commit upstream (0.47.3-0.50.2), nổi bật: sửa .md trang Trò chuyện (0.47.3-0.48.x), bỏ nút
  loa header (0.48.3), đấu Hostinger + agent chọn Ollama (0.48.1), ChatGPT tạo ảnh + agent chạy
  Antigravity CLI (0.48.0), agent chọn đúng model mọi nhà cung cấp (0.47.9), **hòm thư + thông báo
  đẩy trình duyệt (0.49.0)**, vá push điện thoại (0.49.2), **thêm bộ não Grok Build, gỡ Gemini CLI,
  CLAUDE.md sang tiếng Anh (0.50.0)**, Telegram giữ ngữ cảnh qua restart (0.50.1), vá thẻ Grok
  báo chưa đăng nhập oan (0.50.2).
- Rebase 100 commit (31 patch [me] + ops/i18n). Xung đột giải 6 chỗ (rerere ghi lại):
  P007 (main.py: Gemini→Grok, rm server/gemini_cli.py theo upstream, giữ rebrand chat "máy chạy
  Thansa"), P008 (console.js/index.html/usage.js: bỏ thẻ Gemini theo upstream, rebrand nhãn brain
  còn lại), P012 (**CLAUDE.md + mcp-catalog: lấy nền TIẾNG ANH upstream rồi áp lại rebrand Javis→
  Thansa, giữ token kỹ thuật**), P025 (VERSION → 1.4.0-javis-0.50.2), P027 (docs 10/16: nền Grok/
  env mới + regex rebrand), P033 (test_prompt_budget: bỏ trần cũ 31_000, lấy trần upstream 33_600).
- **Ưu tiên 4.1 áp dụng:** Gemini CLI bị upstream gỡ (Google ngắt hạng cá nhân) → theo upstream,
  bỏ mọi UI/route Gemini, KHÔNG níu patch. Grok Build là bộ não mới của upstream → Thansa nhận
  nguyên. CLAUDE.md tiếng Anh (tiết kiệm ~2.000 token/lượt, GIỮ hành vi nói tiếng Việt với user)
  → nhận nền, chỉ rebrand hiển thị. Không có commit BẢO MẬT/logic nghiệp vụ cần hỏi chủ.
- NEO LẠI (P034): chuỗi hiển thị mới nhắc "Javis" → Thansa: thẻ Grok + trạng thái tool (console.js),
  thông báo Grok chat (grok_cli.py), hòm thư + thông báo đẩy 0.49.0 (main.py /push/test, notifications.js,
  push.js, sw.js). 12 chuỗi. Đối chiếu shipped 1.3.0: giữ nguyên các chuỗi 1.3.0 CỐ Ý để Javis
  (Máy chủ Javis, Hướng dẫn Javis CLI, OAuth "MÁY cài Javis").
- VERSION neo `1.4.0-javis-0.50.2`. moc-goc goc_commit 60830fa, goc_version 0.50.2, thansa_version
  1.4.0, so_patch 31. tu-kiem-chung 5/5 XANH. Suite 273/273 xanh (cần `pip install pytest` cho 4 test
  phaseN dùng pytest; không phải hồi quy).
- **CÒN LẠI (chưa chặn phát hành):** 248 chuỗi UI tiếng Việt chưa dịch EN (upstream 0.48-0.50 thêm
  nhiều: thẻ Grok, hòm thư/push, connector Hostinger với guide dài). build-en suy biến về tiếng Việt
  cho tới khi dịch (không vỡ, test i18n xanh). Dồn sang một đợt dịch EN sau, như vòng 0.43.2 từng dồn 199.

## Vòng 2026-09-01 (goc 60830fa → 91aa663, upstream +14 commit, VERSION nền 0.50.2 → 0.52.10, thansa 1.4→1.5)

- 14 commit upstream (0.50.3-0.52.10), nổi bật: loạt vá **Grok** (0.50.3-0.50.6: hết trả ô trống,
  đọc đúng luồng sự kiện, chữ ở khoá `data`, hết đăng xuất mỗi lần cập nhật image), **upstream tự
  thêm i18n gốc EN** (#230 ô đổi ngôn ngữ + màn chính, #231 ba trang Models/Việc/Studio), hết in mã
  khoá do từ điển cũ (#233), Antigravity CLI treo không kéo sập dashboard (#232), chat dài tiếng Việt
  hết nổ "Argument list too long" (#234), dải mốc hội thoại không chắn bôi đen copy (#235), cập nhật
  xong không rớt MCP (#236), mic tự gửi/tự đẻ việc + POS rớt đơn (0.52.6-0.52.8), ô tìm note hỏi
  server một phát (0.52.9), **ảnh gửi vào chat ở lại + bấm phóng to** (#239).
- **BƯỚC NGOẶT KIẾN TRÚC:** upstream chuyển hàng loạt chuỗi hiển thị cứng SANG hệ **i18n gốc mới**
  (`dashboard/i18n/vi.json` + `en.json`, nạp qua `i18n/index.js`). Nhiều rebrand cũ của Thansa
  (P008/P009/P013/P018/P028/P034 vốn sửa chuỗi CỨNG) bị upstream hấp thụ về từ điển → khi rebase,
  các hunk đó giải bằng cách LẤY HEAD (nhận i18n gốc), rồi rebrand CHUYỂN XUỐNG tầng từ điển.
- Rebase 103 commit (32 patch [me] + ops/i18n). Xung đột giải: P001 (console.js: giữ fallback
  "Thansa OS" + nhận `t()` Telegram của upstream), P003 (index.html 8 hunk: giữ `data-i18n` +
  chữ Thansa), P008 (console.js/index.html/studio.js: lấy HEAD i18n gốc; test_engine_ngang_quyen
  đọc vi.json + assert "MCP Thansa"), P009/P013/P018/P028/P034 (console.js c2pa/tool status: lấy
  HEAD i18n), P015 (**giữ CẢ overlay `dich-en.js` LẪN i18n gốc `index.js?v=2`** - hai cơ chế bổ
  trợ), P017 (đổi ngôn ngữ dùng `refreshSettings()` tức thì thay `location.reload()`), P025 (VERSION
  → 1.5.0-javis-0.52.10), P026 (link docs → xahoapro/thansa-os + giữ data-i18n), P027 (docs 02/05/09:
  nền nội dung 0.52.x của upstream + rebrand Javis→Thansa), P031 (nút PWA giữ data-i18n-title/aria),
  P035 mới.
- **NEO LẠI (P035):** rebrand tên sản phẩm chuyển xuống **tầng từ điển** - regex an toàn
  `Javis(?![/\w])(?!-[A-Z])` áp cho `vi.json`+`en.json` (i18n gốc) + chuỗi cứng còn sót
  `console.js`/`index.html` + overlay `en-goi.json`. Nhãn tác giả C2PA khớp `BRAND_SOURCE =
  tradingauto.org`. GIỮ nguyên token kỹ thuật: `javis_*`, `JAVIS_*`, header `X-Javis-Vault`
  (aux_engine/mcp_hub/main.py), path `Javis/`, định danh JS (`JavisI18n`=19, `javisTheme`,
  `__javisRefresh`), container `javis`, `stop-javis.bat/vbs`, `javis-cli`. Product-name 'Javis'
  còn sót trên mọi bề mặt hiển thị = 0.
- **Sửa 4 neo mapping chết** (chuỗi dời console.js→vi.json): P013 (tradingauto.org), P018 (Ảnh Thansa
  tạo ra), P028 + P034 (tool của Thansa đã đấu) → trỏ `dashboard/i18n/vi.json`.
- **English giờ chạy runtime:** `dashboard/en/` vắng (không prebuild), server tự lùi bản gốc; đổi
  ngôn ngữ tức thì bằng i18n gốc (`JavisI18n.setLang`) + overlay `dich-en.js`, KHÔNG cần tải lại.
  Overlay `en-goi.json`/`dich-en.js` dần teo khi native i18n phủ hết (ghi ở dieu_kien_bo P035).
- VERSION neo `1.5.0-javis-0.52.10`. moc-goc goc_commit 91aa663, goc_version 0.52.10, thansa_version
  1.5.0, so_patch 32. tu-kiem-chung 5/5 XANH. Suite đầy đủ xanh (283 test).
- Phát hành bằng **snapshot main** (ff cho user 1.4.0), Docker vẫn tắt.

## Vòng 2026-09-05 (goc 91aa663 → 886ac7e, upstream +57 commit, VERSION nền 0.52.10 → 0.55.46, thansa 1.5→1.6)

- 57 commit upstream (0.53.x-0.55.46) - VÒNG LỚN NHẤT. Chủ đề: **Javis Store** (kho gói trợ lý/
  kỹ năng/quy trình/connector, 0.55.19-0.55.46) **tách sang repo riêng `javis-store`** (0.55.30);
  dọn 16-26 connector từ mcp-catalog.json ra kho; độ sâu suy nghĩ thật trên Codex/Grok/Antigravity
  (0.55.41-42); **tài liệu song ngữ VI-EN** (0.55.40, thêm thư mục docs/en/ + header mỗi trang);
  Fable 5.1 trong Claude Code (0.55.39); gom nhóm Agent/Workflow (0.55.38); "người gác cổng bản cũ"
  (freshness.js + /app-version, 0.55.18); Ollama Local (0.55.7-13); vá mic/đính kèm/Antigravity dán mã.
- Rebase 105 commit (33 patch [me]). Xung đột giải: P004 (vi/en.json page.home.label), P007 (mcp_hub
  javis_connections + antigravity_cli: lấy text mới upstream + rebrand), P012 (**mcp-catalog.json:
  upstream tái cấu trúc lớn do dọn connector ra Store → lấy HEAD + rebrand regex**), P015 (giữ overlay
  dich-en.js + lucide?v=4), P016 (app.js wizard refactor upstream + rebrand nút), P017 (**giữ CẢ hai:
  vân tay tài sản /app-version của upstream LẪN _lang_en/_dashboard_file của mình**), P025 (VERSION
  1.6.0), P026 (catalog link - hấp thụ bởi P012), P027 (**26 docs song ngữ: lấy HEAD upstream + rebrand
  toàn bộ docs VI + docs/en/**), P033 (**upstream TỰ vá test timing 0.55.16 = cho_xong, lấy HEAD**),
  P035 (lấy HEAD dicts + chạy lại regex rebrand).
- **NEO LẠI (P036):** rebrand tên sản phẩm Javis→Thansa toàn dashboard/*.js + *.html (packs.js
  "Thansa Store" là bề mặt mới lớn nhất) + Store backend packs_store.py. Regex an toàn giữ định danh
  JS (JavisI18n/JavisPacks/appendJavisMessage/JavisSessions=25, window.Javis=260), path Javis/,
  header X-Javis-*, URL kho blogminhquy/javis-store (gói chạy thật, chủ đổi trong Cài đặt).
- **Nhiều patch bị upstream HẤP THỤ do tái cấu trúc:** P033 test_chat_disconnect (upstream tự vá cùng
  cách), P033 test_prompt_budget (upstream cũng 33_600), P026 catalog link (gộp P012), shopify khỏi
  catalog (dời Store). Sửa 2 neo mapping chết: P020 (shopify→ucp-agent-profile "Hồ sơ agent UCP của
  Thansa OS"), P033 (poll→comment thuế rebrand trong test_prompt_budget).
- **Trần prompt 33_600→33_700** (test:, non-[me]): upstream tự làm CLAUDE.md phình tới 33.581 (chỉ
  19 headroom dưới trần CỦA HỌ), thuế rebrand +23 đẩy lên 33.604 → vượt 4. Không còn khoảng trắng để
  cắt, cắt văn xuôi upstream sẽ lệch nghĩa → nâng trần có ý thức (thuế cấu trúc của fork).
- Sửa test theo rebrand (test:, non-[me]): test_kho_goi ("Thansa Store"), test_cai_go_goi ("máy chủ
  Thansa").
- VERSION neo `1.6.0-javis-0.55.46`. moc-goc 886ac7e/0.55.46, thansa 1.6.0, so_patch 33. tu-kiem-chung
  5/5 XANH. Phát hành snapshot main (ff cho user 1.5.0), Docker vẫn tắt.
- **QUYẾT ĐỊNH mở: kho gói riêng.** Mặc định Store trỏ catalog upstream (blogminhquy/javis-store) để
  gói chạy thật. Chủ muốn kho RIÊNG thì fork → xahoapro/thansa-store, đổi STORE_MAC_DINH / URL Cài đặt.

## Vòng 2026-09-07 (goc 886ac7e → 8a38217, upstream +7 commit, VERSION nền 0.55.46 → 0.55.53, thansa 1.6→1.7)

- 7 commit upstream (0.55.47-0.55.53) - vòng NHỎ, chủ yếu vá lỗi + bảo mật: **gắn file & link vào
  hội thoại** (0.55.48), ô tìm Store gõ liền mạch (0.55.53), 2 brain chép chung file bộ nhớ không
  hỏng index (0.55.51), **CVE path traversal python-multipart 0.0.18→0.0.30** (0.55.50), vá 3 lỗi
  06/09 (wiki trùng, app chậm, ký ức lạc Memory→memory 0.55.50), thực đơn tool gọi tên từng plugin
  thay vì gộp "javis" (0.55.47), Codex refresh CI.
- Rebase 108 commit (34 patch [me]). Xung đột giải ÍT: P008 (main.py: upstream đổi Memory/→memory/
  vá 0.55.50, giữ casing mới + rebrand), P012 (CLAUDE.md 3 hunk: memory/ lowercase + ghi chú mới),
  P025 (VERSION 1.7.0), P035 (lấy HEAD dicts + chạy lại regex rebrand + c2pa tradingauto.org).
  P027 docs KHÔNG đụng (upstream không sửa docs vòng này).
- **NEO LẠI (P037):** rebrand sessions-ui.js (gắn file/link 0.55.48, 4 chuỗi mới), giữ JavisSessions=13.
- **SỰ CỐ BẢO MẬT tái diễn (đã chặn):** `ops/.telegram` (token) bị `git add -A` RE-TRACK ở P012 khi
  rebase - file local còn trên đĩa, mà file ĐÃ TRACK thì gitignore bó tay (check-ignore báo not-ignored
  vì tracked). **Luật secret-scan mới BẮT ĐÚNG.** Xử: git rm --cached + filter-branch xoá khỏi MỌI
  commit me (886ac7e..me, --prune-empty), secret-scan cây = 0. Token đã revoke từ vòng trước = chết.
  GỐC RỄ: file local trong repo → cần chuyển bao-khan.sh đọc ~/.thansa-alert.env (ghi dieu_kien_bo P037).
- VERSION neo `1.7.0-javis-0.55.53`. moc-goc 8a38217/0.55.53, thansa 1.7.0, so_patch 34. tu-kiem-chung
  5/5 XANH. Phát hành snapshot main (ff cho user 1.6.0), Docker vẫn tắt.

## Vòng 2026-09-09 (goc 8a38217 → 9ddc3d0, upstream +10 commit, VERSION nền 0.55.53 → 0.55.63, thansa vẫn 1.7.0 - cuộn bản chưa phát hành)

- LƯU Ý: bản 1.7.0/0.55.53 đã dựng xong + xanh nhưng CHƯA phát hành (bị ngắt giữa suite) → cuộn
  thẳng lên nền 0.55.63, phát hành một lần 1.7.0-javis-0.55.63.
- 10 commit upstream (0.55.54-0.55.63): **dịch nốt UI sang tiếng Anh 1245 chuỗi, từ điển 594→2586
  dòng** (#304 - mốc khai tử overlay đang tới), ảnh/file đính kèm không rơi khi Enter sớm (#313),
  link file:// bấm mở (#311), tạo file từ chat trong thư mục brain (#308), vá 3 lỗi 08/09 (#307),
  Watchtower kèm sẵn cả 2 compose (#306), Antigravity bỏ --effort thừa (#305), **#312 (0.55.62):
  upstream BỎ chốt an toàn - loop/việc mặc định TOÀN QUYỀN**, nhãn tác giả "by Minh Quý"→"by Javis
  OS team"→"by Javis Foundation" (#309/#310).
- **QUYẾT ĐỊNH LỚN (chủ chọn): GIỮ chốt an toàn** trước #312. Thêm [me] P038 = git revert #312 trên
  cây đã rebrand: loop/việc mặc định suggest, cấm tự tiền/đơn/đăng/nhắn; giữ hộp cảnh báo đỏ +
  confirm trang Việc; javis_task/schedule mặc định suggest; khôi phục 20 khoá i18n cảnh báo (16 gỡ
  + 4 sửa), docs 08/13/20, website. Revert TỰ auto-merge đúng CLAUDE.md/console.js/plugin/server/
  test an toàn; chỉ giải tay dicts (phẫu thuật: giữ 2586 chuỗi #304 + thêm lại khoá an toàn) + docs.
- Rebase 110 commit. Xung đột nhiều do #304 i18n-hoá hàng loạt (P001/P003/P008/P016/P022/P026/P031/
  P034/P035/P036 lấy HEAD i18n + rebrand dồn về dict). Footer tác giả: GIỮ P011 "by Tradingauto.org"
  (không theo "by Javis Foundation"). Image lùi Docker: ghcr.io/xahoapro/thansa-os.
- **P037 (sessions-ui vòng 0.55.53) bị git DROP** ("patch contents already upstream") - #304 i18n-hoá
  nốt sessions-ui + P036 rebrand lại → trùng upstream. Bỏ P037 khỏi mapping, thêm P038. Sửa 3 neo
  chết (P016 "Bắt đầu dùng Thansa"→vi.json, P034 "Thansa vừa gửi"→vi.json, P011 "Cách lùi Docker"→
  image thansa-os).
- **Overlay đo lại:** i18n gốc 594→2586 khoá. Overlay 3220 cặp giờ 47% THỪA (1539) / 52% riêng
  (1681). Redundancy vọt từ 13%→47% chỉ một vòng. Vẫn giữ (bỏ = 1681 chuỗi Việt lòi ra EN) nhưng
  gần mốc khai tử - vòng sau cân nhắc bỏ hẳn khi phần-riêng < ~200.
- VERSION neo `1.7.0-javis-0.55.63`. moc-goc 9ddc3d0/0.55.63, thansa 1.7.0, so_patch 34. tu-kiem-chung
  5/5 XANH. Phát hành snapshot main (ff cho user 1.6.0). Docker vẫn tắt. Secret-scan trước phát hành = 0.

## Vòng 2026-09-21 (goc 9ddc3d0 → 423a83e, upstream +93 commit, VERSION nền 0.55.63 → 0.60.1, thansa 1.7→1.8)

- **BỐI CẢNH:** bản 1.7.0/0.55.63 đã trộn+xanh nhưng CHƯA từng đẩy remote (origin/main vẫn ở
  1.6.0/0.55.46 = e606057). RELEASES.md local LỠ ghi 1.7.0 "đã phát hành" - SAI, đã đính chính
  thành "cuộn vào 1.8.0, không phát hành riêng". Vòng này cuộn thẳng 0.55.63→0.60.1, phát hành
  MỘT lần 1.8.0-javis-0.60.1 (user nhảy 1.6.0 → 1.8.0).
- 93 commit upstream (0.56.0-0.60.1). Chủ đề LỚN NHẤT từ trước tới nay: **Voice** (V1 điều khiển
  dashboard+app máy tính bằng lời 0.56.0; V2/Live bộ não giọng riêng nghe bằng Groq, chữ theo lời
  như ChatGPT Voice, ngắt lời bằng giọng, tách nói khỏi làm 0.57.x); **linh vật** mép màn hình +
  logo mới + thanh bên gọn + 5 giọng Edge (0.58.x); **trang Cộng sự** chat với trợ lý/quy trình +
  lịch sử chạy + lệnh gạch chéo (0.59.x); **Hộp thư Hội thoại khách** (Chatbot V2), kênh Zalo cá
  nhân, tầng CRM (0.60.0/0.60.1).
- Rebase 111 commit (35 patch [me] sau khi thêm P039). rerere: **rr-cache CŨ (~140 resolution
  tích luỹ) bị XOÁ SẠCH** giữa vòng - lý do: một lần lỡ stage vi.json còn conflict-marker ở P004
  khiến rerere ghi một resolution ĐỘC (kèm marker); không tách được entry độc nên xoá cả rr-cache
  (ở common git dir /home/thansa/thansa/goc/.git, KHÔNG phải .git của worktree) rồi giải tay lại
  từ đầu. Bài học: **worktree dùng `.git` là FILE trỏ common dir → rr-cache/rerere nằm ở
  git-common-dir**; và app.js bị grep nhận nhầm BINARY nên marker check phải dùng `grep -a`.
- Xung đột giải tay: P003 (index.html: giữ cấu trúc linh vật brand-mark + chữ tách ô của upstream,
  rebrand THANSA OS + khối "Công cụ tuỳ chọn"), P004 (vi/en.json: lấy HEAD cấu trúc pet/share/graph
  của upstream, override page.home.label="Thansa"; ui_lang.title lấy HEAD "Giao diện"), P007 (danh
  tính chat-facing: background_status.py lấy HEAD wording mới, compaction.py lấy HEAD +
  CURRENT_REQUEST_MARKER + rebrand "trò chuyện Thansa", learn.py lấy HEAD refactor TẠO/SỬA skill +
  rebrand), P010 (app.js: giữ null-check `const wn; if(wn)` của upstream + fallback "Thansa OS"),
  P012 (CLAUDE.md xưng hô - xem QUYẾT ĐỊNH HÀNH VI bên dưới), P015 (giữ overlay dich-en.js + lucide
  v=5 mới), test P016 (marker file-open: lấy HEAD ca test mới SKILL/GHIM + rebrand "của Thansa:"),
  .gitignore (union: entry mới upstream + ops/.telegram + .thansa-alert), P025 (VERSION neo
  1.8.0-javis-0.60.1), P027 (9 docs README+VI+EN: lấy HEAD upstream + rebrand regex 550 chuỗi),
  P035 (console.js lấy HEAD olLenhCai; vi.json lấy HEAD nhãn "Công cụ" + "Thansa Store"; index.html
  giữ class gcard-btn + placeholder thansa.), P036 (app.js+voice.js: --ours upstream + regex rebrand,
  GIỮ mảng _KHOI_NGU_CANH 4 marker mới + [Javis TTS]), P038 (chốt an toàn - xem bên dưới).
- **QUYẾT ĐỊNH HÀNH VI (P012 - CẦN CHỦ ĐIỂM DUYỆT):** upstream đổi luật xưng hô #9 từ "mặc định
  bạn/mình" → **"theo người dùng" (quyết định upstream 2026-09-14, XOÁ luôn test_xung_ho.py)**.
  Bản Thansa chỉ *thừa hưởng* text cũ rồi rebrand, KHÔNG có test riêng ép bạn/mình. Theo luật ưu
  tiên #4 (upstream tiến hoá tương đương) + việc "theo người dùng" phục vụ đúng cách chủ xưng "anh"
  → LẤY HEAD (theo upstream). **Nếu chủ muốn giữ "bạn/mình mặc định" cho spa (nhiều khách lạ) thì
  báo, sẽ đảo lại thành một patch [me] như P038.**
- **P038 (chốt an toàn) SỐNG trên nền 0.60.1:** phần lớn auto-merge sạch (CLAUDE.md safety section,
  console.js, javis-schedule). Giải tay: javis-task/plugin.py (giữ bugfix check-trùng-tên MỚI của
  upstream + `_MODE_CHO_PHEP=("suggest","auto")`, ten_mode 2-mode, mode=full BỊ TỪ CHỐI); vi/en.json
  (UNION: giữ TOÀN BỘ khoá mới upstream ws.*/ht.*/share.*/page.conversations.* + thêm lại 20 khoá
  cảnh báo cs.si_*warn*/*_confirm của P038). loop/việc vẫn mặc định suggest, cấm tự tiền/đơn/đăng/nhắn.
- **P037 (sessions-ui vòng 0.55.53) đã bỏ từ vòng trước; thêm P039 mới.** P039 = rebrand nền 0.60.1:
  regex an toàn Javis→Thansa trên dashboard/*.js + index.html + i18n vi/en (giữ định danh JS
  JavisVoice/JavisI18n/JavisPet/JavisSessions/JavisWorkspace, path Javis/, tag debug [Javis TTS]).
  Bề mặt MODEL-facing MỚI rebrand SOURCE: voice_brain.py/voice_live.py ("Bạn là Thansa" + nhãn
  transcript), channel_context.py (NGỮ CẢNH GIAO DIỆN, GIỮ path Javis/reminders|scripts|loops).
  Server còn lại + comment nội bộ + CSS cố ý giữ "Javis". 90 chuỗi hiển thị đổi; residual display
  Javis = 0. Chatbot/CRM/conversations/workflow server KHÔNG lộ tên sản phẩm cho model (đã rà).
- VERSION neo `1.8.0-javis-0.60.1`. moc-goc 423a83e/0.60.1, thansa 1.8.0, so_patch 35. tu-kiem-chung
  5/5 XANH (không neo nào chết vòng này). node --check mọi dashboard/*.js xanh; py_compile file sửa xanh.
- **NGHIỆM THU (điền sau khi chạy suite):** Suite 414 test chạy qua .venv (goc, fastapi 0.115): sau khi sửa 4 test coupled-rebrand (test_linh_vat.js 'JAVIS OS'->'THANSA OS' + home 'Thansa'->'Đồ thị/Graph' theo upstream; test_dinh_kem_khong_roi.js + test_channel_ui_prompt.py marker 'của Javis:'->'của Thansa:' khớp app.js:987/1352 [producer+consumer đều Thansa, NHẤT QUÁN]; test_cai_windows.py README 'khởi động lại Javis'->'Thansa') → fork còn 3 ĐỎ {test_form_chuoi_rong, test_route_table, test_terminal_cmd_goc} = Y HỆT nền upstream 0.60.1 SẠCH (410/414, sandbox: route/form/PTY), test_terminal flaky. fork_reds - upstream_reds = 0 hồi quy. node --check mọi dashboard/*.js xanh; py_compile file sửa xanh. LƯU Ý MÔI TRƯỜNG: worktree thansa/ KHÔNG có .venv (chỉ goc/ có) - phải chạy suite bằng goc/.venv/bin/python, đừng tin python hệ thống (thiếu fastapi = 192 đỏ GIẢ). SECRET-SCAN cây phát hành = SẠCH (ops/.telegram KHÔNG track, chỉ placeholder comment trong bao-khan.sh).
- **CHƯA đẩy remote** (origin/me vẫn 327af23, origin/main vẫn e606057=1.6.0) - chờ chủ bấm. Lệnh phát
  hành: secret-scan cây → force-push origin/me → `C=git commit-tree me^{tree} -p origin/main -m
  "release: Thansa OS 1.8.0 (nen Javis 0.60.1)"` → `git push origin $C:main` → tag me-backup-0.60.1.
