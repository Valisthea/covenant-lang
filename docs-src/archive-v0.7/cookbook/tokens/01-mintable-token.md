---
title: "Mintable Token"
description: "A fungible token where the owner can mint new supply up to a cap."
section: cookbook
order: 1
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Mintable Token

## Problem

I need a fungible token where an authorized owner can create new tokens, but total supply is capped.

## Solution

```covenant
token MintableToken {
    name: "Mintable Token"
    symbol: "MTK"
    decimals: 18
    supply: 0 tokens
    initial_holder: deployer

    field owner: address = deployer
    field max_supply: amount = 100_000_000 tokens

    event Minted(to: address indexed, amount: amount)
    event OwnershipTransferred(prev: address indexed, next: address indexed)

    error SupplyCapExceeded()
    error ZeroAmount()
    error ZeroAddress()

    action mint(to: address, amount: amount) only owner {
        given amount > 0 or revert_with ZeroAmount()
        given to != address(0) or revert_with ZeroAddress()
        given total_supply + amount <= max_supply or revert_with SupplyCapExceeded()

        balances[to] = balances[to] + amount
        total_supply = total_supply + amount

        emit Minted(to, amount)
    }

    action transfer_ownership(new_owner: address) only owner {
        given new_owner != address(0) or revert_with ZeroAddress()
        emit OwnershipTransferred(owner, new_owner)
        owner = new_owner
    }
}
```

## Explanation

- `supply: 0 tokens` -- starts with zero supply; minting creates it
- `only owner` -- the `mint` action is gated by the owner guard
- The three `given` checks (in order): amount not zero, recipient not zero address, cap not exceeded
- `transfer_ownership` uses a one-step transfer; see [Variations](#variations) for two-step

The compiler desugars `only owner` to `given caller == owner or revert_with Unauthorized()` and prepends it to the action body.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `mint` (cold recipient) | ~65,000 |
| `mint` (warm recipient) | ~25,000 |
| `transfer_ownership` | ~30,000 |

## Common Pitfalls

1. **Missing cap check**: Without `max_supply`, an owner can inflate supply indefinitely. Always set a cap unless supply is intentionally unbounded.
2. **No zero-address guard on mint recipient**: Tokens sent to `address(0)` are permanently burned without triggering `Transfer(addr, 0)`.
3. **One-step ownership**: A single `transfer_ownership` is irreversible if the new owner is wrong. See the two-step variation below.
4. **Overflow**: `total_supply + amount` could overflow without the cap check. The compiler catches this for constant values, but runtime values require an explicit check.
5. **Minting to self**: Minting to the owner\'s own address is valid but may be unintended. Add a check if needed.

## Variations

### Unbounded supply (no cap)

Remove `max_supply` and the cap check if total supply is governed externally:

```covenant
action mint(to: address, amount: amount) only owner {
    given amount > 0 or revert_with ZeroAmount()
    balances[to] = balances[to] + amount
    total_supply = total_supply + amount
    emit Minted(to, amount)
}
```

### Two-step ownership transfer

```covenant
field pending_owner: address = address(0)

action begin_transfer(new_owner: address) only owner {
    pending_owner = new_owner
}

action accept_ownership() {
    given caller == pending_owner or revert_with Unauthorized()
    emit OwnershipTransferred(owner, caller)
    owner = caller
    pending_owner = address(0)
}
```

## See Also

- [Burnable Token](/docs/cookbook/tokens/02-burnable-token)
- [Example 06 -- ERC-20 Token](/docs/examples/06-erc20-token)
- [Auth: Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin)
