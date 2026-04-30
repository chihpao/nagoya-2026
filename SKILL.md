# Skill: Nagoya 2026 Site Maintenance

## Purpose

This document defines a focused maintenance skill for this repository:

- Keep the travel site visually consistent
- Keep gallery interactions smooth with large image sets
- Keep image assets and naming predictable

Authoritative guardrails are defined in `AGENTS.md`.
When this file and `AGENTS.md` overlap, treat `AGENTS.md` as the UI/product requirement source of truth.

## Scope

- `index.html`
- `album.html`
- `data/photos.json`
- `data/album.manifest.js`
- `scripts/migrate_photos_to_r2.py`
- `scripts/fill_photos_urls.py`
- `scripts/set-r2-env.ps1`
- `README.md`
- `AGENTS.md`

## Working Rules

1. Do not remove full-bleed image sections unless explicitly requested.
2. Do not place hero headline text directly over the hero image unless explicitly requested.
3. Keep UI copy and labels in Traditional Chinese (`zh-Hant`) unless explicitly requested.
4. Keep navbar architecture as:
   - Fixed top navigation
   - Journey link (`#journey` on index, `index.html#journey` on album page)
   - Album link (`album.html#album` from index, `#album` on album page)
   - Preserve agreed navigation behavior (including smooth scroll for in-page anchors)
5. Keep gallery architecture as:
   - Day preview cards on home
   - Dedicated album page for all photos
   - Day-based filtering (Day 1-7)
   - Batch rendering for performance
6. Keep keyboard support in lightbox:
   - `ArrowLeft`: previous
   - `ArrowRight`: next
   - `Escape`: close
7. Keep index first-screen 3D-lite experience:
   - Keep Three.js world section with graceful fallback
   - Keep desktop controls (`WASD`/Arrow, `Shift`, `Space`)
   - Keep mobile controls (virtual joystick + boost/jump touch buttons)
   - Keep checkpoint interaction (click jump + auto-jump toggle)
8. Do not remove/replace 3D-lite architecture unless explicitly requested.

## Album Data Update Procedure

When adding new photos:

1. Prepare source images under `images/` (or provide `--source-dir`).
2. Run `python scripts/migrate_photos_to_r2.py --upload --skip-existing`.
3. Ensure `data/photos.json` contains non-empty R2 `url` values.
4. Regenerate `data/album.manifest.js` from `photos.json` when needed for fallback.
5. Verify day switch + load more + lightbox navigation on `album.html`.
6. Verify home day preview cards still render on `index.html`.

## Performance Checklist

- Keep `loading="lazy"` for gallery thumbnails
- Keep batch rendering enabled (`BATCH_SIZE`)
- Avoid rendering all 100+ images in initial viewport
- Keep 3D-lite responsive and avoid heavy geometry/material counts without clear value

## Content Checklist

- README reflects latest page architecture and file conventions
- Workflow description matches `.github/workflows/deploy-pages.yml`
- `photos.json` / `album.manifest.js` stay consistent with current R2 public URL
- No broken image paths in `index.html` and `album.html`
