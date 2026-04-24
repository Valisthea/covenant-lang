---
title: "Rebase Token"
description: "A token whose total supply adjusts periodically via a rebase operation, keeping holder shares constant."
section: cookbook
order: 4
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Rebase Token

## Problem

I need a token where every holder's balance grows (or shrinks) proportionally when an oracle publishes a new rebase index, without having to iterate over every holder.

## Solution

```covenant
token RebaseToken {
    name: "Rebase Token"
    symbol: "RBT"
    decimals: 18
    supply: 0 tokens
    initial_holder: deployer

    field oracle: address = deployer
    field rebase_index: u256 = 1_000_000_000_000_000_000  // 1e18 PRECISION
    field total_shares: u256 = 0
    field shares: mapping<address, u256>

    field immutable PRECISION: u256 = 1_000_000_000_000_000_000

    event Rebased(prev_index: u256, new_index: u256, timestamp: timestamp)
    event SharesMinted(to: address indexed, shares: u256, amount: amount)

    error NotOracle()
    error IndexMustIncrease()
    error ZeroAmount()

    action rebase(new_index: u256) only oracle {
        given new_index >= rebase_index or revert_with IndexMustIncrease()
        emit Rebased(rebase_index, new_index, now)
        rebase_index = new_index
    }

    action balance_of(a: address) -> amount {
        return shares[a] * rebase_index / PRECISION
    }

    action mint(to: address, amount: amount) only oracle {
        given amount > 0 or revert_with ZeroAmount()
        let new_shares = amount * PRECISION / rebase_index
        shares[to] = shares[to] + new_shares
        total_shares = total_shares + new_shares
        total_supply = total_shares * rebase_index / PRECISION
        emit SharesMinted(to, new_shares, amount)
    }

    action transfer(to: address, amount: amount) {
        let shares_to_move = amount * PRECISION / rebase_index
        given shares[caller] >= shares_to_move or revert_with ZeroAmount()
        shares[caller] = shares[caller] - shares_to_move
        shares[to] = shares[to] + shares_to_move
    }
}
```

## Explanation

- Internal accounting is in `shares`, which are immune to rebases
- `balance_of` is a pure function of `shares[a] * rebase_index / PRECISION`
- `rebase` only updates a single field, making it O(1) regardless of holder count
- `PRECISION` is `immutable` so the compiler inlines it and no storage slot is consumed
- `total_supply` is derived on each mint; between rebases it is updated implicitly by the `balance_of` formula

The oracle must never decrease `rebase_index` in a positive-rebase token; the `IndexMustIncrease` guard enforces this.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `rebase` | ~30,000 |
| `mint` (cold) | ~75,000 |
| `transfer` (warm) | ~40,000 |
| `balance_of` (view) | ~3,000 |

## Common Pitfalls

1. **Rounding dust**: `amount * PRECISION / rebase_index` truncates. Over many transfers, dust accumulates; accept it or track residuals per address.
2. **Decreasing index**: A negative rebase (debasement) requires removing the `IndexMustIncrease` guard and using a separate action so callers are not surprised.
3. **Quoting `total_supply` from storage**: Do not cache `total_supply` between rebases; always compute from `total_shares * rebase_index / PRECISION`.
4. **Oracle key compromise**: A malicious oracle can inflate balances arbitrarily. Combine with a multi-sig or time-lock (see See Also).
5. **Integrating with AMMs**: Some pools snapshot balances; a rebase between swaps can break accounting. Use a wrapped non-rebasing variant for DEX integration.

## Variations

### Wrapped non-rebasing version

Expose a 1:1 shares-denominated wrapper for DEX composability:

```covenant
action wrap(amount: amount) {
    let s = amount * PRECISION / rebase_index
    shares[caller] = shares[caller] - s
    wrapped_balances[caller] = wrapped_balances[caller] + s
}

action unwrap(shares_amt: u256) {
    wrapped_balances[caller] = wrapped_balances[caller] - shares_amt
    shares[caller] = shares[caller] + shares_amt
}
```

### Two-sided rebase with floor

```covenant
action rebase(new_index: u256) only oracle {
    given new_index >= MIN_INDEX or revert_with IndexTooLow()
    emit Rebased(rebase_index, new_index, now)
    rebase_index = new_index
}
```

## See Also

- [Mintable Token](/docs/cookbook/tokens/01-mintable-token)
- [Capped Supply Token](/docs/cookbook/tokens/06-capped-supply)
- [Auth: Time-Locked Admin](/docs/cookbook/auth/02-time-locked-admin)
