# AGENTS.md

## Purpose

This document defines non-negotiable product and UI rules for the Nagoya 2026 site.
Any AI or contributor modifying this repo must follow these rules unless the user explicitly asks to change them.

## Source Of Truth

- Primary pages: `index.html` and `album.html`
- Album/photo data source: `data/photos.json` (fallback to `data/album.manifest.js` when photos json is unavailable)

## Current Design Direction (Baseline)

1. Visual direction is "playful / game-like / bold" (Bruno Simon inspired), not minimal corporate style.
2. Keep strong contrast, thick borders, sticker-like chips, and expressive motion as the default art direction.
3. Keep Traditional Chinese (`zh-Hant`) as the visible UI language.
4. Maintain mobile + desktop parity for major interactions.

## Non-Negotiable UI Requirements

1. Full-bleed images are required.
2. Do not replace full-bleed sections with timeline-style blocks unless explicitly requested.
3. Do not place main headline/body text directly on top of hero/day photos unless explicitly requested.
4. Keep Traditional Chinese (`zh-Hant`) as the default UI language for visible labels and copy.

## Index 3D-Lite Requirements (Must Keep)

1. `index.html` keeps a Three.js "3D-lite world" section as first-screen interactive content.
2. The 3D section must degrade gracefully:
   - If WebGL unavailable, show fallback message and keep the rest of page fully usable.
3. Keep journey content architecture after 3D section:
   - Full-bleed photos + Day 1-7 story sections remain intact.
4. Keep 3D interaction model:
   - Keyboard: `WASD` / Arrow keys movement, `Shift` boost, `Space` jump.
   - Pointer drag rotates camera view.
   - Checkpoints are clickable and can jump to Day sections.
5. Keep mobile-first 3D controls:
   - Virtual joystick
   - Touch boost button
   - Touch jump button
6. Keep "auto-jump to checkpoint section" toggle behavior:
   - Toggle available in 3D controls (desktop + mobile)
   - State changes visible in UI label.

## Album Requirements (Must Keep)

1. Album must be organized by Day 1 to Day 7.
2. Keep day preview cards on the home/album entry area.
3. Keep a dedicated album page (`album.html`) with day switching tabs (Day 1-7).
4. Keep batch rendering / load-more behavior for performance.
5. Keep lightbox viewer with keyboard support:
   - `ArrowLeft`: previous
   - `ArrowRight`: next
   - `Escape`: close

## Navbar Requirements (Must Keep)

1. Navbar stays fixed at top and works on desktop and mobile.
2. Navbar must include at least:
   - Journey link (`#journey` or `index.html#journey`)
   - Album link (`album.html#album` or `#album` on album page)
3. Keep smooth-scroll behavior for in-page anchor navigation.
4. From `index.html`, clicking navbar `相簿` must enter the dedicated album page (`album.html`) instead of long-page scrolling.
5. Do not redesign or remove agreed navbar behavior without explicit user request.

## Change Control Rules For AI

1. Before changing layout architecture (hero/day sections, album flow, navbar behavior), get explicit user approval.
2. Before removing/replacing the 3D-lite section or changing its core interaction model, get explicit user approval.
3. Visual redesign is allowed only if all requirements in this file remain satisfied.
4. If a request conflicts with this file, follow the user’s latest explicit request and then update this file in the same change.

## Quick Acceptance Checklist

1. Full-bleed image sections still exist.
2. No unintended text-over-image regression.
3. UI is Traditional Chinese.
4. `index.html` still has 3D-lite section with fallback mode and usable controls on desktop/mobile.
5. Home still has Day 1-7 preview cards and each day can open the dedicated album page.
6. Album page still supports Day 1-7 tabs + load more + lightbox keyboard control.
7. Navbar links and behavior still work on both pages.
