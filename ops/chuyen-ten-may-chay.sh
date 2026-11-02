#!/usr/bin/env bash
# Chuyển MỘT máy đang chạy Thansa (cài từ trước bản 2.0.0) sang tên mới sau khi source bỏ hết chữ javis.
# Dùng cho máy chủ của chủ (thansa-chay); không còn máy người dùng cũ nào khác (chủ xác nhận 01/11/2026).
#
#   bash ops/chuyen-ten-may-chay.sh /home/thansa/thansa-chay      # chạy khi dịch vụ ĐÃ DỪNG, trước khi khởi động bản 2.0.0
#
# Làm: biến JAVIS_* -> THANSA_* trong unit systemd; trong mỗi brain: Javis/ -> Thansa/, .javis/ -> .thansa/,
# bỏ bản sao skill javis-builder cũ (app tự cài thansa-builder), bỏ khoá .javis-learn.lock; xoá cache Store
# (danh mục mới là thansa-store) và gói đang chờ cài theo mã cũ.
set -euo pipefail
GOC="${1:?thư mục cài đặt}"
UNIT=/etc/systemd/system/thansa.service

if [ -f "$UNIT" ] && grep -q 'JAVIS_' "$UNIT"; then
  sudo cp "$UNIT" "$UNIT.truoc-2.0.0"
  sudo sed -i 's/JAVIS_/THANSA_/g' "$UNIT"
  sudo systemctl daemon-reload
  echo "unit: JAVIS_* -> THANSA_* (bản cũ: $UNIT.truoc-2.0.0)"
fi

gop() {   # gộp thư mục $1 vào $2 (không đè file đã có ở đích)
  local a="$1" b="$2"
  [ -d "$a" ] || return 0
  mkdir -p "$b"
  cp -an "$a"/. "$b"/
  rm -rf "$a"
  echo "gộp: $a -> $b"
}

shopt -s nullglob
for brain in "$GOC"/brains/*/; do
  gop "${brain}Javis" "${brain}Thansa"
  gop "${brain}.javis" "${brain}.thansa"
  rm -rf "${brain}skills/javis-builder" "${brain}.claude/skills/javis-builder"
  rm -f "${brain}.javis-learn.lock"
done

rm -f "$GOC/server/packs-store-cache.json"
rm -rf "$GOC/server/packs-staging"
find "$GOC" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
echo "xong: chuyển tên máy chạy $GOC"
