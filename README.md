# Covenant — Website and Manifesto

> The public-facing site and manifesto for [Covenant](https://github.com/Valisthea/covenant-language),
> a declarative smart contract language by [Kairos Lab](https://kairos-lab.org).

## Related repos

| What | Where | License |
|---|---|---|
| **This repo** — Website, manifesto, visual assets | github.com/Valisthea/covenant-lang | CC-BY-4.0 (content) + MIT (code) |
| **Compiler source + specs** | github.com/Valisthea/covenant-language *(private until V1.0)* | Apache-2.0 (code) + CC0-1.0 (specs) |
| **Live manifesto** | [covenant-lang.org](https://covenant-lang.org) | — |

## Current state — V0.9.4 The Fail-Loud Pass (July 2026)

Covenant's latest release closes a class of silent-miscompile bugs — the compiler now errors loudly instead of emitting wrong bytecode.

- **min/max/abs/pow/sqrt no longer miscompile to `a+b`** (E424)
- **`x / 0` with a literal `0` is a compile error**; non-literal divisors get a runtime guard (E519)
- **Text constants over 32 bytes now error** instead of truncating silently (E521)
- **Test-only actions are stripped** from on-chain output
- **Non-zero constant field defaults are now written** to storage
- **The LSP surfaces these diagnostics live** as you type
- **Deployed on Ethereum Sepolia** (milestones M0–M5) and **Robinhood testnet** (M6 — first Covenant token on Robinhood: KairosCoin at `0x3E80F8c7911240e6092D523af79B13c046bd2FdE`)
- **1082 tests passing** across a 21-crate workspace
- **Compiler tagged** `v0.9.4`

**Disclaimer** : Covenant is **testnet-only**. The cryptography is **mocked** — FHE, post-quantum, ZK, VDF and Shamir primitives are deterministic stubs with **zero confidentiality and zero security** ("encrypted" values are readable from chain state; the PQ/ZK verifiers accept forged proofs). Real cryptography is a separate, later release (V2.0). Not for deployment with production value.

## The three principles

1. **Cryptographic properties as language primitives** — `encrypted uint256` should be as native as `uint256`. The compiler, not a bundle of libraries, enforces the guarantees.
2. **Declare guarantees, not implementations** — the SQL shift. A contract states *what* it guarantees (encrypted inputs, homomorphic tally, amnesia after cycle); the compiler generates *how*.
3. **Cryptographic agility as a type-system property** — primitives are exposed via traits and security levels, not hardcoded to a specific scheme. Schemes can evolve without rewriting contracts.

## Styx Protocol as standard library

Covenant compiles against four Ethereum ERCs that form its native stdlib :

| ERC | Role | Layer |
|---|---|---|
| **ERC-8227** | Encrypted Token Standard (FHE balances) | Veil |
| **ERC-8228** | Cryptographic Amnesia Interface | Oblivion |
| **ERC-8229** | FHE Computation Verification | Prism |
| **ERC-8231** | Post-Quantum Key Registry | Fortress |

## Roadmap

| Phase | When | Status |
|---|---|---|
| Design | 2025 – early 2026 | **Complete** — 8 normative docs, Styx ERCs drafted |
| V0.9.4 Fail-Loud Pass | July 2026 | **Shipped (testnet-only)** — silent-miscompile class closed; Sepolia (M0–M5) + Robinhood testnet (M6) deploys |
| V1.0 GA | Next | External third-party audit of the compiler; still testnet-only, mocked crypto |
| V2.0 Real Crypto | Later (12–24 months) | Real FHE / PQ / ZK / VDF / Shamir replacing the deterministic stubs |

Dates are reference milestones, contingent on team formation and funding. Audits to date are internal Kairos Lab self-audits (OMEGA V4/V5/V6), never third-party.

## Get involved

Covenant's specification is CC0-1.0 (public domain). The compiler is Apache-2.0. The project seeks contributors on four profiles :

- **Compiler architects** — experience with Rust, OCaml, Swift, Move, or Cairo toolchains
- **Cryptographers** — FHE (TFHE preferred) to validate primitive semantics and audit for side channels
- **ZK engineers** — IVC systems (Nova, Protostar) for the verification layer
- **Tooling engineers** — LSP, formatter, docs generator, web playground

With V0.1 shipped, contributors can inspect, critique, extend, and port a working compiler — not just a specification.

Initial engagements can be part-time, consulting, or grant-funded open-source contributions.

**Contact** : [@Valisthea](https://x.com/Valisthea) on X, or via [Kairos Lab](https://kairos-lab.org).

## Funding model

No VC, no token, no private raise. Funding comes from three channels :

- Public-goods grants (Ethereum Foundation, Protocol Guild, Aster Foundation)
- Chain-level partnerships for integration work
- Kairos Lab bootstrap (audit revenue, consulting) until external funding stabilises

## Licenses

| What | License |
|---|---|
| This repository — website content | [CC-BY-4.0](LICENSE-CC-BY.txt) — attribution required |
| This repository — HTML / CSS / JS code | [MIT](LICENSE-MIT.txt) |
| Specification (in covenant/ repo, future public) | CC0-1.0 — public domain |
| Compiler source (in covenant/ repo, future public) | Apache-2.0 |

## Related

- [Styx Protocol](https://styx-website.vercel.app) — the four ERCs that form Covenant's stdlib
- **Robinhood Chain** — primary testnet deploy target (Arbitrum Orbit L2, chainId 46630 / 0xB626)
- [Kairos Lab](https://kairos-lab.org) — the organization building Covenant
- [First deployment](https://sepolia.etherscan.io/address/0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133) — Sepolia Coin (COIN) on Ethereum Sepolia

---

*The river has its language now.*
