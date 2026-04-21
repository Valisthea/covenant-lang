# Covenant Manifesto — Changes v2.0 → v2.1

## Date
April 2026

## Reason
V0.1 Basics shipped. First public contract deployed on Ethereum Sepolia at `0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133`.
Manifesto content updated to reflect reality.

## Changes

### Cover
- Metadata bar: "v2.0" → "v2.1 · V0.1 shipped"
- Description: added "Version 0.1 Basics is live" phrase

### Preamble
- Removed "first usable release is planned 24 to 36 months out" (outdated)
- Replaced with "V0.1 Basics shipped April 2026 with the first public contract deployed on Ethereum Sepolia"
- Updated closing: "realistic roadmap" → "current state"

### New status block
- Added between preamble and section 01
- CSS classes added to existing `<style>` block: `.status-block`, `.status-label`, `.status-headline`, `.status-body`, `.status-artifact`, `.status-meta`
- Announces V0.1 with first deployment link (Sepolia Etherscan)
- Notes unaudited / experimental / research-release status
- Metadata line: chain, compiler tag, source line count, bytecode size

### Section 07 Roadmap (opening prose)
- Replaced future-tense "This roadmap is presented with honesty..." with past-tense acknowledgement of design phase completion and V0.1 shipment
- Added: "The roadmap has begun. The design phase is complete."

### Section 07 Roadmap (phase blocks)
- Replaced 4 old phases (Design / V0 / V1 / V2) with 6 updated phases:
  - Design: 2025–early 2026 — marked as complete
  - V0.1 Basics: April 2026 — marked as shipped, with Sepolia link and compiler tag
  - V0.2 Intermediate: 2026–2027 — fhEVM-class contracts
  - V0.3 Advanced: 2027 — amnesia, ZK, reputation primitives
  - V1.0 GA: 2028 — feature completeness, audit, tooling
  - V1.5 Formal: 2028–2029 — Coq/Lean, CL5 conformance
- Updated closing paragraph to acknowledge V0.1 as proof of execution

### Section 08 Team and recruitment
- Added one sentence referencing compiler tag `v0.1.0-basics` and Sepolia deployment as evidence of a working artifact for contributors

### Section 10 Invitation
- Added one sentence at the opening: contributors now have a working compiler to inspect, not just a specification

### Footer
- Version bump: "Version 2.0" → "Version 2.1 · V0.1 Basics"
- Added link to first Sepolia deployment

## New files
- `kairos-lab-covenant-landing.html` — minimal self-contained landing for `kairos-lab.org/covenant` deployment
- `CHANGES.md` — this file

## Files unchanged
- All CSS, fonts, favicons, OG images, section numbering (01–10)
- Sections 01–06, 09
- Visual layout, color palette, typography
- "The river has its language now." closing line
- LICENSE files, `vercel.json`, `robots.txt`, `sitemap.xml`, `package.json`
