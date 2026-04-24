---
title: "Cookbook Overview"
description: "How to use the Covenant Cookbook: recipe format, categories, and how recipes differ from examples."
section: cookbook
order: 1
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Cookbook

The Covenant Cookbook is a collection of ready-to-deploy contract patterns. Each recipe solves a specific, concrete problem with production-quality code.

## Cookbook vs. Examples

| | [By Example](/docs/examples/01-hello-contract) | Cookbook |
|-|----------------|---------|
| **Purpose** | Learn Covenant step-by-step | Solve a specific problem |
| **Reading order** | Sequential (Chapter 1 -> 15) | Browse by category |
| **Code** | Pedagogical, introduces one concept | Complete, deployable |
| **Context** | "How does X work?" | "I need to do X" |

## Recipe Format

Every recipe follows this structure:

1. **Problem** - one or two sentences describing the real need
2. **Solution** - complete, deployable Covenant code
3. **Explanation** - why this approach, not alternatives
4. **Gas estimate** - cost for typical usage
5. **Common pitfalls** - 3-5 mistakes to avoid
6. **Variations** - 1-2 alternative approaches
7. **See also** - related recipes, examples, reference pages

## Categories

### [Tokens](/docs/cookbook/tokens/01-mintable-token)
Fungible tokens with mint, burn, and confidential transfers.

### [Auth](/docs/cookbook/auth/01-multi-sig-admin)
Admin patterns: multisig, time locks, post-quantum signatures.

### [Upgrades](/docs/cookbook/upgrades/01-uups-pattern)
UUPS and beacon proxy upgrade patterns with re-init protection.

### [Privacy](/docs/cookbook/privacy/01-sealed-bid-auction)
Sealed auctions, private voting, ZK airdrops.

### [Integration](/docs/cookbook/integration/01-chainlink-oracle)
Chainlink oracles and ERC-20 bridge patterns.

## Code Quality Bar

Every recipe in this cookbook:
- Compiles on Covenant V0.7
- Is deployable to Sepolia without modification
- Has been checked against the 38 LSP lint detectors
- Does not contain placeholders or TODOs

If a feature requires V0.8+, it is flagged clearly at the top of the recipe.
