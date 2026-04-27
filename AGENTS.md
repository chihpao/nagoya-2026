# AGENTS.md

## Purpose

This document defines non-negotiable product and UI rules for the Nagoya 2026 site.
Any AI or contributor modifying this repo must follow these rules unless the user explicitly asks to change them.

## Source Of Truth

- Primary page: `index.html`
- Album data source: `data/album.manifest.js` (fallback allowed only when manifest is unavailable)

## Non-Negotiable UI Requirements

1. Full-bleed images are required.
2. Do not replace full-bleed sections with timeline-style blocks unless explicitly requested.
3. Do not place main headline/body text directly on top of hero/day photos unless explicitly requested.
4. Keep Traditional Chinese (`zh-Hant`) as the default UI language for visible labels and copy.

## Album Requirements (Must Keep)

1. Album must be organized by Day 1 to Day 7.
2. Keep day preview cards on the home/album entry area.
3. Keep a full album modal with day switching tabs (Day 1-7).
4. Keep batch rendering / load-more behavior for performance.
5. Keep lightbox viewer with keyboard support:
   - `ArrowLeft`: previous
   - `ArrowRight`: next
   - `Escape`: close

## Navbar Requirements (Must Keep)

1. Navbar stays fixed at top and works on desktop and mobile.
2. Navbar must include at least:
   - Journey link (`#journey`)
   - Album link (`#album`)
3. Do not remove smooth-scroll navigation behavior.
4. Do not redesign or remove agreed navbar behavior without explicit user request.

## Change Control Rules For AI

1. Before changing layout architecture (hero/day sections, album flow, navbar behavior), get explicit user approval.
2. Visual redesign is allowed only if all requirements in this file remain satisfied.
3. If a request conflicts with this file, follow the user’s latest explicit request and then update this file in the same change.

## Quick Acceptance Checklist

1. Full-bleed image sections still exist.
2. No unintended text-over-image regression.
3. UI is Traditional Chinese.
4. Album still supports Day 1-7 preview + modal + tabs + load more + lightbox keyboard control.
5. Navbar links and behavior still work.
