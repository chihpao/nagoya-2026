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
- `images/`
- `.github/workflows/image-optimization.yml`
- `README.md`

## Working Rules

1. Do not remove full-bleed image sections unless explicitly requested.
2. Do not place hero headline text directly over the hero image unless explicitly requested.
3. Keep UI copy and labels in Traditional Chinese (`zh-Hant`) unless explicitly requested.
4. Keep navbar architecture as:
   - Fixed top navigation
   - Journey link (`#journey`)
   - Album link (`#album`)
   - Preserve agreed navigation behavior (including smooth scroll)
5. Keep gallery architecture as:
   - Day preview cards on home
   - Full album modal for all photos
   - Day-based filtering (Day 1-7)
   - Batch rendering for performance
6. Keep keyboard support in lightbox:
   - `ArrowLeft`: previous
   - `ArrowRight`: next
   - `Escape`: close

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
4. Verify day switch + load more + lightbox navigation

## Performance Checklist

- Keep `loading="lazy"` for gallery thumbnails
- Keep batch rendering enabled (`BATCH_SIZE`)
- Avoid rendering all 100+ images in initial viewport

## Content Checklist

- README reflects latest gallery behavior and file conventions
- Workflow description matches `.github/workflows/image-optimization.yml`
- No broken image paths in `index.html`
