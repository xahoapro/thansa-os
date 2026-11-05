"""Mô hình nghe ngầm TRÊN MÁY (Vosk tiếng Việt) cho tính năng "Lắng nghe ngầm" (Thansa 2.5.0, 04/11/2026).

Chủ chốt: mic mở sẵn, chỉ dò TỪ KHOÁ (Thần Sa, bật mic...) để gọi; mặc định dò ngay trong trình duyệt bằng
Vosk WebAssembly (dashboard/wake-listen.js) nên âm thanh KHÔNG rời máy cho tới khi nghe thấy từ khoá. Cách
khác (Web Speech của trình duyệt, âm thanh lên Google) chọn được ở Cài đặt.

Máy chủ lo mô hình: tải MỘT LẦN (vosk-model-small-vn, ~34 MB) vào STATE_DIR/wake, đóng lại thành .tar.gz
đúng dạng vosk-browser đọc, rồi phục vụ ở /voice/wake/model. Từ khoá người dùng khai được soát với từ điển
của mô hình: từ mô hình không biết thì báo ra (Vosk lặng lẽ bỏ qua từ lạ trong ngữ pháp).
"""
from __future__ import annotations

import os
import re
import tarfile
import threading
import time
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

from config import STATE_DIR  # noqa: E402 - cùng thư mục trạng thái với cả app
THU_MUC = STATE_DIR / "wake"
TEN_MO_HINH = "vosk-model-small-vn-0.4"
# Hugging Face (CDN nhanh, ~6 giây) trước, máy chủ gốc của Vosk (rất chậm, ~13 KB/s đo 04/11) dự phòng.
# Cùng một tệp: kiểm SHA-256 sau khi tải, lệch là bỏ.
NGUON = [x for x in (os.getenv("THANSA_WAKE_MODEL_URL", ""),
                     f"https://huggingface.co/rhasspy/vosk-models/resolve/main/vi/{TEN_MO_HINH}.zip",
                     f"https://alphacephei.com/vosk/models/{TEN_MO_HINH}.zip") if x]
SHA256 = "efe5c8494212110471a79befc48c79da679e5b1fc52a4ffb500222ff86d622e5"
GOI = THU_MUC / f"{TEN_MO_HINH}.tar.gz"

# Mặc định (người dùng sửa được ở Cài đặt > Giọng nói > Lắng nghe ngầm).
TU_BAT_MAC_DINH = ["thần sa", "thansa", "than sa", "mở mic", "bật mic", "bật nghe", "nghe lệnh"]
TU_TAT_MAC_DINH = ["tắt mic", "tắt nghe", "thôi nghe"]
TOI_DA_TU, TOI_DA_KY_TU = 20, 40

_khoa = threading.Lock()
_trang = {"dang_tai": False, "da_tai": 0, "tong": 0, "loi": "", "luc": 0.0}


def chuan_hoa(tu: str) -> str:
    s = unicodedata.normalize("NFC", str(tu or "")).lower().strip()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def lam_sach_ds(ds, mac_dinh: list) -> list:
    """Danh sách từ khoá từ Cài đặt: chữ thường, bỏ trùng, tối đa 20 cụm x 40 ký tự. Rỗng thì dùng mặc định."""
    if isinstance(ds, str):
        ds = re.split(r"[\n,;]+", ds)
    out = []
    for x in ds or []:
        t = chuan_hoa(x)[:TOI_DA_KY_TU].strip()
        if t and t not in out:
            out.append(t)
        if len(out) >= TOI_DA_TU:
            break
    return out or list(mac_dinh)


def tu_cai_dat(v: dict) -> dict:
    v = v or {}
    eng = v.get("wake_engine") if v.get("wake_engine") in ("local", "browser") else "local"
    return {"wake_engine": eng,
            "wake_words_on": lam_sach_ds(v.get("wake_words_on"), TU_BAT_MAC_DINH),
            "wake_words_off": lam_sach_ds(v.get("wake_words_off"), TU_TAT_MAC_DINH)}


def trang_thai() -> dict:
    ready = GOI.is_file()
    t = dict(_trang)
    pct = int(t["da_tai"] * 100 / t["tong"]) if t["tong"] else 0
    return {"ready": ready, "loading": bool(t["dang_tai"]), "progress": 100 if ready else pct,
            "error": "" if ready else t["loi"], "size_mb": round(GOI.stat().st_size / 1e6, 1) if ready else 0}


def _tai_mot(url: str, tam: Path) -> None:
    import hashlib
    h = hashlib.sha256()
    _trang.update(da_tai=0, tong=0)
    req = urllib.request.Request(url, headers={"User-Agent": "thansa-os"})
    with urllib.request.urlopen(req, timeout=60) as r, open(tam, "wb") as f:
        _trang["tong"] = int(r.headers.get("Content-Length") or 0)
        while True:
            khoi = r.read(256 * 1024)
            if not khoi:
                break
            f.write(khoi)
            h.update(khoi)
            _trang["da_tai"] += len(khoi)
    if h.hexdigest() != SHA256:
        raise RuntimeError("tệp mô hình tải về không khớp SHA-256")


def _tai():
    """Tải zip mô hình (thử lần lượt các nguồn), đóng lại thành tar.gz cho vosk-browser."""
    try:
        THU_MUC.mkdir(parents=True, exist_ok=True)
        tam = THU_MUC / f"{TEN_MO_HINH}.zip.part"
        loi = ""
        for url in NGUON:
            try:
                _tai_mot(url, tam)
                loi = ""
                break
            except Exception as e:   # noqa: BLE001 - nguồn sau
                loi = f"{type(e).__name__}: {str(e)[:120]}"
        if loi:
            raise RuntimeError(loi)
        # Giải zip ra thư mục tạm rồi đóng tar CẢ THƯ MỤC (có mục thư mục): bộ giải nén của vosk-browser không tự
        # tạo thư mục cha, gói thiếu mục thư mục thì ghi tệp hỏng âm thầm và báo "không có tệp mô hình" (đo 04/11).

        import tempfile
        goi_tam = GOI.with_suffix(".part")
        with tempfile.TemporaryDirectory(dir=str(THU_MUC)) as td:
            with zipfile.ZipFile(tam) as z:
                z.extractall(td)
            with tarfile.open(goi_tam, "w:gz") as tar:
                for ten in sorted(os.listdir(td)):
                    tar.add(os.path.join(td, ten), arcname=ten)
        goi_tam.replace(GOI)
        tam.unlink(missing_ok=True)
        _trang["loi"] = ""
    except Exception as e:   # noqa: BLE001 - mạng/đĩa: báo lên trang Cài đặt, lần sau thử lại
        _trang["loi"] = f"{type(e).__name__}: {str(e)[:160]}"
    finally:
        _trang["dang_tai"] = False


def dam_bao_tai() -> dict:
    """Chưa có mô hình thì bắt đầu tải ở nền (một luồng duy nhất). Trả trạng thái hiện tại."""
    with _khoa:
        if not GOI.is_file() and not _trang["dang_tai"]:
            _trang.update(dang_tai=True, da_tai=0, tong=0, loi="", luc=time.time())
            threading.Thread(target=_tai, name="wake-model", daemon=True).start()
    return trang_thai()


# Mô hình nhỏ không kèm danh sách từ (từ vựng nằm trong Gr.fst). Đo trực tiếp bằng Vosk 04/11/2026: trong các
# từ hay dùng làm từ khoá, chỉ "thansa" (viết liền) và "míc" là mô hình không biết; "thần sa", "mic", "bật", "mở",
# "tắt", "nghe", "lệnh", "thôi", "ơi" đều có. Trình duyệt còn soát lần nữa (vosk-browser báo từ lạ trong log).
TU_LA_DA_BIET = {"thansa": "thần sa", "míc": "mic"}


def tu_dien() -> set:
    return set()


def ngu_phap(v: dict) -> dict:
    """Cụm từ cho bộ nhận trên máy (ngữ pháp Vosk) + các từ mô hình không biết (để Cài đặt báo người dùng)."""
    cd = tu_cai_dat(v)
    cum, la = [], []
    for c in cd["wake_words_on"] + cd["wake_words_off"]:
        thieu = [w for w in c.split() if w in TU_LA_DA_BIET]
        if thieu:
            la.extend(w for w in thieu if w not in la)
            c = " ".join(TU_LA_DA_BIET.get(w, w) for w in c.split())   # "thansa" -> "thần sa": vẫn bắt được
        if c not in cum:
            cum.append(c)
    return {"phrases": cum, "unknown_words": la, "ready": GOI.is_file()}
