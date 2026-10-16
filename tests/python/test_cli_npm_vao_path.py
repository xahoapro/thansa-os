"""Regression P069: CLI cài bằng `npm -g` trên Node tải tay phải gõ được và server phải thấy.

    python tests/run.py cli_npm_vao_path

Chủ dự án báo 16/10/2026: cài Claude bằng npm thì install.sh báo xong, mở terminal gõ `claude`
lại không có, nút Đăng nhập Claude chỉ nhảy một cái. Node tải tay nằm ở ~/.thansa/node nên npm
đặt lệnh vào ~/.thansa/node/bin, thư mục không có trong PATH.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import claude_cli as cc  # noqa: E402

_fails = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


def main():
    src = (ROOT / "install.sh").read_text(encoding="utf-8")

    check("server soi ~/.thansa/node/bin", "~/.thansa/node/bin" in cc._THU_MUC_BIN_THEM)

    phan4 = src[src.index("# --- 4. Claude Code CLI"):src.index("# --- 4b.")]
    check("Claude: trình cài chính thức đứng trước npm",
          0 <= phan4.find("claude.ai/install.sh") < phan4.find("npm install -g @anthropic-ai/claude-code"))
    check("Claude: cài npm xong thì nối lệnh vào ~/.local/bin", "noi_bin_npm claude" in phan4)
    check("Claude: không còn báo 'installed' khi gõ claude không thấy",
          "echo installed)\"\n" not in phan4.split("if command -v claude")[0])
    them = src[src.index("cai_them_cli() {"):]
    check("CLI npm khác (Codex) cũng được nối", 'noi_bin_npm "$2"' in them[:them.index("\n}\n")])

    m = re.search(r"^noi_bin_npm\(\) \{.*?^\}\n", src, re.S | re.M)
    check("có hàm noi_bin_npm", bool(m))
    bash = shutil.which("bash")
    if not (m and bash and os.name != "nt"):
        print("skip phần chạy thật (không có bash)")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            home, fake = tmp / "home", tmp / "bin"
            npm_bin = home / ".thansa" / "node" / "bin"
            npm_bin.mkdir(parents=True)
            fake.mkdir()
            (npm_bin / "claude").write_text("#!/bin/sh\necho 9.9.9\n")
            (fake / "npm").write_text(f"#!/bin/sh\n[ \"$1 $2\" = \"prefix -g\" ] && echo {home}/.thansa/node\n")
            for p in (npm_bin / "claude", fake / "npm"):
                p.chmod(0o755)
            for t in ("mkdir", "ln", "sh"):
                w = shutil.which(t)
                if w:
                    (fake / t).symlink_to(w)
            # PATH chỉ có thư mục giả: giống máy mới, `claude` chưa có ở đâu trong PATH.
            r = subprocess.run([bash, "-c", f"set -euo pipefail\n{m.group(0)}noi_bin_npm claude\nclaude"],
                               env={"HOME": str(home), "PATH": str(fake)},
                               capture_output=True, text=True)
            check("sau khi nối, gõ claude chạy được", r.returncode == 0 and r.stdout.strip() == "9.9.9")
            check("lệnh nằm ở ~/.local/bin", (home / ".local" / "bin" / "claude").is_symlink())

    print()
    if _fails:
        print(f"{len(_fails)} FAIL")
        return 1
    print("tất cả ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
