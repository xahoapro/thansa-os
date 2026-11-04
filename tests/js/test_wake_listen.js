// Lắng nghe ngầm (Thansa 2.5.0, chủ chốt 04/11/2026): dò từ khoá để gọi / thôi nghe; cách dò mặc định Trên máy.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "../..");
const M = require(path.join(ROOT, "dashboard/wake-match.js"));

const ON = ["thần sa", "than sa", "mở mic", "bật mic", "bật nghe", "nghe lệnh"];
const OFF = ["tắt mic", "tắt nghe", "thôi nghe"];
const m = M.tao({ on: ON, off: OFF });

// ---- 1. Từ khoá gọi / tắt
for (const c of ["Thần Sa ơi", "thần sa, mở lịch giúp tôi", "Bật mic", "mở mic", "nghe lệnh", "Than sa"]) assert.strictEqual(m.match(c), "on", c);
for (const c of ["tắt mic", "Thôi nghe nhé", "Thần Sa tắt mic"]) assert.strictEqual(m.match(c), "off", c);
// ---- 2. Câu thường / nửa chữ không gọi
for (const c of ["", "hôm nay trời đẹp quá", "micro hỏng rồi", "tôi đi chợ", "mở micro"]) assert.strictEqual(m.match(c), null, c);
// ---- 3. Độ tin cậy (Vosk): câu lạ bị ép thành từ khoá có tin cậy thấp -> bỏ
assert.strictEqual(m.match("thần nghe lệnh", [0.81, 0.41, 0.58]), null, "câu bị ép, tin cậy thấp");
assert.strictEqual(m.match("tắt mic", [0.7, 1.0]), "off", "từ khoá thật, tin cậy đủ");
assert.strictEqual(m.match("thần sa", [1, 1]), "on");
// Đo trong trình duyệt thật 04/11: "Thần Sa, mở lịch giúp tôi" -> Vosk "thần sa mở mic thôi" [0.98,1,1,0.58,0.99].
// Chỉ xét tin cậy trên chính từ khoá: "thần sa" đủ -> gọi; "mở mic" có "mic" 0,58 -> không tính là từ khoá đó.
assert.strictEqual(m.match("thần sa mở mic thôi", [0.98, 1, 1, 0.58, 0.99]), "on");
assert.strictEqual(m.match("mở mic", [1, 0.58]), null);
// ---- 4. Tắt hẳn trong cuộc gọi: cần cả từ tắt lẫn tên gọi
assert.strictEqual(m.tatHan("Thần Sa, tắt mic nhé"), true);
assert.strictEqual(m.tatHan("tắt mic"), false);
assert.strictEqual(m.tatHan("thần sa ơi"), false);
// ---- 5. Từ khoá người dùng tự khai
const m2 = M.tao({ on: ["ê trợ lý"], off: ["đi ngủ đi"] });
assert.strictEqual(m2.match("Ê trợ lý ơi"), "on");
assert.strictEqual(m2.match("đi ngủ đi"), "off");
assert.strictEqual(m2.match("thần sa"), null, "chỉ theo bộ từ đã khai");

// ---- 6. Gắn vào trang và nút mic
const html = fs.readFileSync(path.join(ROOT, "dashboard/index.html"), "utf8");
const app = fs.readFileSync(path.join(ROOT, "dashboard/app.js"), "utf8");
const wl = fs.readFileSync(path.join(ROOT, "dashboard/wake-listen.js"), "utf8");
assert.ok(html.includes('/static/wake-match.js') && html.includes('/static/wake-listen.js'), "nạp script");
assert.ok(html.includes('id="vcWake"') && html.includes('id="vcWakeOn"') && html.includes('id="vcWakeEngine"')
  && html.includes('id="vcWakeWordsOn"') && html.includes('id="vcWakeWordsOff"'), "khối Cài đặt");
assert.ok(/<option value="local"[^>]*>[^<]*<\/option>\s*<option value="browser"/.test(html), "Trên máy đứng đầu (mặc định)");
assert.ok(/engine: "local"/.test(wl), "cách dò mặc định là Trên máy");
assert.ok(/localStorage\.getItem\(LS\) === "1"/.test(wl), "công tắc ở từng máy, mặc định TẮT");
assert.ok(/on: \(\) => \{ if \(handsFree\) return false; voiceBtn\.click\(\); return true; \}/.test(app), "ThansaMic.on gọi như bấm nút");
assert.ok(app.includes("window.ThansaWake.xetCauTat(_cauNguoiCuoi)"), "cúp máy theo lệnh: xét 'Thần Sa tắt mic'");
assert.ok(/if \(!st\.chay \|\| dangGoi\(\) \|\| dangNoi\(\)/.test(wl), "không dò khi đang gọi hay Thansa đang đọc");
assert.ok(fs.existsSync(path.join(ROOT, "dashboard/vendor/vosk-browser/vosk.js")), "thư viện Vosk có sẵn trong app");

console.log("OK - test_wake_listen");
