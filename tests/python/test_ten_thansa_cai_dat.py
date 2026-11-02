"""Thansa OS 2.0.0 tách hẳn khỏi nguồn gốc: source KHÔNG còn tên gốc cũ nào (chủ chốt 01/11/2026).

Đổi tên bằng ops/doi_ten.py, và mỗi bản nguồn mới cũng đi qua đúng bộ đổi tên đó trước khi merge. Test này canh
lại kết quả: không file nào (trừ LICENSE - MIT bắt buộc ghi công tác giả gốc - và ops/, công cụ theo dõi nguồn)
mang tên gốc cũ trong tên file hay nội dung; và các bước "chuyển tên cũ" ngày trước không còn tự xoá nhầm file thật.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_fails = []


def check(name, ok):
    print(("ok   " if ok else "FAIL: ") + name)
    if not ok:
        _fails.append(name)


def doc(f):
    return (ROOT / f).read_text(encoding="utf-8", errors="replace")


TEN_CU = "ja" + "vis"          # ghép lúc chạy để chính file này không chứa tên cũ
MIEN = re.compile(r"^(LICENSE|ops/)")
tracked = [f for f in subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True)
           .stdout.split("\0") if f and not MIEN.match(f)]

# ---- 1. Không còn tên cũ ----
ten = [f for f in tracked if TEN_CU in f.lower()]
check(f"không file/thư mục nào mang tên cũ ({ten[:5]})", not ten)
noi_dung = []
for f in tracked:
    p = ROOT / f
    if not p.is_file() or p.is_symlink():
        continue
    try:
        if re.search(TEN_CU, p.read_text(encoding="utf-8"), re.I):
            noi_dung.append(f)
    except (UnicodeDecodeError, OSError):
        continue
check(f"không file nào còn tên cũ trong nội dung ({noi_dung[:5]})", not noi_dung)
check("LICENSE vẫn ghi công tác giả gốc (MIT)", "Copyright" in doc("LICENSE") and doc("LICENSE").count("Copyright") >= 2)

# ---- 2. File khởi động Windows là file THẬT, bộ cài không được giấu/xoá ----
for f in ("start-thansa.vbs", "stop-thansa.bat", "thansa-autostart.ps1"):
    check(f"{f} có trong repo", f in tracked)
for f in ("install.sh", "install.ps1"):
    check(f"{f} không skip-worktree/xoá start-thansa.vbs, stop-thansa.bat", "skip-worktree" not in doc(f))
check("thansa-autostart.ps1 không còn xoá 'mục cũ' (sau đổi tên chính là mục mới)", "$NameCu" not in doc("thansa-autostart.ps1"))
main_src = doc("server/main.py")
check("autostart Windows: tên mục ThansaOS", '_AUTOSTART_NAME = "ThansaOS"' in main_src)
check("không còn bước chuyển mục tự khởi động tên cũ", "_autostart_chuyen_ten_cu" not in main_src)
check("updater gọi file Windows tên Thansa", "stop-thansa.bat" in doc("server/updater.py")
      and "start-thansa.vbs" in doc("server/updater.py"))

# ---- 3. Repo của Thansa, không trỏ về repo nguồn ----
for f in ("system/mcp-catalog.json", "server/packs_store.py", "server/zalo_cli.py", "server/updater.py"):
    check(f"{f}: không trỏ repo blogminhquy", "blogminhquy" not in doc(f))
check("Store mặc định là xahoapro/thansa-store", "xahoapro/thansa-store" in doc("server/packs_store.py"))
check("Zalo tải từ xahoapro/thansa-zalo", "xahoapro/thansa-zalo" in doc("server/zalo_cli.py"))

if _fails:
    raise SystemExit(f"\nFAIL - test_ten_thansa_cai_dat: {len(_fails)} lỗi: {_fails}")
print("\nOK - test_ten_thansa_cai_dat")
