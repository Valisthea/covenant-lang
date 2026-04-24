---
title: "Sealed-Bid Auction"
description: "An auction where bids are encrypted during the bidding period and revealed only after the deadline."
section: cookbook
order: 1
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Sealed-Bid Auction

## Problem

I need an on-chain auction where bidders submit their bids without revealing amounts to competitors. After the deadline, bids are revealed and the highest bidder wins.

## Solution

```covenant
sealed market Auction {
    field item: text
    field deadline: time
    field min_bid: amount
    field owner: address = deployer

    field bids: map<address, encrypted<amount>>
    field deposits: map<address, amount>
    field winner: address = address(0)
    field settled: bool = false

    event BidPlaced(bidder: address indexed)
    event AuctionSettled(winner: address indexed)
    event Withdrawn(bidder: address indexed, amount: amount)

    error AuctionClosed()
    error AuctionNotClosed()
    error AlreadySettled()
    error BidTooLow()
    error DepositInsufficient()

    action place_bid(encrypted_bid: encrypted<amount>, deposit: amount) {
        given block.timestamp < deadline or revert_with AuctionClosed()
        given deposit >= min_bid or revert_with DepositInsufficient()

        bids[caller] = encrypted_bid
        deposits[caller] = deposits[caller] + deposit
        emit BidPlaced(caller)
    }

    action settle() only owner {
        given block.timestamp >= deadline or revert_with AuctionNotClosed()
        given !settled or revert_with AlreadySettled()

        settled = true
        // Threshold decryption: validators reveal the winning bid
        // The reveal selects the argmax without exposing individual bids
        reveal winner_from bids
        emit AuctionSettled(winner)
    }

    action withdraw_deposit() {
        given block.timestamp >= deadline or revert_with AuctionNotClosed()
        given caller != winner or revert_with Unauthorized()

        let refund = deposits[caller]
        deposits[caller] = 0
        transfer(caller, refund)
        emit Withdrawn(caller, refund)
    }
}
```

## Explanation

- `sealed market` is a Covenant construct that wraps the contract in an ERC-8227 context automatically
- `encrypted<amount>` bids are stored as BFV ciphertexts; no one can read them until `settle`
- `reveal winner_from bids` is a special form that computes `argmax` homomorphically -- it finds the highest bidder without revealing individual bids to anyone except the winner
- Losers withdraw their deposits; the winner\'s deposit stays as payment

The homomorphic `argmax` requires the FHE comparison precompile (`fhe_cmp`). On Aster Chain this costs ~6,000 pGas per comparison; on L1 it is ~90,000 gas per comparison. For auctions with many bidders, Aster is strongly recommended.

## Gas Estimate

| Operation | Gas (L1) | pGas (Aster) |
|-----------|---------|-------------|
| `place_bid` | ~120,000 | ~12,000 |
| `settle` (10 bidders) | ~1,000,000 | ~100,000 |
| `withdraw_deposit` | ~35,000 | ~3,500 |

## Common Pitfalls

1. **No deposit**: Without a deposit, bidders can bid any amount and walk away. The deposit must be at least `min_bid`.
2. **Winner not paying**: The winner\'s deposit is retained as payment. Ensure the deposit equals or exceeds the winning bid.
3. **Settle called too early**: The `only owner` + deadline check prevents premature settlement.
4. **Gas for many bidders**: `settle` cost scales with bidder count. For >50 bidders, use `@prove_offchain` for the argmax computation.
5. **Bid not encrypted before submission**: The bid encryption must happen client-side. The Covenant SDK provides `sdk.encrypt(amount, networkPubKey)`.

## See Also

- [Private Voting](/docs/cookbook/privacy/02-private-voting)
- [ERC-8227 -- Encrypted Tokens](/docs/reference/ercs/02-erc-8227-fhe)
- [Example 07 -- FHE Basics](/docs/examples/07-fhe-basics)
