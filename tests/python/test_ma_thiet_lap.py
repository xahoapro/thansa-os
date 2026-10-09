"""Thiết lập lần đầu TRÊN CHÍNH MÁY chỉ cần TÊN + MẬT KHẨU (0.64.47); mở từ NGOÀI máy thì
đòi thêm mã cài đặt (Thansa, sau sự cố 08/10 - xem test_cong_ngoai_bat_dang_nhap.py).

    python tests/python/test_ma_thiet_lap.py

Trước 0.64.47, chạy public (VPS/Docker) mà chưa có admin thì /auth/setup đòi một mã chỉ in ra
log server. Chủ dự án chốt 24/09: đã có 2FA, bỏ mã đi, màn chào mừng chỉ hỏi tên và mật khẩu.
Máy cài bằng install.sh vẫn có admin sẵn từ .env nên không bao giờ thấy màn này.

File này GỌI THẬT endpoint ở chế độ public và khoá lại:
  1. Tạo được admin chỉ với tên + mật khẩu, không gửi mã nào.
  2. Rào còn lại vẫn đứng: mật khẩu tối thiểu 8 ký tự; đã có admin thì không tạo đè được.
  3. Client cũ còn gửi `setup_token` thì vẫn chạy, không lỗi.
  4. Mã cài đặt chỉ là nhánh HẸP: ô nhập ẩn mặc định, lúc khởi động có admin thì dọn file mã.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import json
import os
import tempfile
from pathlib import Path

state = tempfile.mkdtemp(prefix="javis-setup-")
os.environ["JAVIS_STATE_DIR"] = state
os.environ["BRAINS_DIR"] = str(Path(state) / "brains")
os.environ["JAVIS_SESSIONS_DB"] = str(Path(state) / "sessions.db")
os.environ["JAVIS_REQUIRE_LOGIN"] = "1"      # giả lập deploy public

import main  # noqa: E402
import config as cfgmod  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

fails = []


def check(ten, dieu_kien, them=""):
    print(("ok   " if dieu_kien else "FAIL ") + ten + (("  [" + str(them) + "]") if not dieu_kien and them else ""))
    if not dieu_kien:
        fails.append(ten)


app = FastAPI()
app.post("/auth/setup")(main.auth_setup)
client = TestClient(app)

check("đang giả lập server public, bắt buộc đăng nhập", cfgmod.require_login())
check("và chưa có admin", not cfgmod.auth_enabled())

# ---- 2. Rào mật khẩu vẫn đứng (thử TRƯỚC khi tạo admin) ----
r = client.post("/auth/setup", data={"username": "quy", "password": "ngan"})
check("mật khẩu dưới 8 ký tự vẫn bị chặn", r.status_code == 400 and not cfgmod.auth_enabled(), r.text)

# ---- 1. Tên + mật khẩu là đủ ----
r = client.post("/auth/setup", data={"username": "quy", "password": "matkhau-dai-du"})
check("CANARY: public + chưa admin, tạo được admin CHỈ với tên + mật khẩu", r.status_code == 200 and r.json().get("ok"), r.text)
check("admin đã được ghi, đúng tên", cfgmod.auth_enabled() and cfgmod.read_settings()["auth"]["username"] == "quy")
check("tạo xong là có phiên đăng nhập luôn (cookie)", bool(r.cookies) or "set-cookie" in {k.lower() for k in r.headers})

# ---- 2b. Đã có admin thì không ai tạo đè ----
r = client.post("/auth/setup", data={"username": "ke-la", "password": "matkhau-ke-la"})
check("CANARY: đã có admin thì /auth/setup từ chối, không tạo đè",
      r.status_code == 400 and cfgmod.read_settings()["auth"]["username"] == "quy", r.text)

# ---- 3. Client cũ còn gửi setup_token ----
s = cfgmod.read_settings(); s.pop("auth", None); cfgmod.write_settings(s, cho_xoa_mat_khau=True)
r = client.post("/auth/setup", data={"username": "cu", "password": "matkhau-client-cu", "setup_token": "gi-cung-duoc"})
check("client cũ gửi kèm setup_token vẫn tạo được, không lỗi", r.status_code == 200 and r.json().get("ok"), r.text)

# ---- 4. Mã cài đặt chỉ là nhánh hẹp ----
cu = Path(state) / ".setup_token"
cu.write_text("ma-cu-con-sot\n", encoding="utf-8")
cfgmod.clear_setup_token()
check("clear_setup_token dọn được file mã", not cu.exists())

_main = (SERVER / "main.py").read_text(encoding="utf-8")
check("lúc khởi động: có admin thì dọn file mã", "cfgmod.clear_setup_token()" in _main)
check("chỉ đòi mã khi request đến từ ngoài máy",
      "cfgmod.den_tu_ngoai(request) and not cfgmod.ma_cai_dat_dung(setup_token)" in _main)

_html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
check("ô nhập mã ẩn mặc định", '<div id="wzCodeWrap" style="display:none">' in _html)
check("màn chào mừng vẫn có ô tên và mật khẩu", 'id="wzUser"' in _html and 'id="wzPass"' in _html)
for lang in ("vi", "en"):
    d = json.loads((ROOT / "dashboard" / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))
    check(f"i18n {lang}: có câu hướng dẫn lấy mã", "{cmd}" in d.get("app.wz_code_hint", ""))

print()
if fails:
    print(f"ĐỎ {len(fails)} mục: " + "; ".join(fails))
    raise SystemExit(1)
print("Tất cả xanh.")
