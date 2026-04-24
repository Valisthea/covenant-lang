---
title: "Fuzz Testing"
description: "Run thousands of randomized inputs against your contract to find edge cases automatically."
section: cookbook
order: 2
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Fuzz Testing

## Problem

My inline tests pass for the handful of inputs I thought to check, but my contract handles arbitrary user-supplied values. I want the test runner to generate thousands of inputs and report any that break my expectations — especially overflow, underflow, and rounding bugs.

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

    action transfer(to: address, value: u256) {
        given balances[caller] >= value or revert_with InsufficientBalance()
        balances[caller] = balances[caller] - value
        balances[to] = balances[to] + value
    }

    // --- Fuzz tests ---

    fuzz "no overflow on mint" (amount: u256) {
        assume amount < type::max::<u256>() - total_supply
        let old_supply = total_supply
        act owner.mint(bob, amount)
        expect total_supply == old_supply + amount
    }

    fuzz "transfer preserves total" (a: u256, b: u256) {
        assume a > 0 && b <= a
        act owner.mint(alice, a)
        let sum_before = balances[alice] + balances[bob]
        act alice.transfer(bob, b)
        expect balances[alice] + balances[bob] == sum_before
    }

    fuzz "transfer to self is a no-op" (a: u256) {
        assume a > 0 && a < 1_000_000_000
        act owner.mint(alice, a)
        act alice.transfer(alice, a)
        expect balances[alice] == a
    }

    fuzz "insufficient balance always reverts"
         (balance: u256, attempt: u256) {
        assume attempt > balance
        assume balance < type::max::<u256>() / 2
        act owner.mint(alice, balance)
        expect_revert InsufficientBalance()
        act alice.transfer(bob, attempt)
    }
}
```

Run it:

```bash
covenant fuzz --runs 10000                # default 256 if omitted
covenant fuzz --runs 100000 --seed 0xBEEF # deterministic replay
covenant fuzz --shrink 500                # shrinking budget on failure
covenant fuzz --only "no overflow"        # name filter
```

## Explanation

- `fuzz "name" (args...) { ... }` declares a property-based test. Each parameter becomes a randomly generated input.
- Covenant uses coverage-guided generation: paths that newly covered branches get prioritized, so you reach deep error states faster than pure random.
- `assume expr` rejects the current input and draws a new one. Use it to avoid wasting runs on trivially-invalid inputs (e.g. `amount == 0`, arithmetic that would overflow the *test setup*, not the code under test). Over-constraining with `assume` hides bugs — keep assumptions as loose as possible.
- `expect` behaves just like in `test` blocks, but on failure the runner automatically **shrinks** — it repeatedly halves and mutates the failing input until it finds the smallest one that still fails. A 200-line overflow is reduced to the minimal reproducer, usually in under a second.
- Seed the RNG with `--seed` to reproduce a failure exactly. CI prints the failing seed on every failure.

### `assume` vs `expect`

| Construct | Failure behavior | Purpose |
|-----------|------------------|---------|
| `assume cond` | Silently discards the input, draws a new one | Precondition on the *input* |
| `expect cond` | Records a failure, continues test | Postcondition on the *contract* |
| `assert cond` | Aborts immediately | Postcondition that must hold for the rest of the test to be meaningful |

Rule of thumb: if the condition is about the inputs you were given, use `assume`; if it is about the state the contract produced, use `expect`.

## Gas Estimate

Fuzz runs are off-chain; no on-chain gas. The runner reports per-property statistics:

```
fuzz: no overflow on mint
  runs: 10000  rejects: 41  failed: 0
  mean gas: 48,221   max gas: 51,044
```

Use `--fail-fast` in CI to stop at the first failure; omit it locally so you see all failing properties at once.

## Common Pitfalls

1. **Over-assuming inputs**: `assume amount < 100` turns a fuzz test into a narrow unit test. Keep assumptions at the boundary of "mathematically impossible in setup," not "inputs I happen to care about."
2. **Stateful pollution between runs**: each fuzz iteration re-runs the `deploy()` implicitly. If you disable it with `#[no_reset]`, inputs from run N can poison run N+1.
3. **Mapping keys**: `address` generation is random, so `balances[alice]` may be zero where you expected a balance. Seed with explicit `act owner.mint(alice, X)` inside the fuzz body.
4. **Non-determinism**: avoid `block.timestamp` or `block.prevrandao` inside a fuzz expectation without also fuzzing them. The runner pins timestamps by default; opt in with `fuzz_time = true`.
5. **Ignoring shrink output**: when a fuzz fails, the *shrunk* input is what you read. It's the simplest reproducer; paste it into a regular `test` block to lock the regression in.

## Variations

- **Bounded types**: declare `fuzz ... (amount: u256 in 1..1_000_000) { ... }` to constrain the generator directly instead of `assume`-ing.
- **Custom generators**: register `gen::non_zero::<u256>()` or user-defined `gen::address_in(set)` via `#[fuzz_generator]` attributes.
- **Differential fuzzing**: compare two implementations — `expect reference_impl(x) == my_impl(x)` — to port Solidity code to Covenant safely.

## See Also

- [Inline Tests](/docs/cookbook/testing/01-inline-tests)
- [Invariant Testing](/docs/cookbook/testing/03-invariant-testing)
- [CLI Reference — `covenant fuzz`](/docs/reference/cli/fuzz)
