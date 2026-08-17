# NHIỆM VỤ GĐ1 — Bộ hồ sơ `ops/` + script dò hằng ngày + script tự kiểm chứng

Trạm #1 (Windows) soạn · 2026-08-17 · giao cho trạm #2 (VPS)
Tham chiếu đặc tả: mục 2 (ba tài liệu hồ sơ), mục 3 (bộ dò hằng ngày), mục 2.4 (luật tự kiểm chứng), mục 7 GĐ1.
Nền: `me` đứng trên `goc_commit = 0b8f2c0` (upstream/main, VERSION 0.35.10).

## Mục tiêu
Dựng bộ máy hồ sơ + tự động hoá của Thansa OS để từ GĐ2 trở đi mọi patch đều có nơi khai báo, kiểm chứng, và dò upstream tự động. Kết thúc GĐ1: chạy dò tay 1 lần ra bản tin đúng định dạng; script tự kiểm chứng XANH.

## Phạm vi

### Được tạo (TOÀN FILE MỚI dưới `ops/` — không đụng mã nguồn app)

1. **`ops/moc-goc.json`** — đúng schema mục 2.1:
   - `thansa_version`: "1.0"
   - `goc_commit`: SHA **đầy đủ** của `upstream/main` hiện tại (0b8f2c0…)
   - `goc_version`: "0.35.10"
   - `ngay_tron`: "2026-08-17"
   - `so_patch`: 0   (chưa có patch; GĐ2 sẽ cập nhật)

2. **`ops/mapping.yaml`** — danh sách patch RỖNG + comment tài liệu hoá đủ 7 trường (mục 2.2: `id, ten, y_dinh, commit, diem_neo, vung_theo_doi, anh_goc, kiem_chung, dieu_kien_bo`). Để GĐ2 thêm P001+.

3. **`ops/so-tron.md`** — append-only. Khối mở đầu ghi nền GĐ0 (goc `0b8f2c0`, VERSION 0.35.10, 0 patch) và ghi chú test nhạy timing (xem cuối file).

4. **`ops/ban-tin/`** — thư mục chứa bản tin dò hằng ngày (thêm `.gitkeep`).

5. **`ops/do-hang-ngay.sh`** — script dò (mục 3), KHÔNG sửa bất cứ nhánh nào (chỉ fetch + ghi file bản tin):
   - `git fetch upstream`
   - danh sách file upstream đổi từ lần dò trước (lưu con trỏ SHA lần trước ở `ops/.last-do`)
   - giao với `vung_theo_doi` của mọi patch trong mapping
   - so từng `anh_goc` với nội dung tương ứng ở `upstream/main` mới nhất → khác thì gắn cờ
   - quét message commit mới theo từ khoá bảo mật: `vá|bảo mật|2FA|credential|token|leak|rò` → cờ **KHẨN**
   - ghi `ops/ban-tin/YYYY-MM-DD.md` đúng định dạng mục 3

6. **`ops/tu-kiem-chung.sh`** — script tự kiểm chứng (mục 2.4), 3 luật, `exit != 0` nếu đỏ:
   - (1) số commit `[me]` trên `main..me` == số mục mapping có trường `commit` khớp
   - (2) mọi `diem_neo` tìm thấy trong cây mã nhánh `me`
   - (3) `goc_commit` trong `moc-goc.json` == commit mà `me` đang đứng trên (`git merge-base main me`)

### CẤM đụng
- Mã nguồn app: `server/`, `dashboard/`, `tests/`, `VERSION`, `CHANGELOG*`, `README*`, `docker-compose*`, `dashboard/app.js`… GĐ1 **chỉ có `ops/`**.
- Không tạo patch rebrand nào (đó là GĐ2).
- Không phát hành, không đụng nhánh `release`.

## Kỷ luật commit
- `ops/` + 2 script commit trên `me` như **commit nền (chore)**, thông điệp gợi ý: `ops: khung ho so + script do + tu kiem chung (GD1)`.
- **KHÔNG gắn nhãn `[me]`** (nhãn `[me]` chỉ dành cho patch code từ GĐ2) → giữ luật tự kiểm chứng #1 nhất quán: 0 commit `[me]` == 0 mục mapping.
- Bí mật không vào git (mục 5.3): `ops/` chỉ chứa metadata + script, tuyệt đối không token/khoá.

## Tiêu chí ĐẠT (đo được)
1. `bash ops/tu-kiem-chung.sh` → `exit 0`, in "XANH" cho cả 3 luật.
2. `bash ops/do-hang-ngay.sh` chạy tay 1 lần → sinh `ops/ban-tin/2026-08-17.md` đúng định dạng mục 3 (có các dòng ĐỤNG VÙNG THEO DÕI / ẢNH GỐC LỆCH / BẢO MẬT / Không giao). Mapping rỗng nên "không giao" toàn bộ — hợp lệ.
3. `python3 -c "import json; json.load(open('ops/moc-goc.json'))"` OK; `python3 -c "import yaml; yaml.safe_load(open('ops/mapping.yaml'))"` OK.
4. `.venv/bin/python tests/run.py` (trong `goc/`) vẫn XANH **241/241 khi đã cài `pytest`** — GĐ1 không đụng code nên không được làm đỏ thêm. (Lưu ý: `test_chat_disconnect.py` nhạy timing, có thể flaky khi chạy song song tải nặng → chạy riêng để xác nhận.)
5. Viết `bao-cao/GD1.md` (mục 9.4): việc đã làm; kết quả tự kiểm chứng + bản tin mẫu; vấn đề; việc để lại; đề xuất. Push `me` lên `origin`.

## Chốt câu hỏi mở từ GĐ0 (ĐÃ SỬA sau nghiệm thu độc lập)
Trạm #1 chạy lại test độc lập và phát hiện báo cáo GĐ0 SAI ở điểm này — ghi lại sự thật để không lặp:
- **`pytest` là DEV-DEPENDENCY BẮT BUỘC**, không phải tuỳ chọn. 5 test có `import pytest` **không self-skip** — thiếu pytest thì `test_workflow_graph_phase10.py` (và phase8/11/12) **lỗi cứng `ModuleNotFoundError`**. "241/241 không pytest" trong báo cáo GĐ0 là KHÔNG đúng (thực tế 240/241).
- **Chuẩn "xanh" chính thức = CÓ pytest trong `.venv` → 241/241.** Trạm #1 đã cài `pytest` vào `goc/.venv` (phase10 chạy lại = XANH 39s).
- **Việc GĐ1 phải làm thêm:** ghi `pytest` vào tài liệu môi trường (checklist cấp máy / `env.thansa.example` hoặc một `ops/requirements-dev.txt`) để pytest không "biến mất" lần nữa. Cân nhắc đề xuất lên upstream: bọc `import pytest` bằng self-skip thật, hoặc đưa pytest vào requirements dev.
- `test_chat_disconnect.py` **nhạy timing** (chạy riêng = XANH; flaky khi tải nặng) → ghi `ops/so-tron.md` mục "đã biết", KHÔNG vá trong thansa-os (ngoài phạm vi rebrand); có thể đề xuất upstream (poll thay `sleep` cứng).

## Hạn chót
Không gấp. Xong GĐ1 thì **báo để trạm #1 nghiệm thu** trước khi sang GĐ2 (rebrand P001–P006).
