"""Bộ cài mang tên Thansa: máy cài MỚI không còn tên javis, máy ĐANG CHẠY không gãy (P051).

Chạy: python tests/run.py ten_thansa_cai_dat
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import os
import re
import subprocess

FAIL = []


def check(label, ok):
    print(("PASS" if ok else "FAIL") + ": " + label)
    if not ok:
        FAIL.append(label)


def doc(p):
    return (ROOT / p).read_text(encoding="utf-8")


tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
goc = {t.split("/")[0] for t in tracked}

# ---- 1. File cài đặt / khởi động mang tên Thansa ----
for ten in ("start-thansa.bat", "start-thansa.vbs", "stop-thansa.bat", "stop-thansa.ps1",
            "thansa-autostart.bat", "thansa-autostart.ps1", "Thansa OS.bat", "Thansa OS.app",
            "Start Thansa OS.command", "Stop Thansa OS.command", "thansa.service"):
    check(f"có {ten}", ten in goc)
for ten in ("bin/thansa-start.sh", "bin/thansa-stop.sh", "bin/thansa-autostart.sh",
            "Thansa OS.app/Contents/MacOS/thansa"):
    check(f"có {ten}", ten in tracked)
# Chỉ HAI file cầu nối được phép mang tên javis ở gốc repo.
con_javis = sorted(t for t in goc if "javis" in t.lower())
check(f"gốc repo chỉ còn đúng 2 file cầu nối tên javis ({con_javis})",
      con_javis == ["start-javis.vbs", "stop-javis.bat"])
check("bin/ không còn script tên javis", not any(t.startswith("bin/") and "javis" in t for t in tracked))
plist = doc("Thansa OS.app/Contents/Info.plist")
check("app Mac: CFBundleExecutable khớp file chạy thật (thansa)",
      re.search(r"<key>CFBundleExecutable</key>\s*<string>thansa</string>", plist) is not None)

# ---- 2. Cầu nối cho máy Windows cài trước 1.19 ----
vbs = doc("start-javis.vbs")
check("start-javis.vbs chuyển tiếp sang start-thansa.vbs", "start-thansa.vbs" in vbs and "wscript" in vbs.lower())
bat = doc("stop-javis.bat")
check("stop-javis.bat chuyển tiếp sang stop-thansa.bat", 'call "%~dp0stop-thansa.bat"' in bat)
check("stop-thansa.bat vẫn dọn cửa sổ cũ tiêu đề 'Javis OS'", "WINDOWTITLE eq Javis OS*" in doc("stop-thansa.bat"))

# ---- 3. Máy cài mới không thấy file cầu nối ----
ins = doc("install.sh")
check("install.sh giấu file cầu nối bằng skip-worktree", "update-index --skip-worktree" in ins
      and "start-javis.vbs stop-javis.bat" in ins)
check("install.sh giấu cầu nối TRƯỚC mọi bước khác", ins.index("skip-worktree") < ins.index("# --- 1. python3"))
ps1 = doc("install.ps1")
check("install.ps1 đổi shortcut Startup cũ TRƯỚC khi giấu cầu nối",
      0 < ps1.index('"JAVIS OS.lnk"') < ps1.index("--skip-worktree"))
check("install.sh: unit mang tên Thansa + ghi JAVIS_SERVICE_NAME cho updater",
      "Description=Thansa OS ($SVC)" in ins and 'Environment="JAVIS_SERVICE_NAME=$SVC"' in ins)
check("install.sh: không còn chữ 'Javis OS is up'", "Javis OS is up" not in ins and "Thansa OS is up" in ins)

# ---- 4. Updater dò đúng dịch vụ/nhãn của máy cũ lẫn máy mới ----
import updater  # noqa: E402
_goc_run = updater.subprocess.run


class _R:
    def __init__(self, out):
        self.returncode, self.stdout = 0, out


def _gia(out):
    updater.subprocess.run = lambda *a, **k: _R(out)


os.environ.pop("JAVIS_SERVICE_NAME", None)
_gia("javis.service enabled enabled\nssh.service enabled enabled\n")
check("updater: máy cũ chỉ có javis.service -> javis", updater.systemd_unit() == "javis")
_gia("thansa.service enabled enabled\njavis.service disabled enabled\n")
check("updater: có thansa.service -> ưu tiên thansa", updater.systemd_unit() == "thansa")
_gia("thansa-shop.service enabled enabled\nthansa.service enabled enabled\n")
os.environ["JAVIS_SERVICE_NAME"] = "thansa-shop"
check("updater: unit ghi JAVIS_SERVICE_NAME -> đúng bản của mình", updater.systemd_unit() == "thansa-shop")
os.environ.pop("JAVIS_SERVICE_NAME", None)
_gia("ssh.service enabled enabled\n")
check("updater: không có dịch vụ Thansa -> chế độ khác (nohup)", updater.systemd_unit() == "" and not updater.has_systemd())
updater.subprocess.run = _goc_run
check("updater: không còn gọi cứng systemctl ... javis",
      '"systemctl", "stop", "javis"' not in doc("server/updater.py")
      and '"systemctl", "start", "javis"' not in doc("server/updater.py"))
check("updater gọi file Windows tên mới", "stop-thansa.bat" in doc("server/updater.py")
      and "start-thansa.vbs" in doc("server/updater.py"))

# ---- 5. Tự khởi động Windows: mục ThansaOS, máy cũ JavisOS được chuyển ----
main_src = doc("server/main.py")
check("autostart Windows: tên mục mới ThansaOS", '_AUTOSTART_NAME = "ThansaOS"' in main_src)
check("autostart Windows: chuyển mục JavisOS cũ (kèm cờ Task Manager) trước khi đọc/ghi",
      "def _autostart_chuyen_ten_cu" in main_src and main_src.count("_autostart_chuyen_ten_cu()") >= 2)

# ---- 6. Lệnh cài trong tài liệu ----
for f in ("README.md", "DEPLOY.md", "DEPLOY.en.md", "QUICKSTART.md"):
    t = doc(f)
    check(f"{f}: không còn clone vào thư mục javis", not re.search(r"\.git javis\b|cd javis\b|blogminhquy/javis-os\.git", t))
check("README: lệnh cài clone vào thansa-os", "thansa-os.git && cd thansa-os" in doc("README.md"))

# ---- 7. Link trong app không trỏ về repo Javis gốc ----
# guide_url Zalo trong catalog bị rebase lấy bản upstream làm quay về blogminhquy/javis-os HAI vòng
# liền (0.84.2, 0.84.8) - canh ở đây để vòng sau đỏ ngay thay vì lọt tới người dùng.
for f in ("system/mcp-catalog.json", "system/mcp-catalog.en.json", "dashboard/console.js", "server/updater.py"):
    check(f"{f}: không còn link repo Javis gốc", "blogminhquy/javis-os" not in doc(f))

if FAIL:
    raise SystemExit(f"\nFAIL - test_ten_thansa_cai_dat: {len(FAIL)} lỗi")
print("\nOK - test_ten_thansa_cai_dat: tất cả pass")
