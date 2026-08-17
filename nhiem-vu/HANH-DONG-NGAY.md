# HÀNH ĐỘNG NGAY — Thi hành GĐ2b (trạm #1 Windows → trạm #2 VPS)

> Gửi Claude đang chạy trên VPS. Trạm #1 (máy Windows, chỉ NGHIỆM THU, không sửa code) đã kiểm `origin/me` **3 lần** và **không thấy** bất kỳ commit GĐ2b nào. Persona vẫn `Bạn là Javis`. Rất có thể bạn mới PHÂN TÍCH mà chưa THỰC SỰ sửa file + commit + push. File này là nguồn chuẩn để xử lý dứt điểm.

## 0. Trạng thái đã chốt (để đồng bộ hiểu biết)
- GĐ0, GĐ1, GĐ2 (P001/P003/P004/P005): **ĐẠT**, đã nghiệm thu.
- `origin/me` hiện ở `498c5b9` (chỉ có file nhiệm vụ, chưa có P007–P010). `so_patch=4`, mapping = P001/P003/P004/P005.
- Chủ đã chốt: **làm GĐ2b bây giờ, HOÃN P002 (logo)**.
- Chi tiết đầy đủ đã có ở `nhiem-vu/GD2b.md` — file này là bản THỰC THI rút gọn + kỷ luật commit.

## 1. Nơi làm việc
```
cd /home/thansa/thansa/thansa      # đây là worktree nhánh me
git pull origin me
git status                          # phải sạch trước khi bắt đầu
```

## 2. Bốn patch — mỗi patch PHẢI kết bằng một commit `[me]`

### P007 — Danh tính trợ lý → "Thansa" (chat tự xưng)
- `server/context_compiler.py:111`: `Bạn là Javis, …` → `Bạn là Thansa, …`  ← **quan trọng nhất**
- `server/stt.py` dòng 30, 51, 69, 72, 74: `Javis` → `Thansa` (chuỗi chèn vào chat khi xử lý voice)
- `server/zalo_bot.py` dòng 377, 387, 419, 426, 617: `Javis` → `Thansa` (tin nhắn bot gửi người dùng)
- Sweep: rà thêm chuỗi CHAT-facing chứa "Javis" (chỉ chuỗi bot NÓI/GHI; bỏ qua comment/docstring)
```
git add -A && git commit -m "[me] P007: danh tinh tro ly Thansa"
```

### P008 — Chuỗi sản phẩm HIỂN THỊ ở server → "Thansa OS"
- `server/oauth_mcp.py:245` client_name · `server/codex_models.py:121` title
- `server/main.py:114` `FastAPI(title=...)` · `server/main.py:3837, 3859` template vault · `server/main.py:4476` lỗi hiển thị
- `server/totp.py:96` default `ten_workspace` · `server/main.py:806` (nhãn Authenticator)
- `dashboard/studio.js:639` tooltip badge
- (Tuỳ chọn) `server/engine.py:779, 827, 1659` header `X-Title`
```
git commit -am "[me] P008: chuoi san pham server Thansa OS"
```

### P009 — Brand nhúng ảnh + SỬA TEST kèm
- `server/image_gen.py:114` `BRAND_SOFTWARE="Javis OS"` → `"Thansa OS"`; dòng 178 bỏ chuỗi `javisos.com` (CHƯA có domain Thansa → bỏ, đừng bịa)
- **BẮT BUỘC** sửa `tests/python/test_image_gen.py` dòng 74, 92, 121, 122: bỏ assert `javisos.com`, đổi `Javis OS`→`Thansa OS` (nếu không, test đỏ)
```
git commit -am "[me] P009: brand anh Thansa OS + sua test_image_gen"
```

### P010 — app.js fallback (⚠️ BẪY ENCODING)
- `dashboard/app.js` dòng 80 và 2100: `|| "Javis OS"` → `|| "Thansa OS"`
- **CHỈ đổi đúng 2 string literal**, giữ nguyên phần còn lại byte-for-byte (đừng để editor đổi encoding/EOL). `git diff -- dashboard/app.js` phải chỉ có 2 dòng đổi.
```
git commit -am "[me] P010: app.js fallback Thansa OS"
```

## 3. Hồ sơ (bắt buộc để tự-kiểm-chứng xanh)
- `ops/mapping.yaml`: thêm 4 mục P007, P008, P009, P010 — mỗi mục ĐỦ 7 trường (`id, ten, y_dinh, commit, diem_neo, vung_theo_doi, anh_goc, kiem_chung, dieu_kien_bo`; `diem_neo` bằng ký hiệu, KHÔNG số dòng).
- `ops/moc-goc.json`: `so_patch: 8`.
```
git commit -am "ops: mapping + moc-goc GD2b (so_patch=8)"
```

## 4. Nghiệm thu nội bộ (phải xanh trước khi báo)
```
python3 ops/tu-kiem-chung.py                 # XANH cả 4 luật, exit 0
../goc/.venv/bin/python tests/run.py         # 241/241 (pytest đã cài); test_chat_disconnect flaky khi tải nặng, chạy riêng phải XANH
grep -rn "Bạn là Javis" server/              # phải RỖNG
grep -c '"Javis OS"' dashboard/app.js         # phải 0
```

## 5. PUSH + tín hiệu DONE
```
git push origin me
```
- Nếu `git push` (hoặc `git commit`) bị **chặn quyền** ("đưa dữ liệu ra ngoài"/egress): DỪNG và báo chủ bấm DUYỆT, rồi chạy lại. Đây là nguyên nhân hay gặp khiến "làm rồi mà repo không có gì".
- Dán lại cho chủ:
```
git log --oneline -8
git rev-parse --short origin/me
git show origin/me:server/context_compiler.py | sed -n '111p'
```

## 6. TÍN HIỆU DONE để trạm #1 nghiệm thu
`origin/me` có 4 commit `[me] P007/P008/P009/P010`, `so_patch=8`, và dòng 111 = **`Bạn là Thansa, …`**. Khi đó báo trạm #1.

## 7. Ngoài phạm vi (đừng làm)
- HOÃN **P002 (logo)** — chờ file logo Thansa.
- GIỮ NGUYÊN: biến `JAVIS_*`, thư mục, `javis.service`, tool `javis_*`, enum `source='javis'`, comment/docstring không hiển thị. KHÔNG đụng `VERSION/CHANGELOG/README`, `dashboard/docs/`. KHÔNG phát hành.

## 8. Nếu bạn KHÔNG làm được (để trạm #1 biết đường xử lý)
Nếu có rào cản khiến bạn không sửa/commit/push được (permission, sandbox, plan-mode, mất context…), hãy GHI RÕ rào cản đó vào `bao-cao/GD2b.md` và commit file báo cáo đó — để trạm #1 đọc và đổi cách. Đừng im lặng.
