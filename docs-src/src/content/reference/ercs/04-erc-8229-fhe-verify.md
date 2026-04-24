---
title: "ERC-8229 — FHE Verification Standard"
description: "Standard for generating and verifying zero-knowledge proofs of correct FHE computation, enabling publicly auditable confidential contracts."
section: reference
order: 4
level: reference
---

<!-- Source: doc3-stdlib-spec.md §4, doc1-whitepaper.md §2.3 -->
<!-- Last sync: 2026-04-23 -->

# ERC-8229 — FHE Verification Standard

**Summary**: ERC-8229 defines how to prove — without revealing inputs — that an FHE computation was performed correctly. It combines Nova IVC (Incrementally Verifiable Computation) for unbounded circuits with Halo2 for efficient on-chain verification. The result: encrypted data can be processed by complex logic and any third party can verify the computation was honest.

## The Problem ERC-8229 Solves

ERC-8227 gives you encrypted state. But who verifies the computation was correct? If a contract applies `fhe_mul(balance, rate)` to compute interest, the output is still encrypted — a malicious validator could substitute a different ciphertext and no one would know.

ERC-8229 adds **computational integrity** to FHE:
- The computation is described as a circuit
- A ZK proof is generated that the circuit was applied correctly to the ciphertexts
- Any on-chain verifier can check the proof without seeing the inputs

## Covenant Surface

| Construct | Description |
|-----------|-------------|
| `verified_by(proof)` | Assert that this computation is ZK-verified |
| `selective_disclosure(field, to)` | Reveal a specific field to a specific party with proof |
| `@prove_offchain` | Mark an action as requiring an off-chain proof |
| `zk_prove(circuit, inputs)` | Generate a proof (returns opaque proof handle) |
| `zk_verify(proof, signal)` | Verify a proof on-chain |

## Architecture

ERC-8229 uses a two-layer proof system:

```
FHE computation (off-chain)
        ↓
Nova IVC folding        ← accumulates computation steps
        ↓
Halo2 compression       ← compresses to constant-size proof
        ↓
BN254 on-chain verifier ← verifiable in ~550k gas
```

**Layer 1 — Nova IVC**: Handles unbounded computation depth. Each step of the FHE computation is folded into an accumulator. No trusted setup required. Prover time: O(n) where n = number of computation steps.

**Layer 2 — Halo2**: Compresses the IVC accumulator into a constant-size proof (~4-8 KB). Uses the IPA commitment scheme over Pasta curves (Pallas/Vesta).

**Dual-curve bridging**: Pasta curves are efficient for proof generation but expensive to verify on BN254 (Ethereum's native curve). ERC-8229 includes a Groth16 wrapping step that converts the Halo2 proof to BN254, enabling cheap EVM verification.

## `@prove_offchain` Annotation

For actions that are too compute-intensive for on-chain FHE:

```covenant
@prove_offchain
action compute_interest(account: address) {
    let balance = encrypted_balances[account]
    let accrued = fhe_mul(balance, interest_rate)
    encrypted_balances[account] = fhe_add(balance, accrued)
    
    verified_by(interest_proof)
}
```

When `@prove_offchain` is used:
1. The action body is compiled to a WASM circuit (not EVM bytecode)
2. Callers must supply a `proof` argument alongside their transaction
3. The contract verifies the proof matches the state transition before accepting it
4. Gas cost: circuit verification only (~550k gas), not the FHE computation

The WASM circuit is embedded in the contract metadata so any party can generate proofs off-chain using the Covenant SDK.

## Selective Disclosure

`selective_disclosure` allows revealing one encrypted field to a specific party without revealing others:

```covenant
action audit_disclosure(auditor: address) only regulator {
    selective_disclosure(transaction_amounts, auditor)
    // Does NOT reveal counterparty identities
    // Does NOT reveal balance positions
}
```

This generates a ZK proof that:
- `transaction_amounts` is a subset of the contract's FHE state
- The disclosure is authorized by the `regulator` address
- No other state was disclosed

The proof size is ~6 KB. On Aster Chain, selective disclosure is a native operation (300ms).

## Trusted Setup Considerations

- **Nova IVC**: No trusted setup. Uses random oracle model.
- **Halo2 IPA**: No trusted setup. Fully transparent.
- **Groth16 wrapper**: Requires a one-time trusted setup per circuit. The Covenant Foundation runs a multi-party computation ceremony for the wrapper circuit. Ceremony transcript: [github.com/Valisthea/covenant-trusted-setup](https://github.com/Valisthea/covenant-trusted-setup)

If you define custom circuits with `@prove_offchain`, you must either:
1. Use the universal wrapper (covers 95% of use cases), or
2. Run your own setup ceremony for circuits that exceed the wrapper's size limit (>10M constraints)

## Proof Size and Tradeoffs

| Proof system | Size | On-chain verification | Trusted setup |
|-------------|------|-----------------------|---------------|
| Nova (raw) | ~50 KB | Not directly (too large) | None |
| Halo2 IPA | ~8 KB | ~2M gas (expensive) | None |
| Groth16 (BN254 wrapped) | ~200 bytes | ~200k gas | Yes (MPC) |
| PLONK | ~1 KB | ~500k gas | Universal |

Covenant V0.7 uses **Groth16 wrapped** by default for on-chain verification. The `--proof-system` flag lets you choose:

```bash
covenant build --proof-system plonk ./src/DeFi.cvt
```

## Precompile Addresses

| Address | Name | Description | Gas |
|---------|------|-------------|-----|
| `0x30` | `zk_verify` | Verify Groth16/PLONK/Halo2 proof | 200,000–550,000 |
| `0x31` | `nova_fold` | Accumulate one IVC step | 80,000 |
| `0x32` | `nova_compress` | Compress IVC accumulator to Halo2 | 400,000 |
| `0x33` | `selective_disclose` | Generate selective disclosure proof | 180,000 |
| `0x34` | `circuit_hash` | Hash circuit to commitment | 5,000 |

## Gas Table

| Operation | Gas |
|-----------|-----|
| `zk_verify` (Groth16) | 200,000 |
| `zk_verify` (PLONK) | 500,000 |
| `zk_verify` (Halo2 IPA) | 2,000,000 |
| `selective_disclose` | 180,000 |
| Proof submission (calldata, 200 bytes) | 200 × 16 = 3,200 |

## See Also

- [Example 10 — Zero-Knowledge Proofs](/docs/examples/10-zero-knowledge-proofs)
- [ERC-8227 — Encrypted Tokens](/docs/reference/ercs/02-erc-8227-fhe) — the FHE layer
- [Compiler — IR: ZK opcodes](/docs/reference/compiler/02-ir#zk-opcodes)
- [Cookbook — ZK Airdrop](/docs/cookbook/privacy/03-zk-airdrop)
- [Glossary: ZK proof](/docs/glossary#zk-proof), [Nova IVC](/docs/glossary#nova), [Halo2](/docs/glossary#halo2)
