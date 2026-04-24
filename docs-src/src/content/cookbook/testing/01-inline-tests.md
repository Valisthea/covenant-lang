---
title: "Inline Tests"
description: "Write unit tests directly inside the contract file using Covenant's built-in `test` blocks."
section: cookbook
order: 1
level: beginner
---

<!-- Last sync: 2026-04-23 -->

# Inline Tests

## Problem

I want to unit-test my contract without spinning up a separate test framework, Hardhat node, or Foundry toolchain. Tests should live next to the code they exercise and run in milliseconds.

## Solution

```covenant
token CoinBook {
    field total_supply: amount = 0
    field balances: map<address, amount>
    field owner: address = deployer

    event Transfer(from: address indexed, to: address indexed, value: amount)

    error Unauthorized()
    error InsufficientBalance()

    action mint(to: address, value: amount) {
        given caller == owner or revert_with Unauthorized()
        balances[to] = balances[to] + value
        total_supply = total_supply + value
        emit Transfer(address(0), to, value)
    }

    action transfer(to: address, value: amount) {
        given balances[caller] >= value or revert_with InsufficientBalance()
        balances[caller] = balances[caller] - value
        balances[to] = balances[to] + value
        emit Transfer(caller, to, value)
    }

    view balance_of(who: address) -> amount {
        return balances[who]
    }

    // --- Tests ---

    test "mint increases balance and supply" {
        deploy()
        act owner.mint(alice, 1000)
        expect balance_of(alice) == 1000
        expect total_supply == 1000
    }

    test "transfer moves funds" {
        deploy()
        act owner.mint(alice, 500)
        act alice.transfer(bob, 200)
        expect balance_of(alice) == 300
        expect balance_of(bob) == 200
    }

    test "transfer fails on insufficient balance" {
        deploy()
        act owner.mint(alice, 10)
        expect_revert InsufficientBalance()
        act alice.transfer(bob, 100)
    }

    test "non-owner cannot mint" {
        deploy()
        expect_revert Unauthorized()
        act alice.mint(alice, 1_000_000)
    }

    test "emits Transfer on mint" {
        deploy()
        act owner.mint(alice, 42)
        expect_event Transfer(address(0), alice, 42)
    }

    test "time-based flow" {
        deploy()
        act owner.mint(alice, 100)
        warp(7 days)
        assert block.timestamp > deploy_time + 6 days
    }
}
```

Run the tests:

```bash
covenant test                 # run every test in the project
covenant test CoinBook        # run tests in a single contract
covenant test --match "mint"  # run tests whose name matches a regex
covenant test --gas           # print gas consumption per test
```

## Explanation

- `test "name" { ... }` is a block the compiler picks up alongside `action` definitions. Tests compile against the same AST as the contract and execute in an in-process EVM (no RPC, no node).
- `deploy()` resets state and re-runs the constructor. It is implicit at the start of every `test` block unless you pass `--no-reset`.
- **Test actors** — `alice`, `bob`, `charlie`, `dave`, `eve` are pre-funded test addresses. `owner` is an alias for whichever address called `deploy()`.
- `act actor.method(args)` runs a transaction as `actor`. `act` is the only way to advance state; plain function calls are read-only.
- `expect X` is a soft assertion — on failure, the test records the error and continues so you see every failure at once. `assert X` is hard — it aborts immediately. Prefer `expect` unless a later line would crash without it.
- `expect_revert ErrorName()` wraps the *next* `act` and passes only if it reverts with that exact error.
- `expect_event EventName(args)` checks the event log produced by the last `act`.
- `warp(n)` advances `block.timestamp` by `n` seconds (use `days`, `hours`, `minutes` suffixes for readability). `roll(n)` advances by `n` blocks.

## Gas Estimate

Tests run off-chain, so there is no deployed gas cost. `covenant test --gas` reports the gas each `act` would have consumed on-chain, so you can regression-test gas budgets directly:

```covenant
test "transfer stays under 55k gas" {
    deploy()
    act owner.mint(alice, 100)
    act alice.transfer(bob, 50) with gas_budget(55_000)
}
```

## Common Pitfalls

1. **Forgetting `deploy()`** when `--no-reset` is on: state leaks between tests in unexpected ways. Keep the default (auto-reset) unless you have a reason.
2. **Using `assert` everywhere**: you lose the ability to see multiple failures in a single run. Default to `expect`.
3. **Hard-coded timestamps**: use `warp(n)` deltas, not absolute `block.timestamp = ...`. Absolute timestamps break when the CI clock changes.
4. **Reading private state in tests**: only `view` functions and public fields are accessible. If you need to peek at internals, expose a `#[test_only] view` accessor.
5. **Missing `expect_revert`**: without it, a revert inside `act` fails the whole test. Always wrap expected failures.

## Variations

- **Setup blocks**: factor shared setup into `setup { ... }`. It runs before every test in the same contract.
- **Snapshots**: `let snap = snapshot(); ...; revert_to(snap)` lets you branch state inside one test.
- **Mocking oracles**: `mock(oracle.price(TOKEN), 2000)` stubs an external call for the duration of the test.

## See Also

- [Fuzz Testing](/docs/cookbook/testing/02-fuzz-testing)
- [Invariant Testing](/docs/cookbook/testing/03-invariant-testing)
- [CLI Reference — `covenant test`](/docs/reference/cli/test)
