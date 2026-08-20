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
# Bản gộp khoảng trắng: bắt text node HTML nhiều dòng / thụt dòng khớp cùng một câu.
_WS = re.compile(r"\s+")
DICT_CHUAN = {_WS.sub(" ", k).strip(): v for k, v in DICT.items()}
VN = re.compile(r'[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]', re.I)

def tra(noi_dung):
    """Dịch nội dung một mảnh: khớp nguyên (đã trim), rồi khớp theo bản gộp khoảng trắng."""
    s = noi_dung.strip()
    if not s or not VN.search(s):
        return None
    en = DICT.get(s)
    if en is None:
        en = DICT_CHUAN.get(_WS.sub(" ", s))   # câu nhiều dòng → khớp bản 1 dòng
    if en is None:
        return None
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

def _dich_text_seg(seg):
    """Đoạn HTML (segment template HOẶC literal có thẻ): tách theo thẻ, dịch từng mẩu TEXT
    (kể cả text ở đầu/cuối, cạnh </div>), và dịch attribute hiển thị trong thẻ."""
    if not VN.search(seg):
        return seg
    def _attr(m):
        ten, qa, val = m.group(1), m.group(2), m.group(3)
        if not VN.search(val): return m.group(0)
        en = tra(val)
        return f'{ten}={qa}{en}{qa}' if en is not None else m.group(0)
    out = []
    for part in re.split(r'(<[^<>]*>)', seg):     # tách thẻ <...> khỏi text
        if part.startswith("<") and part.endswith(">"):
            out.append(re.sub(r'\b(' + "|".join(ATTR_HIENTHI) + r')=(["\'])(.*?)\2', _attr, part))
        elif part.strip() and VN.search(part):
            en = tra(part)
            out.append(en if en is not None else part)
        else:
            out.append(part)
    return "".join(out)

def _dong_ngoac(body, start):
    """Tìm chỉ số NGAY SAU '}' đóng cho '${' bắt đầu tại start. Bỏ qua string/template/
    regex/comment bên trong (không đếm ngoặc trong chúng). Trả len(body) nếu không cân."""
    depth, j, n = 1, start + 2, len(body)
    prev = ""
    while j < n and depth:
        c = body[j]; two = body[j:j+2]
        if two == "//":
            k = body.find("\n", j); j = n if k == -1 else k; continue
        if two == "/*":
            k = body.find("*/", j+2); j = n if k == -1 else k+2; continue
        if c in "'\"`":
            j += 1
            while j < n:
                if body[j] == "\\": j += 2; continue
                if body[j] == c: break
                if c == "`" and body[j:j+2] == "${":   # template lồng: nhảy qua cả ${...}
                    j = _dong_ngoac(body, j); continue
                j += 1
            j += 1; prev = c; continue
        if c == "/" and (prev == "" or prev in "(,=:[!&|?{};~^%*+-<>"):
            j += 1; inclass = False
            while j < n:
                if body[j] == "\\": j += 2; continue
                if body[j] == "[": inclass = True
                elif body[j] == "]": inclass = False
                elif body[j] == "/" and not inclass: break
                elif body[j] == "\n": break
                j += 1
            j += 1; prev = "/"; continue
        if c == "{": depth += 1
        elif c == "}": depth -= 1
        if not c.isspace(): prev = c
        j += 1
    return j

def _dich_template(body):
    """Đi qua template: đệ quy dịch string trong ${...} (biểu thức JS), dịch text/attr ngoài."""
    out = []
    i, n = 0, len(body)
    while i < n:
        if body[i:i+2] == "${":
            j = _dong_ngoac(body, i)          # vị trí ngay sau '}' cân đối
            expr = body[i+2:j-1]
            out.append("${" + dich_js(expr) + "}")
            i = j
        else:
            j = body.find("${", i)
            j = n if j == -1 else j
            out.append(_dich_text_seg(body[i:j]))
            i = j
    return "".join(out)

def _dich_body(q, body):
    """Dịch nội dung một literal (đã bóc nháy). q = loại nháy. Trả body mới (chưa kèm nháy)."""
    if not VN.search(body):
        return body
    if q == "`":
        return _dich_template(body)
    plain = unesc(body, q)
    if plain is None:
        return body
    # literal dính thẻ HTML (vd "Tiền mặt tháng này</div>") → tách thẻ dịch từng mẩu text
    if re.search(r'</?[a-zA-Z][^<>]*>', plain):
        return esc(_dich_text_seg(plain), q)
    en = tra(plain)
    return esc(en, q) if en is not None else body

def _quet(src, xu_ly):
    """Scanner có trạng thái: đi qua JS, chỉ đưa NỘI DUNG string/template cho xu_ly(q, body).
    Bỏ qua comment (// /* */) và regex literal (/.../).  xu_ly trả body mới.
    Trả về source đã dựng lại. Đây là cách ĐÚNG (regex thuần lệch pha ở comment có dấu nháy)."""
    out = []
    i, n = 0, len(src)
    # ký tự "có nghĩa" gần nhất, để phân biệt /regex/ với phép chia
    prev = ""
    def truoc_regex(p):
        return p == "" or p in "(,=:[!&|?{};~^%*+-<>" or p in "\n\t "
    while i < n:
        c = src[i]
        two = src[i:i+2]
        if two == "//":
            j = src.find("\n", i)
            j = n if j == -1 else j
            out.append(src[i:j]); i = j; continue
        if two == "/*":
            j = src.find("*/", i+2)
            j = n if j == -1 else j+2
            out.append(src[i:j]); i = j; continue
        if c in "'\"`":
            j = i + 1; body = []
            while j < n:
                if src[j] == "\\":
                    body.append(src[j:j+2]); j += 2; continue
                if src[j] == c:
                    break
                if c == "`" and src[j:j+2] == "${":
                    # nhảy trọn ${...} (có thể chứa template lồng) để không nhầm backtick lồng
                    k = _dong_ngoac(src, j)
                    body.append(src[j:k]); j = k; continue
                body.append(src[j]); j += 1
            raw = "".join(body)
            out.append(c + xu_ly(c, raw) + c)
            i = j + 1; prev = c; continue
        if c == "/" and truoc_regex(prev):
            # regex literal: đi tới '/' đóng, tôn trọng \ và [class]
            j = i + 1; trong_class = False
            while j < n:
                if src[j] == "\\": j += 2; continue
                if src[j] == "[": trong_class = True
                elif src[j] == "]": trong_class = False
                elif src[j] == "/" and not trong_class: break
                elif src[j] == "\n": break   # không phải regex
                j += 1
            out.append(src[i:j+1]); i = j + 1; prev = "/"; continue
        out.append(c)
        if not c.isspace():
            prev = c
        i += 1
    return "".join(out)

def dich_js(src):
    return _quet(src, _dich_body)

def dich_css(src):
    """CSS: dịch chuỗi content: "..." (pseudo-element ::before/::after) — overlay không với
    tới được vì đây là nội dung do CSS sinh, không phải DOM text node."""
    def _ct(m):
        q, val = m.group(1), m.group(2)
        if not VN.search(val): return m.group(0)
        en = tra(val)
        return f'content: {q}{esc(en, q)}{q}' if en is not None else m.group(0)
    return re.sub(r'content:\s*(["\'])((?:\\.|(?!\1).)*)\1', _ct, src)

def khung(src):
    """Bỏ nội dung mọi literal -> khung code, để so sánh bất biến cấu trúc."""
    return _quet(src, lambda q, body: "\x00")

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

def _thu_thap(src, ra):
    """Thu MỌI chuỗi hiển thị tiếng Việt CHƯA có trong từ điển (tra trả None), qua scanner
    đúng. Dùng để biết còn thiếu gì cần dịch (không sinh file)."""
    def _gom(q, body):
        if not VN.search(body):
            return body
        if q == "`":
            for seg in re.split(r'(\$\{[^{}]*\})', body):
                if seg.startswith("${"):
                    # đệ quy nông: gom string trong biểu thức
                    for qq, bb in re.findall(r"""(['"])((?:\\.|(?!\1).)*)\1""", seg):
                        p = unesc(bb, qq)
                        if p and VN.search(p) and tra(p) is None:
                            ra.add(p.strip())
                    continue
                for m in re.findall(r'(?:title|placeholder|aria-label|alt|value)=(["\'])(.*?)\1', seg):
                    if VN.search(m[1]) and tra(m[1]) is None: ra.add(m[1].strip())
                for m in re.findall(r'>([^<>{}]*[^\s<>{}][^<>{}]*)(?=<)', seg):
                    if VN.search(m) and tra(m) is None: ra.add(m.strip())
                s = seg.strip()
                if "<" not in s and ">" not in s and VN.search(s) and tra(s) is None:
                    ra.add(s)
            return body
        p = unesc(body, q)
        if p and VN.search(p) and tra(p) is None:
            ra.add(p.strip())
        return body
    _quet(src, _gom)

def main():
    args = sys.argv[1:]
    if args and args[0] == "--check":
        a, b = Path(args[1]).read_text(encoding="utf-8"), Path(args[2]).read_text(encoding="utf-8")
        print("KHUNG CODE GIONG HET" if khung(a) == khung(b) else "!!! KHUNG LECH")
        return
    if args and args[0] == "--extract":
        import json as _j, glob as _g
        ra = set()
        for f in sorted(_g.glob(str(OPS.parent / "dashboard" / "*.js"))):
            if Path(f).name == "dich-en.js": continue
            _thu_thap(Path(f).read_text(encoding="utf-8"), ra)
        out = sorted({s for s in ra if s and 2 <= len(s) <= 300}, key=len)
        print(_j.dumps(out, ensure_ascii=False, indent=1))
        return
    vao, ra = Path(args[0]), Path(args[1])
    src = vao.read_text(encoding="utf-8")
    la_js = vao.suffix.lower() == ".js"
    la_html = vao.suffix.lower() in (".html", ".htm")
    la_css = vao.suffix.lower() == ".css"
    out = dich_html(src) if la_html else dich_js(src) if la_js else dich_css(src) if la_css else src
    # kiểm bất biến khung code ngoài-template (JS)
    if la_js and khung(src) != khung(out):
        out = src   # lệch khung → thà không dịch còn hơn hỏng code
    # rào cứng: JS phải PARSE được. Hỏng → ghi BẢN GỐC (tính năng chạy, chỉ chưa dịch).
    ra.parent.mkdir(parents=True, exist_ok=True)
    if la_js:
        import subprocess, tempfile
        tmp = Path(tempfile.gettempdir()) / ("_check_" + vao.name)
        tmp.write_text(out, encoding="utf-8")
        try:
            r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, timeout=30)
            if r.returncode != 0:
                out = src   # syntax hỏng → dùng bản gốc
        except Exception:
            pass
        finally:
            try: tmp.unlink()
            except Exception: pass
    ra.write_text(out, encoding="utf-8")
    print(f"{vao.name}: da dich -> {ra}")

if __name__ == "__main__":
    main()
