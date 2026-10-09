# NHIỆM VỤ (BUG — ưu tiên cao) — Cập nhật trên bản native/systemd làm CHẾT app

Trạm #1 soạn · 2026-10-09 · cho trạm #2 (VPS). Nền kiểm: **1.26.0** (`origin/main` c8c809c, `origin/me` 76aef09) — CHƯA có bản vá nào cho các lỗi dưới đây.

Máy dính sự cố: VPS khách `180.93.126.6` (Ubuntu 22.04, cài native bằng `install.sh`, dịch vụ `javis.service`, User=root,
nginx + certbot cho `longtrader.tradingauto.org`). Máy đó đã được vá TẠI CHỖ để chạy tạm (xem cuối file) — repo vẫn lỗi
nên mọi máy native/systemd khác đều dính.

---

## LỖI 1 (NGHIÊM TRỌNG) — Nút "Cập nhật ngay" trên web giết chính updater → app chết hẳn

### Triệu chứng (xảy ra 2 lần: 07/10 03:01 và 09/10 08:26)
- Bấm "Cập nhật ngay" → web chết (nginx 502), KHÔNG tự lên lại; code vẫn bản cũ.
- `server/update.log` dừng đúng tại:
  ```
  [03:01:38] Chế độ restart: systemd
  [03:01:38] Dừng server cũ…
  ```
- `systemctl status javis` → `inactive (dead)`, `code=killed, signal=TERM`.

### Nguyên nhân
- `server/main.py` (1.26.0 ~dòng 12243–12247) spawn updater bằng
  `subprocess.Popen(args, cwd=root, start_new_session=True)`.
  `start_new_session` chỉ tách **session/process group**, KHÔNG tách **cgroup** → updater vẫn nằm trong cgroup của dịch vụ.
- `server/updater.py` `stop_server()` nhánh `systemd` (dòng 190) gọi `systemctl stop <unit>`. `KillMode` mặc định
  `control-group` → systemd giết MỌI tiến trình trong cgroup, gồm cả updater → không bao giờ tới `start_server()` (dòng 213).

### Cách sửa đề xuất (chọn 1)
- **(A, khuyến nghị)** Ở `main.py`, khi `mode == "systemd"`, chạy updater NGOÀI cgroup dịch vụ:
  ```python
  args = ["systemd-run", "--scope", "--quiet", "--collect", f"--unit=thansa-update-{int(time.time())}"] + args
  ```
  (hoặc transient service `systemd-run --unit=... --collect --working-directory=<root> ...`). Có fallback về Popen cũ nếu
  không có `systemd-run`.
- **(B)** Trong `updater.py` nhánh systemd: KHÔNG stop rồi start; làm pull/pip trước khi đụng dịch vụ rồi gọi
  `systemctl restart --no-block <unit>` làm bước cuối và để health-check chạy từ tiến trình ngoài cgroup (vẫn cần A nếu
  muốn rollback được).
- **(C, chữa cháy ở installer)** `install.sh` thêm `KillMode=process` vào unit. Hệ quả: tiến trình con (Claude CLI…) mồ côi
  khi stop — chỉ nên dùng nếu chưa làm được A.

### Kiểm chứng đã làm (trạm #1, trên 180.93.126.6)
Thêm drop-in `KillMode=process` → login + `POST /update` → web tắt ~5s, lên lại ở giây 10, `update.log` chạy đủ
`fetch/merge/stash apply/pip/khởi động/health=True → success`. Xác nhận nguyên nhân đúng là cgroup kill.

---

## LỖI 2 (NGHIÊM TRỌNG) — `update.sh` nhận nhầm "không có systemd" → chạy nohup tranh cổng với dịch vụ

### Triệu chứng (09/10 00:13–00:18)
- `./update.sh` → dịch vụ quay vòng ~30 lần: `[Errno 98] ... ('0.0.0.0', 7777): address already in use`.
- `server/javis.log` mới xuất hiện: `Uvicorn running on http://127.0.0.1:7777` (bản nohup thả nổi).
- Truy cập IP:7777 chết; phiên SSH chạy `update.sh` TREO (tiến trình nohup giữ pty). Chỉ hết khi reboot.

### Nguyên nhân
- `update.sh` có `set -euo pipefail`. Mọi điều kiện dạng `lệnh | grep -q ...`: grep -q khớp xong thoát ngay → lệnh bên trái
  chết SIGPIPE (141) → với pipefail CẢ ỐNG = SAI dù đã khớp.
- Tái hiện trên máy thật:
  `bash -c 'set -o pipefail; systemctl list-unit-files | grep -q "^javis\.service"; echo $?'` → **141** dù `javis.service` tồn tại.
- Chỗ dính trong `update.sh` (1.26.0): dòng **24–25** (docker javis/thansa), **27–28** (systemd javis/thansa — có thể chọn
  sai tên dịch vụ), **47** (`is_docker`), **54** (caddy), **57** (`ss | grep -q .`), **83** (chọn nhánh restart systemd →
  rơi xuống nhánh nohup: kill PID cổng 7777 + chạy uvicorn `--host ${JAVIS_HOST:-127.0.0.1}`).
- Lỗi có từ upstream javis-os (`goc/update.sh:56`) → mỗi vòng trộn sẽ kéo lại nếu chỉ sửa tay.

### Cách sửa (đã chạy đúng trên 180.93.126.6)
Thêm ngay sau dòng `SUDO=...`:
```bash
# KHÔNG viết `lệnh | grep -q` trong file này: dưới pipefail, grep -q thoát sớm → SIGPIPE 141 → điều kiện SAI dù khớp.
_co_unit() { command -v systemctl >/dev/null 2>&1 && systemctl cat "$1.service" >/dev/null 2>&1; }
_ds_container() { command -v docker >/dev/null 2>&1 && docker ps -a --format '{{.Names}}' 2>/dev/null || true; }
_co_container() { local ds; ds="$(_ds_container)"; [ -n "$ds" ] && grep -qx "$1" <<<"$ds"; }
```
Thay:
- dòng 24–25 → `if _co_container javis && ! _co_container thansa; then`
- dòng 27–28 → `elif _co_unit javis && ! _co_unit thansa; then`
- dòng 47 → `_co_container "$NAME"`
- dòng 54 → `if _co_container "$NAME-caddy"; then`
- dòng 57 → `elif command -v ss >/dev/null 2>&1 && [ -n "$(ss -tlnH '( sport = :80 or sport = :443 )' 2>/dev/null)" ]; then`
- dòng 83 → `if _co_unit "$NAME"; then`

### Test phải sửa kèm
`tests/python/test_nhieu_ban_mot_vps.py:172` đang kiểm chuỗi `'grep -qx "$NAME"'` → đổi thành `'_co_container "$NAME"'`, và thêm:
- `update.sh` không còn mẫu `\|\s*grep -q` (bỏ qua phần comment);
- `update.sh` chứa `systemctl cat "$1.service"`.

### Gợi ý chặn tái phát
Thêm vào `tu-kiem-chung.py` (hoặc test) một kiểm tra quét MỌI `*.sh` có `pipefail` không được chứa `| grep -q`.
Ghi vào `mapping.yaml` mục `vung_theo_doi` cho `update.sh` để vòng trộn upstream không đè mất.

---

## LỖI 3 (nhỏ) — `update.sh` / `install.sh` không có bit thực thi trong git
- `git ls-tree origin/main update.sh install.sh` → `100644`. `./update.sh` → `Permission denied`.
- README bảo người dùng `chmod +x install.sh` → tạo thay đổi mode cục bộ → `git pull --ff-only` của `update.sh`
  bị chặn mỗi khi upstream sửa file đó.
- Sửa: `git update-index --chmod=+x update.sh install.sh` (và các `*.sh` khác người dùng chạy trực tiếp).

## LỖI 4 (nhỏ) — `update.sh` báo "npm not found" trên máy cài bằng install.sh
- `install.sh` cài Node vào `~/.javis/node/bin` nhưng `update.sh` không đưa thư mục đó vào PATH → Codex không bao giờ được
  cập nhật (`[!] npm not found; update Codex by hand...`).
- Sửa: đầu `update.sh` thêm `[ -d "$HOME/.javis/node/bin" ] && PATH="$HOME/.javis/node/bin:$PATH"`
  (và đường tương ứng nếu bản mới đổi sang `~/.thansa/node`).

## LỖI 5 (nhỏ) — `install.sh` không phát hiện thiếu `python3.X-venv` (Ubuntu 22.04)
- `install.sh:103` chỉ kiểm `"$PYTHON_BIN" -m venv --help` → câu này CHẠY ĐƯỢC dù thiếu gói `python3.10-venv`, nhưng
  `python -m venv .venv` tạo venv KHÔNG có pip → chết ở `./.venv/bin/pip: No such file or directory`.
- Sửa: kiểm bằng `"$PYTHON_BIN" -c "import ensurepip"`; thiếu thì
  `apt-get install -y "python$("$PYTHON_BIN" -c 'import sys;print(f"{sys.version_info[0]}.{sys.version_info[1]}")')-venv"`;
  và nếu `.venv` đã có mà thiếu `.venv/bin/pip` thì xoá dựng lại (giống nhánh kiểm phiên bản Python ở dòng ~200).

## (Đã vá — chỉ ghi nhận) PATH của unit thiếu `/usr/sbin`
`install.sh:387` của 1.26.0 đã có `/usr/sbin:/sbin` → certbot tìm được nginx. Máy cài trước bản vá vẫn mang unit cũ:
cân nhắc để `update.sh` / migration tự thêm `/usr/sbin:/sbin` vào PATH unit hiện có.

---

## Kỷ luật
- Lỗi 1–2 là vùng LOGIC (không phải rebrand) → mô tả rõ thay đổi hành vi trong báo cáo, để trạm #1/chủ soát.
- Lấy mã patch mới tiếp theo (P060/P061 đã dùng) — gợi ý `[me] P062: update an toan tren systemd (cgroup + pipefail)`.
- Cập nhật `mapping.yaml` + `so_patch`; giữ `tu-kiem-chung.py` XANH. KHÔNG force push.
- Báo cho upstream javis-os nếu có kênh (lỗi 1 và 2 có từ gốc).

## Tiêu chí ĐẠT
1. `tests/run.py` full XANH, gồm các kiểm tra mới cho `update.sh`.
2. Trên một máy native/systemd thật (unit KHÔNG có drop-in KillMode):
   - bấm "Cập nhật ngay" → app tự lên lại, `update.log` kết thúc `→ success`;
   - `./update.sh` → restart qua systemd, `ps` chỉ có MỘT uvicorn, nghe đúng `JAVIS_HOST` của unit, lệnh SSH kết thúc bình thường.
3. `git ls-tree origin/main update.sh install.sh` → `100755`.
4. Ghi `bao-cao/` + `so-tron.md`. Push `me`. Báo trạm #1 nghiệm thu → chủ duyệt phát hành.

## Sau khi phát hành bản vá — dọn máy 180.93.126.6 (trạm #1 làm)
- Gỡ drop-in: `rm /etc/systemd/system/javis.service.d/killmode.conf && systemctl daemon-reload`
- Bỏ bản vá tại chỗ trước khi cập nhật: `cd /root/javis && git checkout -- update.sh install.sh`
  (bản gốc lưu ở `/root/update.sh.goc`).
