"""Nhắc hẹn phải LÀM ĐƯỢC việc user đã hẹn, kèm cảnh báo lúc tạo.

    python tests/run.py nhac_hen_muc_quyen      (KHÔNG mạng, không spawn engine)

Chủ repo báo 2026-08-07 sau khi soát lại một loạt nhắc hẹn: ngày giờ đặt đúng hết, nhưng tới
giờ không có cái nào làm được việc, vì mức quyền bị ghim cứng ở chỉ-đọc. Nhóm tool hành động
ra ngoài (gửi tin, đăng bài, đặt lịch) bị hub xếp loại nguy hiểm nên ở mức đó agent không
những gọi không được mà còn KHÔNG NHÌN THẤY chúng, và prompt còn dặn thêm "tuyệt đối không gửi
tin ra ngoài". Kết cục: đúng giờ nó vẫn thức dậy, chạy, rồi báo về là không làm được - còn
việc thì vẫn chưa ai làm.

Chốt hướng (chủ repo, 2026-08-07): "Bỏ các quyền giúp anh, có cảnh báo là được."

Vì sao mặc định toàn quyền là ĐÚNG với nhắc hẹn mà không đúng với loop: loop tự nghĩ ra việc
để làm mỗi vòng, còn nhắc hẹn làm ĐÚNG một việc user đã viết ra và hẹn giờ - nó là một câu
lệnh trong chat được dời sang giờ khác. Trói nó chặt hơn lúc chat là tự mâu thuẫn.

Test này khoá bốn thứ: mặc định, ba mức dựng engine khác nhau thật, cảnh báo có tới tay user
không, và cảnh báo có viết TRUNG TÍNH không (không gắn với một ca dùng cụ thể nào).
"""
import asyncio
import os
import sys
import tempfile

from _paths import ROOT, SERVER  # noqa: E402,F401

_STATE = tempfile.mkdtemp(prefix="thansa-nhachen-")
os.environ.setdefault("THANSA_STATE_DIR", _STATE)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import reminders as R  # noqa: E402

_fails = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


# ---- 1. Mặc định và chuẩn hoá ----
check("mặc định là toàn quyền", R.MUC_QUYEN_MAC_DINH == "full")
check("ba mức, cùng bộ từ với loop",
      R.VALID_MUC_QUYEN == {"suggest", "auto", "full"})
check("bản ghi CŨ (chưa có trường này) chạy theo mặc định, không rơi vào chỉ-đọc",
      R.muc_quyen_cua({"id": "r_cu"}) == "full")
check("mức lạ trong file cũng quy về mặc định chứ không nổ",
      R.muc_quyen_cua({"muc_quyen": "linh tinh"}) == "full")
check("mức hợp lệ thì giữ nguyên",
      R.muc_quyen_cua({"muc_quyen": "suggest"}) == "suggest"
      and R.muc_quyen_cua({"muc_quyen": "auto"}) == "auto")


# ---- 2. Ba mức dựng engine KHÁC NHAU thật ----
# Đây là phần đáng canh nhất: nhãn trên thẻ đúng mà engine vẫn dựng như cũ thì lỗi y nguyên,
# chỉ khác là giờ nó im lặng.
class _CLI:
    def __init__(self, **kw):
        self.kw = kw
        self.max_wall_s = None
        self.mcp_config = None
        self.mcp_strict = False
        self.disallowed_tools = None

    def is_available(self):
        return True

    async def query(self, prompt):
        _GHI["prompt"] = prompt
        yield {"type": "final", "content": "xong"}


_GHI = {}


class _Deps:
    safe_tools = ["Read", "Write", "Edit"]
    readonly_tools = ["Read", "Glob", "Grep"]
    mcp_allow_patterns = staticmethod(lambda: ["mcp__thansa__*"])
    aux_swap = None
    aux_model = staticmethod(lambda: None)

    @staticmethod
    def brain_root(brain):
        return _STATE

    @staticmethod
    def build_system_prompt(brain):
        return "sysprompt"

    @staticmethod
    def apply_mcp(cli, mode="full", brain=None):
        _GHI["hub_mode"] = mode
        _GHI["hub_brain"] = brain


def _chay(muc_quyen):
    _GHI.clear()

    def _fake_engine(**kw):
        cli = _CLI(**kw)
        _GHI["allowed_tools"] = kw.get("allowed_tools")
        return cli

    that = R.claude_engine
    R.claude_engine = _fake_engine
    try:
        feat = R.RemindersFeature.__new__(R.RemindersFeature)
        feat.deps = _Deps()
        asyncio.run(feat._run_task("brain", "gửi link vào nhóm", muc_quyen))
    finally:
        R.claude_engine = that
    return dict(_GHI)


g = _chay("full")
check("toàn quyền: KHÔNG khoá allowlist (thấy được cả nhóm tool hành động ra ngoài)",
      g["allowed_tools"] is None)
check("toàn quyền: hub chạy ở mức full", g["hub_mode"] == "full")
check("toàn quyền: có truyền brain (plugin in-process cần biết vault nào)",
      g["hub_brain"] == "brain")
check("toàn quyền: prompt KHÔNG còn câu cấm gửi tin ra ngoài",
      "KHÔNG tạo đơn" not in g["prompt"] and "gửi tin ra ngoài" not in g["prompt"])
check("toàn quyền: prompt dặn đừng hỏi lại rồi ngồi đợi (không ai ngồi cạnh)",
      "không ai ngồi cạnh" in g["prompt"].lower() or "Không có ai ngồi cạnh" in g["prompt"])

g = _chay("auto")
check("ghi file: allowlist là bộ tool ghi được", "Write" in (g["allowed_tools"] or []))
check("ghi file: vẫn kèm pattern MCP để gọi được tool đọc",
      "mcp__thansa__*" in (g["allowed_tools"] or []))
check("ghi file: hub chạy ở mức auto", g["hub_mode"] == "auto")
check("ghi file: prompt vẫn cấm hành động ra ngoài",
      "KHÔNG tạo đơn" in g["prompt"] and "gửi tin ra ngoài" in g["prompt"])

g = _chay("suggest")
check("chỉ đọc: allowlist KHÔNG có tool ghi", "Write" not in (g["allowed_tools"] or []))
check("chỉ đọc: hub chạy ở mức suggest", g["hub_mode"] == "suggest")
check("chỉ đọc: prompt nói rõ không ghi file", "KHÔNG ghi file" in g["prompt"])

g = _chay("")     # mức rỗng -> mặc định
check("không nói mức thì chạy theo mặc định (toàn quyền)",
      g["allowed_tools"] is None and g["hub_mode"] == "full")


# ---- 3. Cảnh báo phải tới tay user ----
NOTE = R.CANH_BAO_TOAN_QUYEN
check("cảnh báo nói rõ nó chạy MỘT MÌNH", "MỘT MÌNH" in NOTE)
check("cảnh báo nói rõ không ai duyệt lại", "không có ai duyệt lại" in NOTE)
check("cảnh báo nói rõ phần lớn không rút lại được", "không rút lại được" in NOTE)
check("cảnh báo chỉ luôn lối hạ mức", "chỉ đọc" in NOTE)
check("cảnh báo không dùng em dash (luật CLAUDE.md)", "—" not in NOTE)

# TRUNG TÍNH: chủ repo dặn "đừng chỉ dựa vào casestudy của anh để viết cảnh báo" - đây là tool
# cho mọi người dùng, mỗi người đấu một bộ công cụ khác nhau.
for rieng in ("Zalo", "zalo", "Telegram", "nhóm 136", "chứng khoán", "POS", "Pancake"):
    check(f"cảnh báo không gắn với ca dùng riêng: {rieng!r}", rieng not in NOTE)

SRC = (SERVER / "reminders.py").read_text(encoding="utf-8")
check("endpoint tạo trả kèm canh_bao", '"canh_bao"' in SRC)
check("chỉ cảnh báo đúng ca đáng cảnh báo (task + toàn quyền)",
      'rem["mode"] == "task" and rem.get("muc_quyen") == "full"' in SRC)

PLUGIN = (ROOT / "system" / "plugins" / "thansa-schedule" / "plugin.py").read_text(encoding="utf-8")
check("tool thansa_schedule đọc lại cảnh báo cho user", 'data.get("canh_bao")' in PLUGIN)
check("tool dặn model đừng nuốt cảnh báo", "đừng nuốt" in PLUGIN)
check("tool nhận tham số muc_quyen", '"muc_quyen"' in PLUGIN)

CLAUDEMD = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
check("CLAUDE.md dặn đọc lại nguyên văn cảnh báo",
      "read it back VERBATIM" in CLAUDEMD and "muc_quyen" in CLAUDEMD)


# ---- 4. Giao diện: mức quyền phải hiện ra, và cảnh báo phải nổi (Thansa P038 giữ chốt an toàn) ----
# 0.426.0: reminders/loops are added and edited on the Tasks page (dashboard/tasks.js); console.js keeps no old form.
JS = (ROOT / "dashboard" / "tasks.js").read_text(encoding="utf-8")
check("chi tiết nhắc hẹn và loop hiện mức quyền", 'kv(tw("nv.lp.mode"), \'<span class="nv-lvl\'' in JS and "((it.raw || {}).muc_quyen || \"full\")" in JS)
check("form có ô chọn mức quyền", 'data-k="mq"' in JS)
check("lời nhắc mới mặc định toàn quyền trên form", 'var lv = f.mq || "full";' in JS)
check("ô mức quyền chỉ hiện với kiểu tự-làm", '(f.mode === "do" ? \'<div class="nv-fld"><span>\' + esc(tw("nv.lp.mode"))' in JS)
check("form gửi muc_quyen lên server khi tạo và khi sửa",
      'muc_quyen: f.mq || "full", call: !!f.call' in JS and 'muc_quyen: f.mq || "full",\n' in JS)
check("form hiện hộp cảnh báo đỏ khi chọn toàn quyền", 'lv === "full" ? fullWarn("reminder")' in JS and 'f.lmode === "full" ? fullWarn("loop")' in JS)
check("loop thiếu mức thì về suggest, không phải toàn quyền", 'lmode: lp.mode || "suggest"' in JS and 'mode: f.lmode || "suggest"' in JS)
check("lưu loop toàn quyền phải confirm()", 'f.lmode === "full" && !window.confirm(tw("cs.si_full_confirm"' in JS)
check("bật loop toàn quyền phải confirm()", '(r.raw || {}).mode === "full" && !window.confirm(tw("cs.si_toggle_confirm"' in JS)

if _fails:
    raise SystemExit(f"\nFAIL - test_nhac_hen_muc_quyen: {len(_fails)} lỗi: {_fails}")
print("\nOK - test_nhac_hen_muc_quyen: tất cả pass")
