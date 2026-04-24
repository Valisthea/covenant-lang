---
title: "ZK Airdrop"
description: "Distribute tokens to whitelisted addresses using a Merkle proof, without revealing the full whitelist on-chain."
section: cookbook
order: 3
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# ZK Airdrop

## Problem

I need to airdrop tokens to 10,000 whitelisted addresses without publishing the list on-chain (to protect user privacy and prevent frontrunning).

## Solution

```covenant
contract ZKAirdrop {
    field owner: address = deployer
    field merkle_root: bytes32
    field token: address
    field amount_per_claim: amount = 100 tokens
    field deadline: time

    field claimed: map<address, bool>

    event Claimed(claimant: address indexed)
    event RootUpdated(new_root: bytes32)

    error AlreadyClaimed()
    error InvalidProof()
    error AirdropExpired()
    error AirdropNotStarted()

    action initialize(root: bytes32, token_addr: address, expiry: time) only owner {
        merkle_root = root
        token = token_addr
        deadline = expiry
        emit RootUpdated(root)
    }

    action claim(proof: bytes32[], leaf: bytes32) {
        given block.timestamp <= deadline or revert_with AirdropExpired()
        given !claimed[caller] or revert_with AlreadyClaimed()

        // Verify the caller is in the whitelist
        let computed_leaf = hash(caller, amount_per_claim)
        given computed_leaf == leaf or revert_with InvalidProof()
        given zk_verify(proof, [merkle_root, leaf]) or revert_with InvalidProof()

        claimed[caller] = true
        external_transfer(token, caller, amount_per_claim)
        emit Claimed(caller)
    }

    action update_root(new_root: bytes32) only owner {
        merkle_root = new_root
        emit RootUpdated(new_root)
    }
}
```

## Explanation

- `merkle_root` is a Keccak256 Merkle root of all `(address, amount)` pairs in the whitelist
- `zk_verify(proof, [merkle_root, leaf])` verifies the Merkle inclusion proof -- the proof is generated off-chain using the Covenant SDK
- `computed_leaf = hash(caller, amount_per_claim)` binds the proof to both the caller and the expected amount, preventing someone from claiming a different amount
- `claimed[caller]` prevents double-claims

The whitelist itself never appears on-chain. Anyone with a proof can claim without revealing who else is on the list.

## Generating Proofs (Off-Chain)

```typescript
import { CovenantSDK } from \'@covenant-lang/sdk\';

const sdk = new CovenantSDK({ rpc: \'https://rpc.sepolia.org\' });

// Build tree from whitelist
const tree = sdk.merkle.build(whitelist.map(([addr, amt]) => 
  sdk.merkle.leaf(addr, amt)
));

// Generate proof for user
const proof = tree.getProof(sdk.merkle.leaf(userAddress, amount));

// User calls claim(proof, leaf)
await contract.claim(proof, sdk.merkle.leaf(userAddress, amount));
```

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `initialize` | ~60,000 |
| `claim` (10-level tree, 10k addresses) | ~85,000 |
| `update_root` | ~30,000 |

## Common Pitfalls

1. **Leaf collision**: If `hash(addr, amount)` is not collision-resistant, two different inputs could produce the same leaf. Use `keccak256(abi.encode(addr, amount))`.
2. **Missing deadline**: Without a deadline, unclaimed tokens are locked forever. Add a `reclaim_unclaimed` action callable by owner after deadline.
3. **Amount not bound to leaf**: If the leaf is only `hash(addr)`, anyone can claim any amount. Always include the amount in the leaf.
4. **Root updateable without timelock**: Updating the root can change who is eligible. Use a timelock or immutable root after launch.
5. **Re-entrancy on token transfer**: The `claimed[caller] = true` before `external_transfer` follows CEI.

## See Also

- [ERC-8229 -- FHE Verification Standard](/docs/reference/ercs/04-erc-8229-fhe-verify)
- [Example 10 -- Zero-Knowledge Proofs](/docs/examples/10-zero-knowledge-proofs)
- [Sealed-Bid Auction](/docs/cookbook/privacy/01-sealed-bid-auction)
