---
title: "09 — Post-Quantum Signatures"
description: "Dilithium3 (NIST FIPS 204) signatures as a first-class Covenant primitive."
order: 9
section: "Standards"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


# 09 — Post-Quantum Signatures

Classical ECDSA (secp256k1) will be broken by a sufficiently powerful quantum computer running Shor's algorithm. Covenant provides `@pq_signed` — a decorator that replaces ECDSA verification with **CRYSTALS-Dilithium3** (standardised as NIST FIPS 204 in 2024).

## Applying `@pq_signed`

```covenant
@pq_signed
contract QuantumSafeVault {
  field balance: u256

  action deposit() {
    self.balance += msg.value;
  }

  @nonreentrant
  action withdraw(amount: u256, pq_sig: Bytes) {
    // pq_sig is a Dilithium3 signature over (address, amount, nonce)
    verify_pq_sig(msg.sender, pq_sig);
    require(self.balance >= amount, InsufficientBalance);
    self.balance -= amount;
    transfer_eth(msg.sender, amount);
  }
}
```

When `@pq_signed` is present, the compiler:
1. Adds a Dilithium3 public-key registry (`field pq_keys: Map<Address, Bytes>`)
2. Emits a `register_pq_key(pubkey: Bytes)` action
3. Replaces `msg.sender` authentication with `verify_pq_sig` precompile calls

## Key registration

Users must register their Dilithium3 public key before interacting with `@pq_signed` contracts:

```bash
covenant pq keygen --out my-dilithium.json
covenant pq register --contract 0xABCD... --key my-dilithium.json
```

## Signing transactions

```js
import { dilithium3Sign } from "@covenant-lang/pq-sdk";
import key from "./my-dilithium.json";

const sig = dilithium3Sign(key.privateKey, { sender: wallet.address, amount: 1000n, nonce });
await contract.withdraw(1000n, sig);
```

## Hybrid mode

For a transition period, use `@pq_hybrid` — accepts both ECDSA and Dilithium3 signatures:

```covenant
@pq_hybrid
contract HybridVault {
  // ...
}
```

The contract accepts whichever signature type the caller provides, preferring PQ when both are present.

## Key sizes

| Algorithm | Public key | Signature | Security level |
|-----------|-----------|-----------|----------------|
| ECDSA secp256k1 | 33 bytes | 65 bytes | 128-bit classical |
| Dilithium3 | 1952 bytes | 3293 bytes | 128-bit quantum |
| Dilithium5 | 2592 bytes | 4595 bytes | 256-bit quantum |

Covenant defaults to Dilithium3 (NIST recommendation for most use cases). Switch to Dilithium5 with `[pq] level = 5` in `covenant.toml`.
