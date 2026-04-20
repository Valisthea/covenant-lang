# Covenant

**where cryptographic guarantees become language primitives**

A smart contract language designed for cryptographic agility, with [Styx Protocol](https://styx-website.vercel.app) as its native standard library.

---

## Project status

Covenant is in **design phase** (2026). The first usable release (V0) is planned for 2027–2028. This repository currently hosts the project manifesto and will evolve into the language specification and compiler implementation.

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
| Design | 2026 | Spec V0, team formation, grant applications |
| V0 | 2027 – 2028 | Parser, type checker, codegen → Solidity, first deploy on Base Sepolia |
| V1 | 2028 – 2029 | Full Solidity feature parity, native Aster Chain integration, independent audit |
| V2 | 2029 – 2030 | RFC process, community governance, stable ecosystem |

Dates are reference milestones, not commitments. They will move with team size and funding.

## Get involved

Covenant is open-source (Apache 2.0 for compiler, CC0 for spec) and seeks contributors on four profiles:

- **Compiler architects** — experience on Rust, OCaml, Swift, Move, or Cairo
- **Cryptographers** — FHE (TFHE preferred) to validate primitive semantics
- **ZK engineers** — IVC systems (Nova, Protostar) for the verification layer
- **Tooling engineers** — LSP, formatter, docs generator, web playground

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

---

*The river has its language now.*
