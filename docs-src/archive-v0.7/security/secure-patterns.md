---
title: "Secure Patterns"
description: "Recommended security patterns and best practices for Covenant contracts."
order: 3
section: "Security"
---

# Secure Patterns

Covenant's type system and compiler catch many vulnerabilities automatically. This page documents patterns that go beyond static analysis — design-level decisions that prevent entire vulnerability classes.

## 1. Checks-Effects-Interactions (CEI)

Always perform state changes **before** external calls. Covenant's LSP warns on violations; the compiler enforces it for `@nonreentrant` actions.

```covenant
// CORRECT — effect before interaction
@nonreentrant
action withdraw(amount: u256) {
  require(self.balances[msg.sender] >= amount, InsufficientBalance);
  self.balances[msg.sender] -= amount;    // effect
  transfer_eth(msg.sender, amount);       // interaction
}
```

## 2. Pull payments over push payments

Instead of pushing ETH to recipients (reentrancy risk), let them pull:

```covenant
field pending_withdrawals: Map<Address, u256>

// Internally: schedule payment
internal action _schedule_payment(to: Address, amount: u256) {
  self.pending_withdrawals[to] += amount;
}

// Publicly: recipient pulls their own funds
@nonreentrant
action withdraw_payment() {
  let amount = self.pending_withdrawals[msg.sender];
  require(amount > 0, NothingToWithdraw);
  self.pending_withdrawals[msg.sender] = 0;
  transfer_eth(msg.sender, amount);
}
```

## 3. Use `only()` guards, not `if`/`revert` manually

```covenant
// PREFERRED
action admin_action() { only(owner); ... }

// AVOID — easy to forget, no static verification
action admin_action() {
  if msg.sender != owner() { revert Unauthorised; }
  ...
}
```

## 4. Validate oracle staleness

Always check `updatedAt` when consuming price feeds:

```covenant
let (_, answer, _, updatedAt, _) = feed.latestRoundData();
require(block.timestamp - updatedAt <= MAX_STALENESS, StalePrice);
require(answer > 0, NegativePrice);
```

## 5. Two-step ownership transfer

Single-step `transfer_ownership` can permanently lose a contract if you transfer to a wrong address. Use a two-step pattern:

```covenant
field pending_owner: Address

action propose_ownership(new_owner: Address) {
  only(owner);
  self.pending_owner = new_owner;
}

action accept_ownership() {
  require(msg.sender == self.pending_owner, NotPendingOwner);
  self.pending_owner = Address(0);
  _transfer_ownership(msg.sender);
}
```

## 6. Emit events for all state changes

Every mutation that downstream systems or UIs need to observe should emit an event. Covenant's LSP detector `missing-event` flags state mutations in `@view` contexts.

## 7. Timelocks for governance actions

Protect high-impact actions with a timelock:

```covenant
field upgrade_delay:  u256 = 48 * 3600   // 48 hours
field pending_upgrade: Address
field upgrade_eta:     u256

action propose_upgrade(new_impl: Address) {
  only(owner);
  self.pending_upgrade = new_impl;
  self.upgrade_eta     = block.timestamp + self.upgrade_delay;
  emit UpgradeProposed(new_impl, self.upgrade_eta);
}

action execute_upgrade() {
  only(owner);
  require(block.timestamp >= self.upgrade_eta, TooEarly);
  _upgrade(self.pending_upgrade);
}
```

## 8. Integer overflow

Covenant uses checked arithmetic by default. All `+`, `-`, `*` on integer types revert on overflow. Use `unchecked { }` only when you have mathematically proven safety:

```covenant
// Safe by default
self.total += amount;

// Unchecked (document why it is safe)
unchecked {
  // amount is always < (2^256 - total) because of the cap check above
  self.total += amount;
}
```
