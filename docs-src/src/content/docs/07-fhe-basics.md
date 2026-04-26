---
title: "07 — FHE Basics"
description: "Homomorphic encryption as a first-class language primitive — the encrypted counter pattern."
order: 7
section: "Standards"
---

# 07 — FHE Basics

The simplest FHE pattern: a counter where the value is encrypted on chain. Every observer sees ciphertext bytes; only the designated `owner` can decrypt the value via threshold decrypt. Increments are **homomorphic** — the chain adds to the ciphertext directly, no decryption ever happens during compute.

```covenant
-- ShieldedCounter.cov · an FHE counter.
-- The `encrypted` qualifier means the `total` field is stored on-chain
-- as a TFHE ciphertext (ERC-8227). Every observer sees ciphertext bytes;
-- no one except the owner can see the value. `bump` adds homomorphically
-- without decryption.

encrypted counter ShieldedCounter {
    total: amount

    action bump(by: amount) {
        total += by
    }

    reveal total to owner
}
```

## What just happened?

| Concept | Explanation |
|---------|-------------|
| `encrypted counter` | Top-level keyword pair: a counter where the value is FHE-encrypted on chain (TFHE ciphertext, 32-byte handle per ERC-8227) |
| `total: amount` | Declares the counter value. The `encrypted` qualifier lifted from the construct keyword applies — `total` is a ciphertext, not plaintext |
| `total += by` | A **homomorphic add**. The compiler routes this to a TFHE precompile that adds `by` to the ciphertext directly, producing a new ciphertext. No decryption ever happens on chain |
| `reveal total to owner` | Declarative access policy: only the address designated as `owner` can request a threshold-decrypt of the value. On a real chain this requires validator consensus; in the playground's MockChain the precompile returns a deterministic plaintext |

## Why this matters

Every blockchain prior to FHE-enabled chains made every value public. Privacy was achieved off-chain (mixers, ZK rollups with private state, sidechains) — never inside a single contract.

Covenant + ERC-8227 changes this. The `total` field above is **stored encrypted, computed encrypted, and only revealed to one specific principal**. An observer running an indexer over the chain learns nothing from the bytes. A validator processing the `bump` call learns nothing about the operand.

This is the foundational pattern. From here, you can build:

- [**08 — Encrypted Token**](/docs/examples/08-encrypted-token) — a confidential ERC-20 where balances are encrypted
- **B3 — Private DAO** ([gallery →](https://playground.covenant-lang.org/?example=B3)) — voting where individual votes and running tallies are both encrypted

## Real-chain considerations

The playground's MockChain mocks the FHE precompiles so you can iterate on UX. Real on-chain deployment requires:

- **TFHE-enabled validators** — Aster Chain ships these by default; on Sepolia, FHE precompiles aren't deployed and the contract will revert when an FHE op is reached
- **Threshold decryption coordination** — `reveal X to owner` on real chain triggers an off-chain ceremony where validators each contribute a share of the decryption result. The result is then posted on-chain or returned to the requester

For development, MockChain is the fastest iteration loop. For acceptance testing, deploy to Aster Testnet (configured in `Chain Target → Aster`).

## Try it now

<a href="https://playground.covenant-lang.org/?example=B1&target=mockchain"
   target="_blank"
   rel="noopener noreferrer"
   style="display:inline-block;margin:1.25rem 0;padding:0.7rem 1.4rem;background:#7C3AED;color:#fff;text-decoration:none;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:600;letter-spacing:0.02em;">
  Try in Playground →
</a>

In the playground:

1. **Compile** — note in the Inspector → IR tab how `total += by` lowers to `tfhe_add(total, by)` precompile dispatch
2. **Deploy** to MockChain
3. Call `bump(5)` — the chain shows the call succeeded but the storage slot for `total` shows ciphertext bytes (not `5`)
4. Call `reveal total` — returns `5` (the mocked threshold decrypt)
5. Call `bump(3)`, then `reveal total` — returns `8`

The Privacy panel in the right sidebar lights up with the FHE-related diagnostics + side-channel notes.

## Continue

Move on to [**08 — Encrypted Token**](/docs/examples/08-encrypted-token) to see how the same pattern scales to a full ERC-8227 confidential token.
