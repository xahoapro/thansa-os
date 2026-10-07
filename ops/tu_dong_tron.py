#!/usr/bin/env python3
"""Tự động TRỘN + NGHIỆM THU bản Javis mới cho Thansa - KHÔNG tự phát hành. Cron qua ops/tu-dong-tron.sh.

Chủ chốt 07/10/2026 (cách 2): định kỳ quét Javis; có bản mới thì tự trộn + nghiệm thu trong một WORKTREE
RIÊNG (không đụng nhánh me/main đang làm việc), kết quả để ở nhánh `san-sang-<bản>` trên máy rồi nhắn
Telegram "sẵn sàng, chờ duyệt". Xung đột thật / hồi quy / chốt an toàn hỏng → nhắn Telegram và dừng.
KHÔNG BAO GIỜ đẩy gì lên GitHub: phát hành là việc người duyệt (một phiên Claude làm khi chủ bảo).

    python3 ops/tu_dong_tron.py              # chạy thật (vẫn chỉ trên máy)
    python3 ops/tu_dong_tron.py --chi-xem    # chỉ báo có bản Javis mới hay không
    python3 ops/tu_dong_tron.py --ep         # chạy lại bản đã báo lỗi/đã sẵn sàng (sau khi sửa tay)
    python3 ops/tu_dong_tron.py --nhan "..." # chỉ gửi một tin Telegram (dùng sau khi phát hành tay)

Khi chủ duyệt bản X: phiên Claude đặt me = san-sang-X, đưa main lên đúng goc_commit trong ops/moc-goc.json,
rồi phát hành như quy trình tay (snapshot main, tag + Release, đánh dấu sổ) và nhắn Telegram.
Quy trình đầy đủ: ops/so-tron.md mục "Tự động hoá 2026-10-07".
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import time
import tokenize
import urllib.parse
import urllib.request
from pathlib import Path

ME = Path(__file__).resolve().parent.parent          # worktree nhánh me (chỉ ĐỌC từ đây)
GOC = ME.parent / "goc"
PY = GOC / ".venv" / "bin" / "python"
WT = ME.parent / ".tu-dong"                          # worktree riêng để trộn
WTG = ME.parent / ".tu-dong-goc"                     # upstream sạch để chạy suite đối chứng
BT = ME / "ops" / "ban-tin"
STATE = BT / "tu-dong.state"
LOG = BT / "tu-dong.log"
ENV_TELE = Path.home() / ".thansa-alert.env"

CHI_XEM = "--chi-xem" in sys.argv
EP = "--ep" in sys.argv

# ---------------------------------------------------------------- tiện ích

def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    BT.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def sh(args, cwd=WT, check=True, env=None, timeout=None) -> subprocess.CompletedProcess:
    e = dict(os.environ)
    for k in ("JAVIS_STATE_DIR", "JAVIS_BRAIN", "JAVIS_IN_TERMINAL"):   # bẫy 28/09: test ghi đè state thật
        e.pop(k, None)
    e.setdefault("GIT_EDITOR", "true")
    if env:
        e.update(env)
    r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, env=e, timeout=timeout)
    if check and r.returncode != 0:
        raise Loi(f"lệnh hỏng: {' '.join(map(str, args))}\n{(r.stdout + r.stderr)[-1500:]}")
    return r


def git(*args, cwd=WT, check=True) -> str:
    return sh(["git", *args], cwd=cwd, check=check).stdout.strip()


class Loi(Exception):
    """Cần người xem - dừng lượt chạy, nhắn Telegram."""


def _cfg_tele() -> dict:
    cfg = {}
    if ENV_TELE.exists():
        for line in ENV_TELE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def tg_api(method: str, **params) -> dict:
    """Gọi Bot API của bot cảnh báo. Lỗi mạng → {} (không bao giờ làm hỏng lượt chạy)."""
    tok = _cfg_tele().get("TELEGRAM_BOT_TOKEN")
    if not tok:
        return {}
    data = urllib.parse.urlencode({k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                                   for k, v in params.items()}).encode()
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/{method}", data=data, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log(f"Telegram {method} lỗi: {e}")
        return {}


def tele(tieu_de: str, noi_dung: str, nut: list | None = None) -> int:
    """Nhắn chủ. `nut` = hàng nút inline [[{text, callback_data}...]]. Trả message_id (0 nếu không gửi được)."""
    msg = f"{tieu_de}\n{noi_dung}".strip()
    if len(msg) > 3900:
        msg = msg[:3900] + "\n…(cắt bớt, xem ops/ban-tin/tu-dong.log)"
    cfg = _cfg_tele()
    tok, chat = cfg.get("TELEGRAM_BOT_TOKEN"), cfg.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        with open(BT / "khan-chua-gui.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} CHUA GUI (thieu {ENV_TELE}):\n{msg}\n")
        log("CHƯA GỬI Telegram: thiếu cấu hình")
        return 0
    params = {"chat_id": chat, "text": msg}
    if nut:
        params["reply_markup"] = {"inline_keyboard": nut}
    r = tg_api("sendMessage", **params)
    if r.get("ok"):
        log(f"đã nhắn Telegram: {tieu_de}")
        return int(r["result"]["message_id"])
    return 0


def doc_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ghi_state(**kw) -> None:
    s = doc_state()
    s.update(kw)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def tom_tat_viet(cac_commit: list[str], base: str) -> str:
    """Một-hai câu tiếng Việt cho người dùng, viết bằng `claude -p` trên máy. Hỏng/chậm/lạc đề → tiêu đề gốc."""
    goc = "; ".join(c.split(" ", 1)[1] if " " in c else c for c in cac_commit)
    prompt = ("Viết 1 đến 2 câu tiếng Việt (tối đa 60 từ), không gạch đầu dòng, không dùng dấu gạch dài, "
              "nói các thay đổi sau giúp người dùng phổ thông được gì. Gọi sản phẩm là Thansa, KHÔNG nhắc tên Javis, "
              f"không bịa thêm tính năng: {goc}")
    try:
        r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=180)
        t = re.sub(r"\s+", " ", (r.stdout or "")).strip().replace("\u2014", "-")
        if r.returncode == 0 and 20 < len(t) < 600 and "javis" not in t.lower():
            return t
    except Exception:
        pass
    return f"Theo Javis {base}: {goc}"


def tang_minor(v: str) -> str:
    a, b, _c = (int(x) for x in re.findall(r"\d+", v.split("-javis-")[0])[:3])
    return f"{a}.{b + 1}.0"


def dang_rebase() -> bool:
    gd = Path(git("rev-parse", "--git-dir"))
    gd = gd if gd.is_absolute() else WT / gd
    return (gd / "rebase-merge").exists() or (gd / "rebase-apply").exists()

# ---------------------------------------------------------------- luật rebrand (giống các vòng tay)

RB = re.compile(r"Javis(?![/\w])(?!-[A-Z])")
NGUOC = [("xahoapro/thansa-os", "blogminhquy/javis-os"), ("THANSA OS", "JAVIS OS"), ("thansa.org", "javisos.com"),
         ("tradingauto.org", "minhquy.vn"), ("Duy Quang", "Minh Quý"), ("THANSA", "JAVIS"), ("Thansa", "Javis")]
PATCH_REBRAND = re.compile(r"rebrand|ten san pham|danh tinh|mo ta hien thi|chuoi con sot|thuong hieu", re.I)
MARKER = re.compile(r"^(<<<<<<< |>>>>>>> |=======$)", re.M)
KHOI = re.compile(r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", re.S | re.M)
SKIP_DEM = re.compile(r'^(CHANGELOG|ops/|bao-cao/|nhiem-vu/|docs/superpowers/|docs/dev/|tests/|ANNOUNCEMENTS)')
FILE_BAO_VE = {"server/codex_realtime.py"}          # clientInfo "Javis OS" (P048 GIỮ)
CHUOI_BAO_VE = ("adaptive source contract",)          # header test canh (P048 GIỮ)


def rebrand(t: str) -> str:
    return RB.sub("Thansa", t.replace("JAVIS OS", "THANSA OS"))


def nguoc(t: str) -> str:
    for a, b in NGUOC:
        t = t.replace(a, b)
    return t


def go_file(f: str, la_patch_rebrand: bool) -> bool:
    """Gỡ các khối xung đột. Patch rebrand: lấy upstream + rebrand. Patch khác: chỉ khi mọi từ phía patch
    (đổi ngược thương hiệu) đều có ở phía upstream - patch không mang nội dung riêng nào ngoài tên."""
    p = WT / f
    s = p.read_text(encoding="utf-8", errors="surrogateescape")
    ok = True

    def mot(m):
        nonlocal ok
        ours, theirs = m.group(1), m.group(2)
        if la_patch_rebrand or set(re.findall(r"\w+", nguoc(theirs))) <= set(re.findall(r"\w+", ours)):
            return rebrand(ours)
        ok = False
        return m.group(0)

    s2 = KHOI.sub(mot, s)
    p.write_text(s2, encoding="utf-8", errors="surrogateescape")
    return ok and not MARKER.search(s2)

# ---------------------------------------------------------------- các bước

def chuan_bi(up: str) -> None:
    don_dep()
    sh(["git", "worktree", "add", "-q", "--force", "-B", "tu-dong", str(WT), "origin/me"], cwd=ME)
    sh(["git", "worktree", "add", "-q", "--force", "--detach", str(WTG), up], cwd=ME)


def don_dep() -> None:
    for d in (WT, WTG):
        if d.exists():
            sh(["git", "worktree", "remove", "--force", str(d)], cwd=ME, check=False)
    sh(["git", "worktree", "prune"], cwd=ME, check=False)


def tron(up: str, ver_moi: str, base_moi: str) -> dict:
    ttin = {"tu_go": [], "xoa": []}
    sh(["git", "rebase", up], check=False)
    for _ in range(2000):
        if not dang_rebase():
            break
        patch = git("log", "--format=%h %s", "-1", "REBASE_HEAD", check=False)
        la_rb = bool(PATCH_REBRAND.search(patch))
        for l in [l for l in git("status", "--porcelain").splitlines() if l[:2] in ("UU", "AA", "DU", "UD", "AU", "UA", "DD")]:
            kieu, f = l[:2], l[3:]
            if kieu == "UU" and f == "VERSION":
                (WT / "VERSION").write_text(f"{ver_moi}-javis-{base_moi}\n", encoding="utf-8")
                git("add", "VERSION")
            elif kieu == "UU":
                if not go_file(f, la_rb):
                    raise Loi(f"XUNG ĐỘT cần người xử lý ở patch «{patch}», file {f}")
                git("add", f)
                ttin["tu_go"].append(f"{patch.split(' ')[0]}:{f}")
            elif kieu == "DU" and la_rb:
                git("rm", "-q", f)          # upstream xoá file mà patch chỉ rebrand → bỏ theo upstream
                ttin["xoa"].append(f)
            else:
                raise Loi(f"XUNG ĐỘT loại {kieu} ở patch «{patch}», file {f}")
        for f in git("diff", "--cached", "--name-only").splitlines():
            fp = WT / f
            if fp.is_file() and MARKER.search(fp.read_text(encoding="utf-8", errors="replace")):
                raise Loi(f"còn dấu xung đột trong {f} ở patch «{patch}»")
        r = sh(["git", "rebase", "--continue"], check=False)
        out = r.stdout + r.stderr
        if r.returncode != 0 and "Could not apply" not in out:
            if "nothing to commit" in out or "empty" in out:
                sh(["git", "rebase", "--skip"], check=False)
            elif not [l for l in git("status", "--porcelain").splitlines() if l[:2] == "UU"]:
                raise Loi(f"rebase --continue hỏng ở «{patch}»: {out[-400:]}")
    if dang_rebase():
        raise Loi("rebase không kết thúc")
    if (WT / "VERSION").read_text().strip() != f"{ver_moi}-javis-{base_moi}":
        (WT / "VERSION").write_text(f"{ver_moi}-javis-{base_moi}\n", encoding="utf-8")
        git("add", "VERSION")
        git("commit", "-q", "-m", f"ops: VERSION {ver_moi}-javis-{base_moi} (tu dong)")
    nhiem = sh(["bash", "-c", "git ls-files -z | xargs -0 grep -alE '^(<<<<<<< |>>>>>>> )' 2>/dev/null | head -5"]).stdout.strip()
    if nhiem:
        raise Loi(f"sau rebase còn dấu xung đột: {nhiem}")
    return ttin


def dem(rev: str) -> dict:
    out = {}
    for f in git("ls-tree", "-r", "--name-only", rev).splitlines():
        if SKIP_DEM.match(f) or not re.search(r"\.(py|js|html|json|md|yml|yaml)$", f):
            continue
        b = sh(["git", "show", f"{rev}:{f}"]).stdout
        n = len(RB.findall(b)) + b.count("JAVIS OS")
        if n:
            out[f] = n
    return out


def rebrand_py(f: str) -> int:
    src = (WT / f).read_text(encoding="utf-8")
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    offs = [0]
    for l in src.splitlines(keepends=True):
        offs.append(offs[-1] + len(l))
    loai = {tokenize.STRING} | ({tokenize.FSTRING_MIDDLE} if hasattr(tokenize, "FSTRING_MIDDLE") else set())
    sua = []
    for i, t in enumerate(toks):
        if t.type not in loai or not RB.search(t.string):
            continue
        j = i - 1
        while j >= 0 and toks[j].type in (tokenize.NL, tokenize.COMMENT):
            j -= 1
        k = i + 1
        while k < len(toks) and toks[k].type in (tokenize.NL, tokenize.COMMENT):
            k += 1
        la_doc = (j < 0 or toks[j].type in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)) and \
                 (k >= len(toks) or toks[k].type in (tokenize.NEWLINE, tokenize.ENDMARKER))
        if la_doc or t.string.strip("'\"rbfu") == "Javis" or any(c in t.string for c in CHUOI_BAO_VE):
            continue   # docstring / tên thư mục vault "Javis" / chuỗi được canh → GIỮ
        sua.append((t.start, t.end, RB.sub("Thansa", t.string)))
    s = src
    for (sr, sc), (er, ec), new in sorted(sua, reverse=True):
        a, b = offs[sr - 1] + sc, offs[er - 1] + ec
        s = s[:a] + new + s[b:]
    if sua:
        (WT / f).write_text(s, encoding="utf-8")
    return len(sua)


def rebrand_moi() -> dict:
    """Đổi chữ Javis hiển thị MỚI so với bản phát hành trước + kéo link repo gốc về repo Thansa."""
    cu, moi = dem("origin/main"), dem("HEAD")
    doi = {}
    for f in [f for f, n in moi.items() if n > cu.get(f, 0)]:
        p = WT / f
        if f in FILE_BAO_VE or not p.exists():
            continue
        n = 0
        if f.endswith(".py"):
            n = rebrand_py(f)
        elif re.search(r"\.(md|json|ya?ml)$", f) or f in ("dashboard/index.html", "CLAUDE.md"):
            s = p.read_text(encoding="utf-8")
            t = rebrand(s)
            if t != s:
                n = len(RB.findall(s)) + s.count("JAVIS OS")
                p.write_text(t, encoding="utf-8")
        if n:
            doi[f] = n
    for f in git("ls-files").splitlines():
        if SKIP_DEM.match(f) or f == "server/main.py" or not re.search(r"\.(py|js|html|json|md|ya?ml)$", f):
            continue
        try:
            s = (WT / f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if "blogminhquy/javis-os" in s:
            (WT / f).write_text(s.replace("blogminhquy/javis-os", "xahoapro/thansa-os"), encoding="utf-8")
            doi[f] = doi.get(f, 0) + s.count("blogminhquy/javis-os")
    for f in doi:
        if f.endswith(".py"):
            sh([str(PY), "-m", "py_compile", f])
        elif f.endswith(".json"):
            json.loads((WT / f).read_text(encoding="utf-8"))
    return doi


def chot_an_toan() -> str:
    """P038: loop/việc mặc định chỉ đọc + đề xuất."""
    loi = []
    cl = (WT / "CLAUDE.md").read_text(encoding="utf-8")
    for c in ("ALWAYS forbidden to self-execute", "mode: suggest"):
        if c not in cl:
            loi.append(f"CLAUDE.md mất câu «{c}»")
    if '_MODE_CHO_PHEP = ("suggest", "auto")' not in (WT / "system/plugins/javis-task/plugin.py").read_text(encoding="utf-8"):
        loi.append("javis-task không còn chặn mode full")
    for lang in ("vi", "en"):
        moi = (WT / f"dashboard/i18n/{lang}.json").read_text(encoding="utf-8")
        cu = sh(["git", "show", f"origin/main:dashboard/i18n/{lang}.json"]).stdout
        for k in ("mqwarn", "fullwarn", "full_confirm", "toggle_confirm"):
            if moi.count(k) < cu.count(k):
                loi.append(f"{lang}.json mất khoá cảnh báo {k} ({cu.count(k)}→{moi.count(k)})")
    return "; ".join(loi)


def ghi_ho_so(moc: dict, up: str, ver_moi: str, base_moi: str, cac_commit: list, doi: dict, ttin: dict) -> str:
    hom_nay = time.strftime("%Y-%m-%d")
    mp = (WT / "ops/mapping.yaml").read_text(encoding="utf-8")
    pid = ""
    if doi:
        pid = f"P{max(int(x) for x in re.findall(r'^- id: P(\d+)', mp, re.M)) + 1:03d}"
        neo_file, neo = "", ""
        for f in doi:
            for l in sh(["git", "diff", "-U0", "--", f]).stdout.splitlines():
                if l.startswith("+") and not l.startswith("+++") and "Thansa" in l:
                    i = l.index("Thansa")
                    cand = l[max(1, i - 20):i + 30].strip()
                    if len(cand) >= 12:
                        neo_file, neo = f, cand
                        break
            if neo_file:
                break
        neo_file = neo_file or sorted(doi)[0]
        neo = neo or "Thansa"
        q = lambda s: "'" + s.replace("'", "''") + "'"
        git("add", "--", *sorted(doi))       # CHỈ file đã rebrand - không quét theo file lạ chưa track
        git("commit", "-q", "-m", f"[me] {pid}: rebrand nen {base_moi} (tu dong)\n\n"
            f"Automated merge round: display rebrand Javis -> Thansa for strings new in base {base_moi} "
            f"({sum(doi.values())} spots in {len(doi)} files) under the P007/P026/P027/P048 rules.\n\n"
            + "\n".join(f"- {f}: {n}" for f, n in sorted(doi.items()))
            + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        mp = mp.rstrip("\n") + f"""

- id: {pid}
  ten: "Rebrand nền {base_moi} (tự động)"
  y_dinh: >
    Vòng trộn TỰ ĐỘNG {hom_nay} (ops/tu_dong_tron.py): đổi chữ Javis hiển thị mới của nền {base_moi} sang Thansa
    theo luật P007/P026/P027/P048 ({sum(doi.values())} chỗ / {len(doi)} file) + kéo link repo gốc về xahoapro/thansa-os.
  commit: "[me] {pid}: rebrand nen {base_moi} (tu dong)"
  diem_neo:
    - file: {neo_file}
      ky_hieu: {q(neo)}
  vung_theo_doi:
{chr(10).join(f'    - "{f}"' for f in sorted(doi))}
  anh_goc:
    - file: {neo_file}
      doan: {q(nguoc(neo))}
  kiem_chung: >
    Đếm Javis hiển thị theo file so bản phát hành trước; nghiệm thu fork vs upstream sạch; chốt an toàn P038.
  dieu_kien_bo: >
    Như P048.
"""
    m = dict(moc)
    m.update(thansa_version=ver_moi, goc_commit=up, goc_version=base_moi, ngay_tron=hom_nay,
             so_patch=len(re.findall(r"^- id: P\d+", mp, re.M)))
    (WT / "ops/mapping.yaml").write_text(mp, encoding="utf-8")
    (WT / "ops/moc-goc.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    goc_tom = "; ".join(c.split(" ", 1)[1] for c in cac_commit)
    tom = tom_tat_viet(cac_commit, base_moi)
    rel = (WT / "RELEASES.md").read_text(encoding="utf-8")
    i = rel.index("\n| ", rel.index("|--------"))
    rel = rel[:i + 1] + (f"| {ver_moi} | {base_moi:<9} | `{up[:7]}`  | {hom_nay} (chờ duyệt) | Trộn Javis "
                         f"{moc['goc_version']}→{base_moi} ({len(cac_commit)} commit, tự động): {tom[:500]} "
                         "Giữ mọi tuỳ biến Thansa. |\n") + rel[i + 1:]
    (WT / "RELEASES.md").write_text(rel, encoding="utf-8")
    with open(WT / "ops/so-tron.md", "a", encoding="utf-8") as f:
        f.write(f"""
## Vòng TỰ ĐỘNG {hom_nay} (goc {moc['goc_commit'][:7]} → {up[:7]}, nền {moc['goc_version']} → {base_moi}, thansa {moc['thansa_version']}→{ver_moi})
- {len(cac_commit)} commit upstream: {goc_tom[:600]}
- Rebase tự động trong worktree riêng. Tự gỡ: {", ".join(ttin["tu_go"]) or "không"}. Upstream xoá: {", ".join(ttin["xoa"]) or "không"}.
- Rebrand: {pid or "không cần"} ({sum(doi.values())} chỗ / {len(doi)} file). moc-goc {up[:7]}/{base_moi}/so_patch {m['so_patch']}.
""")
    git("add", "ops/mapping.yaml", "ops/moc-goc.json", "RELEASES.md", "ops/so-tron.md")
    git("commit", "-q", "-m", f"ops: moc-goc {base_moi} + so-tron + RELEASES vong tu dong (thansa {moc['thansa_version']}->{ver_moi})"
        "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    return pid


def tu_kiem(up: str) -> None:
    r = sh([str(PY), "ops/tu-kiem-chung.py"], check=False, env={"TU_KIEM_ME": "HEAD", "TU_KIEM_MAIN": up})
    if "XANH — hồ sơ khớp thực tế" not in r.stdout:
        raise Loi("tu-kiem-chung ĐỎ:\n" + (r.stdout + r.stderr)[-1200:])


def suite(cwd: Path, ten: str) -> tuple[set, str]:
    r = sh([str(PY), "tests/run.py"], cwd=cwd, check=False, timeout=3600)
    (BT / f"tu-dong-{ten}.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    m = re.search(r"^ĐỎ: (.*)$", r.stdout, re.M)
    tong = re.search(r"^(\d+/\d+) xanh", r.stdout, re.M)
    return (set(x.strip() for x in m.group(1).split(",")) if m else set()), (tong.group(1) if tong else "?")


def nghiem_thu() -> str:
    do_fork, tong_fork = suite(WT, "fork")
    do_goc, tong_goc = suite(WTG, "goc")
    con_do = []
    for t in sorted(do_fork - do_goc):   # chạy lại riêng một lần: loại test chập chờn do tải máy
        if t.endswith(".py"):
            r = sh([str(PY), str(WT / "tests" / "python" / t)], check=False, timeout=900)
        else:
            r = sh(["node", str(WT / "tests" / "js" / t)], check=False, timeout=900)
        if r.returncode != 0:
            con_do.append(t)
    if con_do:
        raise Loi(f"HỒI QUY: test chỉ đỏ ở Thansa: {con_do} (Thansa {tong_fork}, Javis gốc {tong_goc})")
    return f"Thansa {tong_fork}, Javis gốc {tong_goc}, đỏ chung {len(do_fork & do_goc)} (môi trường), 0 hồi quy"


def quet_bi_mat() -> str:
    d = sh(["git", "diff", "origin/main", "HEAD"]).stdout
    m = re.search(r"^\+.*(ghp_[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10}|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16})", d, re.M)
    if m:
        return "nghi lộ bí mật: " + m.group(0)[:80]
    for f in git("ls-tree", "-r", "--name-only", "HEAD").splitlines():
        if re.search(r"(^|/)(\.env|\.secret_key|settings\.json)$", f):
            return f"file bí mật bị track: {f}"
    return ""

# ---------------------------------------------------------------- nút Telegram + phát hành khi chủ bấm

LOCK = BT / ".tu-dong.lock"


def nghe_nut() -> int:
    """Cron mỗi phút: đọc lượt bấm nút. Chỉ nhận từ ĐÚNG tài khoản chủ (TELEGRAM_CHAT_ID) và đúng mã của bản đang chờ."""
    chu = str(_cfg_tele().get("TELEGRAM_CHAT_ID", ""))
    het = time.time() + 50          # chờ sẵn ~50 giây/phút: Telegram chỉ cho trả lời lượt bấm trong vài giây
    while time.time() < het:
        r = tg_api("getUpdates", offset=int(doc_state().get("tg_offset", 0)), timeout=min(25, max(1, int(het - time.time()))),
                   allowed_updates=["callback_query"])
        if not r.get("ok"):
            time.sleep(5)
            continue
        _xu_ly_cap_nhat(r.get("result", []), chu)
    return 0


def _xu_ly_cap_nhat(cap_nhat: list, chu: str) -> None:
    for u in cap_nhat:
        ghi_state(tg_offset=u["update_id"] + 1)          # tiêu thụ trước: lỗi ở dưới cũng không xử lý lặp
        cb = u.get("callback_query")
        if not cb:
            continue
        ai = str((cb.get("from") or {}).get("id", ""))
        data = str(cb.get("data", ""))
        st = doc_state()
        if ai != chu:
            tg_api("answerCallbackQuery", callback_query_id=cb["id"], text="Bạn không có quyền.")
            log(f"bỏ qua lượt bấm của người lạ {ai}")
            continue
        try:
            hanh_dong, ver, ma = data.split("|")
        except ValueError:
            continue
        if ver != st.get("san_sang_ver") or ma != st.get("san_sang_ma"):
            tg_api("answerCallbackQuery", callback_query_id=cb["id"], text="Nút này đã hết hạn (bản cũ hoặc đã xử lý).")
            continue
        msg = cb.get("message") or {}
        if hanh_dong == "bo":
            ghi_state(san_sang_ma="")
            tg_api("answerCallbackQuery", callback_query_id=cb["id"], text=f"Đã bỏ qua {ver}.")
            tg_api("editMessageReplyMarkup", chat_id=chu, message_id=msg.get("message_id"), reply_markup={"inline_keyboard": []})
            tele("THANSA", f"Đã bỏ qua bản {ver}. Lượt tự động sau sẽ trộn lại khi Javis có bản mới hơn.")
            continue
        if hanh_dong == "ph":
            ghi_state(san_sang_ma="")                     # vô hiệu nút ngay: bấm 2 lần không phát hành 2 lần
            tg_api("answerCallbackQuery", callback_query_id=cb["id"], text=f"Đang phát hành {ver}…")
            tg_api("editMessageReplyMarkup", chat_id=chu, message_id=msg.get("message_id"), reply_markup={"inline_keyboard": []})
            tele("THANSA", f"⏳ Đang phát hành {ver} (khoảng 1-2 phút)…")
            phat_hanh_san_sang(ver)


def _khoa():
    import fcntl
    f = open(LOCK, "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    return f


def phat_hanh_san_sang(ver: str) -> None:
    """Phát hành nhánh san-sang-<ver> đúng như quy trình tay. Mọi thao tác trên máy làm TRƯỚC khi đẩy;
    hỏng trước bước đẩy thì trả nhánh về như cũ và nhắn lý do."""
    khoa = _khoa()
    if khoa is None:
        ma = os.urandom(4).hex()
        ghi_state(san_sang_ma=ma)
        tele("⚠️ THANSA", f"Chưa phát hành được {ver}: đang có một lượt trộn khác chạy. Đợi vài phút rồi bấm lại.",
             nut=[[{"text": f"🚀 Phát hành {ver}", "callback_data": f"ph|{ver}|{ma}"},
                   {"text": "Bỏ qua", "callback_data": f"bo|{ver}|{ma}"}]])
        return
    st = doc_state()
    nhanh = f"san-sang-{ver}"
    old_me = old_main = ""
    try:
        if st.get("san_sang") != nhanh:
            raise Loi(f"không có bản {ver} đang chờ duyệt")
        def g(*a, cwd=ME, check=True):
            return git(*a, cwd=cwd, check=check)
        if g("rev-parse", "--abbrev-ref", "HEAD") != "me" or g("status", "--porcelain", "--untracked-files=no"):
            raise Loi("worktree nhánh me không sạch hoặc không ở nhánh me (có phiên đang làm tay?)")
        if g("status", "--porcelain", "--untracked-files=no", cwd=GOC) or g("rev-parse", "--abbrev-ref", "HEAD", cwd=GOC) != "main":
            raise Loi("worktree goc không sạch hoặc không ở nhánh main")
        g("fetch", "-q", "origin", "--tags")
        g("fetch", "-q", "upstream", cwd=GOC)
        if g("rev-parse", "origin/me") != st.get("san_sang_base"):
            raise Loi("nhánh me trên GitHub đã thay đổi sau lúc trộn - bản chờ duyệt đã cũ, lượt tự động sau sẽ trộn lại")
        old_me, old_main = g("rev-parse", "me"), g("rev-parse", "main", cwd=GOC)
        moc = json.loads(sh(["git", "show", f"{nhanh}:ops/moc-goc.json"], cwd=ME).stdout)
        g("merge", "-q", "--ff-only", moc["goc_commit"], cwd=GOC)
        g("reset", "-q", "--hard", nhanh)
        r = sh([str(PY), "ops/tu-kiem-chung.py"], cwd=ME, check=False)
        if "XANH — hồ sơ khớp thực tế" not in r.stdout:
            raise Loi("tu-kiem-chung ĐỎ trước khi đẩy:\n" + (r.stdout + r.stderr)[-800:])
        d = sh(["git", "diff", "origin/main", "me"], cwd=ME).stdout
        if re.search(r"^\+.*(ghp_[A-Za-z0-9]{20}|sk-[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10}|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16})", d, re.M):
            raise Loi("quét bí mật thấy nghi vấn - không đẩy")
        rel = (ME / "RELEASES.md").read_text(encoding="utf-8")
        dong = next((l for l in rel.splitlines() if l.startswith(f"| {ver} |")), "")
        mo_ta = dong.split("|")[5].strip() if dong.count("|") >= 6 else f"Trộn Javis {moc['goc_version']}."
    except Loi as e:
        if old_me:
            sh(["git", "reset", "-q", "--hard", old_me], cwd=ME, check=False)
        if old_main:
            sh(["git", "reset", "-q", "--hard", old_main], cwd=GOC, check=False)
        log(f"phát hành {ver} DỪNG: {e}")
        tele("🚨 THANSA - chưa phát hành", f"Bản {ver}: {e}\nKhông có gì bị đẩy lên GitHub.")
        khoa.close()
        return
    # ---- từ đây là đẩy lên GitHub (chủ đã bấm duyệt)
    try:
        g("branch", "-f", f"me-backup-{ver}", "me")
        g("push", "-q", "origin", f"me-backup-{ver}")
        g("push", "-q", f"--force-with-lease=me:{st['san_sang_base']}", "origin", "me")
        c = g("commit-tree", "me^{tree}", "-p", "origin/main", "-m",
              f"release: Thansa OS {ver} (nen Javis {moc['goc_version']})\n\n{mo_ta[:600]}\n\n"
              "Phat hanh khi chu bam duyet tren Telegram.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        g("push", "-q", "origin", f"{c}:refs/heads/main")
        nf = BT / "tu-dong-release.md"
        nf.write_text(f"## Thansa OS {ver} (nền Javis {moc['goc_version']})\n\n{mo_ta}\n\n"
                      "**Cập nhật:** bấm nút **Cập nhật** trong app.\n", encoding="utf-8")
        sh(["gh", "release", "create", f"thansa-v{ver}", "--repo", "xahoapro/thansa-os", "--target", "main",
            "--title", f"Thansa OS {ver}", "--notes-file", str(nf)], cwd=ME)
        short = c[:7]
        rel = (ME / "RELEASES.md").read_text(encoding="utf-8")
        rel = re.sub(rf"^(\| {re.escape(ver)} \|[^\n]*?)\(chờ duyệt\)", rf"\1(đã phát hành, origin/main {short})", rel, count=1, flags=re.M)
        (ME / "RELEASES.md").write_text(rel, encoding="utf-8")
        with open(ME / "ops/so-tron.md", "a", encoding="utf-8") as f:
            f.write(f"- **ĐÃ PHÁT HÀNH {time.strftime('%Y-%m-%d')}** khi chủ bấm duyệt trên Telegram (origin/main {short}, "
                    f"tag + Release thansa-v{ver}; backup me-backup-{ver}).\n")
        g("add", "RELEASES.md", "ops/so-tron.md")
        g("commit", "-q", "-m", f"ops: danh dau {ver} da phat hanh (origin/main {short}, chu duyet qua Telegram)"
          "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        g("push", "-q", "origin", "me")
        xa = [l.split("refs/heads/")[1] for l in g("ls-remote", "--heads", "origin", "me-backup-*").splitlines()]
        g("fetch", "-q", "origin")
        xa.sort(key=lambda b: int(g("log", "-1", "--format=%ct", f"origin/{b}", check=False) or 0), reverse=True)
        for b in xa[3:]:                                   # GitHub giữ 3 nhánh backup mới nhất
            if not g("rev-parse", "-q", "--verify", f"refs/heads/{b}", check=False):
                g("branch", f"{b}-github", f"origin/{b}")
            g("push", "-q", "origin", "--delete", b, check=False)
        ghi_state(san_sang="", san_sang_ver="", ban_cuoi=ver, phat_hanh_luc=time.strftime("%Y-%m-%d %H:%M"))
        log(f"ĐÃ PHÁT HÀNH {ver} (main {short})")
        tele(f"🎉 ĐÃ PHÁT HÀNH Thansa {ver}",
             f"{mo_ta[:700]}\n\nmain {short} · https://github.com/xahoapro/thansa-os/releases/tag/thansa-v{ver}\n"
             "Máy đang chạy: bấm Cập nhật trong app để lên bản mới.")
    except Loi as e:
        log(f"phát hành {ver} LỖI giữa chừng: {e}")
        tele("🚨 THANSA - phát hành lỗi giữa chừng", f"Bản {ver}: {e}\nCần người xem (mở Claude Code ở /home/thansa/thansa).")
    finally:
        khoa.close()

# ---------------------------------------------------------------- chạy

def main() -> int:
    if "--nghe" in sys.argv:
        return nghe_nut()
    if "--phat-hanh" in sys.argv:
        phat_hanh_san_sang(sys.argv[sys.argv.index("--phat-hanh") + 1])
        return 0
    if "--nhan" in sys.argv:
        i = sys.argv.index("--nhan")
        tele("THANSA", " ".join(sys.argv[i + 1:]))
        return 0
    log("=== bắt đầu lượt tự động trộn" + (" (chỉ xem)" if CHI_XEM else ""))
    sh(["git", "fetch", "-q", "origin"], cwd=ME)
    sh(["git", "fetch", "-q", "upstream"], cwd=GOC)
    moc = json.loads(sh(["git", "show", "origin/me:ops/moc-goc.json"], cwd=ME).stdout)
    up = git("rev-parse", "upstream/main", cwd=GOC)
    if up == moc["goc_commit"]:
        log(f"không có bản Javis mới (vẫn {moc['goc_version']})")
        return 0
    if sh(["git", "merge-base", "--is-ancestor", moc["goc_commit"], up], cwd=GOC, check=False).returncode != 0:
        raise Loi(f"Javis {up[:8]} KHÔNG nối tiếp mốc gốc {moc['goc_commit'][:8]} (upstream viết lại lịch sử?)")
    base_moi = git("show", f"{up}:VERSION", cwd=GOC)
    cac_commit = git("log", "--format=%h %s", f"{moc['goc_commit']}..{up}", cwd=GOC).splitlines()
    ver_moi = tang_minor(moc["thansa_version"])
    log(f"Javis mới: {moc['goc_version']} → {base_moi} ({len(cac_commit)} commit) → Thansa {ver_moi}")
    if CHI_XEM:
        return 0
    st = doc_state()
    if not EP and up in (st.get("loi_up"), st.get("san_sang_up")):
        log(f"bản {base_moi} đã xử lý/đã nhắn trước đó - bỏ qua (dùng --ep để chạy lại)")
        return 0
    try:
        chuan_bi(up)
        ttin = tron(up, ver_moi, base_moi)
        log(f"rebase xong; tự gỡ {len(ttin['tu_go'])} khối, theo upstream xoá {len(ttin['xoa'])} file")
        doi = rebrand_moi()
        log(f"rebrand {sum(doi.values())} chỗ / {len(doi)} file")
        an_toan = chot_an_toan()
        if an_toan:
            raise Loi("CHỐT AN TOÀN P038 hỏng: " + an_toan)
        pid = ghi_ho_so(moc, up, ver_moi, base_moi, cac_commit, doi, ttin)
        tu_kiem(up)
        nghiem = nghiem_thu()
        log("nghiệm thu: " + nghiem)
        bm = quet_bi_mat()
        if bm:
            raise Loi(bm)
        nhanh = f"san-sang-{ver_moi}"
        git("branch", "-f", nhanh, "HEAD")
    except Loi as e:
        log(f"LỖI: {e}")
        if WT.exists() and dang_rebase():
            sh(["git", "rebase", "--abort"], check=False)
        don_dep()
        ghi_state(loi_up=up, loi_luc=time.strftime("%Y-%m-%d %H:%M"), loi=str(e)[:500])
        tele("🚨 THANSA - tự trộn Javis DỪNG",
             f"Javis {moc['goc_version']} → {base_moi} ({len(cac_commit)} commit):\n"
             + "\n".join("• " + c.split(" ", 1)[1] for c in cac_commit[:8]) +
             f"\n\nLý do: {e}\n\nKhông có gì bị thay đổi: Thansa vẫn {moc['thansa_version']}, nhánh me/main nguyên vẹn. "
             f"Cần người xử lý: mở Claude Code ở /home/thansa/thansa và nhờ trộn Javis {base_moi}.")
        return 2
    don_dep()
    ma = os.urandom(4).hex()      # mã dùng một lần: nút chỉ phát hành ĐÚNG bản này, bấm lại/tin cũ vô hiệu
    ghi_state(san_sang_up=up, san_sang=nhanh, san_sang_ver=ver_moi, san_sang_ma=ma,
              san_sang_base=sh(["git", "rev-parse", "origin/me"], cwd=ME).stdout.strip(),
              san_sang_luc=time.strftime("%Y-%m-%d %H:%M"), loi_up="")
    mid = tele(f"✅ THANSA {ver_moi} đã trộn xong - CHỜ BẠN DUYỆT",
         f"Theo Javis {moc['goc_version']} → {base_moi} ({len(cac_commit)} commit):\n"
         + "\n".join("• " + c.split(" ", 1)[1] for c in cac_commit[:10]) +
         f"\n\nNghiệm thu: {nghiem}.\nRebrand tự động: {pid or 'không cần'}.\n"
         f"Bản trộn nằm ở nhánh {nhanh} trên máy, CHƯA đẩy lên GitHub. Bấm nút để phát hành.",
         nut=[[{"text": f"🚀 Phát hành {ver_moi}", "callback_data": f"ph|{ver_moi}|{ma}"},
               {"text": "Bỏ qua", "callback_data": f"bo|{ver_moi}|{ma}"}]])
    ghi_state(san_sang_msg=mid)
    log("=== xong (chờ duyệt)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Loi as e:
        log(f"LỖI: {e}")
        st = doc_state()
        if st.get("loi_truoc") != str(e)[:200]:      # lỗi trước khi trộn: nhắn một lần mỗi kiểu lỗi
            tele("🚨 THANSA - tự trộn lỗi", str(e))
            ghi_state(loi_truoc=str(e)[:200])
        sys.exit(2)
