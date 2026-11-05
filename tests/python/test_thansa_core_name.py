"""Thansa Core's own name and style in one brain (owner, 04/11/2026: "add a button so people can rename Thansa Core, and on
the first chat it asks for its name, keeps a style that suits the user and learns, instead of always Thansa Core").

    python tests/run.py thansa_core_name

No network, no model.
- identity(): empty by default; set_identity() cleans the name (one line, no long dashes, 40 characters) and saves it
  in <brain>/Thansa/core.json, one file per brain.
- The role block: no name and never asked = ask once and call op=asked; asked = no asking again; a name = speak as it.
- The agent editor (POST /agents) renames it for that brain only; GET /agents?system=1 shows the name, keeps the slug.
- The chat tool `thansa_core_name` (bundled plugin) writes the same file, owner only.
- The agent routes still refuse to delete or edit Thansa Core, and no longer say it cannot be renamed.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

os.environ["THANSA_STATE_DIR"] = tempfile.mkdtemp(prefix="thansa-core-name-")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

fails = []


def check(name, cond, extra=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  [{str(extra)[:300]}]" if extra and not cond else ""))
    if not cond:
        fails.append(name)


import thansa_core  # noqa: E402

# ---- 1. the identity file ----
A = Path(tempfile.mkdtemp(prefix="core-name-a-"))
B = Path(tempfile.mkdtemp(prefix="core-name-b-"))
check("no name by default", thansa_core.identity(A) == {"name": "", "style": "", "asked": False})
check("...so it is still called Thansa Core", thansa_core.display_name(A) == "Thansa Core")
me = thansa_core.set_identity(A, name="  Mây " + chr(0x2014) + " bé\n xinh  ")
check("the name is cleaned: one line, no long dash, spaces collapsed", me["name"] == "Mây bé xinh", me)
check("a name counts as asked", me["asked"] is True)
check("saved as the name in the brain's own Thansa Core agent file",
      thansa_core._read_file(A / "agents" / "thansa-core.md")[0].get("name") == "Mây bé xinh")
check("another brain keeps its own (none)", thansa_core.identity(B)["name"] == "")
check("40 characters at most", len(thansa_core.set_identity(B, name="x" * 99)["name"]) == 40)
thansa_core.set_identity(B, name="")
check("an empty name goes back to Thansa Core", thansa_core.display_name(B) == "Thansa Core")
thansa_core.set_identity(A, style="thân thiện, ngắn gọn")
check("style is kept apart from the name", thansa_core.identity(A)["name"] == "Mây bé xinh"
      and thansa_core.identity(A)["style"] == "thân thiện, ngắn gọn")

# ---- 2. what the role block tells the model ----
C = Path(tempfile.mkdtemp(prefix="core-name-c-"))
blk = thansa_core.prompt_block(C)
check("no name, never asked: ask once and record it", "CHƯA có tên riêng" in blk and "op=asked" in blk)
thansa_core.set_identity(C, asked=True)
blk = thansa_core.prompt_block(C)
check("asked already: no asking again", "op=asked" not in blk and "chưa có tên riêng" in blk)
blk = thansa_core.prompt_block(A)
check("named: speaks as that name, with the agreed style",
      "**Mây bé xinh**" in blk and "thân thiện, ngắn gọn" in blk and "op=asked" not in blk)
check("without a brain the block is the plain role block", thansa_core.prompt_block() == thansa_core.prompt_block(None)
      and "tên riêng" not in thansa_core.prompt_block().split("# === THANSA CORE ===")[-1].split("Tên và phong cách")[0])
check("the block stays small with a name and a style", len(thansa_core.prompt_block(A)) < 3000, len(thansa_core.prompt_block(A)))
check("the role body tells it to fit its style to the user and save it with the tool",
      "thansa_core_name" in thansa_core.definition()["body"] and "style" in thansa_core.definition()["body"])

# ---- 3. the server: rename button and the Partners list ----
import config as cfgmod  # noqa: E402
import main  # noqa: E402
import mcp_hub  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

if os.environ["THANSA_STATE_DIR"] not in str(cfgmod.STATE_DIR):
    print(f"FAIL state dir is not the temp dir: {cfgmod.STATE_DIR}. STOP.")
    sys.exit(1)

client = TestClient(main.app, base_url="http://127.0.0.1:8080")


def localefmt_en(resp):
    """The same refusal in English, whatever language the server picked for this request."""
    return "edited like any" if "sửa như một trợ lý thường" in resp.json().get("error", "") else ""
D = Path(tempfile.mkdtemp(prefix="core-name-d-"))
(D / "agents").mkdir()
r = client.post("/agents", data={"slug": "thansa-core", "name": "Sky", "role": "", "prompt": "x", "brain": str(D)})
check("the agent editor renames it", r.status_code == 200 and thansa_core.identity(D)["name"] == "Sky", r.text)
ds = client.get("/agents", params={"brain": str(D), "prompt": 0, "system": 1}).json()["agents"]
core = ds[0]
check("the Partners list shows the new name, same slug and system flags",
      core["slug"] == "thansa-core" and core["name"] == "Sky" and core["custom_name"] == "Sky"
      and core["system_name"] == "Thansa Core" and core["system"] is True, core)
sid = main.get_store().create_session(brain=main._brain_key(str(D)), channel=thansa_core.CHANNEL)
check("a Core chat of that brain is told its name", "**Sky**" in main._thansa_core_block(sid))
thansa_core.set_identity(D, name="")
check("an empty name goes back to Thansa Core", thansa_core.display_name(D) == "Thansa Core"
      and client.get("/agents", params={"brain": str(D), "prompt": 0, "system": 1}).json()["agents"][0]["custom_name"] == "")
r = client.post("/agents/delete", data={"slug": "thansa-core", "brain": str(D)})
check("deleting it is still refused", r.status_code == 403)
check("...and the refusal no longer says it cannot be renamed or edited", "renamed" not in r.json().get("error", "")
      and "edited like any" in r.json().get("error", "") + localefmt_en(r), r.text)

# ---- 4. the chat tool ----
check("the tool is the owner's only (a customer bot never renames the owner's assistant)",
      "thansa_core_name" in mcp_hub.OWNER_ONLY_TOOLS)
yml = (ROOT / "system/plugins/thansa-core-name/plugin.yaml").read_text(encoding="utf-8")
check("the plugin ships enabled at the safe level",
      "slug: thansa-core-name" in yml and "enabled: true" in yml and "min_mode: safe" in yml and "thansa_core_name" in yml)
spec = importlib.util.spec_from_file_location("thansa_core_name_plugin", ROOT / "system/plugins/thansa-core-name/plugin.py")
plug = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plug)
reg = {}


class _Reg:
    def register_tool(self, name, desc, fn, **kw):
        reg[name] = fn


plug.register(_Reg())
run = reg["thansa_core_name"]


class _Ctx:
    vault_root = str(Path(tempfile.mkdtemp(prefix="core-name-e-")))


ctx = _Ctx()
check("op=get with no name", "chưa đặt" in run({"op": "get"}, ctx))
run({"op": "asked"}, ctx)
check("op=asked records it", thansa_core.identity(ctx.vault_root)["asked"] is True)
out = run({"op": "set", "name": "Bé Na", "style": "vui vẻ"}, ctx)
check("op=set saves name and style", thansa_core.identity(ctx.vault_root)["name"] == "Bé Na"
      and thansa_core.identity(ctx.vault_root)["style"] == "vui vẻ" and "Bé Na" in out, out)
check("op=set with nothing to set is an error", run({"op": "set"}, ctx).startswith("ERROR"))
run({"op": "reset"}, ctx)
check("op=reset goes back to Thansa Core", thansa_core.identity(ctx.vault_root)["name"] == ""
      and thansa_core.identity(ctx.vault_root)["style"] == "")
check("no brain: refused, nothing written", run({"op": "set", "name": "X"}, type("C", (), {"vault_root": ""})()).startswith("ERROR"))

# ---- 5. the card ----
dashes = [chr(0x2014), chr(0x2013)]
for f in (Path(__file__), ROOT / "system/plugins/thansa-core-name/plugin.py", ROOT / "system/plugins/thansa-core-name/plugin.yaml",
          ROOT / "server/thansa_core.py", ROOT / "system/agents/thansa-core.md"):
    check(f"no em or en dash in {f.name}", not any(d in f.read_text(encoding="utf-8") for d in dashes))

print()
if fails:
    raise SystemExit(f"FAIL {len(fails)}: " + "; ".join(fails[:6]))
print("ALL PASS")
