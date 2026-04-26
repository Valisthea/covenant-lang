---
title: "01 — Hello Contract"
description: "Write your first Covenant contract. Verified against the V0.8 compiler — every line in this page compiles in playground.covenant-lang.org."
order: 1
section: "Fundamentals"
---

# 01 — Hello Contract

The minimal viable Covenant file: a `record` with one field, one setter action, and one read view. This is the canonical starting point.

```covenant
-- Hello.cov · the minimal viable Covenant file.
-- A `record` is a key-value store on chain: fields + actions + views,
-- nothing else. The simplest building block in the language.

record Hello {
    greeting: text

    action update(new_text: text) {
        greeting = new_text
    }

    view read returns text {
        greeting
    }
}
```

## What just happened?

| Concept | Explanation |
|---------|-------------|
| `--` | Single-line comment (Covenant uses Haskell-style, **not** `//`) |
| `record` | Top-level keyword: a key-value store on chain |
| `greeting: text` | Field declaration; `text` is the UTF-8 string type. Inside `record` the `field` keyword is implicit |
| `action update(...)` | State-mutating function. Default visibility is external — no `public`/`external` modifier needed |
| `view read returns text` | Read-only query. **Zero-arg views drop the parentheses** — write `view read returns text`, not `view read() returns text` |
| (no `return` keyword in body) | Single-expression view bodies are expression-bodied: the last expression is the return value |

## Try it now — no install required

<a href="https://playground.covenant-lang.org/?example=A1&target=mockchain"
   target="_blank"
   rel="noopener noreferrer"
   style="display:inline-block;margin:1.25rem 0;padding:0.7rem 1.4rem;background:#7C3AED;color:#fff;text-decoration:none;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:600;letter-spacing:0.02em;">
  Try in Playground →
</a>

The button opens the [Covenant Playground](https://playground.covenant-lang.org) with this contract pre-loaded. From there:

1. **Compile** — the Inspector panel shows real EVM bytecode + ABI
2. **Deploy** (target: MockChain) — the contract gets a deterministic address in ~50ms
3. In Interaction Panel, find `update`, type a string, click **Call**
4. Find `read`, click **Query** — returns what you just set

Switch the **Chain Target** to **Sepolia** to deploy to a real testnet via MetaMask (~30s with confirmation).

## Build it locally (CLI)

```bash
covenant new hello-world
cd hello-world
# replace src/main.cov with the snippet above
covenant build      # emits hello-world.abi + hello-world.bin
covenant test       # runs the snapshot test suite
```

## Continue

Move on to [**02 — Fields & Storage**](/docs/examples/02-fields-and-storage) to see how to declare more complex state.
