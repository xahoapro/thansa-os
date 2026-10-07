#!/usr/bin/env bash
# Cron: tự quét Javis, có bản mới thì tự trộn + nghiệm thu + phát hành Thansa (ops/tu_dong_tron.py).
# Lỗi / xung đột → nhắn Telegram (~/.thansa-alert.env) rồi dừng; phát hành xong cũng nhắn.
# flock: hai lượt không bao giờ chạy chồng (một lượt có nghiệm thu mất ~35 phút).
set -uo pipefail
OPS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="/home/thansa/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export HOME="${HOME:-/home/thansa}"
unset JAVIS_STATE_DIR JAVIS_BRAIN JAVIS_IN_TERMINAL     # bẫy 28/09: test không được ghi state app thật
exec 9>"$OPS/ban-tin/.tu-dong.lock"
flock -n 9 || { echo "$(date -Is) đang có lượt khác chạy - bỏ qua" >> "$OPS/ban-tin/tu-dong.log"; exit 0; }
/usr/bin/python3 "$OPS/tu_dong_tron.py" "$@" >> "$OPS/ban-tin/tu-dong-cron.log" 2>&1
