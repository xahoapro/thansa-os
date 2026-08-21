#!/usr/bin/env python3
"""Tự kiểm chứng hồ sơ (DAC-TA-THANSA-OS.md mục 2.4) — chạy TRƯỚC mỗi vòng trộn.

    python3 ops/tu-kiem-chung.py           # từ đâu cũng được

Hồ sơ lệch thực tế thì mọi quyết định sau đều sai. Một luật ĐỎ = thoát mã 1 = KHÔNG cho trộn.

Luật 1: số commit [me] trên main..me = số mục mapping, và từng trường `commit` khớp
        đúng một subject trong git log.
Luật 2: mọi diem_neo (file + ky_hieu) tìm thấy trong cây mã hiện tại của nhánh me.
Luật 3: goc_commit trong mốc gốc = merge-base(me, main) — đúng nền me đang đứng.
Luật 4: so_patch trong mốc gốc = số mục mapping.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

OPS = Path(__file__).resolve().parent
REPO = OPS.parent
XANH, DO = "XANH", "ĐỎ"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def kiem_tra_commit(mapping) -> list[str]:
    loi = []
    subjects = [s for s in git("log", "--format=%s", "main..me").splitlines() if s.startswith("[me]")]
    khai_bao = [p.get("commit", "").strip() for p in mapping]
    if len(subjects) != len(khai_bao):
        loi.append(f"luật 1: {len(subjects)} commit [me] trên main..me nhưng mapping khai {len(khai_bao)} mục — có patch 'chui' hoặc mapping thừa")
    for c in khai_bao:
        if c not in subjects:
            loi.append(f"luật 1: mapping khai commit \"{c}\" không thấy trong git log main..me")
    trung = {s for s in subjects if subjects.count(s) > 1}
    for s in trung:
        loi.append(f"luật 1: subject [me] trùng nhau \"{s}\" — không đối chiếu 1-1 được")
    return loi


def kiem_tra_diem_neo(mapping) -> list[str]:
    loi = []
    for p in mapping:
        for neo in (p.get("diem_neo") or []):
            f = REPO / neo["file"]
            if not f.is_file():
                loi.append(f"luật 2: {p['id']} — file neo {neo['file']} không tồn tại trên me")
            elif neo["ky_hieu"] not in f.read_text(encoding="utf-8", errors="replace"):
                loi.append(f"luật 2: {p['id']} — ký hiệu {neo['ky_hieu']!r} không còn trong {neo['file']}")
    return loi


def kiem_tra_moc_goc(mapping) -> list[str]:
    loi = []
    moc = json.loads((OPS / "moc-goc.json").read_text(encoding="utf-8"))
    nen = git("merge-base", "me", "main")
    if moc["goc_commit"] != nen:
        loi.append(f"luật 3: mốc gốc ghi {moc['goc_commit'][:12]} nhưng me đứng trên {nen[:12]}")
    return loi


def kiem_tra_so_patch(mapping) -> list[str]:
    moc = json.loads((OPS / "moc-goc.json").read_text(encoding="utf-8"))
    if moc.get("so_patch") != len(mapping):
        return [f"luật 4: mốc gốc ghi so_patch={moc.get('so_patch')} nhưng mapping có {len(mapping)} mục"]
    return []


def kiem_tra_neo_version(mapping) -> list[str]:
    """Luật 5: file VERSION mang neo '<semver>-javis-<nền>' và phần nền PHẢI khớp goc_version.
    Lệch neo = tag ảnh/so-changelog trỏ sai nền → bản phát hành nói dối về gốc của nó."""
    vf = REPO / "VERSION"
    if not vf.is_file():
        return ["luật 5: không thấy file VERSION"]
    v = vf.read_text(encoding="utf-8").strip()
    moc = json.loads((OPS / "moc-goc.json").read_text(encoding="utf-8"))
    goc = str(moc.get("goc_version", "")).strip()
    if "-javis-" not in v:
        return [f"luật 5: VERSION {v!r} chưa mang neo '-javis-<nền>' (cần dạng <semver>-javis-{goc})"]
    neo = v.split("-javis-", 1)[1].strip()
    if neo != goc:
        return [f"luật 5: neo trong VERSION là '{neo}' nhưng goc_version là '{goc}' — lệch nền"]
    return []


def main() -> int:
    mapping = yaml.safe_load((OPS / "mapping.yaml").read_text(encoding="utf-8")) or []
    tat_ca = []
    for ten, loi in [
        ("luật 1 — commit [me] khớp mapping", kiem_tra_commit(mapping)),
        ("luật 2 — điểm neo còn sống", kiem_tra_diem_neo(mapping)),
        ("luật 3 — mốc gốc đúng nền me đang đứng", kiem_tra_moc_goc(mapping)),
        ("luật 4 (bổ sung) — so_patch = số mục mapping", kiem_tra_so_patch(mapping)),
        ("luật 5 (bổ sung) — neo javis trong VERSION khớp goc_version", kiem_tra_neo_version(mapping)),
    ]:
        print(f"  [{DO if loi else XANH}] {ten}")
        tat_ca += loi
    for l in tat_ca:
        print(f"      ! {l}", file=sys.stderr)
    print(("ĐỎ — DỪNG, không cho trộn" if tat_ca else "XANH — hồ sơ khớp thực tế"))
    return 1 if tat_ca else 0


if __name__ == "__main__":
    sys.exit(main())
