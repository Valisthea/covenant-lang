---
title: "Migration from Solidity — Overview"
description: "A guide for Solidity developers moving to Covenant: philosophy, concept mapping, and reading order."
section: migration
order: 1
level: reference
---

<!-- Last sync: 2026-04-23 -->

# Migration from Solidity — Overview

## Who this guide is for

You've shipped Solidity. You know `msg.sender`, you've debugged reentrancy, you've written a `require` statement you later wished you'd written differently. This guide is for you.

It is *not* a Solidity tutorial, nor a complete Covenant reference. It is a bridge — a map that takes the mental model you already have and shows where each piece lands in Covenant.

## Philosophy: Covenant is not "Solidity with new syntax"

It would be easy to read Covenant code and conclude it is a cosmetic rework of Solidity — different keywords, same language. That would miss the point.

Covenant is a **refinement**. It takes roughly fifteen years of smart contract post-mortems and bakes the lessons into the language itself:

- **Stricter defaults.** Checked arithmetic is the only option unless you explicitly opt into `wrapping`. Storage slots are explicit. Actions are non-reentrant by default when they mutate money-typed state.
- **Cryptography as a primitive, not a library.** `encrypted<T>` (FHE), `zk_proof`, and post-quantum signature types are first-class citizens — not imports, not precompile incantations.
- **Contract-level semantics baked into keywords.** Concepts that live in OpenZeppelin mixins — `Ownable`, `Pausable`, `ReentrancyGuard`, `AccessControl` — are expressed as decorators and guards, not inherited base classes.
- **Separation of intent and implementation.** `guard` blocks declare *what* must be true; `action` bodies describe *what changes*. Auditors read guards first.

If you keep trying to write Solidity in Covenant, it will feel awkward. Lean into the new primitives and the code gets shorter *and* more auditable.

## Concept mapping at a glance

Before diving in, here is how twelve core Solidity concepts translate:

| Solidity | Covenant | Notes |
|---|---|---|
| `contract Foo { ... }` | `contract Foo { ... }` | Also `token { ... }` as a higher-level variant |
| `function f() public` | `action f() { ... }` | Public is default; visibility is declared only to restrict |
| `modifier onlyOwner` | `guard only_owner { ... }` | Guards are declarative predicates, not wrapping decorators |
| `require(x, "msg")` | `given x or revert_with Err()` | Errors are typed values, not strings |
| `event Transfer(...)` | `event Transfer(...)` | Same, but emitted with `emit Transfer(...)` always |
| `mapping(K => V) s` | `field s: mapping<K, V>` | Generic syntax; nested mappings compose naturally |
| `msg.sender` | `caller` | Also `origin` for the tx-level sender |
| `address payable` | `address` | No payable distinction — transfer capability is checked at send |
| `uint256 x` | `field x: u256` (or `amount` for balances) | `amount` carries decimals metadata |
| `immutable x` | `field x: T = ...` (deploy-initialized, sealed) | Immutable is the default for deploy-block assignments |
| OpenZeppelin `TransparentProxy` | `@upgradeable` decorator | Storage layout is verified by the compiler |
| Foundry `forge test` | `covenant test` | Tests are inline: `test "name" { ... }` |

If any row surprises you, pages 2–4 expand on it.

## Reading order

The next five pages walk from syntax up to a full port:

1. **Syntax Mapping** — the literal side-by-side: how a Solidity file re-shapes into a Covenant file.
2. **Type System Differences** — where `uint256` is not quite `u256`, and why `amount` exists.
3. **Common Patterns Translated** — ERC-20, Ownable, ReentrancyGuard, Pausable, AccessControl.
4. **Tooling Equivalents** — your Hardhat/Foundry workflow mapped to the `covenant` CLI.
5. **Porting Checklist** — a practical walk-through including a full staking contract ported end-to-end.

Read them in order the first time. After that, they work well as reference.

## A note on what's *not* covered here

This guide focuses on the Solidity → Covenant translation. It does not re-teach:

- FHE and `encrypted<T>` semantics — see the *Privacy* chapter.
- ZK proof workflows — see *Zero-Knowledge Guide*.
- Cross-chain and light-client patterns — see *Interop*.

You can migrate a contract without those features. When you're ready for them, Covenant does not require a rewrite — they slot in as additional fields and decorators on your existing contract.
