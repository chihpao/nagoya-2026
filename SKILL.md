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
- `images/`
- `.github/workflows/image-optimization.yml`
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

## Image Conventions

- Store all assets in `images/`
- Use day-prefixed file names for scalable data entry:
  - `day1-001.jpg` ... `day1-999.jpg`
  - ...
  - `day7-001.jpg` ... `day7-999.jpg`
- Avoid spaces in file names

## Album Data Update Procedure

When adding new photos:

1. Put files into `images/album/day1` ... `images/album/day7`
2. Run `powershell -ExecutionPolicy Bypass -File .\scripts\generate-album-manifest.ps1`
3. Ensure `data/album.manifest.js` is regenerated
4. Verify day switch + load more + lightbox navigation on `album.html`
5. Verify home day preview cards still render on `index.html`

## Performance Checklist

- Keep `loading="lazy"` for gallery thumbnails
- Keep batch rendering enabled (`BATCH_SIZE`)
- Avoid rendering all 100+ images in initial viewport
- Keep 3D-lite responsive and avoid heavy geometry/material counts without clear value

## Content Checklist

- README reflects latest page architecture and file conventions
- Workflow description matches `.github/workflows/image-optimization.yml`
- No broken image paths in `index.html` and `album.html`
