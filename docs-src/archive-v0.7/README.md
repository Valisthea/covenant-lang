# Covenant V0.7 GA — Docs Archive

This directory is a frozen snapshot of the documentation content as of the V0.7 GA release (2026-04-23). It exists so contributors can diff the V0.7 content against the current (V0.8 GA) content to understand what the living docs changed release-over-release.

**This archive is not built by Astro.** It is purely a reference artifact. The authoritative archived V0.7 docs are the git tag:

- Upstream tag: `v0.7.0` on the compiler repo (`github.com/Valisthea/covenant`, private until V1.0)
- This site: checkout tag `v0.7.0-site` to see the live V0.7 docs tree

If you need to publish V0.7 docs on a subdomain in the future, promote this directory into an Astro content collection under `src/content/v0.7/` and add a sibling collection entry in `src/content.config.ts`.

## What's in this snapshot

| Directory | Purpose |
|---|---|
| `docs/` | The 15 Basics tutorials as they existed at V0.7 GA. |
| `cookbook/` | 30+ V0.7 cookbook recipes. |
| `reference/` | V0.7 compiler, ERC, and LSP reference material. |
| `migration/` | V0.7 migration guides (including the deprecated V0.7→V0.8 draft). |
| `security/`, `getting-started/`, `glossary/` | V0.7 frozen copies. |

## See also

- Current (V0.8 GA) docs: `../src/content/`
- V0.8 release notes: `https://github.com/Valisthea/covenant-lang/blob/main/RELEASE_NOTES_v0.8.md` (on the compiler repo, public slice)
- V0.7 → V0.8 migration guide: `../src/content/migration/between-versions/v07-to-v08.md`
