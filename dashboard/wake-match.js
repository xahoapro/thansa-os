/* Lắng nghe ngầm (Thansa 2.5.0): so từ khoá trong câu nghe được. Thuần, chạy được dưới node
   (tests/js/test_wake_listen.js), không đụng DOM.

   - "on"  : câu có một từ khoá BẬT (Thần Sa, bật mic, mở mic...) -> gọi (mở mic như bấm nút).
   - "off" : câu có một từ khoá TẮT (tắt mic, thôi nghe...) -> thôi nghe ngầm hẳn.
   TẮT được xét TRƯỚC BẬT: "Thần Sa tắt mic" chứa tên gọi nhưng là lệnh tắt.

   So theo chữ đã bỏ dấu + chữ thường, nguyên từ (không khớp nửa chữ: "micro" không phải "mic").
   Bộ nhận trên máy (Vosk) chỉ được chọn trong vài từ khoá nên hay ép một câu lạ thành từ khoá gần
   nhất; vì vậy kèm độ tin cậy từng từ thì phải đủ ngưỡng (đo 04/11/2026: từ khoá thật 0,7-1,0, câu
   nói thường bị ép 0,41-0,58). */
(function (root) {
  "use strict";
  const NGUONG_MOT_TU = 0.6, NGUONG_TB = 0.8;

  function boDau(s) {
    return String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/\u0111/g, "d").replace(/\u0110/g, "d").toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
  }

  // Câu "thần sa tắt mic" vẫn là lệnh TẮT HẲN dù đang trong cuộc gọi (bộ não chỉ cúp máy).
  const TEN_GOI = ["than sa", "thansa"];

  function tao(cfg) {
    const on = (cfg && cfg.on || []).map(boDau).filter(Boolean);
    const off = (cfg && cfg.off || []).map(boDau).filter(Boolean);
    const coTu = (cau, ds) => { const s = " " + boDau(cau) + " "; return ds.find(k => s.includes(" " + k + " ")) || null; };
    const duTinCay = (ds) => !ds.length || (Math.min.apply(null, ds) >= NGUONG_MOT_TU
      && ds.reduce((a, b) => a + b, 0) / ds.length >= NGUONG_TB);
    // Từ khoá xuất hiện trong câu VÀ đủ tin cậy trên CHÍNH các từ của nó (đuôi câu nghe kém không kéo
    // "Thần Sa, mở lịch..." xuống). conf lệch số từ (Web Speech không có) thì chỉ xét có/không.
    function timTu(cau, ds, conf) {
      const tu = boDau(cau).split(" ").filter(Boolean);
      const cs = Array.isArray(conf) && conf.length === tu.length ? conf.map(Number) : null;
      for (const k of ds) {
        const kt = k.split(" ");
        for (let i = 0; i + kt.length <= tu.length; i++) {
          if (kt.every((w, j) => tu[i + j] === w) && (!cs || duTinCay(cs.slice(i, i + kt.length)))) return k;
        }
      }
      return null;
    }
    return {
      // conf: độ tin cậy từng từ (Vosk). Trả "on" | "off" | null. TẮT xét trước BẬT.
      match(cau, conf) {
        if (!String(cau || "").trim()) return null;
        if (timTu(cau, off, conf)) return "off";
        if (timTu(cau, on, conf)) return "on";
        return null;
      },
      // Câu người dùng nói TRONG cuộc gọi dẫn tới cúp máy: có cả từ tắt lẫn tên gọi -> thôi nghe ngầm hẳn.
      tatHan(cau) { return !!(coTu(cau, off) && coTu(cau, TEN_GOI)); },
      tuKhoa() { return { on: on.slice(), off: off.slice() }; },
    };
  }

  const api = { boDau, tao, NGUONG_MOT_TU, NGUONG_TB };
  root.ThansaWakeMatch = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
