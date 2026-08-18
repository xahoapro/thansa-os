/* Lớp dịch phủ EN cho dashboard Thansa (bản fork, không có ở upstream).
 *
 * Vì sao tồn tại: hệ i18n gốc mới phủ ~76 key; ~1.100 chuỗi tĩnh còn nằm cứng trong
 * code. i18n hoá toàn bộ = sửa tầng hiển thị diện rộng = mỗi vòng trộn upstream xung
 * đột khắp nơi. Lớp phủ này dịch LÚC HIỂN THỊ bằng từ điển exact-match
 * (en-goi.json: {"chuỗi việt": "english"}), không đụng một dòng code gốc nào ngoài
 * MỘT thẻ <script> trong index.html.
 *
 * Luật an toàn:
 * - Chỉ thay TEXT NODE và attribute hiển thị (title/placeholder/aria-label/alt) khi
 *   khớp NGUYÊN CHUỖI (sau trim). Không đụng HTML, không innerHTML → không cửa XSS.
 * - Chuỗi không có trong từ điển (upstream mới thêm/đổi) giữ nguyên tiếng Việt —
 *   đúng luật suy biến của i18n gốc; bộ dò hằng ngày sẽ nhắc bổ sung từ điển.
 * - Chỉ chạy khi javis.ui_lang === "en". Đổi ngôn ngữ trên UI là app reload sẵn.
 */
(function () {
  "use strict";
  var lang = "";
  try { lang = localStorage.getItem("javis.ui_lang") || ""; } catch (e) {}

  // Đồng bộ cookie thansa_lang theo lựa chọn ngôn ngữ, để server phục vụ bản dịch sẵn
  // dashboard/en/ (P017). Người dùng đã chọn EN từ trước (chỉ có localStorage, chưa có
  // cookie) sẽ được nâng cấp: đặt cookie rồi tải lại MỘT lần để nạp bộ file đã dịch.
  try {
    var muon = (lang === "en") ? "en" : "vi";
    var dangCo = (document.cookie.match(/(?:^|;\s*)thansa_lang=([^;]+)/) || [])[1] || "";
    if (dangCo !== muon) {
      document.cookie = "thansa_lang=" + muon + ";path=/;max-age=31536000;samesite=lax";
      if (!sessionStorage.getItem("thansa_lang_reload")) {
        sessionStorage.setItem("thansa_lang_reload", "1");
        location.reload();
        return;
      }
    }
  } catch (e) {}

  if (lang !== "en") return;

  var TU = null;                 // Map chuỗi việt (nguyên) -> english
  var TU_CHUAN = null;           // Map chuỗi việt (gộp khoảng trắng) -> english, bắt chuỗi nhiều dòng
  var ATTRS = ["title", "placeholder", "aria-label", "alt", "data-ic-title", "value", "data-tip"];
  var BO_QUA = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, TEXTAREA: 1 };

  // Gộp mọi chuỗi khoảng trắng (kể cả \n, thụt dòng của template) thành 1 dấu cách.
  function chuan(s) { return s.replace(/\s+/g, " ").trim(); }

  // Tra: khớp nguyên trước, rồi khớp theo bản gộp khoảng trắng.
  function tra(s) {
    var en = TU.get(s);
    if (en !== undefined) return en;
    return TU_CHUAN.get(chuan(s));
  }

  function dichText(node) {
    var goc = node.nodeValue;
    if (!goc) return;
    var s = goc.trim();
    if (s.length < 2) return;
    var en = tra(s);
    if (en !== undefined && en !== s) {
      // giữ khoảng trắng bao quanh; dùng hàm thay thế để "$" trong en không bị hiểu là pattern
      node.nodeValue = goc.replace(s, function () { return en; });
    }
  }

  function dichAttr(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i];
      if (!el.hasAttribute || !el.hasAttribute(a)) continue;
      var v = el.getAttribute(a);
      var en = v && tra(v.trim());
      if (en !== undefined && en !== v) el.setAttribute(a, en);
    }
  }

  function dichCay(root) {
    if (root.nodeType === 3) { dichText(root); return; }
    if (root.nodeType !== 1 || BO_QUA[root.tagName]) return;
    dichAttr(root);
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, {
      acceptNode: function (n) {
        if (n.nodeType === 1) {
          return BO_QUA[n.tagName] ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_SKIP;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var t;
    while ((t = w.nextNode())) dichText(t);
    // attribute của con cháu
    if (root.querySelectorAll) {
      var els = root.querySelectorAll("[title],[placeholder],[aria-label],[alt],[data-ic-title]");
      for (var j = 0; j < els.length; j++) dichAttr(els[j]);
    }
  }

  // alert/confirm/prompt là HỘP THOẠI NATIVE của trình duyệt — KHÔNG nằm trong DOM nên
  // TreeWalker/observer không với tới. Bọc để dịch tham số thông điệp trước khi hiện.
  function bocHopThoai() {
    ["alert", "confirm", "prompt"].forEach(function (ten) {
      var goc = window[ten];
      if (typeof goc !== "function") return;
      window[ten] = function (msg) {
        if (typeof msg === "string") {
          var en = tra(msg.trim());
          if (en !== undefined) msg = en;
        }
        return goc.call(window, msg, arguments[1]);
      };
    });
  }

  function batDau(tuDien) {
    TU = new Map(Object.entries(tuDien));
    TU_CHUAN = new Map();
    Object.keys(tuDien).forEach(function (k) { TU_CHUAN.set(chuan(k), tuDien[k]); });
    bocHopThoai();
    dichCay(document.body);
    var obs = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        if (m.type === "characterData") { dichText(m.target); continue; }
        if (m.type === "attributes") { if (m.target.nodeType === 1) dichAttr(m.target); continue; }
        for (var j = 0; j < m.addedNodes.length; j++) dichCay(m.addedNodes[j]);
      }
    });
    obs.observe(document.body, {
      childList: true, subtree: true, characterData: true,
      attributes: true, attributeFilter: ATTRS
    });
  }

  function nap() {
    fetch("/static/i18n/en-goi.json?v=1")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d) batDau(d); })
      .catch(function () {});   // thiếu từ điển thì im lặng: UI còn tiếng Việt, không vỡ gì
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", nap);
  } else {
    nap();
  }
})();
