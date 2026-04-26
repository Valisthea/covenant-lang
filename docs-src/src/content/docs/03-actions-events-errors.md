---
title: "03 — Actions, Events & Errors"
description: "Define entry points, emit structured logs, and declare typed errors."
order: 3
section: "Fundamentals"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


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
