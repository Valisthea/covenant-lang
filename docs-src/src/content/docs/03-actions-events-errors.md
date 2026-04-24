---
title: "03 — Actions, Events & Errors"
description: "Define entry points, emit structured logs, and declare typed errors."
order: 3
section: "Fundamentals"
---

# 03 — Actions, Events & Errors

## Actions

Actions are the public interface of a contract — analogous to Solidity functions with visibility `external`.

```covenant
contract Counter {
  field n: u256 = 0

  action increment() {
    self.n += 1;
    emit Incremented(self.n);
  }

  action increment_by(amount: u256) {
    require(amount > 0, InvalidAmount);
    self.n += amount;
    emit Incremented(self.n);
  }

  action value() -> u256 {
    return self.n;
  }
}
```

**Read vs write:** actions that only read state should be annotated `@view`:

```covenant
@view
action value() -> u256 { return self.n; }
```

The compiler enforces that `@view` actions contain no state mutations.

## Events

```covenant
event Incremented(new_value: u256)
event Transfer(from: indexed Address, to: indexed Address, amount: u256)
```

`indexed` fields become Bloom-filter topics (up to 3 per event, same as Solidity). The ABI encoder emits them as `event Transfer(address indexed from, address indexed to, uint256 amount)`.

Emit syntax:

```covenant
emit Transfer(from: sender, to: recipient, amount: value);
```

## Errors

Typed errors revert with ABI-encoded data:

```covenant
error InvalidAmount(provided: u256)
error Unauthorised(caller: Address)
error InsufficientBalance(available: u256, requested: u256)
```

Revert with an error:

```covenant
require(amount > 0, InvalidAmount(amount));
// or imperatively:
if self.balances[caller] < amount {
  revert InsufficientBalance(self.balances[caller], amount);
}
```

## `require` vs `revert`

| Keyword | Behaviour |
|---------|-----------|
| `require(cond, Err)` | Reverts with `Err` if `cond` is false |
| `revert Err(..args)` | Unconditionally reverts |
| `assert(cond)` | Reverts with `Panic(0x01)` — use for invariants only |
