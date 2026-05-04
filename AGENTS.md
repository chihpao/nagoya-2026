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
6. Keep mobile album controls usable without desktop precision:
   - Previous/next day buttons
   - Active day tab visible/centered after switching
   - Clear visible/total photo progress
7. Keep album view density controls:
   - Comfortable mode for larger mobile thumbnails
   - Dense mode for fast scanning
8. Keep touch support in the lightbox:
   - Horizontal swipe changes photos
   - Close button remains reachable on mobile

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
6. Album page still supports Day 1-7 tabs + mobile previous/next day controls + load more.
7. Album page still supports comfortable/dense gallery modes and visible photo progress.
8. Lightbox still supports keyboard control and mobile swipe control.
9. Navbar links and behavior still work on both pages.
10. Footer exists on both pages with correct content.

## Footer Requirements (Must Keep)

1. Both pages must have a footer with the site brand, date range, and tagline.
2. Footer uses dark background (`#0f172a`) with light text for contrast.
3. Footer must respect `safe-area-inset-bottom` on mobile.
4. Footer must not obstruct the mobile bottom day nav on album page.

## SEO & Meta Requirements

1. Both pages must include `<meta name="description">` with relevant content.
2. Both pages must include Open Graph tags (`og:title`, `og:description`, `og:type`).
3. Each page must have a unique, descriptive `<title>`.
4. Use semantic HTML5 elements (`<header>`, `<main>`, `<footer>`, `<nav>`, `<section>`, `<article>`).
5. Each page has exactly one `<h1>`.

## Accessibility Baseline

1. All interactive elements must have minimum 44×44px touch targets on mobile.
2. All images must have `alt` attributes.
3. Lightbox must trap focus when open and restore focus on close.
4. `prefers-reduced-motion: reduce` must disable all animations and transitions.
5. ARIA attributes must be present on dynamic UI (tabs, dialogs, live regions).

## Performance Budget

1. Keep `loading="lazy"` on all gallery thumbnails.
2. Keep batch rendering with `BATCH_SIZE` — never render all photos at once.
3. 3D scene should not exceed ~40 geometry objects without clear value.
4. Photos served from R2 CDN in WebP format for bandwidth efficiency.
