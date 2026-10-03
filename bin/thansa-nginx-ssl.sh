#!/usr/bin/env bash
# thansa-nginx-ssl.sh - dựng nginx reverse proxy + chứng chỉ Let's Encrypt cho bản cài NATIVE
# (systemd / chạy trực tiếp trên Linux, không Docker, không Hostinger).
#
#   sudo bash bin/thansa-nginx-ssl.sh <ten-mien> [cong-app=7777] [email]
#
# Dashboard gọi script này qua `sudo -n` khi người dùng bấm "Kích hoạt" ở thẻ TÊN MIỀN & SSL.
# Tài khoản chạy Thansa không có sudo không-mật-khẩu thì dashboard hiện đúng dòng lệnh trên để
# chạy tay một lần. Chạy lại bao nhiêu lần cũng được: cấu hình được ghi đè, chứng chỉ còn hạn thì
# certbot giữ nguyên (--keep-until-expiring), gia hạn do certbot.timer của hệ thống lo.
#
# Mỗi dòng "STEP:<bước>" / "RESULT:..." là giao thức với server/nginx_ssl.py - đừng đổi chữ.
set -euo pipefail

DOMAIN="$(printf '%s' "${1:-}" | tr 'A-Z' 'a-z')"
PORT="${2:-7777}"
EMAIL="${3:-}"

fail() { echo "RESULT:FAIL:$*"; exit 1; }

# Kiểm lại ở đây dù server đã kiểm: script chạy bằng root, đầu vào phải sạch trước khi chạm /etc.
[[ "$DOMAIN" =~ ^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$ ]] || fail "invalid-domain"
[[ "$PORT" =~ ^[0-9]{2,5}$ ]] || fail "invalid-port"
[[ -z "$EMAIL" || "$EMAIL" =~ ^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$ ]] || fail "invalid-email"
[ "$(id -u)" -eq 0 ] || fail "need-root"

echo "STEP:install"
export DEBIAN_FRONTEND=noninteractive
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
  CONF="/etc/nginx/sites-available/thansa-$DOMAIN.conf"
  LINK="/etc/nginx/sites-enabled/thansa-$DOMAIN.conf"
  # Site khác đang khai cùng server_name thì nginx chọn bừa một cái ("conflicting server name")
  # và certbot có thể gắn chứng chỉ nhầm chỗ. Chỉ gỡ SYMLINK trong sites-enabled, file gốc giữ.
  for f in /etc/nginx/sites-enabled/*; do
    [ -e "$f" ] || continue
    [ "$f" = "$LINK" ] && continue
    if grep -qE "server_name[^;]*[[:space:]]$DOMAIN([[:space:]]|;)" "$f" 2>/dev/null && [ -L "$f" ]; then
      echo "disable-dup:$f"; rm -f "$f"
    fi
  done
else
  CONF="/etc/nginx/conf.d/thansa-$DOMAIN.conf"
  LINK=""
fi
# Biến map đặt tên riêng: tên phổ biến $connection_upgrade rất hay đã có ở site khác, khai trùng
# là nginx -t đỏ và cả máy chủ web ngừng nạp cấu hình.
cat >"$CONF" <<EOF
# Sinh bởi Thansa OS (bin/thansa-nginx-ssl.sh). Chạy lại "Kích hoạt" sẽ ghi đè file này.
map \$http_upgrade \$thansa_conn_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$thansa_conn_upgrade;
        # Chat stream (SSE) và WebSocket: không đệm, giữ kết nối lâu.
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
EOF
[ -z "$LINK" ] || ln -sf "$CONF" "$LINK"
"$NGINX" -t >/dev/null 2>&1 || { "$NGINX" -t 2>&1 | tail -3; fail "nginx-config"; }
systemctl enable nginx >/dev/null 2>&1 || true
if systemctl is-active --quiet nginx; then systemctl reload nginx; else systemctl start nginx; fi || fail "nginx-start"
# Mở tường lửa nếu ufw đang bật (bỏ qua êm nếu không có ufw).
if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
  ufw allow 80/tcp >/dev/null || true
  ufw allow 443/tcp >/dev/null || true
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
"$NGINX" -t >/dev/null 2>&1 || fail "nginx-config"
systemctl reload nginx || fail "nginx-start"
echo "RESULT:OK"
