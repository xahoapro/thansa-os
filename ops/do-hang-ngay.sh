#!/usr/bin/env bash
# Bộ dò upstream hằng ngày (DAC-TA mục 3) — vỏ bọc theo tên trong nhiem-vu/GD1.md.
# Ruột nằm ở ops/do-hang-ngay.py (python3: mapping là YAML, bash không đọc tin cậy được).
# Thoát mã: 0 = bình thường; 2 = CỜ KHẨN.
exec python3 "$(dirname "$0")/do-hang-ngay.py" "$@"
