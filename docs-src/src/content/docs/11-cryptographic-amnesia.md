---
title: "11 — Cryptographic Amnesia"
description: "Provably destroy a secret forever — the ERC-8228 amnesia ceremony, auto-synthesized from a metadata declaration."
order: 11
section: "Advanced"
---

# 11 — Cryptographic Amnesia

The `ceremony` keyword auto-synthesizes the entire ERC-8228 amnesia lifecycle: setup → guardians submit shares → finalize → destroy. After `destroy()` the secret is provably unrecoverable forever — backed by a Wesolowski VDF + Shamir secret sharing + keccak-bound destruction proof at compiler precompiles `0x124–0x127`.

```covenant
-- AmnesiaCeremony.cov · an ERC-8228 Amnesia ceremony contract.
-- The `ceremony` keyword synthesizes the full ERC-8228 lifecycle:
--   setup() → uint256         : initialize ceremony session, returns session_id
--   submit_share(bytes32) → bool : guardian submits their key share
--   finalize() → bool         : ceremony organizer finalizes share collection
--   destroy() → bool          : irrevocably destroys the secret, emits event
--   phase() → uint256         : 0=Setup, 1=Active, 2=Finalized, 3=Destroyed
--   session_id() → uint256    : returns the active session identifier
--   is_destroyed() → bool     : true once destroy() has been called
--   owner() → address         : returns the ceremony organizer (deployer)
--
-- The `on_destroy` block runs when the ceremony is finalized and calls
-- the stdlib `destroy()` to generate an irrevocable destruction proof.

ceremony AmnesiaCeremony {
    guardians: 3
    threshold: 2

    on_destroy {
        destroy(0)
    }
}
```

## What just happened?

| Concept | Explanation |
|---------|-------------|
| `ceremony` | Top-level keyword that synthesizes the ERC-8228 amnesia lifecycle from metadata |
| `guardians: 3` | Three principals will hold a Shamir share of the secret |
| `threshold: 2` | Any two guardians can collaboratively reconstruct the secret. Two-out-of-three Byzantine tolerance |
| `on_destroy { destroy(0) }` | Hook that runs when the ceremony reaches the **Destroyed** phase. Calls the stdlib `destroy()` precompile, producing a Wesolowski VDF + keccak-bound destruction proof emitted as an event |

## What gets generated

The compiler synthesizes the following ABI surface:

| Function | Returns | Purpose |
|---|---|---|
| `setup()` | `uint256` | Initialize ceremony session, returns `session_id` |
| `submit_share(bytes32)` | `bool` | Guardian submits their key share |
| `finalize()` | `bool` | Organizer closes share collection |
| `destroy()` | `bool` | Irrevocably destroys the secret + emits destruction event |
| `phase()` | `uint256` | 0=Setup, 1=Active, 2=Finalized, 3=Destroyed |
| `session_id()` | `uint256` | The active session id |
| `is_destroyed()` | `bool` | True once `destroy()` was called |
| `owner()` | `address` | The ceremony organizer (deployer) |

You write only the metadata (`guardians`, `threshold`) plus the optional `on_destroy` hook. The cryptographic state machine, the share aggregation logic, and the destruction proof generation are all auto-generated and audit-verified.

## Why this matters

Smart contracts up to V0.7 of every chain make one fundamental assumption: **state is permanent**. Once a value is written to storage, it can theoretically be recovered by anyone running an archive node. There has been no way to **provably** delete a secret.

`ceremony` changes this. After `destroy()` returns `true`, the destruction proof event is on-chain. Anyone can verify in pure Python (`tools/verify_destruction_proof.py`) that:

1. The Wesolowski VDF produced a value `Y` from the seed
2. The keccak digest of `Y` matches the on-chain commitment
3. The Shamir reconstruction polynomial is no longer recoverable from the (now overwritten) share storage slots

This is the foundation of "right to be forgotten" smart contracts, time-locked secret reveals (the secret unlocks at time T but only in fragments that re-aggregate after T), and trusted setup ceremony contracts where the toxic waste is provably destroyed.

## Use cases

- **ZK trusted setup ceremonies** — destroy the toxic waste after the ceremony, prove it
- **Cryptographic key sharding** — split a key, distribute to N guardians, reconstruct only when M agree
- **Time-locked secret reveals** — combine with `when now >= unlock_time` guards
- **Dead-man-switch contracts** — pre-deploy a destruction trigger that fires on inactivity

## Try it now

<a href="https://playground.covenant-lang.org/?example=C2&target=mockchain"
   target="_blank"
   rel="noopener noreferrer"
   style="display:inline-block;margin:1.25rem 0;padding:0.7rem 1.4rem;background:#7C3AED;color:#fff;text-decoration:none;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:600;letter-spacing:0.02em;">
  Try in Playground →
</a>

In the playground:

1. **Compile** — the Inspector → ABI tab shows all 8 generated functions
2. **Deploy** to MockChain
3. Call `phase()` — returns `0` (Setup)
4. Call `setup()` — returns a `session_id` like `1`. Phase advances to `1` (Active)
5. Call `submit_share(0x...)` twice (any 32-byte value) to simulate two guardians
6. Call `finalize()` — phase advances to `2` (Finalized)
7. Call `destroy()` — phase advances to `3` (Destroyed); the destruction event fires
8. Call `is_destroyed()` — returns `true` permanently

## ERC-8228 spec

The full ERC-8228 specification is at [/docs/reference/ercs/03-erc-8228-amnesia](/docs/reference/ercs/03-erc-8228-amnesia). It covers the wire format of the destruction proof, the precompile interface (`0x124` setup, `0x125` finalize, `0x126` destroy, `0x127` verify), and the security argument from indistinguishability under chosen-message attack.

## Continue

Move on to [**12 — UUPS Upgradeable**](/docs/examples/12-uups-upgradeable) to see how Covenant handles upgrade patterns without proxies.
