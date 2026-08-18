#!/usr/bin/env bash
# Entry cho cron (GĐ4): chạy bộ dò hằng ngày, có CỜ KHẨN thì báo Telegram.
# KHÔNG sửa nhánh nào, không commit — đúng luật DAC-TA mục 3.
set -uo pipefail
OPS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$OPS/ban-tin/cron.log"
{
  echo "=== $(date -Is) chay do hang ngay"
  bash "$OPS/do-hang-ngay.sh"
  MA=$?
  if [ "$MA" -eq 2 ]; then
    BT="$OPS/ban-tin/$(date +%F).md"
    bash "$OPS/bao-khan.sh" "$(cat "$BT")" || true
  fi
  echo "=== exit $MA"
} >> "$LOG" 2>&1
