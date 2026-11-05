"""Cập nhật trên bản cài native/systemd không được làm CHẾT app.

Sự cố máy khách (Ubuntu 22.04, cài bằng install.sh, dịch vụ thansa.service) 07/10 và 09/10:
  1. Nút "Cập nhật ngay": updater chạy bằng start_new_session=True nhưng vẫn nằm trong cgroup
     của dịch vụ → `systemctl stop` ở bước dừng server giết luôn updater → app chết hẳn.
  2. `./update.sh`: `systemctl list-unit-files | grep -q` dưới pipefail ra 141 (SIGPIPE) dù khớp →
     tưởng không có systemd → rơi nhánh nohup tranh cổng với dịch vụ, phiên SSH treo.
  3. update.sh / install.sh thiếu bit thực thi trong git.
  4. update.sh không thấy npm do install.sh cài Node vào ~/.thansa/node.
  5. install.sh không nhận ra thiếu python3.X-venv → venv không có pip.

    python tests/run.py update_systemd
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("THANSA_STATE_DIR", tempfile.mkdtemp(prefix="thansa-updsysd-"))
import updater  # noqa: E402

_fails = []


def check(name, cond):
    print(("ok  " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


# ---- 1. updater không chết theo `systemctl stop` ----
# Từ nguồn 0.483.0 updater tự giao việc cho một unit systemd-run riêng (_systemd_worker_command), nên
# Thansa bỏ lối bọc `systemd-run --scope` của P062; main.py spawn updater thẳng như nguồn.
UPD_PY = (SERVER / "updater.py").read_text(encoding="utf-8")
check("updater giao việc cho worker systemd-run riêng", "def _systemd_worker_command(" in UPD_PY)
check("không còn lối bọc cgroup cũ", "lenh_tach_cgroup" not in UPD_PY)
MAIN = (SERVER / "main.py").read_text(encoding="utf-8")
check("main.py spawn updater thẳng", "subprocess.Popen(args, cwd=root, start_new_session=True)" in MAIN
      and "lenh_tach_cgroup" not in MAIN)

def bo_comment(text):
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


# ---- 2. không còn `| grep -q` dưới pipefail ----
UPD = (ROOT / "update.sh").read_text(encoding="utf-8")
check("update.sh không còn mẫu `| grep -q`", not re.search(r"\|\s*grep\s+-q", bo_comment(UPD)))
check("update.sh dò dịch vụ bằng `systemctl cat`", 'systemctl cat "$1.service"' in UPD)
check("update.sh chọn nhánh restart systemd bằng _co_unit", 'if _co_unit "$NAME"; then' in UPD)
check("nhánh nohup thả stdin (</dev/null) để phiên SSH không treo", "< /dev/null &" in UPD)
dinh = []
for f in sorted(list(ROOT.glob("*.sh")) + list((ROOT / "bin").glob("*.sh")) + list((ROOT / "ops").glob("*.sh"))):
    t = f.read_text(encoding="utf-8", errors="replace")
    if "pipefail" in t and re.search(r"\|\s*grep\s+-q", bo_comment(t)):
        dinh.append(f.name)
check("mọi *.sh có pipefail không dùng `| grep -q`", not dinh)

# Chạy thật: helper trong update.sh nhận ra unit/container dù lệnh in ra nhiều (đúng tình huống
# grep -q thoát sớm làm SIGPIPE).
if shutil.which("bash"):
    tmp = Path(tempfile.mkdtemp(prefix="thansa-fakebin-"))
    (tmp / "systemctl").write_text('#!/bin/sh\n[ "$1" = cat ] && [ "$2" = thansa.service ] && { seq 1 200000; exit 0; }\nexit 1\n')
    (tmp / "docker").write_text('#!/bin/sh\nseq 1 200000; echo thansa\n')
    for x in ("systemctl", "docker"):
        os.chmod(tmp / x, 0o755)
    helpers = "\n".join(ln for ln in UPD.splitlines() if ln.startswith(("_co_unit()", "_ds_container()", "_co_container()")))
    kich = ("set -euo pipefail\n" + helpers + "\n"
            "_co_unit thansa && echo UNIT_THANSA\n_co_unit khac || echo KHONG_KHAC\n"
            "_co_container thansa && echo CT_THANSA\n_co_container khac || echo KHONG_CT_KHAC\n")
    r = subprocess.run(["bash", "-c", kich], capture_output=True, text=True,
                       env={**os.environ, "PATH": f"{tmp}:{os.environ.get('PATH', '')}"})
    out = r.stdout.split()
    check("chạy thật: _co_unit thấy thansa.service, không thấy unit khác", "UNIT_THANSA" in out and "KHONG_KHAC" in out)
    check("chạy thật: _co_container thấy thansa giữa 200k dòng", "CT_THANSA" in out and "KHONG_CT_KHAC" in out)

# ---- 3. bit thực thi trong git ----
if shutil.which("git") and (ROOT / ".git").exists() or (ROOT / ".git").is_file():
    r = subprocess.run(["git", "ls-files", "-s", "update.sh", "install.sh"], cwd=ROOT, capture_output=True, text=True)
    modes = {ln.split()[-1]: ln.split()[0] for ln in r.stdout.splitlines() if ln.strip()}
    check("git: update.sh + install.sh mang mode 100755",
          modes.get("update.sh") == "100755" and modes.get("install.sh") == "100755")

# ---- 4. update.sh thấy npm của install.sh ----
check("update.sh đưa ~/.thansa/node/bin (và ~/.thansa/node/bin) vào PATH",
      '"$HOME/.thansa/node/bin"' in UPD and '"$HOME/.thansa/node/bin"' in UPD)

# ---- 5. install.sh nhận ra thiếu python3.X-venv ----
INS = (ROOT / "install.sh").read_text(encoding="utf-8")
check("install.sh kiểm ensurepip thay vì `-m venv --help`",
      '-c "import ensurepip"' in INS and "-m venv --help" not in bo_comment(INS))
check("install.sh cài đúng python3.X-venv", '"python${PY_XY}-venv"' in INS)
check("install.sh dựng lại .venv thiếu pip", "[ ! -x ./.venv/bin/pip ]" in INS)

if _fails:
    print(f"\n{len(_fails)} FAIL")
    sys.exit(1)
print("\nTẤT CẢ OK")
