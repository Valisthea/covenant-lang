---
title: "Invariant Testing"
description: "Define global properties that must always hold, then let the fuzzer try to break them."
section: cookbook
order: 3
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Invariant Testing

## Problem

Fuzz tests check that a single action behaves correctly on a single input. Real bugs usually live in the *sequence* of actions: mint, transfer, burn, repay, in some adversarial order that breaks a global property. I want to declare "the sum of balances always equals the total supply" once and have the fuzzer try every sequence it can think of to falsify that.

## Solution

```covenant
token CoinBook {
    field total_supply: u256 = 0
    field balances: map<address, u256>
    field owner: address = deployer

    error Unauthorized()
    error InsufficientBalance()

    action mint(to: address, value: u256) {
        given caller == owner or revert_with Unauthorized()
        balances[to] = balances[to] + value
        total_supply = total_supply + value
    }

    action burn(from: address, value: u256) {
        given caller == owner or revert_with Unauthorized()
        given balances[from] >= value or revert_with InsufficientBalance()
        balances[from] = balances[from] - value
        total_supply = total_supply - value
    }

    action transfer(to: address, value: u256) {
        given balances[caller] >= value or revert_with InsufficientBalance()
        balances[caller] = balances[caller] - value
        balances[to] = balances[to] + value
    }

    // --- Invariants ---

    invariant "sum of balances equals total supply" {
        sum(balances) == total_supply
    }

    invariant "no balance exceeds total supply" {
        forall addr in addresses(balances) {
            balances[addr] <= total_supply
        }
    }

    invariant "owner is immutable" {
        owner == initial(owner)
    }
}
```

### Handler contract (bounded input space)

Random addresses and random amounts rarely exercise the interesting behaviour. A *handler* wraps the target and routes fuzzer draws into a small universe of realistic actors and bounded values:

```covenant
#[handler_for(CoinBook)]
contract CoinBookHandler {
    field target: CoinBook
    field actors: address[] = [alice, bob, charlie]
    field ghost_minted: u256 = 0
    field ghost_burned: u256 = 0

    action h_mint(actor_idx: u8, value: u256) {
        let who = actors[actor_idx % actors.len()]
        let v = value % 1_000_000_000
        act target.owner.mint(who, v)
        ghost_minted = ghost_minted + v
    }

    action h_burn(actor_idx: u8, value: u256) {
        let who = actors[actor_idx % actors.len()]
        let v = value % (target.balances[who] + 1)
        act target.owner.burn(who, v)
        ghost_burned = ghost_burned + v
    }

    action h_transfer(from_idx: u8, to_idx: u8, value: u256) {
        let from = actors[from_idx % actors.len()]
        let to = actors[to_idx % actors.len()]
        let v = value % (target.balances[from] + 1)
        act from.transfer(to, v)
    }

    // Ghost invariant — cross-checks the handler's own accounting
    invariant "ghost matches supply" {
        target.total_supply == ghost_minted - ghost_burned
    }
}
```

Run it:

```bash
covenant invariant --depth 50 --runs 1000
covenant invariant --depth 100 --runs 5000 --seed 0xC0FFEE
covenant invariant --handler CoinBookHandler
covenant invariant --only "ghost matches supply"
```

## Explanation

- `invariant "name" { expr }` declares a boolean predicate that must hold after **every** action in a random sequence, including reverts. The fuzzer builds sequences up to `--depth` actions deep, checks every invariant after each step, and shrinks on failure.
- `sum(map)`, `forall x in map { ... }`, and `initial(field)` are built-in helpers available only inside `invariant` blocks. `initial(owner)` returns the value of `owner` at `deploy()` time.
- **Handlers** (`#[handler_for(T)]`) give you control over the action distribution. Without a handler, the fuzzer picks from every `action` uniformly and generates unconstrained arguments — you'd waste most runs on inputs that trivially revert (mint by non-owner, transfer more than balance). The handler clamps arguments to plausible ranges and keeps *ghost variables* that mirror the target's state, letting you write stronger cross-checks.
- **Ghost variables** (`ghost_minted`, `ghost_burned`) are contract fields on the handler. They let you express invariants like "the target's total supply equals everything the handler has ever minted minus burned," which is much stricter than any single-action assertion.

### Sequence generation

```
deploy()
→ h_mint(0, 500)        # alice += 500
→ h_transfer(0, 1, 100) # alice → bob 100
→ h_burn(1, 50)         # bob -= 50
→ (check all invariants)
→ h_mint(2, 99999)
→ ...
```

If any invariant fails, the runner shrinks by deleting actions and clamping arguments until it finds the minimal reproducing sequence — typically 2–4 actions.

## Gas Estimate

Invariant runs are off-chain. A typical budget: `--depth 50 --runs 1000` ≈ 50,000 actions ≈ 5–30 seconds on a laptop. Each invariant check is O(state size); the `sum(balances)` iteration dominates for ERC-20-sized state. Use `#[cheap_invariant]` to mark invariants that should be re-checked only every N steps if you see CI slowdowns.

## Common Pitfalls

1. **No handler**: without a handler, ~95% of actions revert at the `given` check and the fuzzer never reaches deep state. Always write a handler for anything beyond toy contracts.
2. **Invariants that reference transient state**: "`caller == owner`" is not an invariant — `caller` is only defined during an action. Invariants run *between* actions.
3. **Ghost drift**: if your handler forgets to update a ghost on one path, the ghost invariant will false-positive. Prefer ghosts that mirror a simple monotone quantity (sum, count).
4. **Too-high depth**: `--depth 500` rarely finds bugs that `--depth 50 --runs 10x` wouldn't; prefer more runs over deeper runs until you have evidence otherwise.
5. **Ignoring reverts**: by default, actions that revert still count toward depth. Use `#[only_successful]` on a handler action to skip reverts when counting.
6. **State reset**: invariants are checked against the current state; each *run* starts from a fresh `deploy()`. Persistent bugs across deploys need a separate fork test.

## Variations

- **ERC-4626 vault suite**: invariants `totalAssets >= totalSupply * minPricePerShare`, `sum(shares) == totalSupply`, `convertToAssets(totalSupply) <= totalAssets`.
- **AMM suite**: invariants `reserve0 * reserve1 >= k_initial`, `lp_total == sum(lp_balances)`.
- **Lending suite**: invariants `sum(debt) <= sum(borrow_caps)`, `forall user { health_factor(user) >= 1 || is_liquidatable(user) }`.

## See Also

- [Inline Tests](/docs/cookbook/testing/01-inline-tests)
- [Fuzz Testing](/docs/cookbook/testing/02-fuzz-testing)
- [CLI Reference — `covenant invariant`](/docs/reference/cli/invariant)
- [Example 16 — ERC-20 Invariant Suite](/docs/examples/16-erc20-invariants)
