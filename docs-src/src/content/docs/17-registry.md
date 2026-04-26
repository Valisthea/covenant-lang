---
title: "17 — Post-Quantum Key Registry"
description: "ERC-8231 auto-synthesis with the V0.9 registry construct."
order: 17
section: "V0.9 New"
level: intermediate
---

# 17 — Post-Quantum Key Registry

The `registry` construct auto-synthesizes [ERC-8231](https://github.com/Valisthea/styx-protocol/blob/main/ercs/ERC-8231.md), the post-quantum key registry standard. It's the migration path from ECDSA to Dilithium-5 — let users register their PQ keys on-chain, indexed by their Ethereum address.

```covenant
registry KeyRegistry {
}
```

One line. That's the entire contract.

## What gets synthesized

| Surface | Members |
|---|---|
| **Fields** | `keys: map<address, pq_key>`, `registered: map<address, bool>` |
| **Views** | `is_registered(account)`, `key_of(account)`, `algorithm_id()` |
| **Actions** | `register(pk: pq_key)`, `revoke()` |
| **Events** | `KeyRegistered`, `KeyRevoked`, `KeyUpdated` (reserved) |
| **Errors** | `NotRegistered`, `AlreadyRegistered` |

`algorithm_id()` returns `1` (Dilithium-5 per FIPS 204). V1.0 may add Falcon-512, SPHINCS+, or hybrid scheme IDs.

## Why this matters

By 2030 a cryptographically relevant quantum computer could break ECDSA. Wallets, multisigs, and signature schemes that depend on it would need to migrate. ERC-8231 is the migration vehicle: a standard contract that lets anyone register their post-quantum public key on-chain, allowing services to look up the right key per signature scheme as they roll out PQ support.

The `registry` keyword exists because every PQ-aware protocol will need this surface, and it should be uniform across deployments.

## Usage flow

```text
# 1. Deploy the registry once per chain.
covenant build registry.cov --target-chain sepolia
forge create ... --constructor-args ...

# 2. Users register their PQ key (call from their EOA).
cast send $REGISTRY "register(bytes)" 0x...dilithium_pk...

# 3. Protocols look up keys.
cast call $REGISTRY "is_registered(address)" $USER
cast call $REGISTRY "key_of(address)" $USER
```

## What to notice

- **`pq_key` is a first-class type** in Covenant. The compiler validates that registered keys are well-formed Dilithium-5 public keys (at least at length and structure level — actual cryptographic validation happens in the helper bridge on PQ-signed actions).
- **Open registration.** `register` has no access guard — any address can register a key for itself. `revoke()` clears only the caller's own slot. This matches the ERC-8231 normative spec.
- **`update_key(new_pk, sig)`** (PQ-signed key rotation) is reserved in the synthesizer's name conflict list but not yet emitted. Sprint 35.c will add it once `pq_signed` guards integrate with stdlib synthesis. For now, users `revoke()` then `register()` to rotate.

## Custom guards

If you need a moderated registry — e.g. only DAO-approved keys — declare your own `register` action and the synthesizer skips that name:

```covenant
registry CuratedRegistry {
    field approved: map<address, bool>

    action register(pk: pq_key) {
        only deployer
        given approved[caller] == true
        keys[caller] = pk
        registered[caller] = true
        emit KeyRegistered(caller, pk)
    }
}
```

## Try it

[Open in playground](https://playground.covenant-lang.org/?example=D2-registry) — registers a sample PQ key, queries it, then revokes.

## What's next

- [18 — External Calls](/docs/examples/18-external-call) — `interface` for cross-contract calls
- [Reference: ERC-8231](/docs/reference/ercs/erc-8231) — full normative spec
- [Cookbook: PQ Migration](/docs/cookbook/pq-migration)
