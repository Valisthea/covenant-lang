---
title: "Critical Findings"
description: "Detailed breakdown of the 5 critical security findings from the OMEGA V4 audit."
order: 2
section: "Security"
---

# Critical Findings

All 5 critical findings identified in the [OMEGA V4 audit](/security/audit-report) have been resolved. This page provides detailed descriptions and the fixes applied.

---

## CVN-001 — FHE ciphertext malleability in `fhe_add`

**Severity:** Critical  
**Component:** FHE runtime / `fhe_add` precompile wrapper  
**Fixed in:** v0.7.0-rc5

### Description

The `fhe_add` implementation in the TFHE scheme backend did not validate that both ciphertext operands were produced under the same public key. An attacker could pass a ciphertext produced under a different key as the second operand, causing the resulting ciphertext to decrypt to garbage — or, worse, to a predictable value if the attacker controlled the foreign key.

### Impact

An attacker could manipulate the result of any `fhe_add` operation they participate in, corrupting encrypted balances or vote tallies without triggering any error.

### Fix

Added public-key binding to all FHE ciphertext blobs. The precompile now verifies that both operands carry the same key fingerprint before executing the homomorphic operation. Mismatched keys revert with `FheKeyMismatch`.

---

## CVN-002 — Amnesia pass-1 randomness predictable on low-entropy chains

**Severity:** Critical  
**Component:** Cryptographic amnesia — pass-1 randomisation  
**Fixed in:** v0.7.0-rc5

### Description

Pass 1 of the amnesia protocol used `keccak256(slot . blockhash(N-1))` as the randomisation value. On chains where `BLOCKHASH` returns 0 for unavailable blocks (chains older than 256 blocks — not applicable on mainnet but applicable on short testnets and certain L2s), pass-1 would deterministically write `keccak256(slot . 0)` — a predictable value, defeating the randomisation purpose.

### Fix

Pass-1 now uses `keccak256(slot . blockhash(N-1) . block.prevrandao . tx.origin)`. The `prevrandao` field (post-Merge) provides validator-contributed randomness immune to the zero-blockhash scenario.

---

## CVN-003 — UUPS `_upgrade` missing ERC-1822 magic check

**Severity:** Critical  
**Component:** Standard library — UUPS upgradeable pattern  
**Fixed in:** v0.7.0-rc4

### Description

The built-in `_upgrade(new_impl)` function did not verify that the new implementation contract returns the ERC-1822 magic value (`0x360894...`) from `proxiableUUID()`. This meant any contract address — including a malicious one with no upgrade logic — could be set as the implementation, permanently bricking the proxy.

### Fix

`_upgrade` now calls `proxiableUUID()` on the new implementation and reverts with `InvalidImplementation` if the return value is incorrect. The check is gas-bounded (5000 gas stipend) to prevent griefing via out-of-gas.

---

## CVN-004 — PQ key registry bypass via zero-length signature

**Severity:** Critical  
**Component:** Post-quantum signature verifier  
**Fixed in:** v0.7.0-rc5

### Description

The Dilithium3 verifier did not explicitly check for zero-length signatures before invoking the precompile. Some chain configurations return `true` from the precompile for a zero-length input (implementation-defined behaviour). An attacker submitting an empty byte array as `pq_sig` would bypass authentication entirely.

### Fix

`verify_pq_sig` now rejects any signature shorter than the minimum Dilithium3 signature length (2420 bytes) with `InvalidPqSignatureLength` before invoking the precompile.

---

## CVN-005 — ZK verifier accepts proof for wrong circuit ID

**Severity:** Critical  
**Component:** ZK proof verification — circuit ID binding  
**Fixed in:** v0.7.0-rc5

### Description

The `zk_verify` precompile accepted proofs where the circuit ID embedded in the proof did not match the `circuit` parameter passed by the calling contract. A proof generated for circuit A could be accepted as valid for circuit B if the public inputs happened to satisfy circuit B's public interface.

### Impact

An attacker could submit a valid proof for a permissive circuit (e.g. "prove you know any prime") to satisfy a more restrictive circuit check (e.g. "prove you are KYC verified"), completely bypassing the intended verification logic.

### Fix

The proof blob format now includes a binding commitment to the circuit verification key. `zk_verify` rejects any proof whose circuit commitment does not match the registered VK for the provided circuit ID.
