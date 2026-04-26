---
title: "V0.9.0 Changelog"
description: "Production-real cryptographic primitives on Sepolia · ERC-721 + ERC-8231 auto-synthesis · Foundry-class CLI · OMEGA V5 audit cleared."
order: 0
section: "Releases"
level: reference
---

# V0.9.0 GA Changelog

The production-real release. Cryptographic primitives execute on Sepolia for the first time. Three new top-level constructs. Foundry-class CLI tooling. OMEGA V5 audit cleared.

**Tag:** [v0.9.0](https://github.com/Valisthea/covenant/releases/tag/v0.9.0)  
**Released:** April 2026  
**Compatibility:** Fully backward-compatible with V0.8 source. No breaking changes.

## Helper-Contract Bridge

Cryptographic primitives now route to dedicated helper contracts on each target chain. The compiler embeds CREATE2-deterministic helper addresses based on `--target-chain`.

- **CeremonyHelper** — real ERC-8228 lifecycle on Sepolia (setup → submit_share → finalize → destroy)
- **FHEHelper** — mocked TFHE (deterministic, gas-cheap; real Zama integration at V1.0)
- **PQHelper** — mocked Dilithium-5 verify (correct interface, simplified logic; real at V1.0)
- **ZKHelper** — mocked Halo2 verifier (correct interface; real at V1.0)
- All four deployed via deterministic CREATE2 on Sepolia
- Compiler routes to helper addresses per `--target-chain` flag

Resolves KSR-CVN-005 (V0.8 OMEGA V4: no executor at OP_CALL precompiles on Sepolia).

## New Top-Level Constructs

V0.9 brings the construct count from 14 to 17:

- **`nft`** — ERC-721 auto-synthesis (515-line synthesizer, 11 functions)
- **`registry`** — ERC-8231 auto-synthesis (340-line synthesizer, 5 functions)
- **`interface`** — declares external contract surfaces for typed cross-contract calls

See [16-nft](/docs/examples/16-nft), [17-registry](/docs/examples/17-registry), [18-external-call](/docs/examples/18-external-call).

## CLI Tooling

Foundry-class developer ergonomics:

- `covenant test` — per-test isolation, watch mode (`--watch`), name-heuristic coverage (`--coverage`)
- `covenant fmt` — canonical formatting, `--check` for CI
- `covenant doctor` — 9 environment probes
- `covenant lint` — 6-rule Solidity-ism detector (L001–L006)
- `covenant init` — scaffold from template (token, ceremony, defi)
- `covenant explain <code>` — long-form diagnostic explanations
- `covenant build --target-chain {mockchain|sepolia|aster}` — per-chain helper embedding

See [CLI reference](/docs/getting-started/03-cli-reference).

## Diagnostics + Linter

- LSP gains `goto_definition` and `find_definition_at()`
- 6-rule linter (`covenant-lint`):
  - L001 — `mapping(...)` → `map<...>`
  - L002 — `function` → `action`
  - L003 — `// comment` → `-- comment`
  - L004 — `require(...)` → `given` / `revert_with`
  - L005 — `pragma solidity` → drop
  - L006 — `import "..."` → drop or replace
- Configure via `.covenantlint.json`

## Playground

- Cross-tab sync via BroadcastChannel
- IndexedDB persistence (state survives refresh)
- Named event display (human-readable instead of raw hex topics)
- 12+ verified examples including `nft`, `registry`, `interface`
- 12+ guided tour lessons

## Audit — OMEGA V5

- 10 verifications, all GO
- 1206 tests passing (1172 Rust unit/integration + 34 Foundry)
- 0 clippy warnings on `-D warnings`
- 9 audit fixtures compile end-to-end on both MockChain and Sepolia
- 5 bugs caught empirically during the audit cycle, all fixed before tag

[Full report](https://github.com/Valisthea/covenant/blob/main/OMEGA_V5_AUDIT_REPORT.md)

## Milestones

- **M0** — First Covenant contract on Sepolia ([0xab083fc4…](https://sepolia.etherscan.io/address/0xab083fc4))
- **M1** — First ceremony destruction on Sepolia ([0x2FB87d54…](https://sepolia.etherscan.io/address/0x2FB87d54))

## Known Limitations

- FHE / PQ / ZK helpers are mocked (correct interfaces, simplified logic). Real crypto lands in V1.0.
- Aster Chain: codegen ready, deploy gated on factory verification (M2 milestone).
- 1 cargo audit advisory (idna transitive via tower-lsp) — accepted residual, no IDN code path.

## Compatibility

- Source: backward-compatible with V0.7 and V0.8 — every existing `.cov` file compiles unchanged.
- Bytecode: changes when `--target-chain` differs. Same source, different chain → different helper addresses → different deployed bytecode (correct behavior).
- ERCs: 8227, 8228, 8229, 8231 surfaces unchanged. V0.9 adds reference impls via the helper bridge.

## Next

- [V0.8 → V0.9 migration guide](/docs/migration/between-versions/v08-to-v09)
- [Audit history](/docs/security/audit-report)
- [V1.0 trajectory](/manifesto#section-05)
