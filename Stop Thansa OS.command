#!/bin/bash
# Double-click in Finder to stop Thansa OS.
cd "$(dirname "$0")" || exit 1
bash "bin/thansa-stop.sh"
echo ""
echo "You can close this window."
