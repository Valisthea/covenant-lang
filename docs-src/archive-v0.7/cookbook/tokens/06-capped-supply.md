---
title: "Capped Supply Token"
description: "Hard-cap on total supply enforced at mint time with a permanent, tamper-proof ceiling."
section: cookbook
order: 6
level: beginner
---

<!-- Last sync: 2026-04-23 -->

# Capped Supply Token

## Problem

I need a fungible token with an absolute, permanently-fixed maximum supply -- set at deployment and impossible to raise later, even by the owner.

## Solution

```covenant
token CappedToken {
    name: "Capped Token"
    symbol: "CAP"
    decimals: 18
    supply: 0 tokens
    initial_holder: deployer

    field owner: address = deployer
    field immutable cap: amount = 21_000_000 tokens

    event Minted(to: address indexed, amount: amount)

    error CapExceeded()
    error ZeroAmount()
    error ZeroAddress()

    action mint(to: address, amount: amount) only owner {
        given amount > 0 or revert_with ZeroAmount()
        given to != address(0) or revert_with ZeroAddress()
        given total_supply + amount <= cap or revert_with CapExceeded()

        balances[to] = balances[to] + amount
        total_supply = total_supply + amount

        emit Minted(to, amount)
    }
}
```

## Explanation

- `field immutable cap` is written once at deploy and lives in contract bytecode, not storage
- The compiler replaces every `cap` read with the constant value -- zero `SLOAD` cost
- `given total_supply + amount <= cap` guarantees supply can never exceed the ceiling
- Differs from [Mintable Token](/docs/cookbook/tokens/01-mintable-token): here the cap is truly permanent; in the mintable recipe `max_supply` is a mutable field the owner could change with an extra action

Because `cap` is immutable, even an owner-key compromise cannot raise it -- the attacker can mint up to the cap but never past it.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| Deployment | ~480,000 |
| `mint` (cold recipient) | ~62,000 |
| `mint` (warm recipient) | ~22,000 |
| `cap` read (inlined) | 0 |

## Common Pitfalls

1. **Using `field` instead of `field immutable`**: A regular `field cap` costs 2,100 gas per read and can be silently mutated. Always use `immutable` for a hard cap.
2. **Setting the cap too low**: Since it cannot be raised, pick the cap conservatively. Migration requires deploying a new contract.
3. **Decimals confusion**: `21_000_000 tokens` with `decimals: 18` means `21_000_000 * 10^18` base units. Writing `21_000_000` without the `tokens` suffix bypasses the scaling.
4. **No burn path**: Burned tokens free up cap room for future minting. If you want truly deflationary economics, also burn from `cap` -- but `immutable` prevents that, so choose carefully.

## Variations

### Cap parameterised at deploy

```covenant
constructor(_cap: amount) {
    cap = _cap   // written once, then immutable
}
```

### Combined with Mintable + schedule

```covenant
field immutable cap: amount = 1_000_000_000 tokens
field immutable mint_end: timestamp = deploy_time + 4 * 365 days

action mint(to: address, amount: amount) only owner {
    given now < mint_end or revert_with MintingClosed()
    given total_supply + amount <= cap or revert_with CapExceeded()
    balances[to] = balances[to] + amount
    total_supply = total_supply + amount
    emit Minted(to, amount)
}
```

## See Also

- [Mintable Token](/docs/cookbook/tokens/01-mintable-token)
- [Burnable Token](/docs/cookbook/tokens/02-burnable-token)
- [Rebase Token](/docs/cookbook/tokens/04-rebase-token)
