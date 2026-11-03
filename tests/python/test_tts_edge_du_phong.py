"""Edge TTS: giọng gốc không trả audio thì đọc bằng giọng đa ngôn ngữ cùng giới (Thansa 2.1.1, 03/11/2026).

Dịch vụ Edge lúc này hay đóng lượt KHÔNG kèm âm thanh với giọng vi-VN (NoAudioReceived), người dùng chỉ thấy báo
lỗi cài đặt giọng nói. _tts_edge_stream phải thử lần lượt giọng gốc rồi 2 giọng đa ngôn ngữ, hỏng hết mới báo lỗi.
"""
import asyncio
import os
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ["THANSA_STATE_DIR"] = tempfile.mkdtemp(prefix="thansa-tts-")
sys.path.insert(0, str(ROOT / "server"))

_fails = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _fails.append(name)


goi = []
HONG = set()


class NoAudioReceived(Exception):
    pass


class Communicate:
    def __init__(self, text, voice, rate="+0%"):
        self.voice = voice
        goi.append(voice)

    async def stream(self):
        if self.voice in HONG:
            raise NoAudioReceived("No audio was received.")
        yield {"type": "audio", "data": b"mp3-" + self.voice.encode()}
        yield {"type": "audio", "data": b"-tiep"}


sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=Communicate, NoAudioReceived=NoAudioReceived)
import main  # noqa: E402


async def doc(voice):
    first, gen = await main._tts_edge_stream("Xin chào, bạn", voice, "+0%")
    return b"".join([c async for c in gen])


# giọng gốc chạy được: không đụng giọng dự phòng
goi.clear(); HONG.clear()
out = asyncio.run(doc("vi-VN-HoaiMyNeural"))
check("giọng gốc chạy được thì dùng đúng nó", goi == ["vi-VN-HoaiMyNeural"] and out.startswith(b"mp3-vi-VN-HoaiMy"))

# giọng nữ hỏng -> thử lại chính nó 1 lần (Edge hỏng ngẫu nhiên) -> giọng nữ đa ngôn ngữ
goi.clear(); HONG.clear(); HONG.add("vi-VN-HoaiMyNeural")
out = asyncio.run(doc("vi-VN-HoaiMyNeural"))
check("HoaiMy hỏng -> thử lại 1 lần -> Emma đa ngôn ngữ", goi == ["vi-VN-HoaiMyNeural", "vi-VN-HoaiMyNeural", "en-US-EmmaMultilingualNeural"]
      and out == b"mp3-en-US-EmmaMultilingualNeural-tiep")

# hỏng lần đầu, thử lại thì được: vẫn là giọng tiếng Việt đã chọn
class _MotLanHong(Communicate):
    dem = 0
    async def stream(self):
        _MotLanHong.dem += 1
        if _MotLanHong.dem == 1:
            raise NoAudioReceived("No audio was received.")
        yield {"type": "audio", "data": b"mp3-" + self.voice.encode()}
sys.modules["edge_tts"].Communicate = _MotLanHong
goi.clear(); HONG.clear()
out = asyncio.run(doc("vi-VN-NamMinhNeural"))
check("NamMinh hỏng 1 lần, thử lại được -> vẫn NamMinh", goi == ["vi-VN-NamMinhNeural", "vi-VN-NamMinhNeural"] and b"NamMinh" in out)
sys.modules["edge_tts"].Communicate = Communicate

# giọng nam hỏng -> giọng nam đa ngôn ngữ, hỏng tiếp -> giọng nam thứ hai
goi.clear(); HONG.clear(); HONG.update({"vi-VN-NamMinhNeural", "en-US-AndrewMultilingualNeural"})
out = asyncio.run(doc("vi-VN-NamMinhNeural"))
check("NamMinh hỏng, Andrew hỏng -> Brian", goi[-1] == "en-US-BrianMultilingualNeural" and b"Brian" in out)

# hỏng hết -> lỗi thật để client rơi về đường dự phòng của nó
goi.clear(); HONG.clear(); HONG.update({"vi-VN-HoaiMyNeural", "en-US-EmmaMultilingualNeural", "en-US-AvaMultilingualNeural"})
try:
    asyncio.run(doc("vi-VN-HoaiMyNeural"))
    check("hỏng hết thì báo lỗi", False)
except RuntimeError as e:
    check("hỏng hết thì báo lỗi (nêu lý do)", "NoAudioReceived" in str(e) and len(goi) == 4)

check("requirements đòi edge-tts >= 7.3.1 (7.2.x bị 403)", "edge-tts>=7.3.1" in (ROOT / "requirements.txt").read_text())

if _fails:
    raise SystemExit(f"\nFAIL - test_tts_edge_du_phong: {len(_fails)} lỗi: {_fails}")
print("\nOK - test_tts_edge_du_phong")
