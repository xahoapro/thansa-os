# NHIỆM VỤ GĐ2 — Rebrand hiển thị (P001, P003, P004, P005)

Trạm #1 (Windows) soạn · 2026-08-17 · giao cho trạm #2 (VPS)
Tham chiếu đặc tả: mục 6 (tập patch P001–P006), mục 7 GĐ2, mục 2.2 (mapping 7 trường), mục 4.1 (luật ưu tiên: hiển thị/thương hiệu → patch Thansa thắng).
Nền: `me` @ `55318e6`, mapping RỖNG, `so_patch=0`, `tu-kiem-chung.py` XANH, `pytest` đã có trong `goc/.venv`.

## Mục tiêu
Người dùng thấy **100% "Thansa OS"** ở mọi bề mặt hiển thị, GIỮ NGUYÊN mọi thứ bên trong (biến `JAVIS_*`, tên thư mục, `javis.service`, tên tool `javis_*`). Mỗi patch = **một commit `[me]`** + một mục mapping đủ 7 trường. `so_patch` cập nhật khớp. `tu-kiem-chung.py` và `tests/run.py` vẫn XANH.

## Bản đồ chuỗi hiển thị (trạm #1 đã dò trên `goc`, dùng làm điểm xuất phát — trạm #2 tự rà đủ)

**Fallback tên workspace (`… || "Javis OS"`) + mặc định:**
- `env.example:15` → `WORKSPACE_NAME=Javis OS`
- `server/main.py:7740` → `os.getenv("WORKSPACE_NAME", "Javis OS")`
- `dashboard/console.js` → 2619, 4444, 4532, 4895 (`s.workspace_name || "Javis OS"`)

**Chrome sản phẩm (title/login/welcome/thẻ cập nhật/thông báo):**
- `dashboard/index.html` → `:6 <title>Javis OS`, `:119` noti-sub, `:547` placeholder "Javis OS"
- `dashboard/console.js` → 662–663 (upd-name "Javis OS"), 2602 (gcard-name "Javis OS")
- `dashboard/notifications.js:105`

**i18n:**
- `dashboard/i18n/vi.json`, `en.json` → các chuỗi hiển thị "Javis"/"Javis OS" (vd `page.home.label:"Javis"`, `page.terminal.sub`, các `*.hint`). Rà hết, chỉ đổi chuỗi HIỂN THỊ.

**Compose (ảnh chạy):**
- `docker-compose.yml:24`, `docker-compose.build.yml:12`, `docker-compose.hostinger.yml:32` → `image: ghcr.io/blogminhquy/javis-os:latest`

## Bốn patch (mỗi patch 1 commit `[me]` + 1 mục mapping 7 trường)

| ID | Tên | Đụng | y_dinh (tóm) | kiem_chung |
|---|---|---|---|---|
| **P001** | Fallback tên hiển thị Thansa OS | `env.example`, `server/main.py` (fallback), `console.js` (4 fallback) | Khi chưa đặt `workspace_name`, mọi nơi hiện "Thansa OS", KHÔNG đổi tên biến `WORKSPACE_NAME` | Máy mới chưa cấu hình: sidebar/overview/account hiện "Thansa OS"; grep `\|\| "Javis OS"` = 0 |
| **P003** | Chrome sản phẩm: title + login + welcome + thẻ cập nhật + thông báo | `index.html` (title/noti/placeholder), `console.js` (upd-name, gcard-name), `notifications.js` | Tab trình duyệt, màn đăng nhập, cửa sổ chào mừng, thẻ "Cập nhật/Tổng quan", thông báo đều "Thansa OS" | `<title>`=Thansa OS; login+welcome+noti hiện Thansa OS; không còn chuỗi hiển thị "Javis OS" trong HTML trả về client |
| **P004** | i18n vi/en | `dashboard/i18n/vi.json`, `en.json` | Nhãn/câu hiển thị dùng "Javis" như tên → "Thansa"; KHÔNG đổi key | Đổi ngôn ngữ vi/en: nhãn trang + hint hiện "Thansa"; `grep -i javis` trong 2 file = 0 (hoặc chỉ còn chuỗi kỹ thuật không hiển thị, ghi rõ trong mapping) |
| **P005** | Ảnh GHCR → thansa-os | 3 file `docker-compose*.yml` | Máy Docker kéo `ghcr.io/xahoapro/thansa-os:latest` | `grep -rn "image:.*javis-os" docker-compose*` = 0; 3 file trỏ `ghcr.io/xahoapro/thansa-os:latest` |

**Chủ GHCR = `xahoapro`** (theo `origin`). Ảnh đích: `ghcr.io/xahoapro/thansa-os:latest`.

## P002 — HOÃN (chờ asset)
Logo + favicon: cần **file `logo.png` + `favicon.png` bản Thansa** (hiện đang là ảnh upstream). Trạm #1 sẽ cấp file khi có; tạm để `[me] P002` sang một vòng riêng. Không tự chế logo.

## CẤM đụng (khẳng định lại — mục 6)
- KHÔNG rename biến `JAVIS_*`, thư mục, `javis.service`, tool `javis_*`.
- KHÔNG đụng `VERSION`, `CHANGELOG*`, `README*`, `dashboard/app.js`.
- KHÔNG đụng `docs/` và mô tả "skill hệ thống Javis OS" (nội dung/tài liệu — churn cao, ngoài phạm vi vòng này). Nếu thấy chuỗi "Javis OS" trong docs/skill-desc, GHI vào `vung_theo_doi`/ghi chú, KHÔNG sửa.
- KHÔNG phát hành (release do người bấm).

## Kỷ luật mapping (mục 2.2) — bắt buộc mỗi patch
- Đủ 7 trường: `id, ten, y_dinh, commit, diem_neo (ký hiệu, CẤM số dòng), vung_theo_doi, anh_goc (ảnh đoạn mã upstream NGAY TRƯỚC khi sửa), kiem_chung, dieu_kien_bo`.
- `so_patch` = số mục mapping = số commit `[me]` trên `main..me` (giữ `tu-kiem-chung.py` XANH).
- `dieu_kien_bo` cho từng patch: vd P001/P003 → "nếu upstream đưa toàn bộ chuỗi hiển thị vào i18n/branding config thì bỏ patch, dùng cấu hình chính thức".

## Tiêu chí ĐẠT (đo được) — mục 7 GĐ2
1. `python3 ops/tu-kiem-chung.py` → XANH (so_patch = 4 = số mục mapping = số `[me]`).
2. `goc/.venv/bin/python tests/run.py` → **241/241 với pytest** (chấp nhận `test_chat_disconnect.py` flaky-timing khi tải nặng — chạy riêng phải XANH). GĐ2 chỉ đụng chuỗi hiển thị/compose nên KHÔNG được làm đỏ thêm test nào khác.
3. Toàn bộ `kiem_chung` của P001/P003/P004/P005 XANH.
4. App chạy được (khởi động server), mở dashboard: **không còn chuỗi hiển thị "Javis"/"Javis OS"** ở chrome sản phẩm (title, sidebar, login, welcome, workspace mặc định, thông báo, thẻ cập nhật, nhãn i18n). Grep kiểm chứng cho từng patch = 0.
5. Cập nhật `ops/so-tron.md` (khối vòng GĐ2) + viết `bao-cao/GD2.md` (mục 9.4). Push `me`.

## Hạn chót
Không gấp. Xong thì **báo trạm #1 nghiệm thu** (đọc diff `main..me`, chạy mọi `kiem_chung`, mở app kiểm mắt) trước khi tính phát hành `thansa-v1.0`.
