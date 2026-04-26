---
title: "18 — External Calls via Interface"
description: "Typed cross-contract calls using V0.9 interface declarations."
order: 18
section: "V0.9 New"
level: intermediate
---

# 18 — External Calls via Interface

V0.9 introduces `interface` — a top-level declaration that defines the surface of an external contract for **typed** cross-contract calls. The compiler checks call-site signatures against the declared interface at compile time; bytecode emits a single, properly-encoded `CALL` opcode.

```covenant
interface IERC20 {
    action transfer(to: address, value: amount) returns bool
    view balance_of(who: address) returns amount
}

module Withdrawer {
    field token: address

    action initialize(t: address) {
        only deployer
        token = t
    }

    action withdraw(value: amount) {
        let iface = call_interface(token, IERC20)
        iface.transfer(caller, value)
    }
}
```

## Why this exists

Solidity's `address.call(bytes)` is untyped — you encode arguments by hand and the compiler can't tell you when you got it wrong. Covenant's `interface` declarations solve that:

- **Type-checked at compile time.** If you call `iface.transfer(caller, "wrong type")`, the compiler refuses.
- **No selector typos.** The selector is computed from the interface declaration, not from a string.
- **Auto-decode on return.** `iface.balance_of(addr)` returns `amount` directly — not `bytes` you have to abi-decode.

## What `interface` does NOT do

It does **not** import a contract. There is no inheritance. The interface is a *type signature* the compiler uses to verify your calls. The runtime checks at the EVM layer are the same as a hand-rolled `CALL` would do.

## Storage of external addresses

Store the target contract's address in a `field`, then pass it to `call_interface`:

```covenant
interface IFactory {
    action create_pair(a: address, b: address) returns address
    view get_pair(a: address, b: address) returns address
}

module Router {
    field factory: address

    action route(a: address, b: address, amount_a: amount, amount_b: amount) {
        let f = call_interface(factory, IFactory)
        let pair = f.get_pair(a, b)
        -- ...
    }
}
```

## What to notice

- **Return type matters.** If the external contract reverts, your action reverts too — there's no try/catch in V0.9.0. Use `try_action` (V0.9.x) for revert-tolerant calls.
- **`payable` is implicit on the call site, not the interface.** To send ETH with a call, use the V0.9.x payable variant `iface.action_name{value: ...}(args)` (deferred, currently use raw `call`).
- **Interfaces live at the top level.** They aren't nested inside modules.
- **Forward-compat.** Interfaces are compile-time only — they don't affect bytecode unless used. You can declare an interface and reference it later without runtime cost.

## Common pattern: gating actions on external state

```covenant
interface IERC20 {
    view balance_of(who: address) returns amount
}

module GatedAction {
    field token: address
    field min_balance: amount

    action vip_only_action() {
        let t = call_interface(token, IERC20)
        given t.balance_of(caller) >= min_balance
        -- protected logic
    }
}
```

## Try it

[Open in playground](https://playground.covenant-lang.org/?example=D3-external-call) — deploys a mock ERC-20 + a Withdrawer, then calls `transfer` through the interface.

## What's next

- [Reference: Compiler — Interface Lowering](/docs/reference/compiler/interface)
- [Cookbook: Composability Patterns](/docs/cookbook/composability)
- [Migration: from-solidity — calling external contracts](/docs/migration/from-solidity#calls)
