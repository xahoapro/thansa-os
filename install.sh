#!/usr/bin/env bash
# ============================================================================
# Javis OS - Linux/macOS native installer (no Docker)
#   ./install.sh
# Installs python3 + node + Claude Code CLI, creates a venv, installs deps,
# seeds .env, and registers a systemd service (or falls back to nohup).
#
# TEN MIEN + HTTPS NGAY LUC CAI (Linux co systemd): script hoi ten mien (hoac dat san bien):
#   THANSA_DOMAIN=app.tenmien.com ./install.sh
# DNS da tro ve may nay -> tu cai nginx + Let's Encrypt, cai xong mo thang https://app.tenmien.com.
# Chua co ten mien -> mo tam http://<ip-may-chu> de vao giao dien lan dau, khai ten mien sau trong app.
# THANSA_NGINX=0 = khong dung nginx (vao bang SSH tunnel / Cloudflare Tunnel nhu truoc).
#
# NHIEU BAN TREN CUNG MOT MAY: clone vao THU MUC KHAC roi dat hai bien truoc khi chay.
#   JAVIS_NAME=javis-shop JAVIS_PORT=7778 ./install.sh
# JAVIS_NAME dat ten dich vu systemd (javis-shop.service); JAVIS_PORT la cong nghe.
# Bo trong ca hai = javis.service + cong 7777, y het truoc day.
# ============================================================================
set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${CYAN}->${NC} $*"; }
ok()   { echo -e "${GREEN}OK${NC} $*"; }
warn() { echo -e "${YELLOW}!!${NC} $*"; }
err()  { echo -e "${RED}xx${NC} $*" >&2; }

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

# Ten dich vu + cong cua BAN NAY. Truoc day ca hai deu dong cung, nen cai ban thu hai la ghi de
# /etc/systemd/system/javis.service cua ban thu nhat va hai ban tranh nhau cong 7777.
SVC="${JAVIS_NAME:-javis}"
PORT="${JAVIS_PORT:-7777}"
case "$SVC" in
  *[!A-Za-z0-9._-]*) err "JAVIS_NAME may only contain letters, digits, '.', '_' and '-' (got: $SVC)"; exit 1;;
esac

SUDO=""; [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1 && SUDO="sudo"

# --- 1. python3 >= 3.10 + venv + pip ---
# HARD FLOOR 3.10: uvicorn pinned in requirements.txt needs >=3.10 (every release from
# 0.40 up dropped 3.9). Do NOT trust a bare `python3` here - macOS ships /usr/bin/python3
# = 3.9 and it sits AHEAD of Homebrew in PATH, so the old code happily printed
# "OK Python 3.9.6" and then died 40 lines later with the useless pip error
# "No matching distribution found for uvicorn==0.51.0". Probe for a real interpreter.
PY_MIN="3.10"
py_ok() { "$1" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 10) else 1)' >/dev/null 2>&1; }

PYTHON_BIN=""
find_python() {
  local c d
  # NOT newest-first. requirements.txt pins hard (fastapi 0.141.1, cryptography, uvloop,
  # watchfiles, pydantic-core - all need compiled wheels), so prefer the versions with the
  # widest wheel coverage and fall back to a bleeding-edge interpreter only if nothing else
  # exists: on a brand-new 3.x, pip finds no wheel and tries to BUILD from source, which
  # fails on any machine without a compiler toolchain. 3.11/3.12 is the verified sweet spot.
  for c in python3.12 python3.11 python3.13 python3.10 python3 python3.14 python; do
    if py_ok "$c"; then PYTHON_BIN="$(command -v "$c")"; return 0; fi
  done
  # Homebrew python is keg-only on some setups (never linked into PATH); look directly.
  # Same preference order, explicit rather than a glob (a glob sorts 3.10 ahead of 3.12).
  for d in /opt/homebrew/bin /usr/local/bin; do
    for c in python3.12 python3.11 python3.13 python3.10 python3.14; do
      if py_ok "$d/$c"; then PYTHON_BIN="$d/$c"; return 0; fi
    done
  done
  return 1
}

log "Checking Python >= $PY_MIN..."
if ! find_python; then
  log "No Python >= $PY_MIN found - installing..."
  if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update -qq && $SUDO apt-get install -y python3 python3-venv python3-pip
  elif command -v dnf >/dev/null 2>&1; then $SUDO dnf install -y python3 python3-pip
  elif command -v brew >/dev/null 2>&1; then brew install python
  else err "Install Python $PY_MIN or newer manually, then re-run."; exit 1; fi
  find_python || {
    err "Still no Python >= $PY_MIN after install (found: $(python3 --version 2>&1 || echo none))."
    err "Install it manually (macOS: brew install python), then re-run."
    exit 1
  }
fi
"$PYTHON_BIN" -m venv --help >/dev/null 2>&1 || { command -v apt-get >/dev/null 2>&1 && $SUDO apt-get install -y python3-venv; }
ok "$("$PYTHON_BIN" --version) ($PYTHON_BIN)"

# --- 2. system deps: git, ripgrep, ffmpeg (best-effort) ---
log "Installing system deps (git, ripgrep, ffmpeg)..."
if command -v apt-get >/dev/null 2>&1; then
  $SUDO apt-get install -y git ripgrep ffmpeg curl >/dev/null 2>&1 || warn "some deps skipped"
elif command -v dnf >/dev/null 2>&1; then
  $SUDO dnf install -y git ripgrep ffmpeg curl >/dev/null 2>&1 || warn "some deps skipped"
elif command -v brew >/dev/null 2>&1; then
  brew install git ripgrep ffmpeg >/dev/null 2>&1 || warn "some deps skipped"
fi

# --- 3. Node.js 22 LTS (system pkg -> nodejs.org tarball fallback) ---
need_node() { ! command -v node >/dev/null 2>&1 || [ "$(node -v | sed 's/v//;s/\..*//')" -lt 20 ]; }
if need_node; then
  log "Installing Node.js 22 LTS..."
  if command -v apt-get >/dev/null 2>&1; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO -E bash - >/dev/null 2>&1 && $SUDO apt-get install -y nodejs || true
  elif command -v brew >/dev/null 2>&1; then brew install node@22 || true; fi
  if need_node; then
    arch=$(uname -m); case "$arch" in x86_64) na=x64;; aarch64|arm64) na=arm64;; *) err "unsupported arch $arch"; exit 1;; esac
    tb=$(curl -fsSL https://nodejs.org/dist/latest-v22.x/ | grep -oE "node-v22\.[0-9]+\.[0-9]+-linux-${na}\.tar\.xz" | head -1)
    tmp=$(mktemp -d); curl -fsSL "https://nodejs.org/dist/latest-v22.x/${tb}" -o "$tmp/n.tar.xz"
    mkdir -p "$HOME/.javis"; rm -rf "$HOME/.javis/node"
    tar xf "$tmp/n.tar.xz" -C "$tmp"; mv "$tmp"/node-v22* "$HOME/.javis/node"; rm -rf "$tmp"
    mkdir -p "$HOME/.local/bin"
    ln -sf "$HOME/.javis/node/bin/node" "$HOME/.local/bin/node"
    ln -sf "$HOME/.javis/node/bin/npm"  "$HOME/.local/bin/npm"
    ln -sf "$HOME/.javis/node/bin/npx"  "$HOME/.local/bin/npx"
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi
ok "Node $(node -v)"

# --- 4. Claude Code CLI (the brain) ---
if ! command -v claude >/dev/null 2>&1; then
  log "Installing Claude Code CLI globally via npm..."
  if ! npm install -g @anthropic-ai/claude-code >/dev/null 2>&1; then
    warn "global npm install needs sudo; retrying..."
    $SUDO npm install -g @anthropic-ai/claude-code
  fi
fi
ok "Claude CLI $(claude --version 2>/dev/null || echo installed)"

# --- 4b. Codex CLI (gói ChatGPT) ---
#
# BEST-EFFORT, cố ý khác Claude ở trên: thiếu Claude thì Javis không còn bộ não mặc định nào
# để chạy, còn thiếu cái này chỉ mất đúng một engine. Nên lỗi ở đây chỉ cảnh báo chứ không cho
# `set -e` giết cả lần cài.
#
# Bộ não Google cho tài khoản cá nhân hiện nay là Antigravity CLI (`agy`), KHÔNG cài ở đây:
# trình cài của Google là một script tải về chạy thẳng, để chủ máy tự quyết. Trang Models có
# sẵn lệnh cài trên thẻ.
cai_them_cli() {   # <gói npm> <tên binary> <tên hiển thị>
  # Codex supplies the live model catalog; an installed old CLI must be upgraded.
  if [ "$2" != "codex" ] && command -v "$2" >/dev/null 2>&1; then return 0; fi
  log "Installing $3 globally via npm (best-effort)..."
  if npm install -g "$1" >/dev/null 2>&1 || $SUDO npm install -g "$1" >/dev/null 2>&1; then
    ok "$3 $("$2" --version 2>/dev/null || echo installed)"
  else
    warn "Could not install $3 - that engine will not show on the Models page. Install it by hand: npm i -g $1"
  fi
}
# Engine Gemini CLI đã GỠ HẲN ở 0.50.0 (Google ngắt mọi tài khoản cá nhân từ 18/06/2026).
cai_them_cli @openai/codex@latest codex "Codex CLI"

# --- 4c. agy (Antigravity CLI, đường Google) + grok (Grok Build, đường xAI) ---
#
# Hai engine này KHÔNG cài bằng npm: mỗi nhà một script tải về chạy thẳng. Trước 0.59.13 cài
# xong Javis là người dùng còn phải tự mở terminal gõ hai dòng của hai nhà khác nhau, và chủ
# dự án báo đúng chỗ đó làm người không quen kỹ thuật tắc ở màn Models với hai thẻ "CLI chưa
# cài" (16/09). Nay cài luôn một lượt.
#
# BEST-EFFORT tuyệt đối: chạy script của nhà thứ ba nên hỏng là chuyện bình thường (mạng, máy
# lạ, nhà cung cấp đổi URL) - hỏng thì nói một dòng rồi đi tiếp, không được giết lần cài.
# ĐĂNG NHẬP thì vẫn là việc của người dùng, làm ở trang Models sau khi Javis chạy.
cai_cli_script() {   # <tên binary> <tên hiển thị> <URL script cài>
  if command -v "$1" >/dev/null 2>&1; then ok "$2 da co san"; return 0; fi
  log "Installing $2 (best-effort, script cua nha cung cap)..."
  if curl -fsSL "$3" | bash >/dev/null 2>&1; then
    export PATH="$HOME/.local/bin:$PATH"
    if command -v "$1" >/dev/null 2>&1; then ok "$2"; else
      warn "$2: the installer finished but binary '$1' is not on PATH yet. Open a new terminal and retry: curl -fsSL $3 | bash"
    fi
  else
    warn "Could not install $2 - that engine will not show on the Models page. Install it by hand: curl -fsSL $3 | bash"
  fi
}
cai_cli_script agy "Antigravity CLI (Google)" https://antigravity.google/cli/install.sh
cai_cli_script grok "Grok Build (xAI)" https://x.ai/cli/install.sh

# --- 5. venv + python deps ---
log "Creating virtualenv (.venv)..."
# A .venv left over from a failed run can be built on 3.9 - reusing it reproduces the
# exact uvicorn resolve error the probe above exists to prevent. Rebuild instead.
if [ -d .venv ] && ! py_ok ./.venv/bin/python; then
  warn ".venv runs $(./.venv/bin/python --version 2>&1 || echo 'an unusable Python') - rebuilding with $PYTHON_BIN"
  rm -rf .venv
fi
[ -d .venv ] || "$PYTHON_BIN" -m venv .venv
./.venv/bin/pip install --upgrade pip -q
./.venv/bin/pip install -r requirements.txt -q
ok "Python deps installed"

# --- 6. .env (chmod 600 - holds tokens) ---
if [ ! -f .env ]; then cp env.example .env; chmod 600 .env; ok "Created .env from template"; else chmod 600 .env 2>/dev/null || true; ok ".env exists"; fi

# --- 7. minimal config prompt ---
if [ -t 0 ]; then
  read -rp "Vault path [blank = in-repo vault/]: " VP || true
  if [ -n "${VP:-}" ]; then
    if grep -q '^OBSIDIAN_VAULT_PATH=' .env; then sed -i.bak "s|^OBSIDIAN_VAULT_PATH=.*|OBSIDIAN_VAULT_PATH=$VP|" .env && rm -f .env.bak; else echo "OBSIDIAN_VAULT_PATH=$VP" >> .env; fi
  fi
fi
grep -q '^JAVIS_HOST=' .env || echo "JAVIS_HOST=127.0.0.1" >> .env

# --- 7b. Tài khoản quản trị: ĐẶT SẴN ngay lúc cài ---
#
# Trước đây bước này không tồn tại, nên ai mở Javis ra công khai đều đụng "MÃ THIẾT LẬP":
# server in một chuỗi ngẫu nhiên vào log lúc khởi động, và người dùng phải SSH vào VPS đọc log
# rồi dán vào trình duyệt mới tạo được tài khoản. Cái mã đó có lý do tồn tại - nó chặn người
# lạ chỉ-có-URL chiếm quyền admin lần đầu - nhưng bắt người ta đi đọc log là một trải nghiệm
# tệ, và tệ ĐÚNG LÚC họ mới cài xong và chưa quen gì cả.
#
# Đặt sẵn tài khoản ở đây giải quyết cả hai đầu: người đang chạy script này vốn ĐÃ ngồi trên
# máy chủ rồi, nên hỏi họ một câu không thêm bước nào; mà server thì boot lên đã có admin nên
# `setup_token_required()` trả về false và MÃ THIẾT LẬP không bao giờ hiện ra.
#
# KHÔNG bỏ hẳn cơ chế mã: nó vẫn là lưới cho ai deploy bằng cách khác (compose tay, image trần).
# Bỏ nó đi là mở toang `/auth/setup` cho bất kỳ ai gõ trúng URL trước chủ máy - mà thứ họ chiếm
# được là một máy có Bash, chạy full quyền, cắm sẵn vào POS/quảng cáo/email của chủ.
_gen_pw() { python3 -c "import secrets,string; a=string.ascii_letters+string.digits; print(''.join(secrets.choice(a) for _ in range(20)))"; }

# Ghi .env bằng python chứ không bằng sed: mật khẩu người dùng tự gõ có thể chứa | & \ " '
# và mọi ký tự đó đều làm vỡ một lệnh sed viết theo lối thường gặp. Giá trị đi qua argv nên
# không qua tay shell lần nào; ghi ra dạng nháy kép có escape để python-dotenv đọc lại đúng.
_env_set() {
  python3 - "$1" "$2" <<'PY'
import pathlib, sys
key, val = sys.argv[1], sys.argv[2]
esc = val.replace("\\", "\\\\").replace('"', '\\"')
p = pathlib.Path(".env")
lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
out, done = [], False
for ln in lines:
    if ln.split("=", 1)[0].strip() == key and not ln.lstrip().startswith("#"):
        if not done:
            out.append(f'{key}="{esc}"')
            done = True
    else:
        out.append(ln)
if not done:
    out.append(f'{key}="{esc}"')
p.write_text("\n".join(out) + "\n", encoding="utf-8")
PY
}

_env_has() { grep -qE "^[[:space:]]*$1=[\"']?[^\"'[:space:]]" .env 2>/dev/null; }

ADMIN_PW_SINH=""      # chỉ có giá trị khi script TỰ SINH - để in ra đúng một lần ở cuối
if _env_has JAVIS_ADMIN_PASSWORD; then
  ok "Admin account already set in .env - keeping it"
else
  ADMIN_USER="admin"
  ADMIN_PW=""
  if [ -t 0 ]; then
    echo ""
    log "Javis admin account (required: the AI brain runs with full rights on this machine):"
    read -rp "  Username [admin]: " AU || true
    [ -n "${AU:-}" ] && ADMIN_USER="$AU"
    while :; do
      read -rsp "  Password (Enter = generate a strong one): " AP || true; echo ""
      if [ -z "${AP:-}" ]; then ADMIN_PW="$(_gen_pw)"; ADMIN_PW_SINH="$ADMIN_PW"; break; fi
      # Server cũng chặn dưới 8 ký tự (main.py /auth/setup). Chặn luôn ở đây để người ta biết
      # ngay lúc gõ, thay vì lúc đăng nhập lần đầu mới phát hiện .env có mật khẩu không xài được.
      if [ "${#AP}" -lt 8 ]; then warn "  At least 8 characters."; continue; fi
      read -rsp "  Repeat it: " AP2 || true; echo ""
      if [ "$AP" = "${AP2:-}" ]; then ADMIN_PW="$AP"; break; fi
      warn "  The two entries do not match, try again."
    done
  else
    # Chạy không có bàn phím (curl | bash, CI, script khác gọi vào). Tự sinh chứ KHÔNG bỏ trống:
    # bỏ trống là đẩy người dùng về đúng cái màn đọc-log mà bước này sinh ra để xoá đi.
    ADMIN_PW="$(_gen_pw)"; ADMIN_PW_SINH="$ADMIN_PW"
  fi
  _env_set JAVIS_ADMIN_USER "$ADMIN_USER"
  _env_set JAVIS_ADMIN_PASSWORD "$ADMIN_PW"
  chmod 600 .env
  ok "Admin account saved in .env"
fi

# --- 7c. Xác thực 2 lớp: HỎI ở đây, BẬT ở trình duyệt ---
#
# Cố ý không làm trọn vẹn trong terminal. Bật 2FA cần quét một mã QR, mà vẽ QR ra terminal thì
# nửa số máy hiện sai (font, tỉ lệ ô, nền sáng/tối) và người dùng phải soi điện thoại vào cửa
# sổ SSH. Trong khi vài giây nữa họ sẽ mở trình duyệt để đăng nhập - chỗ hiện QR đúng đắn.
#
# Nên bước này chỉ ghi Ý ĐỊNH vào .env. Server đọc cờ đó rồi mở sẵn màn bật 2FA ở trang Tài
# khoản. Cờ này KHÔNG phải rào bảo mật và không tự bật gì cả: 2FA chỉ thật sự bật sau khi
# người dùng quét QR và nhập đúng một mã, vì bật trước lúc họ chứng minh app sinh đúng mã là
# tự khoá họ ra ngoài chính máy vừa cài.
if ! _env_has JAVIS_SETUP_2FA && [ -t 0 ]; then
  read -rp "  Turn on two-factor sign-in (Google Authenticator)? [y/N]: " TFA || true
  case "${TFA:-}" in
    [yY]*)
      _env_set JAVIS_SETUP_2FA 1
      ok "Noted - the first time you open the dashboard, the Account page will show the QR code to scan"
      ;;
    *) log "Skipped - you can turn it on any time under Dashboard → Account" ;;
  esac
fi

# --- 8. one-time Claude auth reminder ---
if ! claude auth status >/dev/null 2>&1; then
  warn "Claude CLI is not logged in. Run this ONCE (opens a browser-login URL):"
  echo "      claude auth login --claudeai"
fi

# --- 8b. Truy cập từ xa: tên miền + HTTPS ngay lúc cài ---
#
# Bản native chỉ nghe 127.0.0.1 (an toàn mặc định), nên trước đây cài xong người dùng KHÔNG vào
# được giao diện từ máy mình nếu không biết dựng SSH tunnel - mà tên miền + nút Kích hoạt lại nằm
# trong giao diện. Bước này cắt vòng luẩn quẩn đó: nginx đứng trước app, có tên miền thì HTTPS
# luôn, chưa có thì mở tạm http://<ip>. Chỉ làm trên Linux có systemd và có quyền root/sudo.
NGX_DOMAIN=""; NGX_RUN=0; NGX_RESULT=""; NGX_PUBIP=""
_DOMAIN_RE='^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$'
_settings_set() {   # _settings_set <khoá-trong-domain> <giá-trị-json>
  python3 - "$APP_DIR/server/settings.json" "$1" "$2" <<'PY'
import json, os, sys
path, key, val = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
d = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f) or {}
d.setdefault("domain", {})[key] = val
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
os.chmod(tmp, (os.stat(path).st_mode & 0o777) if os.path.exists(path) else 0o600)
os.replace(tmp, path)
PY
}
if [ "${THANSA_NGINX:-1}" != "0" ] && [ "$(uname -s)" = "Linux" ] && command -v systemctl >/dev/null 2>&1 \
   && [ -d /run/systemd/system ] && { [ "$(id -u)" -eq 0 ] || [ -n "$SUDO" ]; }; then
  NGX_RUN=1
  CU="$(python3 -c "import json,sys;print((json.load(open(sys.argv[1])).get('domain') or {}).get('custom',''))" "$APP_DIR/server/settings.json" 2>/dev/null || true)"
  NGX_DOMAIN="$(printf '%s' "${THANSA_DOMAIN:-$CU}" | tr 'A-Z' 'a-z' | sed 's#^https\?://##; s#/.*##')"
  if [ -z "$NGX_DOMAIN" ] && [ -t 0 ]; then
    echo ""
    log "Domain for opening Thansa from anywhere (HTTPS is set up automatically)."
    echo "    Point an A record of the domain to this server's IP first."
    read -rp "  Domain, e.g. app.yourdomain.com [blank = none yet]: " ND || true
    NGX_DOMAIN="$(printf '%s' "${ND:-}" | tr 'A-Z' 'a-z' | sed 's#^https\?://##; s#/.*##')"
  fi
  if [ -n "$NGX_DOMAIN" ] && ! [[ "$NGX_DOMAIN" =~ $_DOMAIN_RE ]]; then
    warn "'$NGX_DOMAIN' is not a valid domain - skipping it (you can enter it later in the app)."
    NGX_DOMAIN=""
  fi
  # Ghi TRƯỚC khi dịch vụ khởi động: proxy=nginx bắt app đòi đăng nhập ngay từ request đầu tiên
  # (mọi request qua nginx đều tới từ 127.0.0.1 - xem config.require_login).
  _settings_set proxy '"nginx"'
  [ -z "$NGX_DOMAIN" ] || _settings_set custom "\"$NGX_DOMAIN\""
fi

# --- 9. service: systemd if available, else nohup ---
PY="$APP_DIR/.venv/bin/python"
if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
  log "Installing systemd service ($SVC.service, port $PORT)..."
  $SUDO tee "/etc/systemd/system/$SVC.service" >/dev/null <<UNIT
[Unit]
Description=Javis OS ($SVC)
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR/server
Environment="JAVIS_HOST=127.0.0.1"
Environment="JAVIS_PORT=$PORT"
Environment="JAVIS_STATE_DIR=$APP_DIR/server"
Environment="PATH=$APP_DIR/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$PY -m uvicorn main:app --host 127.0.0.1 --port $PORT
Restart=always
RestartSec=5
KillSignal=SIGTERM
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable --now "$SVC.service"
  ok "Service installed. Logs: journalctl -u $SVC -f"
else
  warn "systemd not available - starting under nohup..."
  ( cd "$APP_DIR/server" && JAVIS_STATE_DIR="$APP_DIR/server" JAVIS_PORT="$PORT" nohup "$PY" -m uvicorn main:app --host 127.0.0.1 --port "$PORT" > "$APP_DIR/server/javis.log" 2>&1 & )
  ok "Started. Logs: $APP_DIR/server/javis.log"
fi

# --- 9b. nginx: HTTPS cho tên miền, hoặc lối vào tạm bằng IP ---
if [ "$NGX_RUN" = "1" ]; then
  NGX_PUBIP="$(curl -fsS --max-time 5 https://api.ipify.org 2>/dev/null || true)"
  NGX_SH="$APP_DIR/bin/thansa-nginx-ssl.sh"
  if [ -n "$NGX_DOMAIN" ]; then
    DNS_IP="$(getent ahostsv4 "$NGX_DOMAIN" 2>/dev/null | awk 'NR==1{print $1}' || true)"
    if [ -n "$NGX_PUBIP" ] && [ "$DNS_IP" != "$NGX_PUBIP" ]; then
      # Xin chứng chỉ khi DNS chưa đúng chỉ tốn lượt của Let's Encrypt (giới hạn số lần hỏng).
      warn "DNS of $NGX_DOMAIN points to '${DNS_IP:-nothing}', this server is $NGX_PUBIP - HTTPS will wait."
      warn "Fix the A record, then press Activate in the app (Settings -> Domain & SSL)."
    else
      log "Setting up nginx + Let's Encrypt for $NGX_DOMAIN (first time: 1-3 minutes)..."
      if $SUDO bash "$NGX_SH" "$NGX_DOMAIN" "$PORT" | grep -E '^(STEP|RESULT):' | sed 's/^/    /' | tee /tmp/thansa-ngx.$$ >/dev/null \
         && grep -q '^    RESULT:OK' /tmp/thansa-ngx.$$; then
        NGX_RESULT="https"
        _settings_set ssl_enabled true
      else
        warn "HTTPS for $NGX_DOMAIN did not come up ($(grep -o 'RESULT:FAIL:.*' /tmp/thansa-ngx.$$ 2>/dev/null || echo unknown))."
        warn "You can retry later with the Activate button in the app."
      fi
      rm -f /tmp/thansa-ngx.$$
    fi
  fi
  if [ -z "$NGX_RESULT" ]; then
    OUT="$($SUDO bash "$NGX_SH" --ip "$PORT" 2>&1 || true)"
    case "$OUT" in
      *RESULT:OK*) NGX_RESULT="ip" ;;
      *RESULT:FAIL:other-sites*) warn "nginx already serves other sites on this machine - not opening a temporary IP entrance." ;;
      *) warn "Could not open the temporary IP entrance ($(printf '%s' "$OUT" | grep -o 'RESULT:FAIL:.*' || echo unknown))." ;;
    esac
  fi
fi

echo ""
ok "Javis OS is up at: http://127.0.0.1:$PORT"
log "Remote access (SSH tunnel): ssh -L $PORT:localhost:$PORT $(whoami)@<vps-ip>"

# Mật khẩu tự sinh chỉ in ra ĐÚNG chỗ này, đúng một lần. Không ghi vào log service, không in
# lại ở lần chạy sau - `.env` (chmod 600) là nơi giữ nó. In sau phần khởi động để nó nằm ở
# cuối màn hình, chỗ người ta chắc chắn còn nhìn.
if [ -n "${ADMIN_PW_SINH:-}" ]; then
  echo ""
  echo "=================================================================="
  echo "  ADMIN ACCOUNT (saved in .env, shown only ONCE):"
  echo "      Username:  ${ADMIN_USER:-admin}"
  echo "      Password:  $ADMIN_PW_SINH"
  echo "  Copy it somewhere safe now. You can change it later under Dashboard → Account."
  echo "=================================================================="
fi
if [ "$NGX_RESULT" = "https" ]; then
  echo ""
  echo "=================================================================="
  echo "  OPEN THANSA:   https://$NGX_DOMAIN"
  echo "  Sign in with the admin account. Certificate renews automatically."
  echo "=================================================================="
  exit 0
fi
if [ "$NGX_RESULT" = "ip" ]; then
  echo ""
  echo "=================================================================="
  echo "  OPEN THANSA:   http://${NGX_PUBIP:-<server-ip>}"
  echo "  TEMPORARY and NOT encrypted - use it only to finish setup:"
  echo "    sign in -> Settings -> Domain & SSL -> enter your domain -> Activate."
  echo "  After HTTPS is on, this IP entrance closes by itself."
  echo "  Cannot open it? Allow ports 80 and 443 in your VPS provider's firewall."
  echo "=================================================================="
fi
echo ""
log "Remote access through a Cloudflare Tunnel (no open port, HTTPS included):"
echo "    1) Sign in with the admin account above (the AI brain runs with full rights!)."
if command -v cloudflared >/dev/null 2>&1; then
  echo "    2) cloudflared tunnel --url http://localhost:$PORT   → open https://<random>.trycloudflare.com"
else
  echo "    2) Install cloudflared:  curl -fsSL https://pkg.cloudflare.com/cloudflared.deb -o /tmp/cf.deb && $SUDO dpkg -i /tmp/cf.deb"
  echo "       Then:  cloudflared tunnel --url http://localhost:$PORT"
fi
