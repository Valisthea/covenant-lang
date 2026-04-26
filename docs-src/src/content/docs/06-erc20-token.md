---
title: "06 — ERC-20 Token"
description: "Build a complete ERC-20 fungible token with the `token` keyword. Verified against the V0.8 compiler."
order: 6
section: "Standards"
---

# 06 — ERC-20 Token

The `token` keyword auto-synthesizes the entire ERC-20 surface from a metadata declaration. You write the name, symbol, decimals, and supply — the compiler generates every field, action, view, and event the standard requires.

```covenant
-- Coin.cov · a standard ERC-20-conformant token.
-- The `token` keyword generates:
--   - fields: supply, balances, allowances, name, symbol, decimals
--   - actions: transfer, approve, transfer_from
--   - views:   balance_of, allowance
--   - events:  Transfer, Approval
-- The developer writes only the metadata and any custom logic.

token Coin {
    symbol: "COIN"
    name: "Covenant Coin"
    decimals: 18
    supply: 1_000_000 to deployer
}
```

## What just happened?

| Concept | Explanation |
|---------|-------------|
| `token` | A specialized top-level keyword for ERC-20 fungible tokens |
| `symbol`, `name`, `decimals` | Plaintext metadata. `symbol`/`name` are `text`; `decimals` is `amount` |
| `supply: 1_000_000 to deployer` | Genesis mint declaration. The integer literal supports `_` thousand separators. `to deployer` says the entire supply is minted to the contract creator at deploy time |
| (no body needed) | Everything else is auto-synthesized: `balances` map, `allowances` map, `transfer`/`approve`/`transfer_from` actions, `Transfer`/`Approval` events. The ABI is byte-compatible with OpenZeppelin's ERC-20 |

## What gets generated, in detail

The compiler synthesizes the following surface (you can see it all in the playground's Inspector → ABI tab):

- **Fields:** `total_supply: amount`, `balances: map<address, amount>`, `allowances: map<hash, amount>`
- **Actions:** `transfer(to, value)`, `approve(spender, value)`, `transfer_from(from, to, value)`
- **Views:** `balance_of(who) returns amount`, `allowance(owner, spender) returns amount`, `total_supply returns amount`, `decimals returns amount`, `symbol returns text`, `name returns text`
- **Events:** `Transfer(from indexed, to indexed, value)`, `Approval(owner indexed, spender indexed, value)`

## Add custom logic

You can add your own actions and views inside the `token` block. They compose with the auto-synthesized ones:

```covenant
token MintableCoin {
    symbol: "MCOIN"
    name: "Mintable Coin"
    decimals: 18
    supply: 0 to deployer

    action mint(to: address, value: amount) only deployer {
        balances[to] += value
        total_supply += value
        emit Transfer(zero_address, to, value)
    }
}
```

The `only deployer` guard restricts `mint` to the contract creator. See [04 — Guards](/docs/examples/04-guards) for the full guard catalog.

## Try it now

<a href="https://playground.covenant-lang.org/?example=A2&target=mockchain"
   target="_blank"
   rel="noopener noreferrer"
   style="display:inline-block;margin:1.25rem 0;padding:0.7rem 1.4rem;background:#7C3AED;color:#fff;text-decoration:none;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:600;letter-spacing:0.02em;">
  Try in Playground →
</a>

In the playground:

1. **Compile** — note in the Inspector → ABI tab that you get all 7+ generated functions
2. **Deploy** to MockChain
3. Call `balance_of(deployer)` — returns `1000000000000000000000000` (1M with 18 decimals)
4. Call `transfer(<your wallet>, 100_000000000000000000)` — sends 100 tokens
5. Call `balance_of` on the recipient to verify

## ERC-20 vs Confidential Token

Curious about a privacy-preserving variant? See [**08 — Encrypted Token**](/docs/examples/08-encrypted-token) — same metadata-only declaration, but balances are TFHE ciphertexts (ERC-8227).

## Continue

Move on to [**07 — FHE Basics**](/docs/examples/07-fhe-basics) to learn how Covenant treats homomorphic encryption as a first-class language feature.
