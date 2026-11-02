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

import hashlib
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
    bam_cu = {}                                    # sha256 nội dung TRƯỚC khi đổi -> đường dẫn (để băm lại khoá kiểm định)
    for f in files:
        p = goc / f
        if p.is_file() and not p.is_symlink():
            bam_cu.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(), f)
    dx_cu = bam_dan_xuat(goc)
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
    kq["bam_lai"] = bam_lai(goc, bam_cu, dx_cu)
    git("add", "-A")
    return kq


BAM = re.compile(r"\b[0-9a-f]{64}\b")
PY = Path(__file__).resolve().parent.parent.parent / "goc" / ".venv" / "bin" / "python"
_DAN_XUAT = r"""
import ast, hashlib, json, sys
from pathlib import Path
sv = Path(sys.argv[1]) / "server"
out = {}
sel = sv / "improvement_trial_selection.py"
if sel.is_file():
    t = ast.parse(sel.read_text(encoding="utf-8"))
    keys = []
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "_DISCOVERY_CODE" for x in n.targets):
            keys = [k.value for k in n.value.keys]
    for k in keys:
        f = sv / ("claude_sdk_engine.py" if "." in k else "claude_cli.py")
        nodes = ast.parse(f.read_text(encoding="utf-8")).body
        node = None
        for part in k.split("."):
            node = next((i for i in nodes if isinstance(i, (ast.ClassDef, ast.FunctionDef)) and i.name == part), None)
            if node is None:
                break
            nodes = node.body
        if node is not None:
            out["ast:" + k] = hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
if (sv / "improvement_claude.py").is_file():
    sys.path.insert(0, str(sv))
    try:
        import improvement_claude
        out["profile_hash"] = improvement_claude.profile_hash()
    except Exception:
        pass
print(json.dumps(out))
"""


def bam_dan_xuat(goc: Path) -> dict:
    """Băm KHÔNG phải sha256 cả file mà code tự tính lúc chạy: băm AST hàm dò binary (_DISCOVERY_CODE) và
    profile_hash() của hồ sơ Claude native. Đổi tên làm đổi chúng → phải ghi lại ở mọi chỗ khoá."""
    import json
    if not PY.exists():
        return {}
    r = subprocess.run([str(PY), "-c", _DAN_XUAT, str(goc)], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home())})
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {}


def bam_lai(goc: Path, bam_cu: dict, dx_cu: dict | None = None) -> int:
    """File/khối mã bị khoá bằng sha256 (bằng chứng kiểm định native, _GOAL_SOURCE_HASH, _DISCOVERY_CODE,
    profile_hash...) đổi sau khi đổi tên → thay mọi chỗ ghi băm CŨ bằng băm MỚI. Lặp tới khi ổn định
    (file chứa băm cũng bị băm ở chỗ khác)."""
    dx_cu = dict(dx_cu or {})
    tong = 0
    for _ in range(8):
        thay = {}
        for h, f in bam_cu.items():
            p = goc / doi_chu(f)
            if p.is_file():
                h2 = hashlib.sha256(p.read_bytes()).hexdigest()
                if h2 != h:
                    thay[h] = h2
        dx_moi = bam_dan_xuat(goc)
        for k, h in dx_cu.items():
            if k in dx_moi and dx_moi[k] != h:
                thay[h] = dx_moi[k]
        if not thay:
            break
        doi = 0
        for p in goc.rglob("*"):
            if ".git" in p.parts or not p.is_file() or p.is_symlink() or p.stat().st_size > 20_000_000:
                continue
            try:
                s = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            t = BAM.sub(lambda m: thay.get(m.group(0), m.group(0)), s)
            if t != s:
                p.write_text(t, encoding="utf-8")
                doi += 1
        tong += doi
        bam_cu = {thay.get(h, h): f for h, f in bam_cu.items()}
        dx_cu = dx_moi
        if not doi:
            break
    return tong
