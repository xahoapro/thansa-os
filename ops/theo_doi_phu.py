#!/usr/bin/env python3
"""Theo dõi 2 repo PHỤ của nguồn (kho gói + CLI Zalo) và giữ 2 bản tách của Thansa khớp theo - KHÔNG tự đẩy.

    python3 ops/theo_doi_phu.py            # cron (ops/tu-dong-tron.sh --phu): quét, dựng bản chờ duyệt, nhắn Telegram
    python3 ops/theo_doi_phu.py --day store|zalo   # đẩy bản chờ duyệt lên GitHub (nút Telegram gọi; chủ bấm = duyệt)

Chủ chốt 02/11/2026: thansa-store (tách từ javis-store) và thansa-zalo (tách từ javis-zalo) phải tự theo nguồn như
repo chính. Hai bản tách KHÔNG có tuỳ biến riêng ngoài bộ đổi tên, nên mỗi lần nguồn đổi thì DỰNG LẠI toàn bộ cây:
  - store: cây nguồn mới nhất → ops/doi_ten.py → đóng gói lại mọi dist/*.zip (sha256/size vào index.json) → đóng gói
    lại các mcp/*.tgz còn tên cũ (cập nhật sha ở mọi chỗ ghi) → chạy test của kho với chính Thansa (THANSA_OS_DIR).
  - zalo: mỗi TAG mới của nguồn (Thansa chỉ ghim theo tag) → doi_ten → commit + tag cùng tên ở bản tách.
Đạt thì để commit trên nhánh `cho-duyet` của bản tách, nhắn Telegram có nút; chủ bấm mới đẩy (kho đổi là mọi máy
Thansa thấy ngay). Muốn tuỳ biến riêng trong bản tách thì phải đổi cách này sang merge như repo chính.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doi_ten  # noqa: E402
import tu_dong_tron as td  # noqa: E402

PHU = td.ME.parent / "phu"
STATE = td.BT / "phu.state"
REPO = {
    "store": {"nguon": "https://github.com/blogminhquy/javis-store.git", "fork": "xahoapro/thansa-store", "ten": "thansa-store"},
    "zalo": {"nguon": "https://github.com/blogminhquy/javis-zalo.git", "fork": "xahoapro/thansa-zalo", "ten": "thansa-zalo"},
}
CO_AUTHOR = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


class Loi(Exception):
    pass


def doc_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ghi_state(ten: str, **kw) -> None:
    st = doc_state()
    st.setdefault(ten, {}).update(kw)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def git(*a, cwd: Path, check=True) -> str:
    r = td.sh(["git", *a], cwd=cwd, check=False)
    if check and r.returncode != 0:
        raise Loi(f"git {' '.join(a)}: {(r.stdout + r.stderr)[-600:]}")
    return r.stdout.strip()


def clone(ten: str) -> tuple[Path, Path]:
    """Bản sao nguồn + bản tách (đã có thì fetch)."""
    PHU.mkdir(parents=True, exist_ok=True)
    out = []
    for vai, url in (("nguon", REPO[ten]["nguon"]), ("fork", f"https://github.com/{REPO[ten]['fork']}.git")):
        d = PHU / f"{ten}-{vai}"
        if not (d / ".git").exists():
            td.sh(["git", "clone", "-q", url, str(d)], cwd=PHU)
        git("fetch", "-q", "--tags", "--force", "origin", cwd=d)
        out.append(d)
    return out[0], out[1]


def dung_cay(nguon: Path, rev: str, out: Path) -> None:
    """Cây của `rev` trong bản sao nguồn → thư mục `out` đã đổi tên (git tạm để doi_ten dùng git mv)."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    a = td.sh(["bash", "-c", f"git archive {rev} | tar x -C '{out}'"], cwd=nguon)
    if a.returncode != 0:
        raise Loi(f"git archive {rev}: {a.stderr[-300:]}")
    git("init", "-q", "-b", "tam", cwd=out)
    git("add", "-A", cwd=out)
    git("-c", "user.email=tu-dong@thansa", "-c", "user.name=tu-dong", "commit", "-qm", "tam", cwd=out)
    doi_ten.doi_cay(out)


# ---------------------------------------------------------------- store: đóng gói lại

def _zip_tat_dinh(src: Path, dst: Path) -> tuple[str, int]:
    files = sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            zi = zipfile.ZipInfo(p.relative_to(src).as_posix(), (1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, p.read_bytes(), compresslevel=9)
    b = dst.read_bytes()
    return hashlib.sha256(b).hexdigest(), len(b)


def _tgz_doi_ten(p: Path) -> bool:
    """Gói npm (.tgz) còn tên cũ bên trong → ghi lại nội dung qua doi_ten (tất định: mtime 0, thứ tự cố định)."""
    vao = tarfile.open(p, "r:gz")
    mem = [(m, vao.extractfile(m).read() if m.isfile() else None) for m in vao.getmembers()]
    vao.close()
    if not any(b and re.search(rb"javis", b, re.I) for _, b in mem):
        return False
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as ra:
        for m, b in sorted(mem, key=lambda x: x[0].name):
            if b is not None:
                try:
                    b = doi_ten.doi_chu(b.decode("utf-8")).encode("utf-8")
                except UnicodeDecodeError:
                    pass
            ti = tarfile.TarInfo(doi_ten.doi_chu(m.name))
            ti.type, ti.mode, ti.mtime = m.type, m.mode, 0
            if b is not None:
                ti.size = len(b)
                ra.addfile(ti, io.BytesIO(b))
            else:
                ra.addfile(ti)
    with open(p, "wb") as f, gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as g:
        g.write(raw.getvalue())
    return True


def dong_goi_store(out: Path) -> dict:
    kq = {"zip": 0, "tgz": []}
    for z in (out / "dist").glob("*.zip"):
        z.unlink()
    idx_p = out / "index.json"
    idx = json.loads(idx_p.read_text(encoding="utf-8"))
    for p in idx.get("packs", []):
        d = p.get("download") or {}
        u = d.get("url", "")
        src = out / "packs" / p.get("id", "")
        if u.startswith("dist/") and src.is_dir():
            d["sha256"], d["size"] = _zip_tat_dinh(src, out / u)
            kq["zip"] += 1
    idx_p.write_text(json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    thay = {}
    for t in sorted((out / "mcp").glob("*.tgz")):
        cu = hashlib.sha256(t.read_bytes()).hexdigest()
        if _tgz_doi_ten(t):
            thay[cu] = hashlib.sha256(t.read_bytes()).hexdigest()
            kq["tgz"].append(t.name)
    if thay:
        for f in out.rglob("*.json"):
            if ".git" in f.parts:
                continue
            s = f.read_text(encoding="utf-8")
            s2 = doi_ten.BAM.sub(lambda m: thay.get(m.group(0), m.group(0)), s)
            if s2 != s:
                f.write_text(s2, encoding="utf-8")
    return kq


def test_store(out: Path) -> str:
    hong, n = [], 0
    for f in sorted(out.glob("tests/*/test_*.py")):
        n += 1
        r = td.sh([str(td.PY), str(f)], cwd=out, check=False, env={"THANSA_OS_DIR": str(td.ME)}, timeout=900)
        if r.returncode != 0:
            dong = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip()]
            hong.append(f"{f.parent.name}/{f.name} ({dong[-1][:160] if dong else 'không in gì'})")
    if hong:
        raise Loi("test kho đỏ (gói mới đòi lõi Thansa mới hơn thì chờ bản Thansa kế tiếp, lượt sau tự thử lại): "
                  + "; ".join(hong))
    return f"{n}/{n} test kho xanh"


def test_zalo(out: Path) -> str:
    hong = [f.name for f in sorted((out / "src").rglob("*.js"))
            if td.sh(["node", "--check", str(f)], cwd=out, check=False).returncode != 0]
    if hong:
        raise Loi(f"thansa-zalo: lỗi cú pháp {hong}")
    return "cú pháp JS sạch"


# ---------------------------------------------------------------- commit vào bản tách

def commit_cay(fork: Path, out: Path, msg: str) -> str:
    """Thay toàn bộ cây nhánh `cho-duyet` bằng `out` (không đụng .git của out). Trả sha, rỗng nếu không đổi gì."""
    e = {"GIT_WORK_TREE": str(out), "GIT_DIR": str(fork / ".git")}
    for a in (["add", "-A"],):
        r = td.sh(["git", *a], cwd=out, check=False, env=e)
        if r.returncode != 0:
            raise Loi(f"git add: {r.stderr[-300:]}")
    if td.sh(["git", "diff", "--cached", "--quiet"], cwd=out, check=False, env=e).returncode == 0:
        return ""
    r = td.sh(["git", "commit", "-qm", msg + CO_AUTHOR], cwd=out, check=False, env=e)
    if r.returncode != 0:
        raise Loi(f"git commit: {r.stderr[-300:]}")
    return td.sh(["git", "rev-parse", "HEAD"], cwd=out, env=e).stdout.strip()


def _ve_cho_duyet(fork: Path) -> None:
    # -f: commit_cay commit bằng GIT_WORK_TREE=out nên cây làm việc của fork lệch HEAD; không ép thì checkout
    # báo "local changes" và lượt theo dõi kho đỏ mãi (04-06/11). Cây này chỉ script dùng, ép an toàn.
    git("checkout", "-q", "-f", "-B", "cho-duyet", "origin/main", cwd=fork)
    git("reset", "-q", "--hard", "origin/main", cwd=fork)
    git("clean", "-qfd", cwd=fork)


def _ver(t: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", t)[:3])


def quet_store() -> dict | None:
    nguon, fork = clone("store")
    up = git("rev-parse", "origin/main", cwd=nguon)
    st = doc_state().get("store", {})
    if up == st.get("nguon") or up == (st.get("cho") or {}).get("nguon"):
        return None
    cu = st.get("nguon", "")
    cac = git("log", "--format=%h %s", f"{cu}..{up}", cwd=nguon).splitlines() if cu else []
    out = PHU / "store-dung"
    dung_cay(nguon, up, out)
    dg = dong_goi_store(out)
    kq_test = test_store(out)
    _ve_cho_duyet(fork)
    c = commit_cay(fork, out, f"dong bo nguon {up[:7]}: doi ten + dong goi lai {dg['zip']} goi")
    if not c:
        ghi_state("store", nguon=up, cho=None)
        td.log(f"[phụ] store: nguồn {up[:7]} không đổi gì sau khi dịch")
        return None
    return {"ten": "store", "nguon": up, "commit": c, "tom": cac,
            "chi_tiet": f"{dg['zip']} gói đóng lại, tgz: {', '.join(dg['tgz']) or 'không'}; {kq_test}"}


def quet_zalo() -> dict | None:
    nguon, fork = clone("zalo")
    tag_nguon = [t for t in git("tag", cwd=nguon).splitlines() if re.match(r"^v\d+\.\d+\.\d+$", t)]
    tag_fork = set(git("ls-remote", "--tags", "--refs", "origin", cwd=fork).split())
    moi = sorted((t for t in tag_nguon if f"refs/tags/{t}" not in tag_fork), key=_ver)
    moi = [t for t in moi if not tag_fork or _ver(t) > max(_ver(x.rsplit("/", 1)[1]) for x in tag_fork if "refs/tags/" in x)]
    st = doc_state().get("zalo", {})
    if not moi or moi == (st.get("cho") or {}).get("tags"):
        return None
    _ve_cho_duyet(fork)
    out = PHU / "zalo-dung"
    c = ""
    for t in moi:
        dung_cay(nguon, t, out)
        test_zalo(out)
        c = commit_cay(fork, out, f"thansa-zalo {t.lstrip('v')}: dong bo nguon {t}, doi ten") or git("rev-parse", "HEAD", cwd=fork)
        git("tag", "-f", t, c, cwd=fork)
    return {"ten": "zalo", "nguon": moi[-1], "tags": moi, "commit": c, "tom": [f"tag {t}" for t in moi],
            "chi_tiet": f"{len(moi)} tag mới, cú pháp JS sạch"}


def quet() -> int:
    for ten, ham in (("zalo", quet_zalo), ("store", quet_store)):
        try:
            kq = ham()
        except (Loi, td.Loi) as e:
            td.log(f"[phụ] {ten} LỖI: {e}")
            if doc_state().get(ten, {}).get("loi") != str(e)[:300]:
                ghi_state(ten, loi=str(e)[:300])
                td.tele(f"🚨 {REPO[ten]['ten']} - tự theo nguồn DỪNG", f"Lý do: {e}\nKhông có gì bị đẩy lên GitHub.")
            continue
        if not kq:
            continue
        ma = os.urandom(4).hex()
        ghi_state(ten, cho={**kq, "ma": ma}, loi="")
        td.log(f"[phụ] {ten}: bản chờ duyệt {kq['commit'][:9]} ({kq['chi_tiet']})")
        td.tele(f"📦 {REPO[ten]['ten']} theo nguồn xong - CHỜ BẠN DUYỆT",
                "\n".join("• " + x.split(" ", 1)[-1] for x in kq["tom"][:10]) +
                f"\n\n{kq['chi_tiet']}.\nĐẩy lên GitHub thì mọi máy Thansa dùng ngay"
                + (" (kho gói)." if ten == "store" else " (bản Thansa ghim tag này mới tải được)."),
                nut=[[{"text": f"🚀 Đẩy {REPO[ten]['ten']}", "callback_data": f"pp|{ten}|{ma}"},
                      {"text": "Bỏ qua", "callback_data": f"bp|{ten}|{ma}"}]])
    return 0


def day(ten: str) -> None:
    """Chủ đã bấm duyệt: đẩy cho-duyet → main (+ tag). Từ chối nếu main của bản tách đổi sau lúc dựng."""
    cho = (doc_state().get(ten) or {}).get("cho") or {}
    if not cho:
        td.tele("⚠️ THANSA", f"Không có bản {REPO[ten]['ten']} nào đang chờ duyệt.")
        return
    fork = PHU / f"{ten}-fork"
    try:
        git("fetch", "-q", "origin", cwd=fork)
        if td.sh(["git", "merge-base", "--is-ancestor", "origin/main", cho["commit"]], cwd=fork, check=False).returncode != 0:
            raise Loi("main của bản tách đã đổi sau lúc dựng - lượt sau sẽ dựng lại")
        git("push", "-q", "origin", f"{cho['commit']}:refs/heads/main", cwd=fork)
        for t in cho.get("tags") or []:
            git("push", "-q", "origin", f"refs/tags/{t}", cwd=fork)
    except Loi as e:
        td.log(f"[phụ] đẩy {ten} DỪNG: {e}")
        td.tele(f"🚨 {REPO[ten]['ten']} - chưa đẩy", str(e))
        return
    ghi_state(ten, nguon=cho["nguon"], cho=None, da_day=time.strftime("%Y-%m-%d %H:%M"))
    if ten == "zalo":       # lượt trộn chính có thể đang dừng chờ tag này → cho nó chạy lại
        td.ghi_state(loi_up="")
    td.log(f"[phụ] ĐÃ ĐẨY {ten} {cho['commit'][:9]}")
    td.tele(f"🎉 Đã đẩy {REPO[ten]['ten']}", f"https://github.com/{REPO[ten]['fork']}"
            + (f" (tag {', '.join(cho['tags'])})" if cho.get("tags") else ""))


def xu_ly_nut(hanh_dong: str, ten: str, ma: str, cb: dict, chu: str) -> None:
    """Nút pp/bp từ ops/tu_dong_tron.py nghe_nut (đã kiểm đúng chủ)."""
    cho = (doc_state().get(ten) or {}).get("cho") or {}
    if ten not in REPO or ma != cho.get("ma"):
        td.tg_api("answerCallbackQuery", callback_query_id=cb["id"], text="Nút này đã hết hạn.")
        return
    msg = cb.get("message") or {}
    td.tg_api("editMessageReplyMarkup", chat_id=chu, message_id=msg.get("message_id"), reply_markup={"inline_keyboard": []})
    if hanh_dong == "bp":
        ghi_state(ten, cho={**cho, "ma": ""})
        td.tg_api("answerCallbackQuery", callback_query_id=cb["id"], text="Đã bỏ qua.")
        return
    ghi_state(ten, cho={**cho, "ma": ""})
    td.tg_api("answerCallbackQuery", callback_query_id=cb["id"], text=f"Đang đẩy {REPO[ten]['ten']}…")
    day(ten)


if __name__ == "__main__":
    if "--day" in sys.argv:
        day(sys.argv[sys.argv.index("--day") + 1])
        sys.exit(0)
    sys.exit(quet())
