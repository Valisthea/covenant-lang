---
title: "Syntax Mapping"
description: "A side-by-side translation of Solidity syntax to Covenant — contracts, fields, actions, guards, events, constructors, and visibility."
section: migration
order: 2
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Syntax Mapping

This page is the literal translation table. Every section shows the same idea in both languages. If you skim only one page of this guide, make it this one — the rest builds on the vocabulary introduced here.

## Contract declaration

The top-level container is still called a `contract`. Covenant additionally offers `token` as a specialized variant with the ERC-20-shaped fields prewired.

```solidity
// Solidity
pragma solidity ^0.8.24;

contract Vault {
    // ...
}
```

```covenant
// Covenant
contract Vault {
    // ...
}
```

There is no pragma line. The Covenant compiler pins the language version via `covenant.toml`.

## State variables

Solidity puts the type before the name. Covenant follows the Rust/TypeScript convention: `field name: type`. This reads more naturally with generics and nested types.

```solidity
// Solidity
uint256 public totalSupply;
address public owner;
mapping(address => uint256) public balances;
```

```covenant
// Covenant
field total_supply: amount
field owner: address
field balances: mapping<address, amount>
```

Two things changed beyond syntax:

- `uint256` holding a balance became `amount`. `amount` is still 256 bits under the hood, but it carries decimals metadata the compiler uses in unit checks. For plain counters, `u256` is still available.
- `public` is implicit for state variables — the compiler synthesizes a read accessor. If you do not want one, mark the field `@private`.

## Functions → actions

Covenant renames `function` to `action`. The rename is not cosmetic: actions have slightly stricter rules than Solidity functions (no silent reentrancy, explicit state-mutation classification, guards are first-class).

```solidity
// Solidity
function deposit(uint256 amount) external {
    require(amount > 0, "zero");
    balances[msg.sender] += amount;
    emit Deposit(msg.sender, amount);
}
```

```covenant
// Covenant
action deposit(value: amount) {
    given value > 0 or revert_with ZeroDeposit()
    balances[caller] += value
    emit Deposit(caller, value)
}
```

Things to notice:

- `msg.sender` became `caller`. Also available: `origin` (tx-level), `self` (contract's own address).
- `require(cond, "msg")` became `given cond or revert_with Err()`. Errors are typed — see below.
- There is no explicit `external`. Visibility is public-by-default for actions; add `@internal` to restrict.

## Modifiers → guards

Solidity modifiers wrap a function body with `_;`. Covenant `guard` blocks are declarative boolean predicates — they say what must be true, not how to branch.

```solidity
// Solidity
modifier onlyOwner() {
    require(msg.sender == owner, "not owner");
    _;
}

function withdraw(uint256 n) external onlyOwner { ... }
```

```covenant
// Covenant
guard only_owner {
    caller == owner or revert_with NotOwner()
}

action withdraw(n: amount) requires only_owner { ... }
```

Guards can also be applied with the built-in shorthand `only owner` when the field is literally named `owner`.

## Events and errors

Events look identical. The difference is that `emit` is always required (Solidity is lenient about this in some positions) and errors are typed values rather than strings.

```solidity
// Solidity
event Deposit(address indexed from, uint256 amount);
error ZeroDeposit();

function f() external {
    if (msg.value == 0) revert ZeroDeposit();
    emit Deposit(msg.sender, msg.value);
}
```

```covenant
// Covenant
event Deposit(from: address indexed, value: amount)
error ZeroDeposit()

action f() payable {
    given sent > 0 or revert_with ZeroDeposit()
    emit Deposit(caller, sent)
}
```

Custom errors are zero-cost (as in Solidity 0.8.4+) and selector-encoded. The compiler rejects `revert_with` of an undeclared error.

## `require` → `given`

This is the single most common translation you'll do:

```solidity
require(balance >= n, "insufficient");
require(block.timestamp > unlockAt, "locked");
require(to != address(0), "zero addr");
```

```covenant
given balance >= n or revert_with Insufficient()
given now > unlock_at or revert_with Locked()
given to != address(0) or revert_with ZeroAddress()
```

Multiple guards can be grouped:

```covenant
given {
    balance >= n,
    now > unlock_at,
    to != address(0),
} or revert_with Invalid()
```

## Constructors → `deploy` block

Covenant separates construction from regular actions. A `deploy` block runs once at contract creation and is the only place `field` values marked as immutable can be assigned.

```solidity
// Solidity
constructor(address _owner, uint256 _cap) {
    owner = _owner;
    cap = _cap;
}
```

```covenant
// Covenant
deploy(initial_owner: address, initial_cap: amount) {
    owner = initial_owner
    cap = initial_cap
}
```

The `deploy` block does not return anything and cannot be re-entered.

## Visibility modifiers

Solidity has four: `public`, `external`, `internal`, `private`. Covenant collapses these:

| Solidity | Covenant |
|---|---|
| `public` / `external` (action) | default (no annotation) |
| `internal` | `@internal` |
| `private` | `@private` |
| `public` (state var) | default (read accessor synthesized) |
| `private` (state var) | `@private` |

In practice you write fewer annotations. When you *do* see `@internal`, it is a deliberate statement that this code is not part of the contract's public surface.

## Summary card

```
Solidity              Covenant
-----------------------------------------
contract              contract / token
uint256 x             field x: u256 / amount
function              action
modifier              guard
require(c,"m")        given c or revert_with E()
event / emit          event / emit (same)
error                 error (same, always typed)
constructor           deploy
msg.sender            caller
address payable       address
public (default)      (default)
internal              @internal
```

With this vocabulary in hand, move on to the type system — the subtler differences live there.
