# Covenant — Website and Manifesto

> The public-facing site and manifesto for [Covenant](https://github.com/Valisthea/covenant),
> a declarative smart contract language by [Kairos Lab](https://kairos-lab.org).

## Related repos

| What | Where | License |
|---|---|---|
| **This repo** — Website, manifesto, visual assets | github.com/Valisthea/covenant-lang | CC-BY-4.0 (content) + MIT (code) |
| **Compiler source + specs** | github.com/Valisthea/covenant *(private until V1.0)* | Apache-2.0 (code) + CC0-1.0 (specs) |
| **Live manifesto** | [covenant-lang.org](https://covenant-lang.org) | — |

## Current state — V0.1 Basics (April 2026)

Covenant's first public release is live.

- **5 reference contracts compile end-to-end** via the Rust compiler : Hello, Coin, OpenBallot, ShieldedCounter, QuantumBoard
- **First deployment on Ethereum Sepolia** : [0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133](https://sepolia.etherscan.io/address/0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133)
- **ERC-20 synthesis validated** : recognized automatically by Etherscan's Token Tracker ; ABI decoded by ethers.js without modification ; transferable via Metamask
- **508+ tests passing** across 18 Rust crates
- **Compiler tagged** `v0.1.0-basics`

**Disclaimer** : V0.1 is a research release. Unaudited, experimental, intended for demonstration of the language's semantics. Not for deployment with production value.

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
| V0.1 Basics | April 2026 | **Shipped** — 5 examples compile, first Sepolia deploy |
| V0.2 Intermediate | 2026 – 2027 | Planned — PrivateDAO, SealedAuction, SecretCoin, TimeVault, MPCEscrow |
| V0.3 Advanced | 2027 | Cryptographic amnesia, bridges, selective disclosure, reputation |
| V1.0 GA | 2028 | Feature completeness, external audit (Phase C), CLI + LSP |
| V1.5 Formal | 2028 – 2029 | Formal verification artifacts (Coq/Lean), CL5 conformance |

Dates are reference milestones, contingent on team formation and funding.

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
- [Aster Chain](https://asterdex.com) — primary deployment target with native encrypted execution
- [Kairos Lab](https://kairos-lab.org) — the organization building Covenant
- [First deployment](https://sepolia.etherscan.io/address/0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133) — Sepolia Coin (COIN) on Ethereum Sepolia

---

*The river has its language now.*
