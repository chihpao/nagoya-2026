# nagoya-2026
2026/04/01-04/07 名古屋旅行

## Album Pipeline (WebP + R2 + manifest.json)

1. Install dependencies:

```powershell
python -m pip install -r requirements-r2.txt
```

2. Fill R2 env vars (copy from `.env.r2.example`).

3. Convert and generate manifest only:

```powershell
python scripts/build_album_manifest_and_upload.py
```

4. Convert + upload to R2 + update `data/manifest.json`:

```powershell
python scripts/build_album_manifest_and_upload.py --upload
```

Notes:
- Source images: `images/album`
- Converted images: `build/album-webp`
- Manifest output: `data/manifest.json`
