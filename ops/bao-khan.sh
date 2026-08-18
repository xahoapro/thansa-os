#!/usr/bin/env bash
# Gửi cảnh báo CỜ KHẨN qua Telegram (kênh chốt bởi chủ 18/08/2026 — GĐ4).
# Secret KHÔNG vào git: đọc từ /home/thansa/.thansa-alert.env, gồm 2 dòng:
#   TELEGRAM_BOT_TOKEN=123456:ABC...
#   TELEGRAM_CHAT_ID=123456789
# Cách dùng:  bao-khan.sh "noi dung"   hoặc  echo "noi dung" | bao-khan.sh
set -euo pipefail
ENV_FILE="/home/thansa/.thansa-alert.env"
MSG="${1:-$(cat)}"
if [ -f "$ENV_FILE" ]; then
  # shellcheck source=/dev/null
  . "$ENV_FILE"
fi
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
  # Chưa cấu hình → ghi lại để không mất cảnh báo, thoát khác 0 cho cron log thấy.
  LOG="$(dirname "${BASH_SOURCE[0]}")/ban-tin/khan-chua-gui.log"
  printf '%s KHAN CHUA GUI (thieu %s):\n%s\n' "$(date -Is)" "$ENV_FILE" "$MSG" >> "$LOG"
  echo "CHUA GUI: thieu TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID trong $ENV_FILE (da ghi $LOG)" >&2
  exit 3
fi
curl -sf --max-time 20 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=🚨 THANSA — CỜ KHẨN
${MSG}" > /dev/null
echo "da gui Telegram"
