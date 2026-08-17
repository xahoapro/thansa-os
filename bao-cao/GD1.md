# BÁO CÁO GĐ1 — Bộ hồ sơ ops/ + script dò + tự kiểm chứng (trạm #2, VPS)

Ngày: 2026-08-17. Thi hành theo `nhiem-vu/GD1.md` (trạm #1) + DAC-TA mục 2, 3, 7.

## Việc đã làm (commit trên nhánh me)

- `ops: khung ho so + script do + tu kiem chung (GD1)` — theo đúng kỷ luật commit của
  nhiệm vụ: KHÔNG nhãn `[me]` (để dành cho patch GĐ2), mapping rỗng, 0 == 0 ở luật 1.
  - `ops/moc-goc.json` — `thansa_version: "1.0"`, `goc_commit` SHA đầy đủ
    `0b8f2c092487c0b3b7f6a55a292deb4900d6f4c5`, `goc_version: "0.35.10"`,
    `ngay_tron: 2026-08-17`, `so_patch: 0`.
  - `ops/mapping.yaml` — danh sách RỖNG + comment tài liệu hoá đủ 7 trường.
  - `ops/so-tron.md` — khối "Khởi lập" (GĐ0 + GĐ1) + mục "Đã biết" ghi test nhạy timing.
  - `ops/ban-tin/.gitkeep` — thư mục bản tin vào git; bản tin `*.md` và con trỏ
    `ops/.last-do` là file cục bộ VPS (loại bằng `.git/info/exclude`, không đụng
    `.gitignore` upstream).
  - `ops/do-hang-ngay.sh` + `ops/tu-kiem-chung.sh` — đúng tên trong nhiệm vụ.
  - `ops/do-hang-ngay.py` + `ops/tu-kiem-chung.py` — ruột của 2 script trên.

## Lệch so với nhiệm vụ + lý do (trạm #1 phán quyết)

1. **Hai script `.sh` là vỏ bọc, ruột là python3**: bước "giao vung_theo_doi / so anh_goc"
   phải đọc `mapping.yaml` — YAML parse bằng bash thuần không tin cậy được. Python hệ
   thống của VPS có sẵn pyyaml. Giao diện đúng như nhiệm vụ: `bash ops/do-hang-ngay.sh`,
   `bash ops/tu-kiem-chung.sh`, exit code như đặc tả (dò: 2 = CỜ KHẨN; kiểm chứng: !=0 = đỏ).
2. **Tự kiểm chứng có thêm luật 4 (bổ sung)**: `so_patch` trong mốc gốc = số mục mapping —
   chặn quên cập nhật mốc gốc khi thêm patch ở GĐ2. Ba luật của mục 2.4 giữ nguyên.
3. **Lịch sử nhánh me đã viết lại một lần** (force-push): tôi khởi công GĐ1 theo lệnh
   trực tiếp của chủ TRƯỚC khi thấy `nhiem-vu/GD1.md` (commit 36a9004 đến trong lúc đang
   làm), bản đầu lệch kỷ luật (commit `[me] P006` + mapping tự khai). Đã reset về 36a9004,
   làm lại đúng nhiệm vụ. Nhánh me được phép force-push (quyết định #4).

## Kết quả tiêu chí ĐẠT

1. `bash ops/tu-kiem-chung.sh` → exit 0, XANH cả 3 luật (+ luật 4 bổ sung). ✓
2. `bash ops/do-hang-ngay.sh` → sinh `ops/ban-tin/2026-08-17.md` đúng định dạng 4 dòng cờ,
   `+0 commit` (upstream đứng yên từ lúc clone), "không giao" toàn bộ — hợp lệ. ✓
3. `json.load(moc-goc.json)` OK; `yaml.safe_load(mapping.yaml)` OK. ✓
4. `tests/run.py` trong goc theo cấu hình upstream (đã GỠ pytest khỏi `.venv` theo chốt
   của nhiệm vụ): 241/241 XANH. ✓ (5 test dạng pytest tự bỏ qua đúng thiết kế upstream)
5. Báo cáo này + push `me`. ✓

## Diễn tập bộ dò (làm ở bản nháp, đã dọn — không ảnh hưởng kết quả trên)

Lùi con trỏ dò 39 commit + patch giả P999 (đã xoá) để thử các nhánh logic trên dữ liệu thật:
- ĐỤNG VÙNG THEO DÕI: bắt đúng 22 file giao `dashboard/` + `server/main.py` ✓
- ẢNH GỐC LỆCH: đoạn thật khớp không báo oan; đoạn giả báo lệch ✓
- BẢO MẬT: bắt 5 commit chứa từ khoá (khớp ghi nhận "16/08 vá dồn dập" của đặc tả),
  CỜ KHẨN, exit 2 ✓

## Việc để lại + lý do

- Cron chạy dò + kênh báo KHẨN: GĐ4 theo lộ trình.
- Máy khác muốn chạy script ops cần python3 + pyyaml (VPS này có sẵn).

## Đề xuất cho GĐ2

- Trạm #1 soạn `nhiem-vu/GD2.md`: chốt danh sách chuỗi hiển thị cần đổi (P001/P003 — tôi
  sẽ grep toàn bộ "Javis OS" phía client trước khi sửa) và nguồn ảnh logo/favicon Thansa
  cho P002 (cần chủ cung cấp, hoặc chốt phương án tạm).
