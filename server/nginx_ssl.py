"""HTTPS cho bản cài NATIVE trên Linux: nginx reverse proxy + Let's Encrypt (certbot).

Nhánh thứ ba của thẻ TÊN MIỀN & SSL, bên cạnh Docker (Caddy On-Demand) và Hostinger (Traefik
của hPanel). Người dùng nhập tên miền, trỏ DNS, bấm "Kích hoạt" - server gọi
`bin/thansa-nginx-ssl.sh` qua `sudo -n` ở NỀN (cài gói có thể mất vài phút, không được giữ
request chờ), dashboard hỏi tiến độ qua GET /domain/nginx.

Không có sudo không-mật-khẩu thì KHÔNG cố leo quyền kiểu khác: trả đúng dòng lệnh để người dùng
chạy tay một lần (manual_cmd).

Vì sao kiểm chứng chỉ ở 127.0.0.1:443 chứ không mở https://<tên miền>: máy chủ ở nhà / sau NAT
rất hay KHÔNG gọi được chính IP công cộng của mình (router không hỗ trợ hairpin NAT), nên lượt
mở từ trong ra ngoài báo hỏng trong khi Internet vào vẫn chạy. Bắt tay TLS tại chỗ với SNI đúng
tên miền + xác minh chuỗi chứng chỉ trả lời đúng câu "nginx có đang phục vụ chứng chỉ hợp lệ
cho tên miền này không".
"""
from __future__ import annotations

import asyncio
import os
import shutil
import socket
import ssl
import subprocess
import time
from pathlib import Path

import deploy_info
import winproc

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin" / "thansa-nginx-ssl.sh"
STEPS = ("install", "config", "cert", "verify")
_TIMEOUT = 15 * 60

_JOB: dict = {"running": False, "domain": "", "step": "", "ok": None, "error": "",
              "log": [], "started": 0.0, "finished": 0.0}
_TASK = None


def supported() -> bool:
    """Chỉ Linux native có systemd: Docker/Hostinger đã có đường riêng, Windows/Mac không có nginx
    hệ thống để Thansa tự dựng."""
    return (deploy_info.deploy_mode() == "native" and deploy_info.host_platform() == "linux"
            and SCRIPT.exists() and shutil.which("systemctl") is not None)


def _is_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def sudo_ok() -> bool:
    """Chạy được script bằng root mà không hỏi mật khẩu không."""
    if _is_root():
        return True
    if not shutil.which("sudo"):
        return False
    try:
        return subprocess.run(["sudo", "-n", "true"], capture_output=True, timeout=5,
                              **winproc.kwargs_no_window()).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def app_port() -> str:
    return str(os.getenv("JAVIS_PORT", "7777") or "7777").strip()


def manual_cmd(domain: str, email: str = "") -> str:
    tail = f" {email}" if email else ""
    return f"sudo bash {SCRIPT} {domain} {app_port()}{tail}"


def local_tls_ok(domain: str, timeout: float = 4.0, host: str = "127.0.0.1") -> bool:
    """Proxy ở `host`:443 có trả chứng chỉ hợp lệ cho `domain` không (xem docstring module).

    Mặc định hỏi nginx trên CHÍNH máy này; bản Docker hỏi container Caddy (host="caddy") - với
    Caddy On-Demand thì chính lần bắt tay này làm nó đi xin chứng chỉ, nên gọi với timeout dài."""
    if not domain:
        return False
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=domain):
                return True
    except (OSError, ssl.SSLError, ValueError):
        return False


def status() -> dict:
    j = dict(_JOB)
    j["log"] = list(_JOB["log"][-15:])
    return j


def _log_path() -> Path:
    base = os.getenv("JAVIS_STATE_DIR") or str(ROOT / "server")
    return Path(base) / "nginx-ssl.log"


async def _run(domain: str, email: str) -> None:
    args = ["bash", str(SCRIPT), domain, app_port()] + ([email] if email else [])
    if not _is_root():
        args = ["sudo", "-n"] + args
    try:
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            stdin=asyncio.subprocess.DEVNULL, **winproc.kwargs_no_window())
    except OSError as e:
        _JOB.update(running=False, ok=False, error=f"spawn:{type(e).__name__}", finished=time.time())
        return
    result = ""
    try:
        with open(_log_path(), "a", encoding="utf-8") as logf:
            logf.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} {domain}\n")

            async def _doc():
                nonlocal result
                assert proc.stdout is not None
                async for raw in proc.stdout:
                    line = raw.decode("utf-8", "replace").rstrip()
                    logf.write(line + "\n")
                    logf.flush()
                    if line.startswith("STEP:"):
                        _JOB["step"] = line[5:].strip()
                    elif line.startswith("RESULT:"):
                        result = line[7:].strip()
                    elif line:
                        _JOB["log"] = (_JOB["log"] + [line])[-40:]
                await proc.wait()

            await asyncio.wait_for(_doc(), timeout=_TIMEOUT)
    except asyncio.TimeoutError:
        proc.kill()
        result = "FAIL:timeout"
    except OSError:
        pass
    ok = result == "OK"
    _JOB.update(running=False, ok=ok, finished=time.time(),
                error="" if ok else (result[5:] if result.startswith("FAIL:") else (result or f"exit:{proc.returncode}")))


def start(domain: str, email: str = "") -> bool:
    """Bắt đầu job nền. False = đang có job chạy (không chạy chồng hai certbot)."""
    global _TASK
    if _JOB["running"]:
        return False
    _JOB.update(running=True, domain=domain, step="start", ok=None, error="", log=[],
                started=time.time(), finished=0.0)
    _TASK = asyncio.get_running_loop().create_task(_run(domain, email))
    return True
