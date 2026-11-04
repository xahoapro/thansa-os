"""Lắng nghe ngầm (Thansa 2.5.0): mô hình nghe trên máy + từ khoá ở Cài đặt (server/wake_model.py)."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ["THANSA_STATE_DIR"] = tempfile.mkdtemp(prefix="thansa-wake-")
sys.path.insert(0, str(ROOT / "server"))

_fails = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _fails.append(name)


import wake_model as w  # noqa: E402

cd = w.tu_cai_dat({})
check("mặc định cách dò là Trên máy", cd["wake_engine"] == "local")
check("mặc định có từ khoá gọi: thần sa, bật mic, mở mic", all(x in cd["wake_words_on"] for x in ("thần sa", "bật mic", "mở mic")))
check("mặc định có từ khoá tắt: tắt mic", "tắt mic" in cd["wake_words_off"])
check("cách dò lạ -> về Trên máy", w.tu_cai_dat({"wake_engine": "xyz"})["wake_engine"] == "local")
check("chọn Trình duyệt được", w.tu_cai_dat({"wake_engine": "browser"})["wake_engine"] == "browser")

ds = w.lam_sach_ds("Thần Sa!\nBẬT MIC\n\nbật mic, Ê trợ lý", w.TU_BAT_MAC_DINH)
check("ô từ khoá: tách dòng/dấu phẩy, chữ thường, bỏ trùng, bỏ dấu câu", ds == ["thần sa", "bật mic", "ê trợ lý"])
check("ô từ khoá trống -> dùng mặc định", w.lam_sach_ds("", w.TU_TAT_MAC_DINH) == w.TU_TAT_MAC_DINH)
check("tối đa 20 cụm x 40 ký tự", len(w.lam_sach_ds([f"tu {i}" for i in range(50)], [])) == 20
      and len(w.lam_sach_ds(["a" * 99], [])[0]) == 40)

g = w.ngu_phap({"wake_words_on": ["thansa", "bật míc"], "wake_words_off": ["tắt mic"]})
check("từ mô hình không biết được báo ra", set(g["unknown_words"]) == {"thansa", "míc"})
check("và đổi sang cách viết mô hình biết", "thần sa" in g["phrases"] and "bật mic" in g["phrases"])

check("nguồn tải: Hugging Face trước, máy chủ Vosk dự phòng", "huggingface.co" in w.NGUON[0] and "alphacephei" in w.NGUON[-1])
check("kiểm SHA-256 mô hình", len(w.SHA256) == 64)
check("chưa tải thì chưa sẵn sàng", w.trang_thai()["ready"] is False)

import main  # noqa: E402
duong = {getattr(x, "path", "") for x in main.app.routes}
check("có route trạng thái / gói mô hình / ngữ pháp",
      {"/voice/wake/status", "/voice/wake/model", "/voice/wake/grammar"} <= duong)

if _fails:
    raise SystemExit(f"\nFAIL - test_wake_model: {len(_fails)} lỗi: {_fails}")
print("\nOK - test_wake_model")
