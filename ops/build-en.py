#!/usr/bin/env python3
"""Sinh bản dịch tiếng Anh của file dashboard bằng cách áp TỪ ĐIỂN vào string literal.

Ý tưởng (Option B, chốt 18/08): thay vì overlay khớp DOM lúc chạy (mong manh với chuỗi
ghép biến + hộp thoại native), ta dịch NGAY TRONG SOURCE — thay nội dung string literal
tiếng Việt bằng bản tiếng Anh trong en-goi.json, GIỮ NGUYÊN cấu trúc code. Chạy lại mỗi
vòng trộn: chuỗi cũ tự áp lại từ từ điển (gần như miễn phí), chỉ chuỗi MỚI mới cần dịch.

An toàn:
- Chỉ đổi NỘI DUNG bên trong '...', "...", `...` (segment giữa ${..} cho template).
- Kiểm chứng "khung code" (bản đã thay MỌI literal bằng ô trống) của bản gốc và bản dịch
  phải GIỐNG HỆT → chứng minh không đụng một ký tự code nào.
- Chuỗi không có trong từ điển → giữ nguyên tiếng Việt (không vỡ).

    python3 ops/build-en.py <file-vao> <file-ra>
    python3 ops/build-en.py --check <goc> <dich>   # chỉ kiểm khung code
"""
import json, re, sys
from pathlib import Path

OPS = Path(__file__).resolve().parent
DICT = json.load(open(OPS.parent / "dashboard/i18n/en-goi.json", encoding="utf-8"))
VN = re.compile(r'[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]', re.I)

def tra(noi_dung):
    """Dịch nội dung một mảnh: khớp nguyên (đã trim) rồi áp lại khoảng trắng bao quanh."""
    s = noi_dung.strip()
    if not s or not VN.search(s):
        return None
    en = DICT.get(s)
    if en is None:
        return None
    # giữ khoảng trắng đầu/cuối gốc
    dau = noi_dung[:len(noi_dung) - len(noi_dung.lstrip())]
    cuoi = noi_dung[len(noi_dung.rstrip()):]
    return dau + en + cuoi

def esc(s, quote):
    """Escape lại chuỗi English cho đúng loại nháy (json.dumps lo control char \\n \\t)."""
    body = json.dumps(s, ensure_ascii=False)[1:-1]   # escape \\ " \n \t \r kiểu nháy kép
    if quote == '"':
        return body
    if quote == "'":
        return body.replace('\\"', '"').replace("'", "\\'")
    # backtick: cho phép " và ' trần; phải escape ` và ${
    return body.replace('\\"', '"').replace('`', '\\`').replace('${', '\\${')

def unesc(s, quote):
    try:
        if quote == "`":
            return s  # segment template: giữ nguyên, không giải escape phức tạp
        return json.loads(('"' + s + '"') if quote == '"'
                          else ('"' + s.replace('\\\'', "'").replace('"', '\\"') + '"'))
    except Exception:
        return None

# Tách chuỗi literal trong JS: bắt ' " ` cùng nội dung (tôn trọng \escape).
LIT = re.compile(r"""(?P<q>['"`])(?P<body>(?:\\.|(?!(?P=q)).)*)(?P=q)""", re.S)

def dich_js(src):
    def thay(m):
        q = m.group("q"); body = m.group("body")
        if not VN.search(body):
            return m.group(0)
        if q == "`":
            # tách theo ${...}, dịch từng segment literal, giữ nguyên phần ${..}
            parts = re.split(r'(\$\{[^{}]*\})', body)
            ra = []
            for p in parts:
                if p.startswith("${"):
                    ra.append(p); continue
                en = tra(p)          # tra dùng bản trim; segment template giữ nguyên text nguồn
                ra.append(esc(en, q) if en is not None else p)
            return q + "".join(ra) + q
        # ' hoặc "
        plain = unesc(body, q)
        if plain is None:
            return m.group(0)
        en = tra(plain)
        if en is None:
            return m.group(0)
        return q + esc(en, q) + q
    return LIT.sub(thay, src)

def khung(src):
    """Bỏ nội dung mọi literal -> khung code, để so sánh bất biến cấu trúc."""
    return LIT.sub(lambda m: m.group("q") + "\x00" + m.group("q"), src)

ATTR_HIENTHI = ("title", "placeholder", "aria-label", "alt", "data-ic-title", "value", "data-tip")

def dich_html(src):
    """Dịch HTML: (1) inline <script> qua dich_js, (2) text node giữa > <, (3) attribute hiển thị.
    Giữ nguyên comment <!-- -->, thẻ, cấu trúc."""
    # 1) inline script
    def _script(m):
        return m.group(1) + dich_js(m.group(2)) + m.group(3)
    src = re.sub(r'(<script[^>]*>)([\s\S]*?)(</script>)', _script, src, flags=re.I)
    # 2) attribute hiển thị
    def _attr(m):
        ten, q, val = m.group(1), m.group(2), m.group(3)
        en = tra(val)
        return f'{ten}={q}{en}{q}' if en is not None else m.group(0)
    src = re.sub(r'\b(' + "|".join(ATTR_HIENTHI) + r')=(["\'])(.*?)\2',
                 _attr, src)
    # 3) text node (tránh trong <script>/<style> đã xử lý; tránh comment)
    def _text(m):
        truoc, txt = m.group(1), m.group(2)
        if not VN.search(txt):
            return m.group(0)
        en = tra(txt)
        return truoc + en if en is not None else m.group(0)
    # chỉ text nằm ngay sau '>' và trước '<', không chứa < >
    src = re.sub(r'(>)([^<>{}]*[^\s<>{}][^<>{}]*)(?=<)', lambda m: (m.group(1) + (tra(m.group(2)) or m.group(2))) if VN.search(m.group(2)) else m.group(0), src)
    return src

def main():
    args = sys.argv[1:]
    if args and args[0] == "--check":
        a, b = Path(args[1]).read_text(encoding="utf-8"), Path(args[2]).read_text(encoding="utf-8")
        print("KHUNG CODE GIONG HET" if khung(a) == khung(b) else "!!! KHUNG LECH")
        return
    vao, ra = Path(args[0]), Path(args[1])
    src = vao.read_text(encoding="utf-8")
    la_html = vao.suffix.lower() in (".html", ".htm")
    out = dich_html(src) if la_html else dich_js(src)
    # kiểm bất biến khung ngay (chỉ cho JS — HTML có transform text node hợp lệ)
    if not la_html and khung(src) != khung(out):
        print("!!! KHUNG LECH - KHONG GHI", file=sys.stderr); sys.exit(1)
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(out, encoding="utf-8")
    # đếm literal đã dịch
    n = sum(1 for m in LIT.finditer(src) if VN.search(m.group("body")))
    print(f"{vao.name}: {n} literal co tieng Viet -> {ra}")

if __name__ == "__main__":
    main()
