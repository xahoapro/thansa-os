"""HTTPS tự động cho bản cài native Linux (nginx + Let's Encrypt) - nhánh thứ ba của thẻ tên miền.

Chạy: python tests/run.py nginx_ssl
"""
import os
import tempfile

# Đặt state tạm TRƯỚC khi import config - test ghi settings.json (xem bẫy JAVIS_STATE_DIR).
os.environ["JAVIS_STATE_DIR"] = tempfile.mkdtemp(prefix="thansa-nginx-test-")
os.environ.pop("JAVIS_REQUIRE_LOGIN", None)
os.environ["JAVIS_HOST"] = "127.0.0.1"

from _paths import ROOT, SERVER  # noqa: E402,F401
import asyncio  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402

import config as cfgmod  # noqa: E402
import nginx_ssl  # noqa: E402
from routes import domain as dom  # noqa: E402

FAIL = []


def check(label, ok):
    print(("PASS" if ok else "FAIL") + ": " + label)
    if not ok:
        FAIL.append(label)


SCRIPT = ROOT / "bin" / "thansa-nginx-ssl.sh"


def chay(*args):
    env = {"PATH": "/usr/bin:/bin"}
    r = subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=env, timeout=20)
    return r.returncode, r.stdout


# ---- Script root: đầu vào bẩn bị chặn TRƯỚC khi chạm hệ thống ----
check("script tồn tại", SCRIPT.exists())
for xau in ("", "bad domain", "a.b;rm -rf /", "../etc", "x.com/../y"):
    code, out = chay(xau, "7777")
    check(f"từ chối tên miền bẩn {xau!r}", code != 0 and "RESULT:FAIL:invalid-domain" in out)
code, out = chay("vi.du.com", "77;id")
check("từ chối cổng bẩn", code != 0 and "RESULT:FAIL:invalid-port" in out)
code, out = chay("vi.du.com", "7777", "khong-phai-email")
check("từ chối email bẩn", code != 0 and "RESULT:FAIL:invalid-email" in out)
if os.geteuid() != 0:
    code, out = chay("vi.du.com", "7777")
    check("không phải root thì dừng, không cài gì", code != 0 and "RESULT:FAIL:need-root" in out
          and "STEP:install" not in out)
src = SCRIPT.read_text(encoding="utf-8")
check("biến map RIÊNG từng site (hai bản Thansa một máy không trùng biến, không đụng $connection_upgrade)",
      'MAPVAR="thansa_conn_upgrade_$(' in src and "map \\$http_upgrade \\$$MAPVAR" in src
      and "$connection_upgrade" not in src)
check("PATH đầy đủ có /usr/sbin, không thừa kế PATH thiếu sbin của dịch vụ (certbot tìm nginx theo PATH)",
      'export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"' in src)
for _unit in ("install.sh", "javis.service"):
    check(f"{_unit}: unit systemd có /usr/sbin trong PATH",
          "/usr/sbin:" in [l for l in (ROOT / _unit).read_text(encoding="utf-8").splitlines() if 'Environment="PATH=' in l][0])
check("nginx -t đỏ thì trả lại cấu hình cũ (không để file hỏng trong sites-enabled)", "rollback" in src)

# ---- Lối vào tạm bằng IP (--ip) cho lần cài đầu chưa có tên miền ----
code, out = chay("--ip", "77;id")
check("--ip: từ chối cổng bẩn", code != 0 and "RESULT:FAIL:invalid-port" in out)
if os.geteuid() != 0:
    code, out = chay("--ip", "7777")
    check("--ip: không phải root thì dừng", code != 0 and "RESULT:FAIL:need-root" in out)
check("--ip chỉ dựng trên nginx trống (không cướp web có sẵn)", 'fail "other-sites:' in src)
check("--ip nhận mọi host lạ bằng default_server", "listen 80 default_server;" in src and "server_name _;" in src)
check("kích hoạt tên miền xong thì đóng lối vào IP (http trần)", "close-ip-entry" in src)
check("server dịch được mã lỗi other-sites", "nginx" in dom._nginx_error_text("other-sites"))

# ---- install.sh: tên miền + HTTPS ngay lúc cài ----
INS = (ROOT / "install.sh").read_text(encoding="utf-8")
check("install.sh nhận THANSA_DOMAIN / hỏi tên miền", "THANSA_DOMAIN" in INS and "Domain, e.g." in INS)
check("install.sh gọi script cho tên miền và lối IP", '"$NGX_SH" "$NGX_DOMAIN" "$PORT"' in INS and '"$NGX_SH" --ip "$PORT"' in INS)
check("install.sh ghi proxy=nginx TRƯỚC khi dịch vụ khởi động",
      INS.index("_settings_set proxy") < INS.index("# --- 9. service"))
check("install.sh không xin chứng chỉ khi DNS chưa trỏ đúng", '"$DNS_IP" != "$NGX_PUBIP"' in INS)
check("install.sh tắt được nhánh nginx", 'THANSA_NGINX:-1' in INS)

# ---- Docker: vào bằng IP đi thẳng vào app, không bị đẩy sang https://<ip> ----
for _fn in ("docker-compose.yml", "docker-compose.https.yml"):
    _t = (ROOT / _fn).read_text(encoding="utf-8")
    check(f"{_fn}: Caddy cho IP vào thẳng app, tên miền mới chuyển HTTPS",
          "@ip header_regexp Host" in _t and "handle @ip" in _t and "reverse_proxy javis:7777" in _t)
check("certbot không hỏi, tự chuyển HTTPS, giữ chứng chỉ còn hạn",
      all(x in src for x in ("--non-interactive", "--redirect", "--keep-until-expiring")))
check("proxy giữ WebSocket + stream", "proxy_buffering off" in src and "Upgrade \\$http_upgrade" in src)

# ---- Lệnh chạy tay khi thiếu sudo ----
cmd = nginx_ssl.manual_cmd("vi.du.com")
check("lệnh chạy tay đủ đường dẫn script + cổng", cmd.startswith("sudo bash ") and str(SCRIPT) in cmd
      and cmd.endswith(" vi.du.com 7777"))

# ---- Phân nhánh phương thức SSL ----
_goc = nginx_ssl.supported
nginx_ssl.supported = lambda: True
check("hostinger vẫn là hostinger", dom._ssl_method("hostinger") == "hostinger")
check("docker/vps vẫn là caddy", dom._ssl_method("vps") == "caddy")
check("native linux -> nginx", dom._ssl_method("native") == "nginx")
nginx_ssl.supported = lambda: False
check("windows/mac -> none", dom._ssl_method("windows") == "none")
nginx_ssl.supported = _goc

# ---- Mã lỗi script -> câu người dùng hiểu ----
check("lỗi certbot nhắc DNS + cổng 80", "80" in dom._nginx_error_text("certbot"))
check("lỗi cổng bận nêu tên chương trình", "caddy" in dom._nginx_error_text("ports-busy:caddy"))

# ---- Hàng rào trước khi đụng hệ thống ----
cfg = cfgmod.read_settings()
cfg.setdefault("domain", {})["custom"] = "vi.du.com"
cfgmod.write_settings(cfg)
check("bản native 127.0.0.1 mặc định không bắt đăng nhập (tiền đề)", cfgmod.require_login() is False)

_started = []
nginx_ssl.start = lambda d, e="": _started.append(d) or True
nginx_ssl.sudo_ok = lambda: True

r = asyncio.run(dom._activate_nginx(cfgmod.read_settings(), "vi.du.com", "", True))
check("chưa có mật khẩu -> 409, không chạy job",
      getattr(r, "status_code", 200) == 409 and b"need_password" in r.body and not _started)
check("bị chặn vì mật khẩu thì chưa ghi proxy=nginx",
      (cfgmod.read_settings().get("domain") or {}).get("proxy") != "nginx")

cfg = cfgmod.read_settings()
cfg.setdefault("auth", {})["password_hash"] = "x"
cfgmod.write_settings(cfg)

dom._detect_public_ip = lambda: "1.2.3.4"
r = asyncio.run(dom._activate_nginx(cfgmod.read_settings(), "khong-ton-tai.invalid", "", False))
check("DNS chưa trỏ -> 409 dns_not_ready, không chạy job",
      getattr(r, "status_code", 200) == 409 and b"dns_not_ready" in r.body and not _started)

r = asyncio.run(dom._activate_nginx(cfgmod.read_settings(), "vi.du.com", "a b@c", True))
check("email bẩn -> 400", getattr(r, "status_code", 200) == 400 and not _started)

r = asyncio.run(dom._activate_nginx(cfgmod.read_settings(), "vi.du.com", "", True))
check("đủ điều kiện -> chạy job nền", isinstance(r, dict) and r.get("started") and _started == ["vi.du.com"])
check("kích hoạt nginx -> bắt buộc đăng nhập (fail-closed sau proxy)", cfgmod.require_login() is True)

nginx_ssl.sudo_ok = lambda: False
r = asyncio.run(dom._activate_nginx(cfgmod.read_settings(), "vi.du.com", "", True))
body = json.loads(r.body) if hasattr(r, "body") else {}
check("thiếu sudo -> trả lệnh chạy tay", body.get("needs_sudo") and body.get("cmd", "").endswith("vi.du.com 7777"))

# ---- Giao diện + từ điển ----
UI = (ROOT / "dashboard" / "branding.js").read_text(encoding="utf-8")
check("UI hỏi tiến độ qua /domain/nginx", "/domain/nginx" in UI and "brand.activate" in UI)
for lang in ("vi", "en"):
    d = json.loads((ROOT / "dashboard" / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))
    can = [k for k in ("brand.activate", "brand.nginx_hint", "brand.nginx_need_password", "brand.nginx_need_sudo",
                       "brand.nginx_running", "brand.nginx_failed", "brand.copy_cmd", "brand.nginx_unsupported")
           + tuple("brand.nginx_step_" + s for s in ("start",) + nginx_ssl.STEPS) if k not in d]
    check(f"{lang}.json đủ khoá nginx", not can)

# ---- Docker: Caddy dựng sẵn trong compose mặc định, bấm Kích hoạt là xin chứng chỉ ----
import yaml  # noqa: E402
_dc = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
_cd = _dc["services"].get("caddy") or {}
check("compose mặc định có sẵn Caddy", _cd.get("image", "").startswith("caddy:"))
check("Caddy tắt được bằng JAVIS_CADDY", str((_cd.get("deploy") or {}).get("replicas")) == "${JAVIS_CADDY:-1}")
check("Caddy mang tên theo bản (JAVIS_NAME)", _cd.get("container_name") == "${JAVIS_NAME:-javis}-caddy")
_cf = ((_dc.get("configs") or {}).get("javis_caddyfile") or {}).get("content", "")
check("Caddy chỉ xin chứng chỉ khi /tls-check gật (on-demand có cổng gác)",
      "ask http://javis:7777/tls-check" in _cf and "on_demand" in _cf)
check("Caddy giữ chứng chỉ qua restart", any(str(v).startswith("caddy-data:") for v in _cd.get("volumes", [])))
_mu = yaml.safe_load((ROOT / "docker-compose.multi.yml").read_text(encoding="utf-8"))
check("nhiều bản/VPS: overlay multi tắt Caddy riêng (proxy chung giữ 443)",
      ((_mu["services"].get("caddy") or {}).get("deploy") or {}).get("replicas") == 0)
_up = (ROOT / "update.sh").read_text(encoding="utf-8")
check("update.sh không để Caddy mới giành 80/443 của web server có sẵn", "export JAVIS_CADDY=0" in _up)

cfg = cfgmod.read_settings()
dom._caddy_reachable = lambda: False
r = asyncio.run(dom._activate_caddy(cfg, "vi.du.com"))
body = json.loads(r.body) if hasattr(r, "body") else {}
check("Docker chưa có Caddy -> trả lệnh CỘNG THÊM lớp HTTPS (không đè compose của người dùng)",
      body.get("needs_cmd") and "-f docker-compose.https.yml up -d" in body.get("cmd", "")
      and "curl -fsSLO" in body.get("cmd", "") and "docker-compose.yml &&" not in body.get("cmd", ""))
dom._caddy_reachable = lambda: True
_goi = []
_tls = nginx_ssl.local_tls_ok
nginx_ssl.local_tls_ok = lambda d, t=4.0, h="127.0.0.1": _goi.append((d, h, t)) or True
r = asyncio.run(dom._activate_caddy(cfgmod.read_settings(), "vi.du.com"))
check("Docker có Caddy -> bắt tay TLS với container caddy bằng đúng tên miền",
      isinstance(r, dict) and r.get("ssl_active") and _goi and _goi[0][:2] == ("vi.du.com", "caddy") and _goi[0][2] >= 30)
nginx_ssl.local_tls_ok = _tls
check("UI dùng chung nút Kích hoạt cho mọi cách cài",
      'tog.textContent = j.ssl_active ? window.t("brand.reactivate") : window.t("brand.activate");' in UI
      and "caddy_need_cmd" in UI)

if FAIL:
    raise SystemExit(f"\nFAIL - test_nginx_ssl: {len(FAIL)} lỗi")
print("\nOK - test_nginx_ssl: tất cả pass")
