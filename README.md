# Covenant

**where cryptographic guarantees become language primitives**

A smart contract language designed for cryptographic agility, with [Styx Protocol](https://styx-website.vercel.app) as its native standard library.

---

## Current state — V0.1 Basics (April 2026)

- 5 reference contracts compile end-to-end
- First public deployment on Ethereum Sepolia: [0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133](https://sepolia.etherscan.io/address/0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133)
- ERC-20 synthesis validated via Etherscan Token Tracker and ethers.js
- Compiler at tag `v0.1.0-basics`
- Research release, unaudited, not for production value

Read the full manifesto: **[covenant-lang.org](https://covenant-lang.org)**

## The three principles

1. **Cryptographic properties as language primitives** — `encrypted uint256` should be as native as `uint256`. The compiler, not a bundle of libraries, enforces the guarantees.
2. **Declare guarantees, not implementations** — the SQL shift. A contract states *what* it guarantees (encrypted inputs, homomorphic tally, amnesia after cycle); the compiler generates *how*.
3. **Cryptographic agility as a type-system property** — primitives are exposed via traits and security levels, not hardcoded to a specific scheme. Schemes can evolve without rewriting contracts.

## Styx Protocol as standard library

Covenant compiles against four Ethereum ERCs that form its native stdlib:

| ERC | Role | Layer |
|---|---|---|
| **ERC-8227** | Encrypted Token Standard (FHE balances) | Veil |
| **ERC-8228** | Cryptographic Amnesia Interface | Oblivion |
| **ERC-8229** | FHE Computation Verification | Prism |
| **ERC-8231** | Post-Quantum Key Registry | Fortress |

## Roadmap

| Phase | When | Milestone |
|---|---|---|
| Design | 2025 – early 2026 | Specs V0 complete, 8 normative docs published, Styx ERCs drafted |
| **V0.1 Basics** | **April 2026 (shipped)** | **5 examples compile end-to-end; first ERC-20 deployed on Sepolia** |
| V0.2 Intermediate | 2026 – 2027 | fhEVM-class support: private DAO, sealed auction, encrypted token, time-locked vault |
| V0.3 Advanced | 2027 | Cryptographic amnesia, bridges, ZK selective disclosure, reputation primitives |
| V1.0 GA | 2028 | Feature completeness, external audit Phase C, CLI + LSP + IDE support |
| V1.5 Formal | 2028 – 2029 | Coq/Lean formal verification artifacts, CL5 conformance achievement |

Dates are reference milestones, not commitments. They will move with team size and funding.

## Get involved

Covenant is open-source (Apache 2.0 for compiler, CC0 for spec) and seeks contributors on four profiles:

- **Compiler architects** — experience on Rust, OCaml, Swift, Move, or Cairo
- **Cryptographers** — FHE (TFHE preferred) to validate primitive semantics
- **ZK engineers** — IVC systems (Nova, Protostar) for the verification layer
- **Tooling engineers** — LSP, formatter, docs generator, web playground

With V0.1 shipped, contributors can inspect, critique, extend, and port a working compiler — not just a specification.

Initial engagements can be part-time, consulting, or grant-funded open-source contributions.

**Contact:** [@Valisthea](https://x.com/Valisthea) on X, or via [Kairos Lab](https://styx-website.vercel.app).

## Funding model

No VC, no token, no private raise. Funding comes from three channels:

- Public-goods grants (Ethereum Foundation, Protocol Guild, Aster Foundation)
- Chain-level partnerships for integration work
- Kairos Lab bootstrap (audit revenue, consulting) until external funding stabilises

## Licenses

| What | License |
|---|---|
| Specification | [CC0-1.0](LICENSE-CC0.txt) — public domain |
| Compiler & tooling code | [Apache-2.0](LICENSE-APACHE.txt) |

## Related

- [Styx Protocol](https://styx-website.vercel.app) — the four ERCs that form Covenant's stdlib
- [Aster Chain](https://asterdex.com) — primary deployment target with native encrypted execution
- [First deployment](https://sepolia.etherscan.io/address/0x6C7986a3d79E1AFECfE242f92f2A0DFeC3397133) — Sepolia Coin (COIN) on Ethereum Sepolia

---

*The river has its language now.*
