# Quy trình ĐÃ ĐỔI — trạm #2 báo trạm #1 (2026-08-25)

Loạt patch P022–P027 (fork-only, nền 0.40.0) đổi vài quy ước **dùng chung**. Trạm #1 cần
nắm để không hoà trộn sai + theo đúng khi bump/phát hành. Chi tiết đầy đủ ở `ops/so-tron.md`.

## 1. Đánh version ĐỔI HẲN — VERSION giờ mang NEO

- File `VERSION` KHÔNG còn là số Thansa thuần. Dạng mới: **`<semver-thansa>-thansa-<nền-thansa>`**
  (hiện tại `1.2.0-thansa-0.40.0`).
- Semver Thansa (phần đầu) lái nút Update + là thứ HIỂN THỊ. Đuôi `-thansa-<nền>` là NEO nội
  bộ, **ẩn khỏi mọi chỗ người dùng thấy** (UI trả `1.2.0`, tag ảnh `1.2.0`).
- **Khi bump/phát hành:** đổi `VERSION` semver Thansa, và **giữ `moc-goc.json` khớp** —
  `thansa_version` = semver Thansa, `goc_version` = nền Thansa = đúng phần sau `-thansa-`.
- **`tu-kiem-chung` có LUẬT 5 mới:** neo trong `VERSION` PHẢI == `goc_version`. Lệch = ĐỎ.
- Đã thêm `RELEASES.md` (sổ neo Thansa↔Thansa) — mỗi lần phát hành thêm một dòng.
- Hàm `_ver_thansa` (cắt neo, hiển thị/so update) + `_ver_thansa` (lấy nền, so trang Nhật ký
  vì changelog đánh số theo Thansa) ở `server/main.py`. Đừng so VERSION thô ở chỗ mới.

## 2. Kênh phát hành trỏ FORK (không upstream)

- `GITHUB_REPO` = `xahoapro/thansa-os` (override env `THANSA_UPDATE_REPO`). Nút Update +
  CHANGELOG + ANNOUNCEMENTS lấy từ fork.
- **Repo đã PUBLIC** → `raw.githubusercontent` đọc được VERSION/CHANGELOG. (Trước private nên
  404, nút Update câm.)
- Phát hành cho user vẫn là **`git push origin me:main`** (ff sạch, `me` là hậu duệ `main`);
  push lên `main` tự chạy CI + build image `ghcr.io/xahoapro/thansa-os:latest`+`:<semver>`.

## 3. Rebrand bản quyền/tên (P026–P027) — vùng ĐÃ đụng, tránh hoà trùng

- `LICENSE`: GIỮ copyright Nguyễn Minh Quý (bắt buộc theo MIT) + THÊM Duy Quang (thansa.org).
- Đổi: thansa.org→thansa.org, tradingauto.org→tradingauto.org, Minh Quý→Duy Quang,
  xahoapro/thansa-os→xahoapro/thansa-os; tên sản phẩm Thansa OS→Thansa OS trong README/docs.
- `_rebrand_hien_thi` (`server/main.py`) nay đổi cả domain/tác giả/repo (không chỉ Thansa→Thansa).
- **GIỮ NGUYÊN** (đừng rebrand): token kỹ thuật `THANSA_*`/`thansa_*`/`Thansa/` path/`thansa.service`;
  dữ liệu ví dụ trong test (`Minh Quý`/`tradingauto.org` ở test_2fa/cred/learn); `CHANGELOG.md`
  upstream (rebrand lúc hiển thị); class CSS `.bubble.thansa`; `ops/`+`bao-cao/`+`nhiem-vu/`+
  `docs/superpowers|dev` (lịch sử).

## 4. ws-disconnect — cần trạm #1

`bao-cao/BUG-ws-disconnect.md`: trạm #2 **không tái hiện** trên VPS (45+ lần xanh, đường code
test **byte-identical** v1.0↔me, chỉ nhánh CLI đổi ở 0.37.1 — test dùng api). Đề nghị trạm #1:
gửi `python -c "import sys,fastapi,starlette; print(sys.version, fastapi.__version__, starlette.__version__)"`
+ `pip freeze | grep -iE "fastapi|starlette|anyio|uvicorn"`, và chạy lại trên `me` mới nhất. Nếu
là race timing theo máy → cân nhắc nới cửa sổ chờ test (0.08s→~0.3s), nhưng trạm #1 giữ quyền test đó.

## Tình trạng cổng release

Kỹ thuật đã sẵn (public repo, version scheme, image tự build). CÒN CHẶN: (1) nghiệm thu lại
ws-disconnect; (2) chủ quyết phát hành. Trạm #2 chưa đẩy `me→main`.
