# BÁO CÁO — Cập nhật trên bản native/systemd làm chết app (P062)

Trạm #2 (VPS) · 2026-10-09 · trả lời `nhiem-vu/BUG-update-systemd.md`. Nền: 1.26.0 (`origin/me` 76aef09).

## Tóm tắt

Sửa đủ 5 lỗi trong một patch `[me] P062`, thêm test `tests/python/test_update_systemd.py` (20 mục) và
một chỗ cùng lỗi pipefail mà nhiệm vụ chưa liệt kê (`bin/thansa-nginx-ssl.sh`).

## Thay đổi HÀNH VI (vùng logic - cần soát)

### Lỗi 1 - updater bị `systemctl stop` giết theo cgroup
- `server/updater.py`: thêm `_cgroup_dich_vu()` (đọc `/proc/self/cgroup`, bỏ qua `user@<uid>.service`) và
  `lenh_tach_cgroup(args)`: nếu tiến trình đang nằm trong một dịch vụ systemd, là root và có `systemd-run` thì
  bọc lệnh bằng `systemd-run --scope --quiet --collect --unit=thansa-update-<ts>`. Không thỏa thì giữ nguyên lệnh
  cũ (Windows, launchd, nohup, dịch vụ chạy User không phải root).
- `server/main.py` (`POST /update`, nhánh git không phải Windows): `Popen(_updmod.lenh_tach_cgroup(args), ...)`.
- Chọn cách (A) của nhiệm vụ. `--scope` giữ nguyên env (JAVIS_STATE_DIR, JAVIS_SERVICE_NAME...) và cwd, nên
  updater chạy y như trước, chỉ khác cgroup. KHÔNG đổi `KillMode` của unit: tiến trình con (Claude CLI...) vẫn
  bị dọn khi dừng dịch vụ như cũ.
- **Kiểm trên systemd thật (VPS này):** hai dịch vụ tạm `systemd-run` tự `systemctl stop`: con tách bằng
  `setsid` (cách cũ) → BỊ GIẾT; con bọc `systemd-run --scope` (cách mới) → SỐNG, ghi được file sau khi cha dừng.
- Giới hạn: dịch vụ chạy `User=` không phải root thì `systemd-run --scope` cần quyền → giữ lệnh cũ. Trường hợp đó
  `systemctl stop` của updater vốn cũng không có quyền, nên không tệ hơn trước.

### Lỗi 2 - `| grep -q` dưới pipefail
- `update.sh`: thêm `_co_unit` (`systemctl cat "$1.service"`), `_ds_container`, `_co_container` (grep trên
  here-string, không ống). Thay đủ 6 chỗ nhiệm vụ liệt kê (24-25, 27-28, 47, 54, 57, 83).
- Nhánh nohup thêm `< /dev/null` để tiến trình nền không giữ pty (phiên SSH chạy `update.sh` hết treo).
- **Thêm ngoài danh sách:** `bin/thansa-nginx-ssl.sh:170` (`ufw status | grep -q`, cũng `set -euo pipefail`) → có
  thể bỏ qua bước mở 80/443 trên ufw. Đã sửa cùng kiểu.
- Tái hiện SIGPIPE: `bash -c 'set -o pipefail; seq 1 300000 | grep -q "^1$"; echo $?'` → 141.
- Chặn tái phát: test quét MỌI `*.sh` ở gốc, `bin/`, `ops/` có `pipefail` không được chứa `| grep -q` (bỏ comment),
  và chạy thật các helper với `systemctl`/`docker` giả in 200k dòng.

### Lỗi 3 - bit thực thi
- `git update-index --chmod=+x update.sh install.sh` → `100755`. Các `*.sh` khác vốn đã 755.

### Lỗi 4 - npm not found
- Đầu `update.sh`: đưa `~/.thansa/node/bin`, `~/.javis/node/bin` (máy cũ), `~/.local/bin` vào PATH nếu có.
  (install.sh hiện cài Node vào `~/.thansa/node`, không phải `~/.javis/node` như nhiệm vụ ghi.)

### Lỗi 5 - thiếu python3.X-venv
- `install.sh`: kiểm `import ensurepip`; thiếu thì `apt-get install python<X.Y>-venv` (lùi `python3-venv`).
  `.venv` đã có mà không có `bin/pip` → xoá dựng lại.

## Chưa làm
- PATH unit cũ thiếu `/usr/sbin` (mục "đã vá - ghi nhận"): chưa thêm migration sửa unit có sẵn.
- Báo upstream javis-os (lỗi 1, 2 có từ gốc): chưa có kênh tự động - để chủ quyết.
- Tiêu chí 2 (bấm Cập nhật trên máy native/systemd KHÔNG drop-in) cần máy khách thật: VPS này chạy kiểu nohup.
  Cơ chế đã chứng minh bằng dịch vụ tạm như trên.

## Test
- `test_update_systemd` 20/20; `test_nhieu_ban_mot_vps` (sửa chuỗi `_co_container "$NAME"`), `test_update*`,
  `test_updater_*`, `test_ten_thansa_cai_dat` xanh. Suite đầy đủ chạy bằng venv cài đúng requirements.txt + pytest
  (KHÔNG dùng goc/.venv - fastapi cũ, xem P060).
