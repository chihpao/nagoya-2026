# nagoya-2026

2026/04/01-2026/04/07 名古屋旅行紀錄網站

## 目前網站架構

- 首頁旅程頁: `index.html`
  - 首屏保留 Three.js `3D-lite` 互動世界（含 WebGL fallback）
  - 保留 Day 1-7 全版圖片旅程段落
  - 保留首頁 Day 預覽卡（相簿入口）
  - Navbar `相簿` 直接導向獨立相簿頁 `album.html#album`
- 相簿頁: `album.html`
  - Day 1-7 分頁切換
  - 批次載入（Load More）
  - Lightbox 鍵盤操作 (`ArrowLeft` / `ArrowRight` / `Escape`)
- 相簿資料來源: `data/album.manifest.js`
  - 若 manifest 不可用，頁面會用內建 fallback 圖片清單

## 設計方向（目前基準）

- 視覺方向: playful / game-like / bold（Bruno Simon 靈感）
- 表現語言: 高對比色塊、厚邊框、貼紙感、明顯動態
- 文案語系: `zh-Hant` 為主
- 原則: 功能優先，不為了造型破壞既有 Day 1-7 與相簿流程

## 3D-Lite 首屏規格（index）

- 技術: Three.js module（CDN 載入）
- 鍵盤操作:
  - `WASD` / `Arrow` 移動
  - `Shift` 加速
  - `Space` 跳躍
- 滑鼠/觸控:
  - Pointer 拖曳視角
  - 站點可點擊跳轉到對應 Day 區塊
- 手機控制:
  - 虛擬搖桿
  - 觸控加速按鈕
  - 觸控跳躍按鈕
- 站點互動:
  - 可切換「自動跳轉：開/關」
  - 靠近站點時可自動 smooth scroll 到對應 Day 區塊
- 退化策略:
  - WebGL 不可用時顯示 fallback，不影響後續旅程與相簿瀏覽

## 本機預覽

```powershell
python -m http.server 8000
```

打開 `http://localhost:8000/index.html` 與 `http://localhost:8000/album.html`

## Album Pipeline (WebP + R2 + photos.json)

1. 安裝依賴

```powershell
python -m pip install -r requirements-r2.txt
```

2. 填入 R2 環境變數（可從 `.env.r2.example` 複製）
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`
- `R2_PUBLIC_URL`

3. 只做掃描 + WebP 轉檔 + `data/photos.json` 產出

```powershell
python scripts/migrate_photos_to_r2.py
```

4. 轉檔 + 上傳 R2 + 將完整 URL 寫入 `data/photos.json`

```powershell
python scripts/migrate_photos_to_r2.py --upload
```

5. 上傳成功後再刪除 repo 原始圖片（可選）

```powershell
python scripts/migrate_photos_to_r2.py --upload --delete-originals
```

補充：若要把 HEIC/HEIF 一起轉 WebP，可加上 `--extensions .jpg,.jpeg,.png,.gif,.heic,.heif`

## 部署注意事項（GitHub Actions / GitHub Pages）

- `.github/workflows/deploy-pages.yml` 使用 `path: '.'` 上傳整個 repo 當部署內容。
- 因此新增 `album.html` 會自動一起部署，不需額外調整 workflow。
- 目前 CI 不做圖片壓縮或轉檔，僅負責靜態網站部署。
