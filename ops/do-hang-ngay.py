#!/usr/bin/env python3
"""Bộ dò upstream hằng ngày (DAC-TA-THANSA-OS.md mục 3) — script thuần, KHÔNG AI.

    python3 ops/do-hang-ngay.py            # chạy tay hoặc qua cron, từ đâu cũng được

Mỗi lần chạy: fetch upstream → tính file đổi từ lần dò trước → giao với vung_theo_doi
của mọi patch trong mapping → so anh_goc với upstream/main → quét từ khoá bảo mật
trong message commit mới → ghi bản tin ops/ban-tin/YYYY-MM-DD.md.

KHÔNG sửa gì vào bất cứ nhánh nào, KHÔNG commit. Bản tin (ops/ban-tin/*.md) + con trỏ
dò (ops/.last-do) là file làm việc cục bộ trên VPS (đã loại khỏi git bằng
.git/info/exclude). Chạy qua vỏ bọc `bash ops/do-hang-ngay.sh` cũng được.

Thoát mã: 0 = bình thường; 2 = có CỜ KHẨN (để cron/kênh báo GĐ4 bắt được).
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

OPS = Path(__file__).resolve().parent
REPO = OPS.parent
BAN_TIN = OPS / "ban-tin"
LAST_DO = OPS / ".last-do"  # con trỏ SHA lần dò trước (nhiem-vu/GD1.md)

# Từ khoá quét message commit mới (DAC-TA mục 3 bước 4). Có → CỜ KHẨN.
TU_KHOA_BAO_MAT = re.compile(r"vá|bảo mật|2FA|credential|token|leak|rò", re.IGNORECASE)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def sha_lan_truoc() -> str:
    """Mốc dò lần trước: ops/.last-do, không có thì lấy goc_commit trong mốc gốc."""
    if LAST_DO.is_file():
        return LAST_DO.read_text(encoding="utf-8").strip()
    return json.loads((OPS / "moc-goc.json").read_text(encoding="utf-8"))["goc_commit"]


def duong_dan(muc: str) -> str:
    """'server/main.py: hàm settings/general' → 'server/main.py'."""
    return muc.split(":")[0].strip()


def main() -> int:
    git("fetch", "upstream", "--quiet")

    truoc = sha_lan_truoc()
    sau = git("rev-parse", "upstream/main")
    khoang = f"{truoc}..{sau}"

    commit_moi = git("log", "--format=%h %s", khoang).splitlines() if truoc != sau else []
    file_doi = git("diff", "--name-only", truoc, sau).splitlines() if truoc != sau else []

    mapping = yaml.safe_load((OPS / "mapping.yaml").read_text(encoding="utf-8")) or []

    # 1) Giao file đổi với vùng theo dõi của từng patch
    dung_vung = []  # (id_patch, [file giao nhau])
    for patch in mapping:
        theo_doi = [duong_dan(m) for m in (patch.get("vung_theo_doi") or [])]
        giao = sorted({f for f in file_doi for v in theo_doi if f == v or f.startswith(v.rstrip("/") + "/")})
        if giao:
            dung_vung.append((patch["id"], giao))

    # 2) So ảnh gốc với upstream/main mới nhất
    anh_lech = []  # (id_patch, file)
    for patch in mapping:
        for anh in (patch.get("anh_goc") or []):
            try:
                noi_dung = git("show", f"upstream/main:{anh['file']}")
            except subprocess.CalledProcessError:
                anh_lech.append((patch["id"], f"{anh['file']} (file biến mất khỏi upstream)"))
                continue
            if anh["doan"] not in noi_dung:
                anh_lech.append((patch["id"], anh["file"]))

    # 3) Quét từ khoá bảo mật
    bao_mat = [c for c in commit_moi if TU_KHOA_BAO_MAT.search(c)]
    khan = bool(bao_mat) or bool(anh_lech)

    # 4) Ghi bản tin
    so_giao = len({f for _, fs in dung_vung for f in fs})
    khong_giao = len(commit_moi)  # ước lượng: tổng commit; ghi rõ số commit không chạm vùng nào
    dong = [f"# {date.today().isoformat()} — upstream +{len(commit_moi)} commit ({truoc[:7]} → {sau[:7]})"]
    dong.append(
        "- ĐỤNG VÙNG THEO DÕI: "
        + ("; ".join(f"{pid} ({', '.join(fs)})" for pid, fs in dung_vung) if dung_vung else "không")
    )
    dong.append(
        "- ẢNH GỐC LỆCH: "
        + ("; ".join(f"{pid} ({f})" for pid, f in anh_lech) if anh_lech else "không")
    )
    if bao_mat:
        dong.append(f"- BẢO MẬT: {len(bao_mat)} commit → CỜ KHẨN, nên trộn sớm")
        dong += [f"    - {c}" for c in bao_mat]
    else:
        dong.append("- BẢO MẬT: không")
    dong.append(f"- Không giao: {khong_giao - so_giao if khong_giao >= so_giao else khong_giao} commit còn lại (docs/tests/vùng không theo dõi)")

    BAN_TIN.mkdir(exist_ok=True)
    ban_tin = BAN_TIN / f"{date.today().isoformat()}.md"
    ban_tin.write_text("\n".join(dong) + "\n", encoding="utf-8")
    LAST_DO.write_text(sau + "\n", encoding="utf-8")

    print(ban_tin)
    print("\n".join(dong))
    if khan:
        # Kênh báo (Telegram/email) chốt ở GĐ4 — tạm thời: thoát mã 2 cho cron bắt.
        print("\n*** CỜ KHẨN — nên mở vòng trộn sớm ***", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
