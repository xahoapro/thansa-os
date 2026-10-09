"""Request từ NGOÀI máy (qua nginx / IP lạ) luôn phải đăng nhập, kể cả khi CHƯA có mật khẩu.

Sự cố 08/10: bản nghe 127.0.0.1 sau nginx dựng tay (thiếu domain.proxy=nginx), auth trong
settings.json bị xoá trắng → require_login() tưởng chạy cá nhân → ai gõ https://<ip>/ cũng
vào thẳng dashboard, đọc /settings và mở /ws. Giờ: chưa có mật khẩu mà đến từ ngoài thì chỉ
vào được màn TẠO tài khoản; trình duyệt trên chính máy / SSH tunnel vẫn như cũ.

    python tests/run.py cong_ngoai_bat_dang_nhap
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import os
import sys
import tempfile

os.environ["JAVIS_STATE_DIR"] = tempfile.mkdtemp(prefix="javis-congngoai-")
os.environ.pop("JAVIS_REQUIRE_LOGIN", None)
os.environ["JAVIS_HOST"] = "127.0.0.1"

import config as cfg                           # noqa: E402
import main                                    # noqa: E402
from starlette.testclient import TestClient    # noqa: E402

_fails = []


def check(name, cond):
    print(("ok  " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


class _Conn:
    def __init__(self, client="127.0.0.1", **headers):
        self.headers = {k.replace("_", "-"): v for k, v in headers.items()}
        self.client = type("C", (), {"host": client})() if client else None


# ---- 1. Hàm thuần ----
check("cục bộ, không header proxy → không phải ngoài", not cfg.den_tu_ngoai(_Conn()))
check("qua nginx (X-Forwarded-For) → ngoài", cfg.den_tu_ngoai(_Conn(x_forwarded_for="1.2.3.4")))
check("qua nginx (X-Real-IP) → ngoài", cfg.den_tu_ngoai(_Conn(x_real_ip="1.2.3.4")))
check("client IP LAN/Internet → ngoài", cfg.den_tu_ngoai(_Conn(client="203.0.113.9")))
check("không có conn → giữ hành vi cũ", not cfg.den_tu_ngoai(None))
check("chưa mật khẩu + cục bộ → không chặn (UX cá nhân giữ nguyên)", cfg.gate_active(_Conn()) is False)
check("chưa mật khẩu + qua nginx → chặn", cfg.gate_active(_Conn(x_forwarded_for="1.2.3.4")) is True)
os.environ["JAVIS_REQUIRE_LOGIN"] = "0"
check("JAVIS_REQUIRE_LOGIN=0 KHÔNG mở cửa cho request từ ngoài",
      cfg.require_login(_Conn(x_real_ip="1.2.3.4")) is True)
os.environ.pop("JAVIS_REQUIRE_LOGIN", None)

# ---- 2. Qua app thật ----
c = TestClient(main.app)   # client.host = "testclient" ≈ cục bộ
NGOAI = {"X-Forwarded-For": "194.110.87.242", "X-Real-IP": "194.110.87.242", "Host": "117.2.213.176"}

r = c.get("/settings", headers=NGOAI)
check("qua IP, chưa mật khẩu: /settings → 401 setup_required",
      r.status_code == 401 and r.json().get("setup_required") is True)
s = c.get("/auth/status", headers=NGOAI).json()
check("qua IP: /auth/status báo phải tạo tài khoản, chưa authed",
      s.get("needs_setup") is True and s.get("auth_required") is True and s.get("authed") is False)
check("qua IP: màn chính / vẫn mở để hiện form tạo tài khoản", c.get("/", headers=NGOAI).status_code == 200)

try:
    with c.websocket_connect("/ws", headers=NGOAI) as ws:
        ws.receive_text()
    ws_ok = False
except Exception:
    ws_ok = True
check("qua IP, chưa mật khẩu: /ws bị từ chối", ws_ok)

LOCAL_AUTHED = c.get("/auth/status", headers={"Host": "localhost:7777"}).json().get("authed")
r = c.post("/auth/setup", data={"username": "x", "password": "ngan"}, headers={"Host": "localhost:7777"})
check("trên chính máy: KHÔNG đòi mã (lỗi chỉ là mật khẩu ngắn)", r.status_code == 400 and not r.json().get("need_setup_code"))

# ---- 3. Mã cài đặt khi tạo admin TỪ NGOÀI máy ----
s = c.get("/auth/status", headers=NGOAI).json()
check("qua IP: /auth/status đòi mã cài đặt và chỉ đường tới file",
      s.get("setup_code_required") is True and s.get("setup_code_path", "").endswith(".setup_token"))
r = c.post("/auth/setup", headers=NGOAI, data={"username": "ke-la", "password": "matkhau-ke-la"})
check("qua IP, thiếu mã: KHÔNG tạo được admin",
      r.status_code == 403 and r.json().get("need_setup_code") and not cfg.auth_enabled())
r = c.post("/auth/setup", headers=NGOAI, data={"username": "ke-la", "password": "matkhau-ke-la", "setup_token": "AAAAAAAA"})
check("qua IP, sai mã: KHÔNG tạo được admin", r.status_code == 403 and not cfg.auth_enabled())
ma = cfg.ma_cai_dat()
check("mã 8 ký tự, file chỉ chủ đọc được",
      len(ma) == 8 and (os.stat(cfg.ma_cai_dat_path()).st_mode & 0o077) == 0)
r = c.post("/auth/setup", headers=NGOAI, data={"username": "chu", "password": "matkhau-chu-may", "setup_token": ma.lower()})
check("qua IP, đúng mã (gõ thường cũng được): tạo được admin", r.status_code == 200 and cfg.auth_enabled())
check("tạo xong thì mã bị dọn (dùng một lần)", not os.path.exists(cfg.ma_cai_dat_path()))
c.cookies.clear()
r = c.get("/settings", headers=NGOAI)
check("đã có admin: qua IP vẫn phải đăng nhập", r.status_code == 401 and not r.json().get("setup_required"))
r = c.get("/settings", headers={"Host": "localhost:7777"})
check("đã có admin: trên chính máy cũng phải đăng nhập", r.status_code == 401)
s2 = c.get("/auth/status", headers=NGOAI).json()
check("đã có admin: không còn đòi mã", s2.get("setup_code_required") is False)

s = {"authed": LOCAL_AUTHED}
check("trình duyệt trên chính máy: vẫn vào thẳng như cũ", s.get("authed") is True)

if _fails:
    print(f"\n{len(_fails)} FAIL")
    sys.exit(1)
print("\nTẤT CẢ OK")
