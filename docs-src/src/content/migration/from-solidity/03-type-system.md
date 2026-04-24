---
title: "Type System Differences"
description: "Where Covenant's type system diverges from Solidity's — amount vs u256, address capabilities, safe arithmetic, timestamps, and encrypted<T>."
section: migration
order: 3
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Type System Differences

Syntax is the easy part. The types are where Covenant expresses opinions — opinions that show up as compile errors when you try to write Solidity habits verbatim. This page walks through the differences that matter.

## `amount` vs `uint256`

In Solidity every balance, allowance, fee, and reward is a `uint256`. The type system tells you nothing about *what kind* of integer you're holding.

Covenant keeps `u256` for plain unsigned integers but introduces `amount` for values denominated in a token or currency.

```solidity
// Solidity — all uint256, no compiler help
uint256 userBalance;
uint256 blockNumber;
uint256 feeBps;
```

```covenant
// Covenant — intent encoded in types
field user_balance: amount
field block_number: u64
field fee_bps: u16
```

An `amount` carries decimals metadata. The compiler rejects adding an `amount` to a `u256` without an explicit cast. It also rejects mixing two `amount`s with different decimals — you cannot accidentally add 6-decimal USDC to 18-decimal ETH.

```covenant
action bad() {
    let a: amount<6> = 1_000_000  // 1 USDC
    let b: amount<18> = 1e18       // 1 ETH
    let c = a + b  // compile error: mismatched decimals
}
```

When the decimals parameter is elided (`amount` without angle brackets), it means "whatever the containing token declares."

## `address` — no `payable` distinction

Solidity carries a scar from its early design: `address` and `address payable` are different types, and converting between them is a ritual.

Covenant has one `address`. The capability to receive value is checked at send time, not tracked in the type.

```solidity
// Solidity
address payable recipient = payable(msg.sender);
recipient.transfer(amount);
```

```covenant
// Covenant
let recipient: address = caller
transfer(recipient, value) or revert_with TransferFailed()
```

`transfer` here is the built-in send primitive. It returns a `Result` — the `or revert_with` handles the failure branch. Silently ignoring a failed send is not expressible.

## `mapping<K, V>` — generic syntax

Solidity's `mapping(K => V)` has its own syntax. Covenant uses the same angle-bracket generic syntax as everything else, which makes nested mappings easier to read.

```solidity
// Solidity
mapping(address => mapping(address => uint256)) public allowances;
```

```covenant
// Covenant
field allowances: mapping<address, mapping<address, amount>>
```

Iteration over mappings is still forbidden (same as Solidity — no implicit key set). If you need iteration, use a sidecar array or the standard-library `enumerable_mapping`.

## `bytes` vs `bytes32`

Covenant keeps the same split — variable-length `bytes` versus fixed-width `bytes32` — but adds `bytes<N>` as a uniform syntax for any fixed size.

```solidity
// Solidity
bytes32 hash;
bytes4 selector;
bytes memory payload;
```

```covenant
// Covenant
field hash: bytes<32>
field selector: bytes<4>
let payload: bytes = ...
```

`bytes32` still works as an alias — you don't have to rewrite existing hash-shaped fields.

## Arithmetic: safe by default

Solidity 0.8 made checked arithmetic the default. Covenant goes one step further: wrapping arithmetic must be explicitly opted into per-operation, and it cannot hide inside an `unchecked { ... }` block.

```solidity
// Solidity 0.8+
uint256 a = x + y;                 // checked, reverts on overflow
unchecked { uint256 b = x + y; }   // wrapping, block-scoped
```

```covenant
// Covenant
let a: u256 = x + y                 // checked, reverts on overflow
let b: u256 = x.wrapping_add(y)     // wrapping, explicit at call site
```

Every arithmetic operator has a `wrapping_*`, `checked_*` (returning `Option<T>`), and `saturating_*` counterpart. Auditors searching for overflow risk grep for `wrapping_` — a much narrower surface than scanning every `unchecked` block.

## `timestamp` is not `u64`

In Solidity `block.timestamp` is a `uint256` (or `uint`). In Covenant it is a `timestamp`, which is a distinct nominal type wrapping a `u64` second-since-epoch.

```solidity
// Solidity — timestamps and durations are just numbers
uint256 unlockAt = block.timestamp + 7 days;
if (block.timestamp > unlockAt) { ... }
```

```covenant
// Covenant — timestamps and durations have distinct types
field unlock_at: timestamp = now + 7.days
given now > unlock_at or revert_with Locked()
```

You cannot add two timestamps together (what would that mean?), nor subtract a duration from a plain `u64`. The type system catches the entire family of off-by-86400 bugs at compile time.

`.days`, `.hours`, `.minutes`, and `.seconds` are duration constructors — each produces a `duration` value, and `timestamp + duration -> timestamp`.

## `encrypted<T>` — a new first-class type

This has no Solidity equivalent. `encrypted<T>` is a fully-homomorphically-encrypted wrapper around a base type. You can store, add, and compare encrypted values without decrypting them.

```covenant
contract SealedBid {
    field bids: mapping<address, encrypted<amount>>

    action submit(bid: encrypted<amount>) {
        bids[caller] = bid
    }

    action reveal_winner() returns (address) {
        // arithmetic and comparison happen on ciphertext
        let (winner, _) = bids.argmax_encrypted()
        return winner
    }
}
```

Three rules to internalize:

- An `encrypted<T>` cannot be implicitly decrypted. A `.decrypt()` call requires a `decryption_key` capability, which is minted by the contract's FHE key manager.
- Arithmetic on `encrypted<T>` uses the same operators as `T` but compiles to FHE circuits. Gas cost is substantially higher — the compiler emits a warning when an `encrypted<T>` op appears in a hot action.
- Emitting an `encrypted<T>` in an event is allowed; emitting its decryption is not, unless explicitly declared `event Decrypted(value: T)`.

See the *Privacy* chapter for the underlying BFV/CKKS parameter selection, key rotation, and threshold decryption.

## Type cheat sheet

```
Solidity                Covenant
--------------------------------------------
uint256 (balance)       amount  (decimals-aware)
uint256 (counter)       u256
uint64                  u64
int256                  i256      (same checked rules)
bool                    bool
bytes32                 bytes<32>
bytes (dynamic)         bytes
string                  string    (utf-8, bounded)
address                 address   (no payable split)
address payable         address
mapping(K=>V)           mapping<K,V>
block.timestamp (uint)  now: timestamp
(none)                  encrypted<T>, zk_proof<C>, pq_sig
```

The overall trend: move information from comments and convention into the type system, so the compiler can catch more at build time than your tests can catch at run time.
