---
title: "01 — Hello Contract"
description: "Write and deploy your first Covenant contract."
order: 1
section: "Fundamentals"
---

# 01 — Hello Contract

The simplest possible Covenant contract — a greeting stored on-chain and exposed as a read action.

```covenant
contract HelloWorld {
  /// Greeting stored on chain.
  field greeting: String = "hello, world"

  /// Read the greeting.
  action greet() -> String {
    return self.greeting;
  }

  /// Update the greeting (owner only).
  action set_greeting(msg: String) {
    only(owner);
    self.greeting = msg;
  }
}
```

## What just happened?

| Concept | Explanation |
|---------|-------------|
| `contract` | Top-level declaration; compiles to a single EVM account |
| `field` | Persistent storage slot — initialised with the literal after `=` |
| `action` | Public entry point, maps to an ABI function |
| `only(owner)` | Built-in guard: reverts unless `msg.sender == owner()` |

## Build it

```bash
covenant new hello-world
cd hello-world
# Replace src/main.cov with the snippet above
covenant build      # emits hello-world.abi + hello-world.bin
covenant test       # runs the snapshot test suite
```

## Deploy to a local devnet

```bash
covenant devnet &           # starts Anvil-compatible devnet
covenant deploy --dev       # deploys to 0x0…01 with test key
```

The CLI prints the deployed address. Continue to **02 — Fields & Storage** to learn about all storage types.
