---
title: "05 — External Calls"
description: "Call other contracts, handle return values, and avoid reentrancy."
order: 5
section: "Fundamentals"
---

# 05 — External Calls

## Calling an interface

Define an `interface` and call through it:

```covenant
interface IERC20 {
  action transfer(to: Address, amount: u256) -> Bool
  action balanceOf(who: Address) -> u256
}

contract Spender {
  field token: Address

  action spend(amount: u256) {
    let tok = IERC20(self.token);
    let ok = tok.transfer(msg.sender, amount);
    require(ok, TransferFailed);
  }
}
```

## Safety: reentrancy guard

Covenant's built-in `@nonreentrant` decorator locks the contract for the duration of the action:

```covenant
@nonreentrant
action withdraw(amount: u256) {
  require(self.balances[msg.sender] >= amount, InsufficientBalance);
  self.balances[msg.sender] -= amount;      // effect before interaction
  let ok = IERC20(self.token).transfer(msg.sender, amount);
  require(ok, TransferFailed);
}
```

The compiler also enforces checks-effects-interactions order via a static lint — disable with `@allow(cei_violation)` only when you have verified the call is safe.

## Low-level calls

For untyped calls (e.g. proxies):

```covenant
let result = call(target, data: calldata_bytes, value: 0);
require(result.success, CallFailed);
```

## Sending ETH

```covenant
action fund(recipient: Address) {
  require(msg.value > 0, ZeroValue);
  transfer_eth(recipient, msg.value);
}
```

`transfer_eth` is equivalent to Solidity `call{value: amount}("")` with a 2300 gas stipend check disabled (Covenant does not use the Solidity 2300-gas anti-pattern).

## staticcall

Use `@view` actions on external interfaces — the compiler emits `STATICCALL` automatically:

```covenant
@view
action quote(amount: u256) -> u256 {
  return IOracle(self.oracle).price() * amount / 1e18;
}
```
