#!/usr/bin/env python3
"""Đổi tên TOÀN BỘ javis → thansa trong một cây mã (nội dung + tên file), giữ kiểu chữ hoa/thường.

Chủ chốt 01/11/2026: source Thansa không còn chữ javis nào. Cùng một bộ đổi tên này chạy cho:
  1. cây Thansa (một lần), và
  2. mỗi bản Javis mới TRƯỚC khi merge (ops/tu_dong_tron.py) → hai bên cùng "nói tiếng Thansa", xung đột chỉ
     còn ở chỗ Thansa tuỳ biến thật.

    python3 ops/doi_ten.py <thư-mục-worktree>      # đổi tại chỗ (git mv + ghi nội dung), không commit

Dùng chung cho 3 repo: thansa-os, thansa-store (fork javis-store), thansa-zalo (fork javis-zalo).
GIỮ NGUYÊN: LICENSE (MIT bắt buộc giữ dòng bản quyền tác giả gốc) và ops/ (công cụ bảo trì nói về nguồn Javis).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BO_QUA_FILE = re.compile(r"^(LICENSE|ops/)")
# Repo/tên miền của Javis → của Thansa (01/11: fork javis-store → thansa-store, javis-zalo → thansa-zalo).
THAY_TRUOC = [("blogminhquy/javis-", "xahoapro/thansa-"), ("blogminhquy/thansa-", "xahoapro/thansa-"),
              ("javisos.com", "thansa.org"), ("minhquy.vn", "tradingauto.org")]
JV = re.compile(r"javis", re.I)
KIEU = {"javis": "thansa", "Javis": "Thansa", "JAVIS": "THANSA"}


def _doi(m: re.Match) -> str:
    w = m.group(0)
    if w in KIEU:
        return KIEU[w]
    return "thansa" if w[0].islower() else ("THANSA" if w.isupper() else "Thansa")


def doi_chu(s: str) -> str:
    for cu, moi in THAY_TRUOC:
        s = s.replace(cu, moi)
    return JV.sub(_doi, s)


def doi_cay(goc: Path) -> dict:
    def git(*a):
        return subprocess.run(["git", *a], cwd=goc, check=True, capture_output=True, text=True).stdout

    files = [f for f in git("ls-files", "-z").split("\0") if f]
    co = set(files)
    kq = {"noi_dung": 0, "doi_ten": 0, "bo_trung": []}
    for f in files:
        if BO_QUA_FILE.match(f):
            continue
        p = goc / f
        if p.is_symlink() or not p.is_file():
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            s = None
        if s is not None:
            t = doi_chu(s)
            if t != s:
                p.write_text(t, encoding="utf-8")
                kq["noi_dung"] += 1
        moi = doi_chu(f)
        if moi != f:
            if moi in co:                  # đã có bản Thansa (vd start-thansa.vbs) → bỏ bản javis
                git("rm", "-q", "-f", "--", f)
                kq["bo_trung"].append(f)
            else:
                (goc / moi).parent.mkdir(parents=True, exist_ok=True)
                git("mv", "-k", "--", f, moi)
                co.add(moi)
                kq["doi_ten"] += 1
    git("add", "-A")
    return kq


if __name__ == "__main__":
    print(doi_cay(Path(sys.argv[1]).resolve()))
