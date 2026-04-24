---
title: "ERC-8228 — Cryptographic Amnesia"
description: "Standard for irreversible on-chain data destruction with cryptographic proofs of erasure and shamir-secret-sharing governance."
section: reference
order: 3
level: reference
---

<!-- Source: doc3-stdlib-spec.md §5, doc1-whitepaper.md §2.5 -->
<!-- Last sync: 2026-04-23 -->

# ERC-8228 — Cryptographic Amnesia

**Summary**: ERC-8228 defines a protocol for governance-controlled, cryptographically verifiable data destruction. A multi-party `ceremony` collects shares of a master key, time-locks them behind a VDF, then destroys both the key and the data it protects. A ZK proof of erasure is generated on-chain so any verifier can confirm destruction without re-executing it.

OMEGA V4 audit finding **KSR-CVN-001** (Critical) identified a phase enforcement bypass. All ERC-8228 implementations in Covenant V0.7 include the enforced phase state machine required by the finding's resolution.

## Covenant Surface

| Construct | Description |
|-----------|-------------|
| `amnesia { }` | Block of code whose state is eligible for destruction |
| `ceremony { }` | Multi-party key gathering ceremony definition |
| `destroy(field)` | Intrinsic to irreversibly erase a field |
| `on_destroy` | Lifecycle hook called before destruction |
| `@amnesia_eligible` | Annotate a field as destructible |

## Phase State Machine

An ERC-8228 ceremony progresses through exactly five phases. Invalid transitions revert:

```
IDLE → GATHERING → FINALIZED → LOCKED → DESTROYED
```

| Phase | Transitions to | Trigger |
|-------|---------------|---------|
| `IDLE` | `GATHERING` | `ceremony.begin()` called by authorized initiator |
| `GATHERING` | `FINALIZED` | Threshold of shares submitted |
| `GATHERING` | `IDLE` | `ceremony.abort()` before threshold |
| `FINALIZED` | `LOCKED` | VDF computation completed (off-chain), proof submitted |
| `LOCKED` | `DESTROYED` | VDF time-lock expired + `ceremony.execute()` |
| `DESTROYED` | *(terminal)* | — |

**KSR-CVN-001 fix**: Before V0.7.1, a reentrancy pattern allowed callers to skip `FINALIZED → LOCKED` and jump directly to `DESTROYED`. The fix adds a `phase_guard` check at the top of `execute()` using a CEI (Checks-Effects-Interactions) pattern enforced by the compiler.

## Shamir Secret Sharing

The master destruction key is split using Shamir's Secret Sharing over GF(2^256). The ceremony parameters are specified in the contract:

```covenant
ceremony DestroyMasterKey {
    shares: 5
    threshold: 3
    time_lock: 30 days
    participants: [admin1, admin2, admin3, admin4, admin5]
    
    on_destroy {
        destroy(user_data)
        destroy(private_keys)
        emit DataDestroyed(block.timestamp)
    }
}
```

This compiles to:
- `threshold = 3`, `shares = 5` — 3 of 5 participants must submit shares
- Each participant receives a share off-chain (computed at deployment time)
- When 3 shares are submitted on-chain, the master key reconstruction begins

The shares are committed as Pedersen commitments on-chain. The contract verifies each submitted share against the commitment before accepting it.

## VDF Time-Lock

After shares reach threshold, a **Verifiable Delay Function** prevents immediate destruction. This ensures:
- A governance veto window exists even after the threshold is reached
- Time-lock cannot be shortcut by faster hardware (VDF is inherently sequential)

ERC-8228 uses the **Wesolowski VDF** construction:
- Input: hash of collected shares + block hash at threshold
- Delay: configurable (minimum 24h recommended, 30 days in example above)
- Output: VDF proof `(y, π)` where `y = g^(2^T) mod N`

The VDF computation happens **off-chain** by any participant. The on-chain contract only verifies the proof (cheap) not runs it (expensive). Verification via the `0x22` precompile costs ~45,000 gas.

## ZK Proofs of Destruction

After `DESTROYED`, the contract generates a **proof of erasure** — a ZK statement that:
1. The fields listed in `destroy()` contained non-zero values before the ceremony
2. Those storage slots are now zero
3. The transition was authorized by the correct threshold of shares

The proof is a Groth16 proof (~200 bytes) stored in contract metadata:

```json
{
  "type": "amnesia_erasure",
  "erc": "8228",
  "destroyed_slots": ["0x01", "0x02"],
  "ceremony_block": 21847392,
  "proof": "0x1f2a...c4d9"
}
```

Any verifier can check this proof on-chain using the `0x23` precompile without replaying the destruction.

## `on_destroy` Lifecycle Hook

The `on_destroy` hook runs immediately before storage is zeroed. Use it to emit events, notify dependent contracts, or settle final state:

```covenant
amnesia {
    field secret_key: bytes32 @amnesia_eligible
    field user_mapping: map<address, bytes32> @amnesia_eligible
    
    on_destroy {
        emit SecretDestroyed(block.timestamp)
        // settle any outstanding claims first
        for addr in pending_settlements {
            settle(addr)
        }
        destroy(secret_key)
        destroy(user_mapping)
    }
}
```

**Warning**: Any external call in `on_destroy` is a reentrancy risk if the called contract is untrusted. The compiler emits warning **W-AMN-001** if an external call precedes `destroy()` without a reentrancy lock.

## Precompile Addresses

| Address | Name | Description | Gas |
|---------|------|-------------|-----|
| `0x20` | `amnesia_destroy` | Zero storage slots with proof | 30,000 + 5,000/slot |
| `0x21` | `shamir_verify` | Verify a Shamir share commitment | 8,000 |
| `0x22` | `vdf_verify` | Verify Wesolowski VDF proof | 45,000 |
| `0x23` | `erasure_proof_verify` | Verify stored Groth16 erasure proof | 180,000 |
| `0x24` | `phase_transition` | Atomic phase state transition with event | 5,000 |

## Gas Table

| Operation | Gas cost |
|-----------|----------|
| `ceremony.begin()` | 50,000 |
| Submit share | 25,000 |
| `ceremony.finalize()` (at threshold) | 80,000 |
| Submit VDF proof | 45,000 + storage |
| `ceremony.execute()` (destroy N fields) | 30,000 + 5,000×N |
| Erasure proof verification | 180,000 |

## See Also

- [Example 11 — Cryptographic Amnesia](/docs/examples/11-cryptographic-amnesia)
- [ERC-8227 — Encrypted Tokens](/docs/reference/ercs/02-erc-8227-fhe)
- [Security: OMEGA V4 Critical Findings](/docs/security/critical-findings) — KSR-CVN-001
- [Glossary: amnesia](/docs/glossary#amnesia), [VDF](/docs/glossary#vdf), [Shamir Secret Sharing](/docs/glossary#shamir)
