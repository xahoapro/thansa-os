#!/usr/bin/env bash
# Tự kiểm chứng hồ sơ (DAC-TA mục 2.4) — vỏ bọc theo tên trong nhiem-vu/GD1.md.
# Ruột nằm ở ops/tu-kiem-chung.py. Thoát mã khác 0 = ĐỎ = không cho trộn.
exec python3 "$(dirname "$0")/tu-kiem-chung.py" "$@"
