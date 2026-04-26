---
title: "Playground (Fastest)"
description: "Try Covenant in your browser — no install required."
order: 0
---

# Playground (Fastest start)

The fastest way to try Covenant is in your browser. Visit **[playground.covenant-lang.org](https://playground.covenant-lang.org)** — no install, no Rust, no PATH setup.

## Three minutes from open to deploy

1. **Pick an example** — click *Examples* and choose `Hello` (the simplest contract).
2. **Compile** — click *Compile*. The browser runs the same compiler that ships in CI; bytecode appears in the panel below.
3. **Deploy on MockChain** — click *Deploy*. MockChain is an in-tab EVM simulator: deterministic, instant, free. Reset on demand.
4. **Interact** — call actions and views from the typed UI panel. Events stream as human-readable names, not raw hex topics.

## Real testnet via Sepolia

Switch the target to *Sepolia* and connect MetaMask. The same source compiles to Sepolia-targeted bytecode — helper-bridge addresses (CeremonyHelper, FHE/PQ/ZK helpers) are embedded automatically. Deployments take ~30 seconds.

## Tour

The playground includes a **12+ lesson tour** covering:

- Hello / fields & storage / actions, events, errors
- Guards (`only`, `given`, `when`)
- ERC-20 token, encrypted token (ERC-8227)
- FHE basics, post-quantum signatures, zero-knowledge proofs
- Cryptographic amnesia (full ceremony lifecycle on Sepolia)
- NFT (ERC-721 in 5 lines), PQ key registry (ERC-8231), external calls

Each lesson has compilable source and a "deploy and interact" step.

## State persistence

- **IndexedDB** — your contracts persist across page reloads.
- **BroadcastChannel** — open multiple tabs, state syncs in real time.
- **Reset on demand** — clear the chain or reset everything from the menu.

## When to use the CLI instead

The playground is the right answer for:

- Trying the language
- Following a tutorial
- Demos and screencasts
- Sharing a snippet with someone (deep links work)

For projects with version-controlled source, CI, multiple files, or production deployments, install the CLI:

→ [Installation (CLI)](/docs/getting-started/01-install)
