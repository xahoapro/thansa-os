#!/usr/bin/env bash
# thansa-nginx-ssl.sh - dựng nginx reverse proxy + chứng chỉ Let's Encrypt cho bản cài NATIVE
# (systemd / chạy trực tiếp trên Linux, không Docker, không Hostinger).
#
#   sudo bash bin/thansa-nginx-ssl.sh <ten-mien> [cong-app=7777] [email]
#   sudo bash bin/thansa-nginx-ssl.sh --ip [cong-app=7777]
#
# Chế độ tên miền: dashboard gọi qua `sudo -n` khi người dùng bấm "Kích hoạt" ở thẻ TÊN MIỀN &
# SSL (install.sh cũng gọi khi người cài khai tên miền ngay từ đầu). Không có sudo không-mật-khẩu
# thì dashboard hiện đúng dòng lệnh trên để chạy tay một lần. Chạy lại bao nhiêu lần cũng được:
# cấu hình ghi đè, chứng chỉ còn hạn thì certbot giữ nguyên (--keep-until-expiring), gia hạn do
# certbot.timer của hệ thống lo. Xong tên miền thì lối vào tạm bằng IP (chế độ --ip) bị gỡ.
#
# Chế độ --ip: lối vào TẠM http://<ip-máy-chủ> cho lần đầu, khi người cài chưa có tên miền.
# Bản native chỉ nghe 127.0.0.1 nên không có lối này thì khách không vào nổi giao diện để mà khai
# tên miền. Chỉ dựng khi nginx CHƯA phục vụ site nào khác (không đè web có sẵn của máy).
#
# Mỗi dòng "STEP:<bước>" / "RESULT:..." là giao thức với server/nginx_ssl.py - đừng đổi chữ.
set -euo pipefail

# PATH đầy đủ, KHÔNG thừa kế: dịch vụ Thansa (unit systemd cũ) chạy với PATH=.venv/bin:/usr/local/bin:
# /usr/bin:/bin - thiếu /usr/sbin. Gọi qua sudo có env_reset thì được secure_path cứu, nhưng app chạy
# bằng root (hoặc sudo không reset PATH) là script thừa kế nguyên PATH đó, và certbot - tự tìm
# `nginx` theo PATH - báo "Could not find a usable 'nginx' binary" ngay lần cài đầu.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

fail() { echo "RESULT:FAIL:$*"; exit 1; }

MODE="domain"
if [ "${1:-}" = "--ip" ]; then
  MODE="ip"
  DOMAIN=""
  PORT="${2:-7777}"
  EMAIL=""
else
  DOMAIN="$(printf '%s' "${1:-}" | tr 'A-Z' 'a-z')"
  PORT="${2:-7777}"
  EMAIL="${3:-}"
  # Kiểm lại ở đây dù server đã kiểm: script chạy bằng root, đầu vào phải sạch trước khi chạm /etc.
  [[ "$DOMAIN" =~ ^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$ ]] || fail "invalid-domain"
fi
[[ "$PORT" =~ ^[0-9]{2,5}$ ]] || fail "invalid-port"
[[ -z "$EMAIL" || "$EMAIL" =~ ^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$ ]] || fail "invalid-email"
[ "$(id -u)" -eq 0 ] || fail "need-root"

echo "STEP:install"
export DEBIAN_FRONTEND=noninteractive
# Cài certbot cả ở chế độ --ip: lát nữa người dùng bấm Kích hoạt là khỏi chờ cài thêm lần nữa.
if ! command -v nginx >/dev/null 2>&1 && [ ! -x /usr/sbin/nginx ] || ! command -v certbot >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq || true
    apt-get install -y -qq nginx certbot python3-certbot-nginx >/dev/null || fail "apt-install"
  elif command -v dnf >/dev/null 2>&1; then
    dnf install -y -q nginx certbot python3-certbot-nginx >/dev/null || fail "dnf-install"
  else
    fail "no-package-manager"
  fi
fi
NGINX="$(command -v nginx || echo /usr/sbin/nginx)"

# Cổng 80/443 đang bị tiến trình KHÁC nginx giữ (Caddy, Apache, Traefik...) thì nginx không lên
# được và certbot không qua được thử thách HTTP-01. Báo thẳng tên tiến trình thay vì để hỏng mù.
if command -v ss >/dev/null 2>&1; then
  khac="$(ss -tlnpH '( sport = :80 or sport = :443 )' 2>/dev/null | grep -o 'users:(("[^"]*"' | cut -d'"' -f2 | grep -v '^nginx$' | sort -u | tr '\n' ' ' || true)"
  [ -z "${khac// /}" ] || fail "ports-busy:${khac% }"
fi

echo "STEP:config"
if [ -d /etc/nginx/sites-available ]; then
  SITES_AV=/etc/nginx/sites-available; SITES_EN=/etc/nginx/sites-enabled
else
  SITES_AV=/etc/nginx/conf.d; SITES_EN=""
fi
BOOT_NAME="thansa-bootstrap.conf"

if [ "$MODE" = "ip" ]; then
  # Chỉ dựng lối vào bằng IP trên một nginx TRỐNG: nó nhận MỌI tên miền lạ (default_server), nên
  # máy đang phục vụ web khác mà chen vào là cướp truy cập của web đó.
  if [ -n "$SITES_EN" ]; then
    for f in "$SITES_EN"/*; do
      [ -e "$f" ] || continue
      case "$(basename "$f")" in default|"$BOOT_NAME") continue;; esac
      fail "other-sites:$(basename "$f")"
    done
  else
    for f in /etc/nginx/conf.d/*.conf; do
      [ -e "$f" ] || continue
      [ "$(basename "$f")" = "$BOOT_NAME" ] && continue
      grep -qE '^[[:space:]]*server[[:space:]]*\{' "$f" && fail "other-sites:$(basename "$f")"
    done
  fi
  CONF="$SITES_AV/$BOOT_NAME"
  LINK="${SITES_EN:+$SITES_EN/$BOOT_NAME}"
  MAPVAR="thansa_conn_upgrade_ip"
  LISTEN="listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;"
else
  CONF="$SITES_AV/thansa-$DOMAIN.conf"
  LINK="${SITES_EN:+$SITES_EN/thansa-$DOMAIN.conf}"
  # Tên biến map RIÊNG cho từng tên miền: hai bản Thansa trên một máy mà khai trùng một biến map
  # là `nginx -t` đỏ ("duplicate variable") và cả máy chủ web ngừng nạp cấu hình.
  MAPVAR="thansa_conn_upgrade_$(printf '%s' "$DOMAIN" | tr '.-' '__')"
  LISTEN="listen 80;
    listen [::]:80;
    server_name $DOMAIN;"
  if [ -n "$SITES_EN" ]; then
    # Site khác đang khai cùng server_name thì nginx chọn bừa một cái ("conflicting server name")
    # và certbot có thể gắn chứng chỉ nhầm chỗ. Chỉ gỡ SYMLINK trong sites-enabled, file gốc giữ.
    for f in "$SITES_EN"/*; do
      [ -e "$f" ] || continue
      [ "$f" = "$LINK" ] && continue
      if grep -qE "server_name[^;]*[[:space:]]$DOMAIN([[:space:]]|;)" "$f" 2>/dev/null && [ -L "$f" ]; then
        echo "disable-dup:$f"; rm -f "$f"
      fi
    done
  fi
fi

# Giữ bản cũ để trả lại nếu cấu hình mới làm `nginx -t` đỏ: một file hỏng trong sites-enabled là
# lần reload kế tiếp của BẤT KỲ ai trên máy này cũng hỏng theo.
BAK=""
if [ -f "$CONF" ]; then BAK="$CONF.thansa-bak"; cp -p "$CONF" "$BAK"; fi
rollback() {
  if [ -n "$BAK" ]; then mv -f "$BAK" "$CONF"; else rm -f "$CONF"; [ -z "$LINK" ] || rm -f "$LINK"; fi
}

cat >"$CONF" <<EOF
# Sinh bởi Thansa OS (bin/thansa-nginx-ssl.sh). Chạy lại sẽ ghi đè file này.
map \$http_upgrade \$$MAPVAR {
    default upgrade;
    ''      close;
}

server {
    $LISTEN

    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$$MAPVAR;
        # Chat stream (SSE) và WebSocket: không đệm, giữ kết nối lâu.
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
EOF
[ -z "$LINK" ] || ln -sf "$CONF" "$LINK"
# Site "Welcome to nginx" của Debian cũng khai default_server - để nguyên là trùng, nginx -t đỏ.
# Chỉ gỡ symlink, file gốc vẫn nằm trong sites-available.
if [ "$MODE" = "ip" ] && [ -n "$SITES_EN" ] && [ -L "$SITES_EN/default" ]; then rm -f "$SITES_EN/default"; fi
if ! "$NGINX" -t >/dev/null 2>&1; then
  "$NGINX" -t 2>&1 | tail -3
  rollback
  fail "nginx-config"
fi
rm -f "$BAK"
systemctl enable nginx >/dev/null 2>&1 || true
if systemctl is-active --quiet nginx; then systemctl reload nginx; else systemctl start nginx; fi || fail "nginx-start"
# Mở tường lửa nếu ufw đang bật (bỏ qua êm nếu không có ufw).
# Không `ufw status | grep -q`: dưới pipefail grep -q thoát sớm → SIGPIPE → điều kiện sai dù khớp.
if command -v ufw >/dev/null 2>&1 && grep -q "Status: active" <<<"$(ufw status 2>/dev/null || true)"; then
  ufw allow 80/tcp >/dev/null || true
  ufw allow 443/tcp >/dev/null || true
fi

if [ "$MODE" = "ip" ]; then
  echo "RESULT:OK"
  exit 0
fi

echo "STEP:cert"
if [ -n "$EMAIL" ]; then ACC=(--email "$EMAIL"); else ACC=(--register-unsafely-without-email); fi
if ! certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos "${ACC[@]}" \
      --redirect --keep-until-expiring 2>&1 | tail -20; then
  fail "certbot"
fi
# certbot trả 0 cả khi không cài được chứng chỉ vào cấu hình -> kiểm thẳng file.
[ -s "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ] || fail "certbot"
grep -q "ssl_certificate" "$CONF" || fail "certbot-install"

echo "STEP:verify"
# Tên miền đã có HTTPS: đóng lối vào tạm bằng IP (http trần, không mã hoá).
if [ -e "$SITES_AV/$BOOT_NAME" ]; then
  echo "close-ip-entry"
  rm -f "$SITES_AV/$BOOT_NAME"; [ -z "$SITES_EN" ] || rm -f "$SITES_EN/$BOOT_NAME"
fi
"$NGINX" -t >/dev/null 2>&1 || fail "nginx-config"
systemctl reload nginx || fail "nginx-start"
echo "RESULT:OK"
