---
title: "Burnable Token"
description: "A fungible token where holders can permanently destroy their own tokens."
section: cookbook
order: 2
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Burnable Token

## Problem

I need token holders to be able to permanently destroy (burn) their own tokens, reducing total supply.

## Solution

```covenant
token BurnableToken {
    name: "Burnable Token"
    symbol: "BTK"
    decimals: 18
    supply: 10_000_000 tokens
    initial_holder: deployer

    event Burned(from: address indexed, amount: amount)
    error InsufficientBalance()
    error ZeroAmount()

    action burn(amount: amount) {
        given amount > 0 or revert_with ZeroAmount()
        given balances[caller] >= amount or revert_with InsufficientBalance()

        balances[caller] = balances[caller] - amount
        total_supply = total_supply - amount

        emit Burned(caller, amount)
    }

    action burn_from(owner: address, amount: amount) {
        given amount > 0 or revert_with ZeroAmount()
        given allowances[owner][caller] >= amount or revert_with Unauthorized()
        given balances[owner] >= amount or revert_with InsufficientBalance()

        allowances[owner][caller] = allowances[owner][caller] - amount
        balances[owner] = balances[owner] - amount
        total_supply = total_supply - amount

        emit Burned(owner, amount)
    }
}
```

## Explanation

`burn` lets callers destroy their own tokens. `burn_from` uses the allowance mechanism (standard ERC-20 `approve`/`transferFrom`) to let approved spenders burn on behalf of a holder -- useful for DeFi protocols (lending, AMMs) that need to destroy collateral tokens.

Both actions decrement `total_supply`, making burns visible to anyone querying supply.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `burn` | ~35,000 |
| `burn_from` | ~45,000 |

## Common Pitfalls

1. **Not decrementing `total_supply`**: If you only zero the balance, `total_supply` becomes inconsistent. Always update both.
2. **Burning more than balance**: The `>=` check prevents underflow. Without it, Covenant\'s `amount` type would revert on underflow, but the error message is less clear.
3. **Missing allowance decrement in `burn_from`**: The allowance must be reduced before the balance -- CEI pattern.
4. **No `burn_from` -> no DeFi compatibility**: Protocols like Aave expect `burnFrom` to exist. Include it even if you don\'t plan to use it immediately.

## Variations

### Owner-only burning

```covenant
action burn(target: address, amount: amount) only owner {
    balances[target] = balances[target] - amount
    total_supply = total_supply - amount
    emit Burned(target, amount)
}
```

## See Also

- [Mintable Token](/docs/cookbook/tokens/01-mintable-token)
- [Confidential Payroll](/docs/cookbook/tokens/03-confidential-payroll)
- [Example 06 -- ERC-20 Token](/docs/examples/06-erc20-token)
