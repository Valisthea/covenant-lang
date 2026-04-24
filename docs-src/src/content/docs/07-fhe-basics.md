---
title: "07 — FHE Basics"
description: "Homomorphic encryption as a first-class language primitive."
order: 7
section: "Standards"
---

# 07 — FHE Basics

Fully Homomorphic Encryption (FHE) lets you perform arithmetic on ciphertext — computations happen on encrypted data, and only the key holder can decrypt the result.

Covenant wraps FHE operations in the `encrypted<T>` type family.

## Declaring encrypted fields

```covenant
contract SecretVoting {
  field tally: encrypted<u256> = fhe_zero()
}
```

`fhe_zero()` initialises the accumulator to an encryption of 0.

## Supported operations

| Function | Description |
|----------|-------------|
| `fhe_add(a, b)` | Homomorphic addition |
| `fhe_mul(a, b)` | Homomorphic multiplication |
| `fhe_sub(a, b)` | Homomorphic subtraction |
| `fhe_eq(a, b)` | Equality test (returns `encrypted<Bool>`) |
| `fhe_lt(a, b)` | Less-than comparison |
| `fhe_decrypt(c, key)` | Decrypt with a key — emits proof of correct decryption |
| `fhe_reencrypt(c, pubkey)` | Re-encrypt under a different public key |

## Example: private vote accumulator

```covenant
contract PrivateVoting {
  field tally: encrypted<u256> = fhe_zero()
  field voted:  Map<Address, Bool>

  error AlreadyVoted

  action cast_vote(encrypted_vote: encrypted<u256>) {
    require(!self.voted[msg.sender], AlreadyVoted);
    self.voted[msg.sender] = true;
    // Add ciphertext directly — no decryption needed
    self.tally = fhe_add(self.tally, encrypted_vote);
  }

  // Owner can decrypt the final tally
  action reveal_tally() -> u256 {
    only(owner);
    return fhe_decrypt(self.tally, fhe_owner_key());
  }
}
```

## Scheme selection

Covenant is scheme-agnostic at the source level. Configure the FHE backend in `covenant.toml`:

```toml
[fhe]
scheme = "tfhe"   # options: tfhe | bgv | ckks
params = "default_128"
```

The compiler emits precompile calls to the scheme-specific EVM precompile registered at the target chain's genesis.

## Gas model

FHE operations are expensive — each `fhe_add` costs ~2 M gas and `fhe_mul` ~40 M gas on a standard EVM. On Aster Chain (ID 1996), the privacy precompiles are subsidised by the validator set and cost 10–100× less.

> **Tip:** batch FHE operations in a single action to amortise proof-verification overhead.
