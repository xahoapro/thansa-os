"""Cập nhật trên bản cài native/systemd không được làm CHẾT app.

Sự cố máy khách (Ubuntu 22.04, cài bằng install.sh, dịch vụ javis.service) 07/10 và 09/10:
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

os.environ.setdefault("JAVIS_STATE_DIR", tempfile.mkdtemp(prefix="javis-updsysd-"))
import updater  # noqa: E402

_fails = []


def check(name, cond):
    print(("ok  " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


# ---- 1. updater ra khỏi cgroup của dịch vụ ----
CG_DV = "0::/system.slice/javis.service\n"
CG_SSH = "0::/user.slice/user-1000.slice/user@1000.service/app.slice/tmux-spawn-1.scope\n"
CG_PHIEN = "0::/user.slice/user-1000.slice/session-5.scope\n"
check("nhận ra đang trong dịch vụ javis.service", updater._cgroup_dich_vu(CG_DV) == "javis.service")
check("phiên SSH/tmux (user@.service) KHÔNG tính là dịch vụ", updater._cgroup_dich_vu(CG_SSH) == "")
check("phiên đăng nhập thường không phải dịch vụ", updater._cgroup_dich_vu(CG_PHIEN) == "")
check("cgroup v1 nhiều dòng vẫn nhận ra",
      updater._cgroup_dich_vu("12:pids:/system.slice/thansa.service\n1:name=systemd:/system.slice/thansa.service\n")
      == "thansa.service")

args = ["/venv/bin/python", "updater.py", "--port", "7777"]
l = updater.lenh_tach_cgroup(args, cgroup_text=CG_DV, euid=0, systemd_run="/usr/bin/systemd-run", now=123)
check("root trong dịch vụ: bọc systemd-run --scope", l[:3] == ["/usr/bin/systemd-run", "--scope", "--quiet"]
      and "--collect" in l and "--unit=thansa-update-123" in l and l[-len(args):] == args)
check("không nằm trong dịch vụ: giữ lệnh cũ",
      updater.lenh_tach_cgroup(args, cgroup_text=CG_PHIEN, euid=0, systemd_run="/usr/bin/systemd-run") == args)
check("không có systemd-run: giữ lệnh cũ",
      updater.lenh_tach_cgroup(args, cgroup_text=CG_DV, euid=0, systemd_run="") == args)
check("không phải root: giữ lệnh cũ (systemd-run --scope cần quyền)",
      updater.lenh_tach_cgroup(args, cgroup_text=CG_DV, euid=1000, systemd_run="/usr/bin/systemd-run") == args)
MAIN = (SERVER / "main.py").read_text(encoding="utf-8")
check("main.py spawn updater qua lenh_tach_cgroup",
      "subprocess.Popen(_updmod.lenh_tach_cgroup(args), cwd=root, start_new_session=True)" in MAIN)


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
    tmp = Path(tempfile.mkdtemp(prefix="javis-fakebin-"))
    (tmp / "systemctl").write_text('#!/bin/sh\n[ "$1" = cat ] && [ "$2" = javis.service ] && { seq 1 200000; exit 0; }\nexit 1\n')
    (tmp / "docker").write_text('#!/bin/sh\nseq 1 200000; echo javis\n')
    for x in ("systemctl", "docker"):
        os.chmod(tmp / x, 0o755)
    helpers = "\n".join(ln for ln in UPD.splitlines() if ln.startswith(("_co_unit()", "_ds_container()", "_co_container()")))
    kich = ("set -euo pipefail\n" + helpers + "\n"
            "_co_unit javis && echo UNIT_JAVIS\n_co_unit thansa || echo KHONG_THANSA\n"
            "_co_container javis && echo CT_JAVIS\n_co_container thansa || echo KHONG_CT_THANSA\n")
    r = subprocess.run(["bash", "-c", kich], capture_output=True, text=True,
                       env={**os.environ, "PATH": f"{tmp}:{os.environ.get('PATH', '')}"})
    out = r.stdout.split()
    check("chạy thật: _co_unit thấy javis.service, không thấy thansa", "UNIT_JAVIS" in out and "KHONG_THANSA" in out)
    check("chạy thật: _co_container thấy javis giữa 200k dòng", "CT_JAVIS" in out and "KHONG_CT_THANSA" in out)

# ---- 3. bit thực thi trong git ----
if shutil.which("git") and (ROOT / ".git").exists() or (ROOT / ".git").is_file():
    r = subprocess.run(["git", "ls-files", "-s", "update.sh", "install.sh"], cwd=ROOT, capture_output=True, text=True)
    modes = {ln.split()[-1]: ln.split()[0] for ln in r.stdout.splitlines() if ln.strip()}
    check("git: update.sh + install.sh mang mode 100755",
          modes.get("update.sh") == "100755" and modes.get("install.sh") == "100755")

# ---- 4. update.sh thấy npm của install.sh ----
check("update.sh đưa ~/.thansa/node/bin (và ~/.javis/node/bin) vào PATH",
      '"$HOME/.thansa/node/bin"' in UPD and '"$HOME/.javis/node/bin"' in UPD)

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
