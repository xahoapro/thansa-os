"""Azure Speech (Thansa 2.4.x): TUỲ CHỌN cùng giọng Edge qua dịch vụ chính thức, lỗi thì lùi về Edge.

Chủ chốt 04/11: mặc định vẫn Edge miễn phí; Azure chỉ chạy khi người dùng chọn nhóm "Azure Speech" (tts_provider=azure).

Edge miễn phí bỏ âm thanh ngẫu nhiên với giọng vi-VN, nên câu trả lời lúc HoaiMy lúc giọng dự phòng. Có khoá +
vùng Azure Speech thì /tts đọc giọng Edge đã chọn qua Azure; Azure lỗi (hết hạn mức, sai khoá, mạng) thì vẫn đọc
bằng Edge như cũ, không bao giờ im lặng.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ["THANSA_STATE_DIR"] = tempfile.mkdtemp(prefix="thansa-azure-")
sys.path.insert(0, str(ROOT / "server"))

_fails = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _fails.append(name)


import config as cfgmod  # noqa: E402
import main  # noqa: E402

goi = {"azure": [], "edge": []}
CFG = {"voice": {"tts_provider": "azure", "azure_speech_key": "k-thu", "azure_speech_region": "southeastasia"}}
AZ_HONG = {"on": False}


async def fake_azure(text, voice, rate, cfg):
    goi["azure"].append((text, voice))
    if AZ_HONG["on"]:
        raise RuntimeError("401 Unauthorized")
    return b"mp3-azure"


async def fake_edge(text, voice, rate):
    goi["edge"].append((text, voice))

    async def gen():
        yield b"mp3-edge"
    return b"mp3-edge", gen()


main._tts_azure = fake_azure
main._tts_edge_stream = fake_edge


def doc(cfg, voice="vi-VN-HoaiMyNeural"):
    cfgmod.read_settings = lambda: cfg
    main.cfgmod.read_settings = lambda: cfg
    goi["azure"].clear(); goi["edge"].clear()
    r = asyncio.run(main.tts(text="Xin chào, tôi là Thansa", voice=voice, rate="+0%"))
    return r


r = doc(CFG)
check("chọn Azure + có khoá: giọng đọc qua Azure", goi["azure"] and not goi["edge"] and r.body == b"mp3-azure")
check("Azure nhận đúng giọng đã chọn và chữ đã phiên âm", goi["azure"][0][1] == "vi-VN-HoaiMyNeural"
      and "than sa" in goi["azure"][0][0].lower())

AZ_HONG["on"] = True
r = doc(CFG)
check("Azure lỗi: lùi về Edge, không im lặng", goi["azure"] and goi["edge"] and type(r).__name__ == "StreamingResponse")
AZ_HONG["on"] = False

r = doc({"voice": {"tts_provider": "edge"}})
check("mặc định Edge: đi thẳng Edge, không gọi Azure", not goi["azure"] and goi["edge"])

r = doc({"voice": {"tts_provider": "edge", "azure_speech_key": "k-thu", "azure_speech_region": "southeastasia"}})
check("CÓ khoá Azure nhưng vẫn chọn Edge: KHÔNG tự sang Azure (Azure là tuỳ chọn)", not goi["azure"] and goi["edge"])

AZ_HONG["on"] = True
r = doc({"voice": {"tts_provider": "azure"}})
check("chọn Azure mà chưa có khoá: vẫn đọc bằng Edge", goi["edge"] and type(r).__name__ == "StreamingResponse")
AZ_HONG["on"] = False
check("mặc định của cài đặt mới là Edge", cfgmod.DEFAULTS["voice"]["tts_provider"] == "edge" if hasattr(cfgmod, "DEFAULTS") else '"tts_provider": "edge"' in (ROOT / "server/config.py").read_text())

check("khoá Azure là secret (mã hoá khi lưu)", "voice.azure_speech_key" in cfgmod.SECRET_FIELDS
      if hasattr(cfgmod, "SECRET_FIELDS") else "voice.azure_speech_key" in (ROOT / "server/config.py").read_text())
check("có route thử khoá /voice/azure/check", any(getattr(x, "path", "") == "/voice/azure/check" for x in main.app.routes))

if _fails:
    raise SystemExit(f"\nFAIL - test_tts_azure: {len(_fails)} lỗi: {_fails}")
print("\nOK - test_tts_azure")
