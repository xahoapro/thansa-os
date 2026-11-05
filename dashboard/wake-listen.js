/* Lắng nghe ngầm (Thansa 2.5.0, chủ chốt 04/11/2026).

   Mic mở sẵn nhưng CHỈ dò từ khoá; không gửi gì cho bộ não, không lưu, không hiện chữ. Nghe thấy từ khoá
   BẬT (Thần Sa, bật mic, mở mic...) thì gọi như bấm nút mic; nghe thấy từ khoá TẮT (tắt mic, thôi nghe...)
   thì thôi nghe ngầm hẳn. Trong cuộc gọi: "tắt mic" (bộ não cúp máy) hay im lặng quá lâu -> về nghe ngầm;
   "Thần Sa tắt mic" -> cúp máy VÀ thôi nghe ngầm.

   Hai cách dò, chọn ở Cài đặt > Giọng nói (mặc định "local"):
   - local   : Vosk WebAssembly ngay trong trình duyệt, mô hình tiếng Việt do máy chủ Thansa phục vụ
               (/voice/wake/model). Âm thanh không rời máy.
   - browser : Web Speech của trình duyệt (Chrome/Edge); âm thanh gửi lên máy chủ nhận giọng của hãng.
   Công tắc bật/tắt ở TỪNG MÁY (localStorage "thansa.wake"), mặc định TẮT. Chỉ nghe khi trang đang mở. */
(function () {
  "use strict";
  const LS = "thansa.wake";
  const M = window.ThansaWakeMatch;
  const st = {
    bat: (() => { try { return localStorage.getItem(LS) === "1"; } catch (e) { return false; } })(),
    engine: "local", on: [], off: [], phrases: [],
    chay: false, trang: "tat", loi: "", tienDo: 0,
  };
  let matcher = M ? M.tao({ on: [], off: [] }) : null;
  const ngheTheo = [];
  function bao() {
    ngheTheo.forEach(f => { try { f(trangThai()); } catch (e) {} });
    const b = document.getElementById("voiceBtn");
    if (b) {
      b.classList.toggle("wake-on", st.chay && st.trang === "nghe");
      if (st.chay && st.trang === "nghe" && !b.classList.contains("in-call")) b.title = t("wake.btn_title");
    }
  }
  const t = (k, p) => (window.t ? window.t(k, p) : k);
  function trangThai() { return { bat: st.bat, engine: st.engine, trang: st.trang, loi: st.loi, tienDo: st.tienDo }; }
  const mic = () => window.ThansaMic || null;
  const dangGoi = () => !!(mic() && mic().isOn());
  const dangNoi = () => !!(mic() && mic().speaking && mic().speaking());

  // ---------------------------------------------------------------- nghe được một câu
  let _lanCuoi = 0;
  function nghe(cau, conf) {
    if (!st.chay || dangGoi() || dangNoi() || !matcher) return;      // Thansa đang đọc: đừng tự nghe tiếng mình
    const k = matcher.match(cau, conf);
    if (!k || Date.now() - _lanCuoi < 1500) return;
    _lanCuoi = Date.now();
    if (k === "on") {
      tamDung();
      try { ting(); } catch (e) {}
      if (mic() && mic().on) mic().on();
    } else if (k === "off") {
      batTat(false);
      if (mic() && mic().note) mic().note(t("wake.off_by_voice"));
    }
  }
  function ting() {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.value = 880; g.gain.value = 0.08;
    o.connect(g); g.connect(ctx.destination); o.start();
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);
    o.stop(ctx.currentTime + 0.26); setTimeout(() => ctx.close(), 400);
  }

  // ---------------------------------------------------------------- cách dò: trình duyệt (Web Speech)
  const trinhDuyet = {
    rec: null,
    async bat() {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) throw new Error(t("wake.err_no_webspeech"));
      const rec = new SR();
      rec.lang = "vi-VN"; rec.continuous = true; rec.interimResults = true;
      rec.onresult = (e) => { for (let i = e.resultIndex; i < e.results.length; i++) nghe(e.results[i][0].transcript); };
      rec.onerror = (e) => { if (e.error === "not-allowed" || e.error === "service-not-allowed") { st.loi = t("wake.err_mic"); dung(); bao(); } };
      rec.onend = () => { if (this.rec === rec && st.chay) setTimeout(() => { try { rec.start(); } catch (e) {} }, 300); };   // trình duyệt tự ngắt ~1 phút
      this.rec = rec; rec.start();
    },
    tat() { const r = this.rec; this.rec = null; if (r) { try { r.onend = null; r.abort(); } catch (e) {} } },
  };

  // ---------------------------------------------------------------- cách dò: trên máy (Vosk)
  const trenMay = {
    model: null, rec: null, ctx: null, src: null, node: null, stream: null, napThuVien: null,
    thuVien() {
      if (window.Vosk) return Promise.resolve();
      if (!this.napThuVien) this.napThuVien = new Promise((ok, loi) => {
        const s = document.createElement("script");
        s.src = "/static/vendor/vosk-browser/vosk-0.0.8.min.js"; s.onload = ok; s.onerror = () => loi(new Error(t("wake.err_lib")));
        document.head.appendChild(s);
      });
      return this.napThuVien;
    },
    async choMoHinh() {
      for (;;) {
        const s = await fetch("/voice/wake/status?start=1", { cache: "no-store" }).then(r => r.json());
        st.tienDo = s.progress || 0;
        if (s.ready) return;
        if (s.error) throw new Error(t("wake.err_model", { loi: s.error }));
        st.trang = "tai"; bao();
        await new Promise(r => setTimeout(r, 1500));
        if (!st.chay) throw new Error("stopped");
      }
    },
    async bat() {
      await this.thuVien();
      await this.choMoHinh();
      if (!this.model) {
        st.trang = "nap"; bao();
        this.model = await window.Vosk.createModel(location.origin + "/voice/wake/model");
      }
      const g = await fetch("/voice/wake/grammar", { cache: "no-store" }).then(r => r.json()).catch(() => ({}));
      st.phrases = (g && g.phrases) || [];
      this.stream = await navigator.mediaDevices.getUserMedia({ video: false, audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 } });
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      const rec = new this.model.KaldiRecognizer(this.ctx.sampleRate, JSON.stringify(st.phrases.concat(["[unk]"])));
      rec.setWords(true);
      rec.on("result", (m) => {
        const r = (m && m.result) || {};
        nghe(r.text || "", (r.result || []).map(w => w.conf));
      });
      this.rec = rec;
      this.src = this.ctx.createMediaStreamSource(this.stream);
      this.node = this.ctx.createScriptProcessor(4096, 1, 1);
      this.node.onaudioprocess = (e) => { try { if (this.rec) this.rec.acceptWaveform(e.inputBuffer); } catch (err) {} };
      this.src.connect(this.node); this.node.connect(this.ctx.destination);
    },
    tat() {
      try { if (this.node) { this.node.onaudioprocess = null; this.node.disconnect(); } } catch (e) {}
      try { if (this.src) this.src.disconnect(); } catch (e) {}
      try { if (this.stream) this.stream.getTracks().forEach(x => x.stop()); } catch (e) {}
      try { if (this.ctx) this.ctx.close(); } catch (e) {}
      try { if (this.rec) this.rec.remove(); } catch (e) {}
      this.node = this.src = this.stream = this.ctx = this.rec = null;   // giữ this.model: bật lại nhanh
    },
  };
  const dongCo = () => (st.engine === "browser" ? trinhDuyet : trenMay);

  // ---------------------------------------------------------------- vòng đời
  let _dangMo = false;
  async function mo() {
    if (_dangMo || st.chay) return;
    _dangMo = true; st.chay = true; st.loi = ""; st.trang = "mo"; bao();
    try {
      await dongCo().bat();
      if (st.chay) st.trang = "nghe";
    } catch (e) {
      if (st.chay) { st.loi = (e && e.message) || String(e); dung(); }
    } finally { _dangMo = false; bao(); }
  }
  function dung() { st.chay = false; st.trang = st.bat ? "cho" : "tat"; trinhDuyet.tat(); trenMay.tat(); bao(); }
  function tamDung() { dung(); }   // nhường mic cho cuộc gọi; vòng dưới tự mở lại khi cúp máy

  // Mỗi giây: có bật + không gọi + không đang đọc -> nghe ngầm; đang gọi -> nhả mic.
  setInterval(() => {
    const nen = st.bat && !dangGoi();
    if (nen && !st.chay && !_dangMo && !st.loi) mo();
    else if (!nen && st.chay) dung();
  }, 1000);

  function batTat(on) {
    st.bat = !!on;
    try { localStorage.setItem(LS, on ? "1" : "0"); } catch (e) {}
    st.loi = "";
    if (!on) dung(); else bao();
  }
  async function napCauHinh() {
    try {
      const o = await fetch("/voice/options?brains=0", { cache: "no-store" }).then(r => r.json());
      const v = (o && o.voice) || {};
      cauHinh(v);
    } catch (e) {}
  }
  function cauHinh(v) {
    const doi = (v.wake_engine || "local") !== st.engine;
    st.engine = v.wake_engine === "browser" ? "browser" : "local";
    st.on = v.wake_words_on || []; st.off = v.wake_words_off || [];
    matcher = M ? M.tao({ on: st.on, off: st.off }) : null;
    if (st.chay && doi) { dung(); }               // đổi cách dò: vòng trên mở lại bằng cách mới
    else if (st.chay && st.engine === "local") { dung(); }   // từ khoá mới -> ngữ pháp Vosk mới
    bao();
  }

  window.ThansaWake = {
    trangThai, batTat, cauHinh, napCauHinh,
    // Một chỗ nghe duy nhất (trang Cài đặt vẽ lại thì thay, không chồng thêm).
    onChange: (f) => { ngheTheo.length = 0; if (f) { ngheTheo.push(f); f(trangThai()); } },
    // app.js gọi khi cúp máy theo lệnh: câu cuối có cả "tắt" lẫn tên gọi -> thôi nghe ngầm hẳn.
    xetCauTat(cau) { if (st.bat && matcher && matcher.tatHan(cau)) { batTat(false); return true; } return false; },
    thuLai() { st.loi = ""; bao(); },
  };
  napCauHinh();
})();
