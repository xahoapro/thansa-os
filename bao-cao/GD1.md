# BÁO CÁO GĐ1 — Bộ hồ sơ ops/ + script dò + tự kiểm chứng (trạm #2, VPS)

Ngày: 2026-08-17. Thi hành theo `nhiem-vu/GD1.md` (bản sửa 13e2c03 — pytest bắt buộc)
+ `nhiem-vu/GD1-bosung.md` + DAC-TA mục 2, 3, 7.

## Việc đã làm (commit trên nhánh me, theo thứ tự)

- `ops: khung ho so + script do + tu kiem chung (GD1)` (ffa429a) — đúng kỷ luật nhiệm vụ:
  KHÔNG nhãn `[me]` (để dành cho patch GĐ2), mapping RỖNG, luật 1 = 0==0.
  - `ops/moc-goc.json` — `thansa_version: "1.0"`, `goc_commit` SHA đầy đủ
    `0b8f2c092487c0b3b7f6a55a292deb4900d6f4c5`, `goc_version: "0.35.10"`, `so_patch: 0`.
  - `ops/mapping.yaml` — danh sách rỗng + comment tài liệu hoá đủ 7 trường.
  - `ops/so-tron.md` — khối "Khởi lập" + mục "Đã biết".
  - `ops/ban-tin/.gitkeep` — thư mục bản tin vào git; bản tin `*.md` và con trỏ
    `ops/.last-do` là file cục bộ VPS (loại bằng `.git/info/exclude`, không đụng
    `.gitignore` upstream).
  - `ops/do-hang-ngay.sh`, `ops/tu-kiem-chung.sh` — đúng tên nhiệm vụ; là VỎ BỌC,
    ruột python3 (`.py` cùng tên) vì phải parse YAML — bash thuần không tin cậy được.
    Exit code như đặc tả: dò trả 2 khi CỜ KHẨN; kiểm chứng trả khác 0 khi ĐỎ.
- `ops: requirements-dev + dinh chinh chuan xanh (nhiem-vu sua doi)` — việc bổ sung theo
  bản sửa nhiệm vụ: `ops/requirements-dev.txt` (pytest, kèm lý do), sửa mục "Đã biết"
  trong sổ trộn theo chốt mới.
- 2 commit `bao-cao:` (GD1 lần đầu + bản này).

## Đính chính báo cáo GĐ0 (trạm #1 phát hiện đúng)

Báo cáo GĐ0 viết "5 test dạng pytest tự BỎ QUA khi thiếu pytest, 241/241" — **SAI**.
Sự thật: chỉ `test_chat_disconnect.py` có self-skip trong khối `__main__`; 4 test
phase8/10/11/12 `import pytest` ngay đầu file → thiếu pytest là ĐỎ CỨNG
`ModuleNotFoundError` (lần chạy đầu GĐ0 thực tế 237/241, không phải 241/241).
Đã kiểm chứng lại hôm nay: gỡ pytest → 239/241 đỏ. pytest là dev-dependency BẮT BUỘC,
nay ghi ở `ops/requirements-dev.txt` để không "biến mất" lần nữa.

## Kết quả tiêu chí ĐẠT (theo bản sửa nhiệm vụ)

1. `bash ops/tu-kiem-chung.sh` → exit 0, XANH cả 3 luật (+ luật 4 bổ sung: `so_patch`
   = số mục mapping, chặn quên cập nhật mốc gốc ở GĐ2). ✓
2. `bash ops/do-hang-ngay.sh` → `ops/ban-tin/2026-08-17.md` đúng định dạng 4 dòng cờ,
   `+0 commit` (upstream đứng yên từ lúc clone), "không giao" toàn bộ — hợp lệ. ✓
3. `json.load(moc-goc.json)` OK; `yaml.safe_load(mapping.yaml)` OK. ✓
4. `tests/run.py` với pytest: **240/241, đỏ duy nhất `test_chat_disconnect.py`** —
   xem mục dưới: trên VPS này nó đỏ ỔN ĐỊNH chứ không flaky, đã đo ngưỡng. ⚠ trạm #1
   phán quyết.
5. Báo cáo này + push `me`. ✓

## test_chat_disconnect trên VPS: đỏ ổn định, có số đo

Khác quan sát của trạm #1 (Windows: chạy riêng = xanh): trên VPS này chạy riêng vẫn đỏ
7/7 lần. Đo ngưỡng bằng bản sao ngoài goc (không sửa goc): chờ **80ms (gốc) → ĐỎ;
300ms → XANH; 800ms → XANH; 2000ms → XANH**. Kết luận: việc ghi nền trên VPS mất
~0.1–0.3s, ngưỡng cứng `asyncio.sleep(0.08)` của test quá sát cho máy này — vẫn là
LỖI NGƯỠNG TEST, không phải lỗi mã app. Đề xuất: chấp nhận "240/241 + chat_disconnect
đỏ do ngưỡng" là chuẩn xanh trên VPS, và đề xuất upstream đổi sleep cứng thành poll
(chờ tối đa X giây, thăm dò mỗi 50ms).

## Sự cố trong GĐ1 + cách xử lý (minh bạch để trạm #1 soát)

1. Tôi khởi công theo lệnh trực tiếp của chủ TRƯỚC khi thấy `nhiem-vu/GD1.md` (commit
   36a9004 đến giữa chừng); bản đầu lệch kỷ luật (commit `[me] P006` + mapping tự khai).
   Đã reset làm lại đúng nhiệm vụ (nhánh me được phép force-push — quyết định #4).
2. Một cú `git reset --hard origin/me` trên worktree (nghi tai nạn thao tác) đã văng
   2 commit làm-lại + chính bản sửa nhiệm vụ 13e2c03. Khôi phục đủ từ reflog, không mất gì.
3. pytest từng bị tôi gỡ khỏi `goc/.venv` (theo chuẩn cũ của nhiệm vụ bản đầu) — đã cài
   lại theo bản sửa.

## Thi hành nhiem-vu/GD1-bosung.md (nghiệm thu bổ sung: XANH cả 4)

File bổ sung của trạm #1 được push lên `origin/me` (nền lịch sử cũ) ĐÚNG LÚC tôi
force-push lịch sử mới → văng tạm khỏi remote; đã cherry-pick trở lại (4851f46),
không mất gì. Đối chiếu từng việc:
1. Sửa bản ghi "chuẩn xanh" trong khối Khởi lập của `ops/so-tron.md` theo đúng câu
   trạm #1 yêu cầu ✓ (mục "Đã biết" đã sửa từ trước theo 13e2c03).
2. `ops/requirements-dev.txt` ✓ + dòng pytest trong `ops/checklist-cap-may.md` (file
   checklist cấp máy chưa tồn tại nên tạo mới — `env.thansa.example` để dành GĐ2/P001).
3. Đề xuất upstream: ghi nhận, chờ chủ quyết.
Nghiệm thu bổ sung: `tu-kiem-chung` exit 0 ✓; `import pytest` OK (9.1.1) ✓; so-tron
phản ánh đúng chuẩn ✓; `test_workflow_graph_phase10.py` chạy riêng XANH (27s) ✓.
Lưu ý số liệu: trạm #1 đo "không pytest → 240/241", tôi đo 239/241 (17/08) và 237/241
(lần đầu GĐ0) — khác nhau phần đuôi phụ thuộc trạng thái venv, kết luận không đổi:
pytest bắt buộc.

## Việc để lại + lý do

- Cron chạy dò + kênh báo KHẨN: GĐ4 theo lộ trình.
- Đề xuất upstream (self-skip pytest thật + poll thay sleep): chờ chủ quyết có gửi không
  (repo mình private, quan hệ upstream chỉ fetch).

## Đề xuất cho GĐ2

- Trạm #1 soạn `nhiem-vu/GD2.md`: chốt danh sách chuỗi hiển thị cần đổi (P001/P003 — tôi
  sẽ grep toàn bộ "Javis OS" phía client trước khi sửa) + nguồn ảnh logo/favicon Thansa
  cho P002 (cần chủ cung cấp ảnh, hoặc chốt phương án tạm) + xác nhận image GHCR
  `ghcr.io/xahoapro/thansa-os` cho P005.
