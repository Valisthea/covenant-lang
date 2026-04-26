---
title: "Audit History"
description: "OMEGA audit history across V0.6, V0.8, and V0.9 — 60 findings total, all resolved or mitigated."
order: 1
section: "Security"
---

# OMEGA Audit History

Covenant has cleared three audit cycles. Each is documented here with severity counts, scope, and resolution status. External audit by a third-party firm gates V1.0 mainnet.

## OMEGA V5 — V0.9 (April 2026)

**Auditor:** Kairos Lab internal (OMEGA V5 methodology)  
**Audit period:** Sprint 46 of V0.9 master plan  
**Version audited:** Covenant compiler v0.9.0  
**Methodology:** Empirical-loop-driven self-audit. Every claim grounded in a runnable command whose output was observed.  
**Status:** ✅ GO — all 10 verifications cleared

### Verifications

1. **Build hygiene** — 1206 tests passing (1172 Rust + 34 Foundry), 0 clippy warnings on `-D warnings`, 1 documented residual cargo audit advisory (idna transitive, no IDN code path)
2. **Helper bridge end-to-end** — CeremonyHelper deployed at deterministic CREATE2 on Sepolia, lifecycle (setup → submit_share → finalize → destroy) verified on Etherscan
3. **NFT auto-synthesis** — 11 ERC-721 functions emitted from 5-line declaration, ABI matches normative spec
4. **Registry auto-synthesis** — 5 ERC-8231 functions emitted from 1-line declaration, Dilithium-5 algorithm ID returned
5. **Interface lowering** — typed cross-contract calls produce single CALL with correct selector + ABI encoding
6. **CLI per-test isolation** — `covenant test` runs each test in fresh state, no cross-test pollution
7. **Linter ICE bug** — found and fixed during audit pack assembly (was crashing on `interface` blocks)
8. **9 audit fixtures** — all compile end-to-end on both MockChain and Sepolia targets
9. **M0 + M1 milestones** — both deployments live and verifiable on Sepolia Etherscan
10. **Documentation deliverables** — SECURITY.md, audit scope, threat model, helper deep-dive, audit fixture pack all complete

### Bugs caught empirically during the cycle

5 bugs were discovered through audit-pack-driven fuzzing and reading the helper bridge integration code. All were fixed before the V0.9.0 tag. Details in the [full audit report](https://github.com/Valisthea/covenant/blob/main/OMEGA_V5_AUDIT_REPORT.md).

### Conditions on V1.0 mainnet

NOT met. V1.0 requires:

- Real cryptographic primitives (Zama TFHE, real Dilithium-5 verifier, Halo2 on-chain)
- External audit by a third-party firm
- Mainnet helper deployment
- Partial formal verification (privacy flow soundness)
- 3+ production protocol deployments validating the model

## OMEGA V4 — V0.8 (April 2026)

**Auditor:** Kairos Lab internal  
**Audit period:** April 2026 (V0.8 GA preparation)  
**Version audited:** Covenant compiler v0.8.0  
**Status:** 9 findings · 8 verified + 1 mitigated (KSR-CVN-005, fully resolved in V0.9)

### Findings

- Playground multi-target architecture verified
- Mainnet hard-refusal path validated
- WASM/JS boundary documented
- KSR-CVN-005 (no executor at OP_CALL precompiles `0x124–0x127` on Sepolia) → mitigated in V0.8 with documentation, fully resolved in V0.9 via the helper-contract bridge

## OMEGA V4 — V0.6 (December 2025 → January 2026)

**Auditor:** OMEGA Security Labs  
**Audit period:** November 4 – December 20, 2025  
**Version audited:** Covenant compiler v0.7.0-rc3  
**Report date:** January 10, 2026  
**Status:** All 41 findings resolved ✓

## Executive summary

OMEGA Security Labs conducted a comprehensive audit of the Covenant compiler, runtime library, and standard contract library. The audit covered:

- Covenant compiler (Rust codebase, ~48,000 LOC)
- EVM code generation backend
- FHE precompile integration layer
- ZK proof verification circuits
- Post-quantum signature verifier
- Cryptographic amnesia two-pass erasure protocol
- Standard library contracts (ERC-20, UUPS, Beacon, etc.)

**41 findings were identified. All 41 have been resolved.**

## Finding summary

| Severity | Count | Resolved |
|----------|-------|---------|
| Critical | 5 | 5 ✓ |
| High | 9 | 9 ✓ |
| Medium | 14 | 14 ✓ |
| Low | 9 | 9 ✓ |
| Informational | 4 | 4 ✓ |
| **Total** | **41** | **41 ✓** |

## Critical findings overview

All 5 critical findings are described in detail in the [Critical Findings](/security/critical-findings) page.

| ID | Title | Status |
|----|-------|--------|
| CVN-001 | FHE ciphertext malleability in `fhe_add` | Fixed in v0.7.0-rc5 |
| CVN-002 | Amnesia pass-1 randomness is predictable on low-entropy chains | Fixed in v0.7.0-rc5 |
| CVN-003 | UUPS `_upgrade` missing ERC-1822 magic check | Fixed in v0.7.0-rc4 |
| CVN-004 | PQ key registry bypass via zero-length signature | Fixed in v0.7.0-rc5 |
| CVN-005 | ZK verifier accepts proof for wrong circuit ID | Fixed in v0.7.0-rc5 |

## Audit methodology

1. **Automated analysis** — Slither, Semgrep, and OMEGA's proprietary FHE taint-analysis tool
2. **Manual code review** — line-by-line review of all compiler output paths
3. **Property-based fuzzing** — 72-hour Echidna campaign on the standard library
4. **Formal verification** — critical paths modelled in Lean 4; proofs machine-checked
5. **Differential testing** — Covenant-generated bytecode compared against reference Solidity for 200 test cases

## Recommendations implemented

All OMEGA recommendations were implemented before the V0.7 GA release:

- **CEI enforcement**: compiler now statically checks and rejects checks-effects-interactions violations unless explicitly overridden
- **Reentrancy auto-detection**: the LSP flags missing `@nonreentrant` on any action making external calls
- **FHE parameter validation**: scheme-specific parameter bounds checked at compile time
- **Amnesia log suppression**: event emission inside `amnesia { }` blocks now raises a compiler error

## Full report

The complete 147-page report is available at: [covenant-lang.org/omega-v4-audit.pdf](https://covenant-lang.org/omega-v4-audit.pdf)
