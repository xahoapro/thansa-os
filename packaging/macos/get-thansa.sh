#!/bin/bash
# ============================================================
# THANSA OS - one-line install for macOS, no "cannot be opened" block
#
#   curl -fsSL https://raw.githubusercontent.com/xahoapro/thansa-os/main/packaging/macos/get-thansa.sh | bash
#
# Downloads the same ThansaOS-macOS.dmg the website links to, copies THANSA OS.app into
# Applications, then runs its first-time install right here in this Terminal window.
# Why no Gatekeeper prompt: macOS only checks files a browser saved (they carry a quarantine
# flag), and the app is not signed with an Apple Developer ID yet. A file curl downloads
# carries no such flag.
# ============================================================
set -euo pipefail

URL="https://github.com/xahoapro/thansa-os/releases/download/desktop/ThansaOS-macOS.dmg"
[ "$(uname -s)" = "Darwin" ] || { echo "This installer is for macOS. On Linux run ./install.sh from the repo."; exit 1; }

TMP="$(mktemp -d)"
MNT=""
cleanup() { [ -n "${MNT}" ] && hdiutil detach -quiet "${MNT}" 2>/dev/null; rm -rf "${TMP}"; }
trap cleanup EXIT

echo ""
echo "  THANSA OS: dang tai bo cai... (downloading)"
curl -fL --progress-bar -o "${TMP}/ThansaOS-macOS.dmg" "${URL}"
MNT="$(hdiutil attach -nobrowse -readonly "${TMP}/ThansaOS-macOS.dmg" | awk -F'\t' '/\/Volumes\//{print $NF}')"
[ -d "${MNT}/THANSA OS.app" ] || { echo "The disk image has no THANSA OS.app"; exit 1; }

# /Applications when it is writable (an admin account), else ~/Applications.
DEST="/Applications"
[ -w "${DEST}" ] || { DEST="${HOME}/Applications"; mkdir -p "${DEST}"; }
# Replace only the app bundle; the brain lives in ~/ThansaOS and is never touched here.
rm -rf "${DEST}/THANSA OS.app"
cp -R "${MNT}/THANSA OS.app" "${DEST}/"
xattr -dr com.apple.quarantine "${DEST}/THANSA OS.app" 2>/dev/null || true
echo "  Da chep THANSA OS vao ${DEST} (copied to ${DEST})"

APP="${DEST}/THANSA OS.app"
if [ -d "${HOME}/ThansaOS/.git" ] && [ -x "${HOME}/ThansaOS/.venv/bin/python" ]; then
  echo "  Thansa da cai san, dang mo... (already installed, opening)"
  open "${APP}"
  exit 0
fi
# First install in THIS window. stdin is the curl pipe, so give the installer the keyboard
# back: install.sh asks for the Thansa admin account and may ask for the Mac password.
bash "${APP}/Contents/Resources/bootstrap.sh" < /dev/tty
