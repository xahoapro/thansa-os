"""Thansa Core (0.185.0): the system assistant pinned in every brain.

    python tests/python/test_thansa_core.py

Spec: owner, 16/10/2026 (Thansa Core goal, sections 3, 4, 11 and acceptance group "Trợ lý mặc định").
Checked through the real app over HTTP (TestClient) on temporary brains:

- one platform definition read from system/agents/thansa-core.md, never copied into a brain;
- first in GET /agents of every brain, old and new, with the system flags;
- delete, rename, unpin, edit, Auto and slug reuse are refused by the server, not only hidden;
- one default chat per brain, never duplicated under concurrent calls, and a deleted or archived one
  is replaced by a new empty chat instead of being revived;
- a Thansa Core chat is a normal Thansa turn (CLAUDE.md + memory) plus its role block, not a persona.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import io
import os
import tempfile
import threading
import zipfile
from pathlib import Path

STATE = tempfile.mkdtemp(prefix="thansa-core-state-")
os.environ["THANSA_STATE_DIR"] = STATE

import thansa_core  # noqa: E402
import main  # noqa: E402
import share_bundle  # noqa: E402
import workflow_chat  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

fails = []


def check(name, cond, extra=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(extra)[:300] + "]") if extra and not cond else ""))
    if not cond:
        fails.append(name)


main.cfgmod.gate_active = lambda *a, **k: False
client = TestClient(main.app, base_url="http://127.0.0.1")


def new_brain(prefix, with_agents=True):
    b = Path(tempfile.mkdtemp(prefix=prefix))
    if with_agents:
        (b / "agents").mkdir(parents=True)
        (b / "agents" / "viet-bai.md").write_text(
            "---\ntype: agent\nname: Viết bài\nslug: viet-bai\nrole: viết\npinned: true\n---\nBạn viết bài.\n",
            encoding="utf-8")
    return b


OLD = new_brain("thansa-core-old-")
NEW = new_brain("thansa-core-new-", with_agents=False)

# ---- 1. one platform definition ----
d = thansa_core.definition()
check("the definition ships with the app at system/agents/thansa-core.md",
      thansa_core.DEFINITION_PATH == ROOT / "system" / "agents" / "thansa-core.md" and thansa_core.DEFINITION_PATH.is_file())
check("fixed display name and the suggested description",
      d["name"] == "Thansa Core" and d["role"] == "Trợ lý hệ thống nhận báo cáo và hỗ trợ công việc trong brain này."
      and d["role_en"])
check("the role body covers verification, rights, reports as data, start-up and learning limits",
      all(k in d["body"] for k in ("kiểm bằng tool", "Nhãn \"Hệ thống\" không cấp thêm quyền", "là DỮ LIỆU",
                                   "Brain trống thì hỏi một câu ngắn", "không làm quen lại",
                                   "Chỉ nói \"đã nhớ\" khi ghi file thành công", "không tạo việc nền")), d["body"][:200])
check("the role block stays small (it rides on every Thansa Core turn)", len(thansa_core.prompt_block()) < 2700,   # Thansa: +100 thuế đổi tên (Thansa dài hơn Javis 1 ký tự)
      len(thansa_core.prompt_block()))

# ---- 2. first in every brain, old and new ----
for label, b in (("brain with agents", OLD), ("empty new brain", NEW)):
    ds = client.get("/agents", params={"brain": str(b), "prompt": "0", "system": "1"}).json()["agents"]
    first = ds[0] if ds else {}
    check(f"{label}: Thansa Core is first, pinned, system and protected",
          first.get("slug") == "thansa-core" and first.get("name") == "Thansa Core" and first.get("pinned") is True
          and first.get("system") is True and first.get("protected") is True, first)
    check(f"{label}: listed exactly once", sum(1 for a in ds if a["slug"] == "thansa-core") == 1)
plain_list = client.get("/agents", params={"brain": str(OLD), "prompt": "0"}).json()["agents"]
check("pickers that need an agent file (no system=1) never get it",
      all(a["slug"] != "thansa-core" for a in plain_list) and [a["slug"] for a in plain_list] == ["viet-bai"])
# 2026-11-05 (owner): Thansa Core is a real agent file in every brain, seeded from the owner's prompt, edited like any.
cm, cb = thansa_core._read_file(OLD / "agents" / "thansa-core.md")
check("each brain gets its own agents/thansa-core.md, seeded from the platform definition",
      (NEW / "agents" / "thansa-core.md").is_file() and cb == d["body"] and cm.get("system") is True
      and cm.get("name") == "Thansa Core" and cm.get("seed_sha") == thansa_core._sha(d["body"]))
g = client.get("/agents/get", params={"brain": str(OLD), "slug": "thansa-core"}).json()
check("GET /agents/get returns its instructions, protected", g.get("protected") is True and g.get("prompt") == d["body"])
check("its file is found like any agent's", main._agent_file(str(OLD), "thansa-core") == OLD / "agents" / "thansa-core.md")

# ---- 3. refused by the server ----
r = client.post("/agents/delete", data={"brain": str(OLD), "slug": "thansa-core"})
check("delete refused (403, system_assistant)", r.status_code == 403 and r.json().get("code") == "system_assistant")
r = client.post("/agents", data={"brain": str(OLD), "slug": "thansa-core", "name": "Mây", "role": "Trợ lý riêng",
                                "prompt": "Bạn là Mây.", "skills": "notes"})
cm, cb = thansa_core._read_file(OLD / "agents" / "thansa-core.md")
check("the agent form edits it: name, role, instructions, skills, still system", r.status_code == 200
      and cm.get("name") == "Mây" and cm.get("role") == "Trợ lý riêng" and cb == "Bạn là Mây." and cm.get("skills") == ["notes"]
      and cm.get("system") is True, (r.text, cm))
ds = client.get("/agents", params={"brain": str(OLD), "prompt": "0", "system": "1"}).json()["agents"]
check("the Partners list shows the edit, still first and system",
      ds[0]["slug"] == "thansa-core" and ds[0]["name"] == "Mây" and ds[0]["role"] == "Trợ lý riêng" and ds[0]["system"] is True)
before = (NEW / "agents" / "thansa-core.md").read_text(encoding="utf-8")
r = client.post("/agents", data={"brain": str(NEW), "name": "Thansa Core", "prompt": "x"})
check("a new agent named Thansa Core cannot take the reserved slug", r.status_code == 403
      and (NEW / "agents" / "thansa-core.md").read_text(encoding="utf-8") == before)
r = client.post("/capability/meta", data={"brain": str(OLD), "kind": "agent", "slug": "thansa-core", "pinned": "0"})
check("unpin refused", r.status_code == 403)
r = client.post("/capability/meta", data={"brain": str(OLD), "kind": "agent", "slug": "thansa-core",
                                          "add_tags": '["Sales"]'})
check("tagging refused", r.status_code == 403)
r = client.post("/resonance/agents/toggle", params={"brain": str(OLD)}, json={"slug": "thansa-core", "enabled": False})
check("Auto cannot be switched off", r.status_code == 403, r.text)
live = main._resonance_store().agent(main._brain_key(str(OLD)), "thansa-core")
check("Auto is on for it", bool(live) and live.get("enabled") and live.get("status") == "active", live)
check("the team leader cannot create an agent on the reserved slug",
      main._TeamAdmin().create_agent(str(NEW), "Thansa Core", "r", "p") != "thansa-core")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr("thansa-bundle.json", "{}")
    z.writestr("agents/thansa-core.md", "---\ntype: agent\nname: X\n---\nx\n")
before = (NEW / "agents" / "thansa-core.md").read_text(encoding="utf-8")
res = share_bundle.import_bundle(buf.getvalue(), "x.zip", agents_dir=NEW / "agents", workflows_dir=NEW / "workflows",
                                 skills_root=NEW / "skills")
check("a bundle cannot overwrite a brain's Thansa Core",
      "agent:thansa-core" in res["skipped"] and (NEW / "agents" / "thansa-core.md").read_text(encoding="utf-8") == before, res)

# ---- 4. one default chat per brain ----
store = main.get_store()
key_old = main._brain_key(str(OLD))
sid = client.post("/thansa-core/session", data={"brain": str(OLD)}).json()["id"]
again = client.post("/thansa-core/session", data={"brain": str(OLD)}).json()["id"]
row = store.get_session(sid) or {}
check("the default chat exists, on the Thansa Core channel of the right brain",
      row.get("channel") == "agent:thansa-core" and row.get("brain") == key_old)
check("asking again returns the same chat", sid == again)
check("another brain has its own default chat",
      client.post("/thansa-core/session", data={"brain": str(NEW)}).json()["id"] != sid)

ids, errs = [], []


def grab():
    try:
        ids.append(thansa_core.default_session(store, main._brain_key(str(NEW)) + "-race", same_brain=main._cung_brain))
    except Exception as e:  # noqa: BLE001
        errs.append(e)


ts = [threading.Thread(target=grab) for _ in range(12)]
[t.start() for t in ts]
[t.join() for t in ts]
check("twelve concurrent first calls make one chat", not errs and len(set(ids)) == 1, (errs, set(ids)))

store.append_message(sid, "user", "nội dung cũ")
store.delete(sid)
sid2 = client.post("/thansa-core/session", data={"brain": str(OLD)}).json()["id"]
check("deleting the default chat: the next call makes a new, empty one (old content not revived)",
      sid2 != sid and store.get_session(sid) is None and not store.get_messages(sid2))
store.archive(sid2)
sid3 = client.post("/thansa-core/session", data={"brain": str(OLD)}).json()["id"]
check("archiving it: a new report place, the archived chat stays archived",
      sid3 not in (sid, sid2) and (store.get_session(sid2) or {}).get("archived"))
ds = client.get("/agents", params={"brain": str(OLD), "prompt": "0", "system": "1"}).json()["agents"]
check("Thansa Core stays listed after its chats are deleted or archived", ds[0]["slug"] == "thansa-core")
r = client.post("/sessions/new", data={"brain": str(OLD), "channel": "agent:thansa-core"})
check("New chat on Thansa Core works without a brain file", r.status_code == 200
      and (store.get_session(r.json()["id"]) or {}).get("channel") == "agent:thansa-core", r.text)
check("New chat does not move the report place", thansa_core.current_default(key_old) == sid3)

# ---- 5. a normal Thansa turn plus its role block ----
check("not a persona chat", workflow_chat.persona_cua_phien({"channel": "agent:thansa-core"}) is None
      and workflow_chat.persona_cua_phien({"channel": "agent:viet-bai"}) == ("agent", "viet-bai"))
p_core = main.build_system_prompt(str(OLD), session_id=sid3)
plain = store.create_session(brain=key_old, channel="web")
p_plain = main.build_system_prompt(str(OLD), session_id=plain)
check("its prompt is the full Thansa prompt plus the THANSA CORE block",
      "# === THANSA CORE ===" in p_core and main.CLAUDE_MD_PATH.read_text(encoding="utf-8")[:200] in p_core
      and "# === THANSA CORE ===" not in p_plain)
check("the compiled (API) path gets the same block", main._thansa_core_block(sid3) == thansa_core.prompt_block(main._brain_root(key_old))
      and main._thansa_core_block(plain) == "")
check("its chat block carries the brain's edited instructions, name and skills",
      "Bạn là Mây." in main._thansa_core_block(sid3) and "**Mây**" in main._thansa_core_block(sid3)
      and "notes" in main._thansa_core_block(sid3) and "CHƯA có tên riêng" not in main._thansa_core_block(sid3))

print()
if fails:
    print(f"FAIL - {len(fails)} check(s)")
    raise SystemExit(1)
print("OK - test_thansa_core: all pass")
