---
title: "Styx Protocol — ERCs Overview"
description: "The four Ethereum Improvement Proposals that standardize Covenant's cryptographic primitives on-chain."
section: reference
order: 1
level: reference
---

<!-- Source: Styx Protocol specification, doc3-stdlib-spec.md §12, doc1-whitepaper.md -->
<!-- Last sync: 2026-04-23 -->

# Styx Protocol — ERCs Overview

Covenant's cryptographic primitives are not proprietary extensions — they are standardized through four Ethereum Improvement Proposals collectively called the **Styx Protocol**. Each ERC defines an on-chain interface that any EVM-compatible contract can implement, whether written in Covenant, Solidity, or Vyper.

## The Four Standards

| ERC | Title | Covenant Surface | Status |
|-----|-------|-----------------|--------|
| [ERC-8227](/docs/reference/ercs/02-erc-8227-fhe) | Encrypted Tokens and State | `encrypted<T>`, `reveal`, FHE precompiles | Draft |
| [ERC-8228](/docs/reference/ercs/03-erc-8228-amnesia) | Cryptographic Amnesia | `amnesia { }`, `ceremony`, `destroy()` | Draft |
| [ERC-8229](/docs/reference/ercs/04-erc-8229-fhe-verify) | FHE Verification Standard | `verified_by`, `selective_disclosure`, `@prove_offchain` | Draft |
| [ERC-8231](/docs/reference/ercs/05-erc-8231-pq) | Post-Quantum Key Registry | `pq_key`, `@pq_signed` | Draft |

All four ERCs are currently in Draft status. The target for Final status is Q4 2026, with ERC-8227 (FHE Tokens) scheduled to move to Review first due to its broader applicability.

## What Is an ERC?

An **Ethereum Request for Comment** is a proposal that defines a standard interface for contracts on the EVM. Well-known examples: ERC-20 (fungible tokens), ERC-721 (NFTs), ERC-4337 (account abstraction).

ERCs become standards through community review, implementation, and adoption. Covenant implements all four Styx ERCs natively — when you write `encrypted token` in Covenant, the compiler generates an ERC-8227-compliant contract automatically.

## Implementation Profiles

The Styx specification defines five compliance profiles (CL1–CL5) to allow incremental adoption:

| Profile | Requirements | Typical use |
|---------|-------------|-------------|
| CL1 | ERC-8227 storage interface only (no on-chain computation) | Off-chain FHE with on-chain ciphertext storage |
| CL2 | CL1 + `fhe_add` / `fhe_mul` precompiles | Basic confidential arithmetic (payroll, balances) |
| CL3 | CL2 + `fhe_cmp` + threshold decryption | Sealed auctions, private voting |
| CL4 | CL3 + ERC-8229 ZK verification | Publicly verifiable FHE computations |
| CL5 | CL4 + ERC-8228 amnesia + ERC-8231 PQ signatures | Full Styx compliance |

Covenant V0.7 contracts compile to **CL5** by default when using all features. You can constrain the output profile using the `--compliance-profile` flag:

```bash
covenant build --compliance-profile CL2 ./src/Payroll.cvt
```

## How ERCs Map to Covenant Constructs

```
Covenant source                →  ERC standard         →  EVM precompile
─────────────────────────────────────────────────────────────────────────
encrypted<uint256>             →  ERC-8227 §3.1         →  0x0f (fhe_encrypt)
fhe_add(a, b)                  →  ERC-8227 §3.2         →  0x10 (fhe_add)
reveal field to caller         →  ERC-8227 §3.4         →  0x13 (fhe_decrypt_auth)
amnesia { destroy(secret) }    →  ERC-8228 §2           →  0x20 (amnesia_destroy)
ceremony { ... }               →  ERC-8228 §4           →  0x21–0x24 (phase management)
zk_verify(proof, signal)       →  ERC-8229 §2           →  0x30 (zk_verify)
@prove_offchain                →  ERC-8229 §5           →  (off-chain WASM circuit)
pq_key type                    →  ERC-8231 §2           →  0x40 (pq_register)
@pq_signed(key)                →  ERC-8231 §3           →  0x41 (pq_verify)
```

## Standardization Timeline

| Milestone | Target date |
|-----------|-------------|
| ERC-8227 Draft | ✅ Q1 2026 |
| ERC-8228 Draft | ✅ Q1 2026 |
| ERC-8229 Draft | ✅ Q2 2026 |
| ERC-8231 Draft | ✅ Q2 2026 |
| ERC-8227 Review | Q3 2026 |
| ERC-8228 Review | Q3 2026 |
| ERC-8229/8231 Review | Q4 2026 |
| ERC-8227 Final | Q4 2026 |
| ERC-8228/8229/8231 Final | 2027 |
| Ethereum mainnet precompile proposals | 2027–2028 |

## Relation to the Covenant Compiler

The Covenant compiler (V0.7) generates ERC-8227/8228/8229/8231 compliant bytecode without requiring any manual ABI wiring. If you write:

```covenant
encrypted token ConfidentialUSDC {
    name: "Confidential USDC"
    symbol: "cUSDC"
    decimals: 6
}
```

The compiler generates:
- The ERC-8227 `IConfidentialToken` interface implementation
- The correct precompile call sequences
- The CBOR metadata blob with ERC ID annotations

If you're building tooling (block explorers, wallets, bridge relayers) that needs to interact with Covenant contracts without the Covenant compiler, the ERC specifications are your source of truth.

## See Also

- [ERC-8227 — Encrypted Tokens](/docs/reference/ercs/02-erc-8227-fhe)
- [ERC-8228 — Cryptographic Amnesia](/docs/reference/ercs/03-erc-8228-amnesia)
- [ERC-8229 — FHE Verification Standard](/docs/reference/ercs/04-erc-8229-fhe-verify)
- [ERC-8231 — Post-Quantum Key Registry](/docs/reference/ercs/05-erc-8231-pq)
- [Glossary: FHE](/docs/glossary#fhe), [ZK proofs](/docs/glossary#zk-proof), [PQ signatures](/docs/glossary#pq-signature)
