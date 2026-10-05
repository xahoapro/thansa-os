"""Tên miền riêng + HTTPS tự động (Caddy On-Demand TLS).

Bóc nguyên văn khỏi main.py ở 0.9.243. Phụ thuộc duy nhất còn lại vào main là `_deploy_mode`,
nhận qua deps.

Lưu ý về `/tls-check`: nó nằm trong danh sách đường dẫn CÔNG KHAI của middleware xác thực
(`_AUTH_PUBLIC_EXACT` trong main.py). Danh sách đó khớp theo CHUỖI đường dẫn và ở lại main,
nên việc bóc file không đụng tới nó. Nhưng đừng bao giờ đổi đường dẫn này: Caddy gọi nó
TRƯỚC khi xin chứng chỉ, mất quyền công khai là nó nhận 401 thay vì 200/403 và việc cấp
chứng chỉ trên production hỏng.
"""
import asyncio
import os
import re
import socket
from dataclasses import dataclass
from typing import Callable

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse

import config as cfgmod
import localefmt
import nginx_ssl


@dataclass
class DomainDeps:
    """_deploy_mode ở lại main (khối cập nhật cũng dùng nó) nên tiêm vào đây."""
    deploy_mode: Callable[[], str]


_DEPS: DomainDeps = None

# Bản Docker: Caddy là service `caddy` trong cùng project compose (docker-compose.yml nay dựng
# sẵn; bản cài cũ thêm bằng docker-compose.https.yml). Lệnh dưới là lớp CỘNG THÊM, không đè file
# compose người dùng đã sửa (bind-mount brain...), và update.sh nhận ra Caddy để giữ nó.
CADDY_HOST = "caddy"
CADDY_CMD = ("curl -fsSLO https://raw.githubusercontent.com/xahoapro/thansa-os/main/docker-compose.https.yml"
             " && docker compose -f docker-compose.yml -f docker-compose.https.yml up -d")

_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
_PUBLIC_IP_CACHE = {"ip": None, "ts": 0.0}


def _norm_domain(d):
    d = (d or "").strip().lower()
    d = d.replace("https://", "").replace("http://", "")
    d = d.split("/")[0].split(":")[0].strip().strip(".")
    return d


def _domain_deploy_target(request: Request = None):
    """Phân biệt Hostinger (Traefik do hPanel quản lý) với VPS Docker/Caddy.

    Hostinger không cho container sửa label Traefik đang chạy, vì vậy UI chỉ có thể lưu
    tên miền + kiểm tra DNS rồi hướng dẫn đúng bước Environment/Redeploy. Compose mới đặt
    JAVIS_DEPLOY_TARGET rõ ràng; nhận diện hostname .hstgr.cloud giữ tương thích bản cũ.
    """
    explicit = (os.getenv("JAVIS_DEPLOY_TARGET", "") or "").strip().lower()
    if explicit in ("hostinger", "vps", "native", "windows"):
        return explicit
    host = ""
    if request is not None:
        host = (request.headers.get("host", "") or "").split(":")[0].strip().lower()
    if host.endswith(".hstgr.cloud"):
        return "hostinger"
    mode = _DEPS.deploy_mode()
    return "vps" if mode == "docker" else mode


def _ssl_method(target: str) -> str:
    """Ai cấp HTTPS cho bản cài này: hostinger (Traefik hPanel) | caddy (Docker/VPS compose) |
    nginx (Linux native - Thansa tự dựng, xem nginx_ssl.py) | none (Windows/Mac native)."""
    if target == "hostinger":
        return "hostinger"
    if target in ("vps", "docker"):
        return "caddy"
    return "nginx" if nginx_ssl.supported() else "none"


def _nginx_error_text(code: str) -> str:
    """Mã lỗi từ bin/thansa-nginx-ssl.sh (dòng RESULT:FAIL:<mã>) -> câu người dùng hiểu được."""
    code = code or ""
    if code.startswith("ports-busy"):
        who = code.split(":", 1)[1] if ":" in code else ""
        return localefmt.chu(f"Cổng 80/443 đang bị chương trình khác giữ ({who}). Tắt nó rồi bấm Kích hoạt lại.",
                             f"Ports 80/443 are held by another program ({who}). Stop it, then press Activate again.")
    table = {
        "certbot": ("Let's Encrypt không cấp được chứng chỉ - kiểm tra DNS đã trỏ đúng IP và cổng 80 mở từ Internet (router/firewall).",
                    "Let's Encrypt could not issue the certificate - check that DNS points to this IP and port 80 is open from the Internet (router/firewall)."),
        "certbot-install": ("Đã có chứng chỉ nhưng certbot không gắn được vào cấu hình nginx.",
                            "The certificate exists but certbot could not install it into the nginx config."),
        "nginx-config": ("Cấu hình nginx bị lỗi (nginx -t). Xem nhật ký nginx-ssl.log.",
                         "The nginx configuration is invalid (nginx -t). See nginx-ssl.log."),
        "nginx-start": ("Không khởi động được nginx.", "Could not start nginx."),
        "apt-install": ("Cài nginx/certbot bằng apt thất bại.", "Installing nginx/certbot with apt failed."),
        "dnf-install": ("Cài nginx/certbot bằng dnf thất bại.", "Installing nginx/certbot with dnf failed."),
        "no-package-manager": ("Không tìm thấy apt hay dnf để cài nginx.", "Neither apt nor dnf was found to install nginx."),
        "need-root": ("Script cần quyền root.", "The script needs root."),
        "timeout": ("Quá 15 phút chưa xong - đã dừng.", "Did not finish within 15 minutes - stopped."),
        "other-sites": ("nginx trên máy này đang phục vụ site khác.", "nginx on this machine already serves other sites."),
    }
    vi, en = table.get(code, (f"Lỗi: {code}", f"Error: {code}"))
    return localefmt.chu(vi, en)


def _nginx_payload(domain: str) -> dict:
    """Trạng thái job nginx cho UI (kèm câu lỗi đã dịch và lệnh chạy tay)."""
    j = nginx_ssl.status()
    j["error_text"] = _nginx_error_text(j["error"]) if j.get("ok") is False else ""
    j["sudo_ok"] = nginx_ssl.sudo_ok()
    j["cmd"] = nginx_ssl.manual_cmd(domain) if domain else ""
    return j


def _caddy_reachable() -> bool:
    """Container Caddy có đứng trong mạng compose không (chỉ mở TCP, không bắt tay TLS)."""
    try:
        with socket.create_connection((CADDY_HOST, 443), timeout=2):
            return True
    except OSError:
        return False


def _detect_public_ip():
    import time as _t
    now = _t.time()
    if _PUBLIC_IP_CACHE["ip"] and now - _PUBLIC_IP_CACHE["ts"] < 600:
        return _PUBLIC_IP_CACHE["ip"]
    ip = None
    for url in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"):
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=4) as r:
                ip = (r.read().decode() or "").strip()
            if ip:
                break
        except Exception:
            ip = None
    if ip:
        _PUBLIC_IP_CACHE.update(ip=ip, ts=now)
    return ip


def _req_is_secure(request: Request) -> bool:
    """Request hiện tại có phải HTTPS không (tôn trọng proxy qua X-Forwarded-Proto)."""
    xf = (request.headers.get("x-forwarded-proto", "") or "").split(",")[0].strip().lower()
    if xf:
        return xf == "https"
    return request.url.scheme == "https"


async def _probe_https(domain: str):
    """Mở https://<domain>/health TỪ CHÍNH server → buộc Caddy On-Demand cấp chứng chỉ ở lần đầu
    và xác minh HTTPS chạy thật. Trả (active: bool, reason: str) với lý do dễ hiểu để hướng dẫn."""
    if not domain:
        return False, localefmt.chu("Chưa đặt tên miền", "No domain set")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            r = await client.get(f"https://{domain}/health")
        if r.status_code < 500:
            return True, localefmt.chu("HTTPS đang hoạt động", "HTTPS is working")
        return False, localefmt.chu(f"Máy chủ trả HTTP {r.status_code}", f"The server returned HTTP {r.status_code}")
    except Exception as e:
        s = (str(e) + " " + type(e).__name__).lower()
        if "ssl" in s or "certificate" in s or "verify" in s:
            return False, localefmt.chu("Chứng chỉ chưa hợp lệ - DNS chưa trỏ đúng hoặc chứng chỉ chưa cấp xong",
                                        "Certificate not valid yet - DNS does not point here yet or the certificate is still being issued")
        if "connect" in s or "timeout" in s or "timed out" in s or "refused" in s:
            return False, localefmt.chu("Không kết nối được cổng 443 - Caddy/HTTPS chưa chạy, hoặc cổng 80/443 bị proxy khác chiếm",
                                        "Cannot connect to port 443 - Caddy/HTTPS is not running, or ports 80/443 are taken by another proxy")
        return False, type(e).__name__


def _make_router() -> APIRouter:
    router = APIRouter()

    @router.get("/tls-check")
    async def tls_check(domain: str = ""):
        """Cổng gác cho Caddy On-Demand TLS: chỉ 200 khi hostname == tên miền admin đã đặt,
        chống kẻ trỏ DNS bừa vào IP ép server xin cert vô hạn (cạn rate-limit Let's Encrypt)."""
        want = _norm_domain((cfgmod.read_settings().get("domain", {}) or {}).get("custom", ""))
        got = _norm_domain(domain)
        if want and got and got == want:
            return JSONResponse({"ok": True})
        return JSONResponse({"ok": False}, status_code=403)

    @router.post("/domain")
    async def domain_set(domain: str = Form("")):
        d = _norm_domain(domain)
        if d and not _DOMAIN_RE.match(d):
            return JSONResponse({"ok": False, "error": localefmt.chu("Tên miền không hợp lệ (vd: javis.tencuaban.com)",
                                                                   "Invalid domain (e.g. javis.yourdomain.com)")}, status_code=400)
        cfg = cfgmod.read_settings()
        cfg.setdefault("domain", {})
        cfg["domain"]["custom"] = d
        cfgmod.write_settings(cfg)
        return {"ok": True, "domain": d}

    @router.get("/domain/status")
    async def domain_status(request: Request):
        cfg = cfgmod.read_settings()
        dom = cfg.get("domain", {}) or {}
        custom = _norm_domain(dom.get("custom", ""))
        ssl_enabled = bool(dom.get("ssl_enabled", False))
        server_ip = _detect_public_ip()
        dns_ip = None
        dns_ok = False
        if custom:
            try:
                import socket as _sock
                dns_ip = _sock.gethostbyname(custom)
                dns_ok = bool(server_ip) and dns_ip == server_ip
            except Exception:
                dns_ip = None
        host = (request.headers.get("host", "") or "").split(":")[0].strip().lower()
        on_domain = bool(custom) and host == custom
        secure_now = _req_is_secure(request)
        # SSL: nếu đang mở chính tên miền qua HTTPS thì chắc chắn đang chạy; nếu không, chủ động probe.
        target = _domain_deploy_target(request)
        method = _ssl_method(target)
        ssl_active, ssl_reason = False, localefmt.chu("Chưa đặt tên miền", "No domain set")
        if custom:
            if on_domain and secure_now:
                ssl_active, ssl_reason = True, localefmt.chu("Bạn đang mở qua HTTPS", "You are browsing over HTTPS")
            elif method == "nginx" and await asyncio.to_thread(nginx_ssl.local_tls_ok, custom):
                ssl_active, ssl_reason = True, localefmt.chu("HTTPS đang hoạt động (nginx)", "HTTPS is working (nginx)")
            elif method == "caddy" and await asyncio.to_thread(nginx_ssl.local_tls_ok, custom, 4.0, CADDY_HOST):
                ssl_active, ssl_reason = True, localefmt.chu("HTTPS đang hoạt động (Caddy)", "HTTPS is working (Caddy)")
            else:
                ssl_active, ssl_reason = await _probe_https(custom)
        route_domain = _norm_domain(os.getenv("DOMAIN_NAME", ""))
        return {"domain": custom, "server_ip": server_ip, "dns_ip": dns_ip,
                "dns_ok": dns_ok, "on_domain": on_domain, "secure_now": secure_now,
                "deploy_mode": _DEPS.deploy_mode(), "ssl_enabled": ssl_enabled,
                "ssl_active": ssl_active, "ssl_reason": ssl_reason,
                "deployment_target": target, "route_domain": route_domain,
                "ui_can_enable_ssl": method in ("caddy", "nginx"),
                "ssl_method": method, "auth_enabled": cfgmod.auth_enabled(cfg),
                "nginx": _nginx_payload(custom) if method == "nginx" else None,
                "caddy_cmd": CADDY_CMD if method == "caddy" else "",
                "requires_redeploy": target == "hostinger" and bool(custom) and custom != route_domain}

    @router.post("/domain/ssl")
    async def domain_ssl(request: Request, enabled: str = Form("1"), email: str = Form(""),
                         force: str = Form("")):
        """Bật/tắt SSL cho tên miền. Bật → lưu ý định + chủ động probe HTTPS (buộc Caddy cấp chứng chỉ),
        trả trạng thái thật + gợi ý lệnh nếu chưa bật được (bản Docker cần compose HTTPS)."""
        on = str(enabled).strip().lower() in ("1", "true", "yes", "on")
        cfg = cfgmod.read_settings()
        cfg.setdefault("domain", {})
        custom = _norm_domain(cfg["domain"].get("custom", ""))
        if on and not custom:
            return JSONResponse({"ok": False, "error": localefmt.chu("Hãy nhập và lưu tên miền trước khi bật SSL.",
                                                                   "Enter and save a domain before turning on SSL.")}, status_code=400)
        if on and _domain_deploy_target(request) == "hostinger":
            return JSONResponse({
                "ok": False,
                "error": localefmt.chu(
                    "Hostinger quản lý HTTPS bằng Traefik. Hãy đặt DOMAIN_NAME trong Docker Manager rồi Redeploy; Thansa không thể sửa route của hPanel từ bên trong container.",
                    "Hostinger manages HTTPS with Traefik. Set DOMAIN_NAME in Docker Manager and Redeploy; Thansa cannot change hPanel routes from inside the container."),
                "hostinger": True,
                "domain": custom,
                "docs": "https://github.com/xahoapro/thansa-os/blob/main/docs/15-thuong-hieu-ten-mien.md",
            }, status_code=409)
        if on and _ssl_method(_domain_deploy_target(request)) == "nginx":
            return await _activate_nginx(cfg, custom, (email or "").strip(), str(force).strip() == "1")
        if on and _ssl_method(_domain_deploy_target(request)) == "caddy":
            return await _activate_caddy(cfg, custom)
        cfg["domain"]["ssl_enabled"] = on
        cfgmod.write_settings(cfg)
        if not on:
            return {"ok": True, "enabled": False, "ssl_active": False, "ssl_reason": localefmt.chu("Đã tắt SSL", "SSL turned off")}
        active, reason = await _probe_https(custom)
        resp = {"ok": True, "enabled": True, "ssl_active": active, "ssl_reason": reason}
        if not active and _DEPS.deploy_mode() == "docker":
            resp["hint_cmd"] = "docker compose -f docker-compose.yml -f docker-compose.https.yml up -d"
        return resp

    @router.get("/domain/nginx")
    async def domain_nginx():
        """Tiến độ job nginx/certbot đang chạy nền (dashboard hỏi mỗi 2 giây khi đang Kích hoạt)."""
        custom = _norm_domain((cfgmod.read_settings().get("domain", {}) or {}).get("custom", ""))
        j = _nginx_payload(custom)
        j["ssl_active"] = (not j["running"]) and await asyncio.to_thread(nginx_ssl.local_tls_ok, custom)
        return j

    return router


async def _activate_caddy(cfg: dict, custom: str):
    """Docker: Caddy On-Demand đã đứng sẵn - bắt tay TLS với nó bằng đúng tên miền là nó tự hỏi
    /tls-check rồi xin chứng chỉ. Không có Caddy (cài bằng compose cũ, trước khi Caddy vào mặc định) thì trả lệnh
    cộng thêm lớp HTTPS để chạy một lần trên máy chủ."""
    cfg["domain"]["ssl_enabled"] = True
    cfgmod.write_settings(cfg)
    if not await asyncio.to_thread(_caddy_reachable):
        return JSONResponse({"ok": False, "needs_cmd": True, "cmd": CADDY_CMD, "error": localefmt.chu(
            "Bản Docker này chưa có Caddy (lớp HTTPS). Chạy lệnh bên dưới một lần trong thư mục chứa docker-compose.yml trên máy chủ, rồi bấm Kích hoạt lại.",
            "This Docker install has no Caddy (HTTPS layer) yet. Run the command below once in the folder holding docker-compose.yml on the server, then press Activate again.")},
            status_code=409)
    # Lần đầu Caddy phải đi xin chứng chỉ ngay trong lúc bắt tay - cho hẳn 45 giây.
    if await asyncio.to_thread(nginx_ssl.local_tls_ok, custom, 45.0, CADDY_HOST):
        return {"ok": True, "enabled": True, "method": "caddy", "ssl_active": True,
                "ssl_reason": localefmt.chu("HTTPS đang hoạt động (Caddy)", "HTTPS is working (Caddy)")}
    return {"ok": True, "enabled": True, "method": "caddy", "ssl_active": False,
            "ssl_reason": localefmt.chu(
                "Caddy chưa xin được chứng chỉ - kiểm tra DNS đã trỏ đúng IP và cổng 80/443 mở từ Internet",
                "Caddy could not get a certificate yet - check that DNS points to this IP and ports 80/443 are open from the Internet")}


async def _activate_nginx(cfg: dict, custom: str, email: str, force: bool):
    """Linux native: dựng nginx + Let's Encrypt bằng bin/thansa-nginx-ssl.sh chạy nền.

    Hai hàng rào TRƯỚC khi đụng hệ thống:
    - Phải có mật khẩu đăng nhập. Bản native nghe 127.0.0.1 nên mặc định KHÔNG bắt đăng nhập
      (config.require_login); nginx đứng trước thì mọi request Internet đều tới từ 127.0.0.1 -
      không chặn ở đây là mở dashboard điều khiển Claude full quyền cho cả thế giới.
    - DNS phải trỏ về IP máy chủ: Let's Encrypt giới hạn số lần xác thực hỏng, xin bừa khi DNS
      chưa đúng là tự khoá mình ngoài cả giờ. `force` để người dùng sau CDN/proxy DNS bỏ qua.
    """
    if email and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return JSONResponse({"ok": False, "error": localefmt.chu("Email không hợp lệ.", "Invalid email.")}, status_code=400)
    if not cfgmod.auth_enabled(cfg):
        return JSONResponse({"ok": False, "need_password": True, "error": localefmt.chu(
            "Hãy đặt mật khẩu đăng nhập (Cài đặt → Bảo mật) trước khi mở Thansa ra Internet qua tên miền.",
            "Set a login password (Settings → Security) before exposing Thansa to the Internet on a domain.")},
            status_code=409)
    if not force:
        server_ip = await asyncio.to_thread(_detect_public_ip)
        try:
            dns_ip = await asyncio.to_thread(socket.gethostbyname, custom)
        except OSError:
            dns_ip = None
        if not dns_ip or (server_ip and dns_ip != server_ip):
            return JSONResponse({"ok": False, "dns_not_ready": True, "error": localefmt.chu(
                f"DNS của {custom} chưa trỏ về IP máy chủ ({server_ip or '?'}). Sửa bản ghi A ở bước 2 rồi thử lại.",
                f"DNS for {custom} does not point to this server's IP ({server_ip or '?'}) yet. Fix the A record in step 2 and retry.")},
                status_code=409)
    # Ghi ý định TRƯỚC khi chạy: proxy=nginx làm require_login() bật cứng (fail-closed) kể cả khi
    # job hỏng giữa chừng hay người dùng tự chạy lệnh tay.
    cfg["domain"]["ssl_enabled"] = True
    cfg["domain"]["proxy"] = "nginx"
    cfgmod.write_settings(cfg)
    if not nginx_ssl.sudo_ok():
        return JSONResponse({"ok": False, "needs_sudo": True, "cmd": nginx_ssl.manual_cmd(custom, email),
                             "error": localefmt.chu(
                                 "Tài khoản chạy Thansa không có quyền sudo không mật khẩu. Chạy lệnh bên dưới một lần trên máy chủ rồi bấm Kiểm tra lại.",
                                 "The account running Thansa has no passwordless sudo. Run the command below once on the server, then press Check again.")},
                            status_code=409)
    started = nginx_ssl.start(custom, email)
    return {"ok": True, "method": "nginx", "started": started, "already_running": not started,
            "nginx": _nginx_payload(custom)}


def register(app, deps: DomainDeps):
    """Gắn router vào app. Gọi ĐÚNG vị trí dòng cũ trong main.py - xem routes/__init__.py."""
    global _DEPS
    _DEPS = deps
    router = _make_router()
    app.include_router(router)
    return router
