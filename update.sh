#!/usr/bin/env bash
# ============================================================================
# Thansa OS - cập nhật lên bản mới nhất từ GitHub.
#   ./update.sh            (tự nhận Docker hay native)
#   ./update.sh docker     (ép chế độ Docker)
#   ./update.sh native     (ép chế độ native/systemd)
# ============================================================================
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
MODE="${1:-auto}"
SUDO=""; [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1 && SUDO="sudo"
# KHÔNG viết `lệnh | grep -q` trong file này: dưới pipefail, grep -q khớp xong thoát sớm → lệnh bên
# trái chết SIGPIPE (141) → cả ống SAI dù đã khớp. Vụ máy khách 09/10: `systemctl list-unit-files |
# grep -q` ra 141 → tưởng không có systemd → rơi nhánh nohup tranh cổng với dịch vụ.
_co_unit() { command -v systemctl >/dev/null 2>&1 && systemctl cat "$1.service" >/dev/null 2>&1; }
_ds_container() { command -v docker >/dev/null 2>&1 && docker ps -a --format '{{.Names}}' 2>/dev/null || true; }
_co_container() { local ds; ds="$(_ds_container)"; [ -n "$ds" ] && grep -qx "$1" <<<"$ds"; }
# install.sh cài Node riêng vào ~/.thansa/node (máy cũ: ~/.javis/node) + symlink ~/.local/bin; phiên
# SSH thường thiếu cả hai trong PATH → "npm not found" và Codex không bao giờ được cập nhật.
for _d in "$HOME/.thansa/node/bin" "$HOME/.javis/node/bin" "$HOME/.local/bin"; do
  [ -d "$_d" ] && PATH="$_d:$PATH"
done

# Tên bản Thansa Ở THƯ MỤC NÀY. Nhiều bản trên cùng VPS thì mỗi bản một .env riêng; không đọc
# .env ở đây thì `./update.sh` của bản này đi restart container/dịch vụ của bản khác.
_env_val() { [ -f .env ] && sed -n "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*//p" .env | tail -1 | tr -d '"' || true; }
NAME="${THANSA_NAME:-${JAVIS_NAME:-}}"
[ -n "$NAME" ] || NAME="$(_env_val THANSA_NAME)"
[ -n "$NAME" ] || NAME="$(_env_val JAVIS_NAME)"
# Không đặt tên: bản cài mới mang tên "thansa", máy cài trước 1.19 mang tên cũ "javis" (container
# Docker / dịch vụ systemd). Dò cái đang THẬT SỰ tồn tại, thiếu bước này là update.sh đi tìm
# "thansa" trên máy cũ, không thấy, rồi rẽ nhầm nhánh.
if [ -z "$NAME" ]; then
  NAME="thansa"
  if _co_container javis && ! _co_container thansa; then
    NAME="javis"
  elif _co_unit javis && ! _co_unit thansa; then
    NAME="javis"
  fi
fi
# Docker: compose đặt tên container theo JAVIS_NAME (mặc định nay là thansa) - máy cũ phải giữ
# đúng tên container đang chạy, không thì compose dựng container MỚI tranh cổng với container cũ.
export JAVIS_NAME="$NAME"
# Nhãn launchd (Mac): bản mới com.thansa.os, máy cũ com.javis.os.
LABEL="${THANSA_LAUNCHD_LABEL:-${JAVIS_LAUNCHD_LABEL:-}}"
if [ -z "$LABEL" ]; then
  LABEL="com.thansa.os"
  [ -f "$HOME/Library/LaunchAgents/com.thansa.os.plist" ] || { [ -f "$HOME/Library/LaunchAgents/com.javis.os.plist" ] && LABEL="com.javis.os"; }
fi

echo "==> Pulling the latest code from GitHub..."
git pull --ff-only

is_docker() {
  [ -f docker-compose.yml ] && _co_container "$NAME"
}

if [ "$MODE" = "docker" ] || { [ "$MODE" = "auto" ] && is_docker; }; then
  echo "==> Docker → pulling the new image from GHCR and restarting..."
  # Đang bật HTTPS (Caddy)? Giữ nguyên override để cập nhật KHÔNG gỡ mất Caddy.
  HTTPS_ARGS=""
  if _co_container "$NAME-caddy"; then
    HTTPS_ARGS="-f docker-compose.yml -f docker-compose.https.yml"
    echo "==> Caddy (HTTPS) detected → keeping the HTTPS setup."
  elif command -v ss >/dev/null 2>&1 && [ -n "$(ss -tlnH '( sport = :80 or sport = :443 )' 2>/dev/null)" ]; then
    # docker-compose.yml nay dựng sẵn Caddy. Máy chưa có Caddy mà 80/443 đã có web server khác
    # (nginx/Apache tự dựng) thì Caddy mới sẽ giành cổng và hỏng `up` - tắt nó cho lượt này.
    export JAVIS_CADDY=0
    echo "==> Ports 80/443 are already in use by another web server → leaving the built-in Caddy off (JAVIS_CADDY=0)."
  fi
  # Đứng sau proxy dùng chung (nhiều bản, mỗi bản một tên miền) thì giữ luôn override multi,
  # không thì lượt cập nhật này gỡ mất nhãn Caddy và bản đó rơi khỏi proxy.
  if [ -f docker-compose.multi.yml ] && docker network inspect javis-web >/dev/null 2>&1; then
    HTTPS_ARGS="-f docker-compose.yml -f docker-compose.multi.yml"
    echo "==> Shared proxy (javis-web) detected → keeping the multi-instance setup."
  fi
  docker compose $HTTPS_ARGS pull
  docker compose $HTTPS_ARGS up -d
  echo "==> Done. Follow the logs:  docker compose logs -f"
else
  echo "==> Native → updating Python libraries and restarting the service..."
  [ -d .venv ] && ./.venv/bin/pip install -r requirements.txt -q || true
  # Updating Python alone leaves the ChatGPT model catalog on an old Codex CLI.
  if command -v npm >/dev/null 2>&1; then
    if ! npm install -g @openai/codex@latest && ! $SUDO npm install -g @openai/codex@latest; then
      echo "[!] Could not update Codex; the ChatGPT model list may be out of date."
    fi
  else
    echo "[!] npm not found; update Codex by hand to get the newest ChatGPT models."
  fi
  if _co_unit "$NAME"; then
    $SUDO systemctl restart "$NAME"
    echo "==> Restarted. Follow the logs:  journalctl -u $NAME -f"
  elif [ "$(uname)" = "Darwin" ] && \
       launchctl print "gui/$(id -u)/$LABEL" >/dev/null 2>&1; then
    # Mac chạy dưới launchd (KeepAlive): kill PID rồi tự chạy nohup là đua bind cổng với bản
    # launchd respawn ([Errno 48], vụ 14/08/2026). Để launchd tự đổi ca bằng kickstart -k.
    TARGET="gui/$(id -u)/$LABEL"
    echo "==> launchd ($TARGET) detected → kickstart -k..."
    launchctl kickstart -k "$TARGET"
    echo "==> Asked launchd to restart Thansa. Logs: server/thansa.log"
  else
    # Mac / Linux không systemd: kill tiến trình đang giữ cổng rồi chạy lại nền (như install.sh)
    PORT="${JAVIS_PORT:-7777}"
    PIDS="$(lsof -ti tcp:"$PORT" 2>/dev/null || true)"
    if [ -n "$PIDS" ]; then
      echo "==> Stopping the old process (PID: $PIDS)..."
      kill $PIDS 2>/dev/null || true
      sleep 2
    fi
    # </dev/null: không thì tiến trình nền giữ pty và phiên SSH chạy update.sh treo không thoát.
    ( cd server && JAVIS_STATE_DIR="$PWD" nohup ../.venv/bin/python -m uvicorn main:app \
        --host "${JAVIS_HOST:-127.0.0.1}" --port "$PORT" > thansa.log 2>&1 < /dev/null & )
    echo "==> Restarted (nohup). Logs: server/thansa.log"
  fi
fi
