---
title: "11 — Cryptographic Amnesia"
description: "Provable on-chain data erasure with amnesia blocks."
order: 11
section: "Advanced"
---

# 11 — Cryptographic Amnesia

Cryptographic amnesia gives smart contracts the ability to **provably erase data** — producing a ZK proof that a storage slot has been overwritten with zeros and that all historical references have been scrubbed from the Merkle trie.

This satisfies on-chain "right to be forgotten" requirements without requiring chain rollbacks or off-chain trust.

## `amnesia { }` block

```covenant
contract PrivateRecord {
  field records: Map<Address, String>

  action store(data: String) {
    self.records[msg.sender] = data;
  }

  action erase() {
    amnesia {
      // Everything inside this block is provably erased.
      // The compiler inserts a two-pass erasure:
      //   Pass 1: overwrite with random bytes
      //   Pass 2: overwrite with zeros + emit erasure proof
      delete self.records[msg.sender];
    }
    emit RecordErased(msg.sender);
  }
}
```

## Two-pass erasure protocol

1. **Pass 1 — Randomisation**: the slot is overwritten with `keccak256(slot . blockhash(N-1))` — ensures no value is predictable.
2. **Pass 2 — Zeroing**: the slot is set to 0x00…00 and a ZK proof is emitted attesting that the slot was at value V at block N-1 and is now 0.
3. **Proof publication**: the proof is stored in the erasure receipt log (EIP-7XX, pending) so any observer can verify erasure.

## Verifying an erasure off-chain

```bash
covenant amnesia verify   --contract 0xABCD...   --slot 0x...         --block 19000000     --receipt 0xtx...
```

Output:

```
Erasure proof VALID
  Slot 0x... zeroed at block 19000001
  Pre-image hash: 0xdeadbeef...
  Prover: Halo2 recursive
```

## What amnesia can and cannot erase

| Can erase | Cannot erase |
|-----------|--------------|
| Current-state storage slots | Historical block headers |
| In-contract `field` values | Event logs already emitted |
| Map entries | Calldata of past transactions |
| List elements | Data already mirrored off-chain |

The compiler warns when an `amnesia` block is applied to an event-indexed field — event logs are permanent.

## GDPR / regulatory context

Cryptographic amnesia satisfies "erasure" under data minimisation frameworks because:
- The current state provably contains zeros.
- The ZK proof commits to the pre-erasure value's hash, not the value itself.
- No trusted third party is needed to certify erasure.

> This is not legal advice. Consult a privacy attorney for regulatory compliance.
