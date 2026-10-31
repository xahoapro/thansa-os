// 0.275.0 (customer report, codes 15 and 27): Full stays the default level for background work (owner, 2026-10-22),
// but the Add-work form says in one line what the picked level may do, and javis_schedule tells the model to say it.
//
//     node tests/js/test_level_note_0275.js
"use strict";
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..", "..");
// 0.426.0: the forms moved to the Tasks page (dashboard/tasks.js): the loop edit form and the reminder options.
const cs = fs.readFileSync(path.join(root, "dashboard", "tasks.js"), "utf8");
const plug = fs.readFileSync(path.join(root, "system", "plugins", "javis-schedule", "plugin.py"), "utf8");
const vi = JSON.parse(fs.readFileSync(path.join(root, "dashboard", "i18n", "vi.json"), "utf8"));
const en = JSON.parse(fs.readFileSync(path.join(root, "dashboard", "i18n", "en.json"), "utf8"));
let fails = 0;
function check(name, cond) { console.log((cond ? "ok   " : "FAIL ") + name); if (!cond) fails++; }

// Thansa P038 (chủ giữ chốt an toàn): loop mặc định Suggest, nhắc hẹn tự-làm vẫn Full.
check("defaults: loops Suggest, task reminders Full",
  /lmode: lp\.mode \|\| "suggest"/.test(cs) && /var lv = f\.mq \|\| "full";/.test(cs) && /muc_quyen: f\.mq \|\| "full"/.test(cs)
  && /mode: suggest\\n/.test(plug));
check("a note sits under both level rows", (cs.match(/class="nv-hint/g) || []).length === 2);
check("the note follows the picked level in both forms",
  /tw\(LP_NOTE\[f\.lmode\] \|\| LP_NOTE\.suggest\)/.test(cs) && /tw\(LP_NOTE\[lv\]\)/.test(cs)
  && /LP_NOTE = \{ suggest: "cs\.si_level_note_suggest", auto: "cs\.si_level_note_auto", full: "cs\.si_level_note_full" \}/.test(cs));
const keys = ["cs.si_level_note_full", "cs.si_level_note_auto", "cs.si_level_note_suggest"];
check("notes in vi and en, one short line each (no (i) needed)",
  keys.every(k => vi[k] && en[k] && vi[k].length <= 100 && en[k].length <= 100));
check("the Full note says it edits files and acts outside without asking",
  /sửa file/.test(vi["cs.si_level_note_full"]) && /không hỏi lại/.test(vi["cs.si_level_note_full"]));
// Thansa P038: loop qua chat luôn suggest nên chỉ nhắc hẹn mức Full cần câu giải thích.
check("javis_schedule asks the model to explain a Full reminder job in plain words",
  /FULL_LEVEL_NOTE if mq == "full"/.test(plug));
check("no em or en dash", [cs, plug].every(t => t.indexOf(String.fromCharCode(0x2014)) < 0 && t.indexOf(String.fromCharCode(0x2013)) < 0));
process.exit(fails ? 1 : 0);
