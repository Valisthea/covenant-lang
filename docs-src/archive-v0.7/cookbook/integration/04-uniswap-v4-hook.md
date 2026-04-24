---
title: "Uniswap V4 Hook"
description: "Implement a Uniswap V4 hook contract that runs custom logic before/after swap, add, or remove liquidity."
section: cookbook
order: 4
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Uniswap V4 Hook

## Problem

Uniswap V4 replaces V3's static pool contracts with a single `PoolManager` plus programmable *hooks*: contracts whose addresses encode which lifecycle callbacks they handle. I want to write a hook that refunds 10 basis points of swap fees to whitelisted users -- a classic "fee rebate" pattern -- using the `beforeSwap` and `afterSwap` callbacks.

## Solution

```covenant
// V4 core types (abridged)
struct PoolKey {
    currency0: address
    currency1: address
    fee: u24
    tick_spacing: i24
    hooks: address
}

struct SwapParams {
    zero_for_one: bool
    amount_specified: i256
    sqrt_price_limit_x96: u160
}

// Packed (int128 currency0Delta, int128 currency1Delta) + hook-added fee override
struct BeforeSwapDelta {
    delta_specified: i128
    delta_unspecified: i128
}

struct BalanceDelta {
    amount0: i128
    amount1: i128
}

external contract IPoolManager {
    action take(currency: address, to: address, amount: u256)
    action settle(currency: address) returns (paid: u256) payable
    action sync(currency: address)
}

contract FeeRebateHook {
    field owner: address = deployer
    field pool_manager: IPoolManager
    field whitelisted: mapping<address, bool>

    // 10 basis points = 0.10%
    const REBATE_BPS: u24 = 10
    const BPS_DENOMINATOR: u24 = 10000

    // Return selector for BeforeSwapDelta-returning hook
    const BEFORE_SWAP_SELECTOR: bytes4 = 0x575e24b4
    const AFTER_SWAP_SELECTOR: bytes4 = 0xb47b2fb1

    event Whitelisted(user: address indexed, allowed: bool)
    event RebatePaid(user: address indexed, currency: address, amount: u256)

    error NotPoolManager()
    error NotOwner()

    guard only_pm {
        given caller == address(pool_manager) or revert_with NotPoolManager()
    }

    guard only_owner {
        given caller == owner or revert_with NotOwner()
    }

    action init(pm: address) {
        given address(pool_manager) == address(0)
        pool_manager = IPoolManager(pm)
    }

    action set_whitelist(user: address, allowed: bool) only_owner {
        whitelisted[user] = allowed
        emit Whitelisted(user, allowed)
    }

    // --- Hook callbacks ---
    // The hook address must have the before_swap and after_swap permission bits set
    // in its low-order bits (V4 encodes flags in the deployed address).

    @hook(before_swap)
    action before_swap(
        sender: address,
        key: PoolKey,
        params: SwapParams,
        hook_data: bytes
    ) only_pm returns (selector: bytes4, delta: BeforeSwapDelta, fee_override: u24) {

        // No-op before swap; we do the rebate math in after_swap where we know the
        // actual traded amount.
        return (
            BEFORE_SWAP_SELECTOR,
            BeforeSwapDelta { delta_specified: 0, delta_unspecified: 0 },
            0  // 0 == use pool's default fee
        );
    }

    @hook(after_swap)
    action after_swap(
        sender: address,
        key: PoolKey,
        params: SwapParams,
        delta: BalanceDelta,
        hook_data: bytes
    ) only_pm returns (selector: bytes4, hook_delta: i128) {

        // Only rebate whitelisted users
        given whitelisted[sender] {
            // Which currency did the user pay in?
            let paid_currency = params.zero_for_one ? key.currency0 : key.currency1
            let gross_in: u256 = params.zero_for_one
                ? u256(-delta.amount0)
                : u256(-delta.amount1)

            // rebate = gross_in * REBATE_BPS / BPS_DENOMINATOR
            let rebate: u256 = (gross_in * REBATE_BPS) / BPS_DENOMINATOR

            given rebate > 0 {
                // The hook is solvent in `paid_currency` (funded by the owner).
                // Tell the PoolManager to send `rebate` from hook's credit balance to the swapper.
                pool_manager.take(paid_currency, sender, rebate)
                emit RebatePaid(sender, paid_currency, rebate)

                // Report the negative hook delta so the PoolManager accounts for it.
                return (AFTER_SWAP_SELECTOR, i128(rebate))
            }
        }

        return (AFTER_SWAP_SELECTOR, 0)
    }

    // Owner funds the hook with rebate reserves in either pool currency.
    action fund(currency: address, amount: u256) only_owner {
        pool_manager.sync(currency)
        // caller must have approved `amount` of `currency` to this hook
        // ... transferFrom(caller, address(this), amount)
        pool_manager.settle(currency)
    }
}
```

## Explanation

- **Hook address encodes permissions**: V4 reads the low bits of the deployed address to decide which callbacks to invoke. Deploy with `CREATE2` and mine an address whose low byte has the `BEFORE_SWAP_FLAG | AFTER_SWAP_FLAG` bits set. Covenant's `@hook(...)` decorators are a compile-time assertion that the final address must carry those flags.
- **Two-phase rebate**: `before_swap` is a no-op here because we don't know the realized amount until after. `after_swap` receives the `BalanceDelta` with signed amounts -- negative means the user owes the pool, positive means the pool owes the user.
- **`IPoolManager.take`** pulls from the hook's currency credit balance and credits the user's wallet -- this is how V4 hooks disburse funds.
- **Hook delta reporting**: Returning a positive `hook_delta` tells the PoolManager to reduce the hook's credit by that amount, which keeps the pool's flash-accounting invariant balanced.
- **Return selector check**: The PoolManager verifies the first return value against the canonical selector. Returning the wrong selector reverts the whole swap.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `before_swap` (whitelisted user) | ~4,000 |
| `after_swap` (whitelisted, rebate paid) | ~55,000 |
| `after_swap` (not whitelisted) | ~6,000 |
| `set_whitelist` | ~28,000 |
| Hook deployment with mined address | ~2,000,000 + mining time |

## Common Pitfalls

1. **Wrong hook address flags**: If your deployed address doesn't have the correct permission bits, the PoolManager silently skips the callback. Use `HookMiner` or similar to mine until flags match; verify with a test that calls the hook-flag inspector.
2. **Not calling `pool_manager.take` / `settle`**: V4 uses flash accounting -- every debit must be matched by a settle before the top-level call returns, or the whole tx reverts. Forgetting this is the #1 V4 hook bug.
3. **Using `tx.origin` for whitelist check**: Use `sender` (the address that initiated the swap via the router), not `tx.origin`. Bots often route through aggregators -- decide whether to whitelist routers, end users, or both.
4. **Returning the wrong selector**: Each hook callback has its own selector constant. Returning `beforeSwap`'s selector from `afterSwap` makes the PoolManager reject the result and revert.
5. **Rebate larger than swap**: Always cap `rebate <= gross_in` to prevent a whitelisted user from draining the hook with a microscopic swap that rounds favourably.
6. **Hook insolvency**: If the hook runs out of `paid_currency` credit, `take` reverts mid-swap and every user's trade fails. Monitor balances and top up proactively.

## Variations

### Dynamic fee hook

Return a non-zero `fee_override` from `before_swap` to override the pool's static fee per-trade (e.g., charge less during off-peak hours). Requires the pool to be initialized with `LPFeeLibrary.DYNAMIC_FEE_FLAG`.

### JIT rebalancing hook

Use `before_add_liquidity` / `before_remove_liquidity` to warm up a just-in-time rebalance strategy. Combine with `IPoolManager.unlock` for arbitrary flash-accounted logic.

### Per-pool rebate rates

Store `rebate_bps: mapping<bytes32, u24>` keyed by `PoolKey.toId()` so the same hook can serve many pools with different rebates.

## See Also

- [Chainlink Oracle Integration](/docs/cookbook/integration/01-chainlink-oracle)
- [Safe (Gnosis) Multisig Integration](/docs/cookbook/integration/03-safe-multisig)
- [Uniswap V4 Hooks documentation](https://docs.uniswap.org/contracts/v4/concepts/hooks)
