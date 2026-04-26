---
title: "16 — NFT in 5 Lines"
description: "ERC-721 auto-synthesis with the V0.9 nft construct."
order: 16
section: "V0.9 New"
level: beginner
---

# 16 — NFT in 5 Lines

V0.9 introduces the `nft` construct — a top-level keyword that auto-synthesizes the entire ERC-721 surface from a metadata-only declaration. Where Solidity needs ~150 lines and a base contract import, Covenant needs five lines.

```covenant
nft CoolApes {
    name: "Cool Apes"
    symbol: "APE"
    base_uri: "https://api.example.com/"
}
```

That's the entire contract. It compiles to deployable EVM bytecode.

## What gets synthesized

From those five lines the compiler emits:

| Surface | Members |
|---|---|
| **Fields** | `owners`, `balances`, `token_approvals`, `operator_approvals` |
| **Views** | `name`, `symbol`, `tokenURI`, `balanceOf`, `ownerOf`, `getApproved`, `isApprovedForAll` |
| **Actions** | `approve`, `setApprovalForAll`, `transferFrom`, `mint` |
| **Events** | `Transfer`, `Approval`, `ApprovalForAll` (all properly indexed per ERC-721) |
| **Errors** | `NotTokenOwner`, `TokenAlreadyMinted`, `TokenDoesNotExist`, `NotApprovedOrOwner` |

Every member matches the ERC-721 normative spec. The bytecode is a drop-in replacement for an OpenZeppelin-based ERC-721 — wallets, marketplaces, and indexers see the same interface.

## What to notice

- **No inheritance.** Covenant has no inheritance system. The `nft` keyword itself does the auto-synthesis at compile time. There is no parent contract to import or override.
- **Metadata is constant by default.** `name`, `symbol`, and `base_uri` become immutable values baked into bytecode. To make them mutable, declare them as `field` instead.
- **Mint is open by default.** Add `only deployer` to the synthesized `mint` action if you want only the deployer to mint:
  ```covenant
  nft CoolApes {
      name: "Cool Apes"
      symbol: "APE"
      base_uri: "https://api.example.com/"
      mint: only deployer    -- or: only(some_minter_role)
  }
  ```
- **`tokenURI(id)` returns `base_uri` verbatim** in V0.9.0. ID-concatenation (`base_uri + id.toString()`) lands in V0.9.x alongside text-interpolation primitives. For now, point `base_uri` at an API that handles the concatenation server-side.
- **`safeTransferFrom`** (with the receiver-hook callback) is deferred to V0.9.x — included in the synthesizer's reserved name list but not emitted yet, to keep the V0.9.0 audit surface minimal.

## Custom logic on top

If you need custom mint logic, additional fields, or extra actions, just write them inline. The `nft` keyword synthesizes the ERC-721 baseline; you add whatever else you need:

```covenant
nft CoolApes {
    name: "Cool Apes"
    symbol: "APE"
    base_uri: "https://api.example.com/"

    field mint_price: amount
    field minted_count: u256

    action public_mint() {
        given block.value >= mint_price
        given minted_count < 10000
        mint(caller, minted_count + 1)
        minted_count = minted_count + 1
    }
}
```

## Try it

Open this in the [playground](https://playground.covenant-lang.org/?example=D1-nft) — it compiles, deploys to MockChain, and lets you mint a token in three clicks.

## What's next

- [17 — Post-Quantum Registry](/docs/examples/17-registry) — `registry` construct, ERC-8231
- [18 — External Calls](/docs/examples/18-external-call) — `interface` declarations
- [Reference: ERCs](/docs/reference/ercs) — ERC-721 spec details
