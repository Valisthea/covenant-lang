---
title: "05 — External Calls"
description: "Call other contracts, handle return values, and avoid reentrancy."
order: 5
section: "Fundamentals"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


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
