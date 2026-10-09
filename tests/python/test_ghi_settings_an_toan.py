"""settings.json không bao giờ bị "reset về mặc định" vì một lần đọc trúng lúc file đang ghi dở.

Sự cố Thansa 08/10: settings.json bị reset gần hết về mặc định (mật khẩu admin, Discord, Slack,
Lark, voice...) mà không có request ghi nào. Cơ chế: write_text cắt file về 0 byte rồi mới ghi;
luồng khác đọc đúng lúc đó → json lỗi → read_settings nuốt lỗi trả bộ MẶC ĐỊNH → caller sửa một
mục rồi ghi cả bộ xuống. File này khoá ba lớp chặn:
  1. Ghi nguyên tử (file tạm + os.replace): người đọc không bao giờ thấy file dở.
  2. Đọc lỗi thì lùi về bản đọc tốt gần nhất, không trả mặc định.
  3. write_settings không ghi auth rỗng đè lên mật khẩu đang có, trừ khi caller nói rõ.

    python tests/run.py ghi_settings_an_toan
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import json
import os
import sys
import tempfile
import threading
from pathlib import Path

state = tempfile.mkdtemp(prefix="javis-ghiset-")
os.environ["JAVIS_STATE_DIR"] = state

import config as cfg  # noqa: E402

_fails = []


def check(name, cond):
    print(("ok  " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


P = Path(cfg.SETTINGS_PATH)


def co_mat_khau(c):
    return bool(((c.get("auth") or {}).get("password_hash")))


# ---- chuẩn bị: một admin thật + vài kênh ----
s = cfg.read_settings()
h, salt = cfg.hash_password("matkhau-that-dai")
s["auth"] = {"username": "chu", "password_hash": h, "salt": salt}
s.setdefault("discord", {})["enabled"] = True
cfg.write_settings(s)
check("chuẩn bị: có mật khẩu trên đĩa", co_mat_khau(json.loads(P.read_text(encoding="utf-8"))))
check("ghi nguyên tử không để lại file tạm", not [f for f in os.listdir(state) if f.endswith(".tmp")])

# ---- 2. file hỏng giữa chừng: đọc lùi về bản tốt, KHÔNG trả mặc định ----
tot = P.read_text(encoding="utf-8")
P.write_text(tot[: len(tot) // 2], encoding="utf-8")       # giả lập file đang ghi dở
c = cfg.read_settings()
check("file dở: read_settings vẫn có mật khẩu (bản tốt gần nhất)", co_mat_khau(c))
check("file dở: read_settings vẫn giữ kênh Discord", (c.get("discord") or {}).get("enabled") is True)
P.write_text(tot, encoding="utf-8")

# ---- 3. chốt cuối: cfg mặc định (auth rỗng) không ghi đè được mật khẩu ----
mac_dinh = json.loads(json.dumps(cfg._DEFAULT))
mac_dinh.setdefault("model", {})["ghi_chu"] = "caller sửa một mục trên cfg hỏng"
cfg.write_settings(mac_dinh)
tren_dia = json.loads(P.read_text(encoding="utf-8"))
check("ghi cfg auth rỗng: mật khẩu trên đĩa được GIỮ", co_mat_khau(tren_dia))
check("...và mục caller sửa vẫn được ghi", (tren_dia.get("model") or {}).get("ghi_chu"))

# ---- 4. tắt đăng nhập có chủ ý vẫn làm được ----
c = cfg.read_settings()
c["auth"] = {"username": "", "password_hash": "", "salt": ""}
cfg.write_settings(c, cho_xoa_mat_khau=True)
check("cho_xoa_mat_khau=True: xoá được mật khẩu (đường /auth/disable)",
      not co_mat_khau(json.loads(P.read_text(encoding="utf-8"))))
_src = (SERVER / "main.py").read_text(encoding="utf-8")
check("/auth/disable truyền cho_xoa_mat_khau=True", "cfgmod.write_settings(cfg, cho_xoa_mat_khau=True)" in _src)

# ---- 5. đọc/ghi song song: không lần đọc nào mất mật khẩu ----
c = cfg.read_settings()
c["auth"] = {"username": "chu", "password_hash": h, "salt": salt}
cfg.write_settings(c)
mat = []
dung = threading.Event()


def doc():
    while not dung.is_set():
        cfg._SETTINGS_CACHE["sig"] = None             # ép đọc đĩa thật mỗi lần
        if not co_mat_khau(cfg.read_settings()):
            mat.append(1)


def ghi():
    for i in range(150):
        x = cfg.read_settings()
        x.setdefault("model", {})["dem"] = i
        cfg.write_settings(x)


t = [threading.Thread(target=doc) for _ in range(3)]
for x in t:
    x.start()
g = threading.Thread(target=ghi)
g.start()
g.join()
dung.set()
for x in t:
    x.join()
check("150 lần ghi xen 3 luồng đọc: không lần nào thấy mất mật khẩu", not mat)
check("cuối cùng mật khẩu vẫn còn", co_mat_khau(json.loads(P.read_text(encoding="utf-8"))))

# ---- 6. file hỏng hẳn lúc khởi động (chưa có bản tốt): không ghi đè mất dấu ----
cfg._SETTINGS_CACHE["sig"] = None
cfg._SETTINGS_CACHE["cfg"] = None
P.write_text('{"auth": {"password_hash": "abc", ', encoding="utf-8")
c = cfg.read_settings()
cfg.write_settings(c)
hong = [f for f in os.listdir(state) if f.startswith("settings.json.hong-")]
check("file hỏng lúc khởi động: bản hỏng được cất lại (settings.json.hong-*) để cứu tay", bool(hong))

if _fails:
    print(f"\n{len(_fails)} FAIL")
    sys.exit(1)
print("\nTẤT CẢ OK")
