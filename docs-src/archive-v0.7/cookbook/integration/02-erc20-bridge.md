---
title: "ERC-20 Bridge"
description: "A simple lock-and-mint bridge that wraps an existing ERC-20 token into a Covenant token on another chain."
section: cookbook
order: 2
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# ERC-20 Bridge

## Problem

I need to bridge an existing ERC-20 token (e.g., USDC on Ethereum) to a Covenant token on Aster Chain via a lock-and-mint pattern.

## Solution

```covenant
// ---- Source chain (Ethereum): Lock contract ----
contract ERC20Locker {
    field owner: address = deployer
    field token: address           // The ERC-20 to lock
    field bridge_validator: address
    field locked: map<address, amount>
    field nonce: uint = 0

    event Locked(user: address indexed, amount: amount, nonce: uint indexed)
    event Released(user: address indexed, amount: amount, nonce: uint indexed)

    error InvalidSignature()
    error NonceReused()
    error ZeroAmount()

    field used_nonces: set<uint>

    action lock(amount: amount) {
        given amount > 0 or revert_with ZeroAmount()

        // Pull tokens from caller (requires prior approve)
        external_transfer_from(token, caller, address(this), amount)
        locked[caller] = locked[caller] + amount

        let n = nonce
        nonce = nonce + 1
        emit Locked(caller, amount, n)
    }

    action release(user: address, amount: amount, release_nonce: uint, sig: bytes65) {
        given !used_nonces.contains(release_nonce) or revert_with NonceReused()

        let msg = hash(user, amount, release_nonce, address(this))
        given recover_signer(msg, sig) == bridge_validator or revert_with InvalidSignature()

        used_nonces.add(release_nonce)
        locked[user] = locked[user] - amount
        external_transfer(token, user, amount)
        emit Released(user, amount, release_nonce)
    }
}

// ---- Destination chain (Aster): Mint contract ----
token BridgedToken {
    name: "Bridged USDC"
    symbol: "bUSDC"
    decimals: 6
    supply: 0 tokens
    initial_holder: deployer

    field bridge_validator: address = deployer
    field used_nonces: set<uint>

    event Minted(user: address indexed, amount: amount, nonce: uint indexed)
    event Burned(user: address indexed, amount: amount, nonce: uint indexed)

    error InvalidSignature()
    error NonceReused()

    action mint(user: address, amount: amount, mint_nonce: uint, sig: bytes65) {
        given !used_nonces.contains(mint_nonce) or revert_with NonceReused()

        let msg = hash(user, amount, mint_nonce, address(this))
        given recover_signer(msg, sig) == bridge_validator or revert_with InvalidSignature()

        used_nonces.add(mint_nonce)
        balances[user] = balances[user] + amount
        total_supply = total_supply + amount
        emit Minted(user, amount, mint_nonce)
    }

    action burn_for_bridge(amount: amount) {
        given balances[caller] >= amount or revert_with InsufficientBalance()
        balances[caller] = balances[caller] - amount
        total_supply = total_supply - amount

        let n = total_supply  // use as nonce approximation; proper impl uses separate counter
        emit Burned(caller, amount, n)
    }
}
```

## Explanation

- **Lock-and-mint**: Tokens are locked on the source chain; equivalent tokens are minted on the destination chain
- **Bridge validator**: A trusted off-chain relayer watches `Locked` events on Ethereum and calls `mint` on Aster with a signature
- **Nonce tracking**: Each `Locked` event has a unique nonce to prevent replay attacks on the mint side
- `recover_signer` verifies the ECDSA signature is from the bridge validator

For production bridges, the validator should be a multisig or decentralized validator set.

## Gas Estimate

| Operation | Chain | Gas |
|-----------|-------|-----|
| `lock` (Ethereum) | EVM | ~65,000 |
| `mint` (Aster) | Aster | ~50,000 |
| `burn_for_bridge` (Aster) | Aster | ~35,000 |
| `release` (Ethereum) | EVM | ~55,000 |

## Common Pitfalls

1. **No nonce on release**: Without nonce tracking on the Ethereum side, a bridge validator could release the same funds multiple times.
2. **Single validator**: A single validator is a single point of failure and trust. Use a 3-of-5 multisig or decentralized validator set.
3. **No rate limiting**: A compromised validator could drain the locker. Add daily limits on `release`.
4. **Missing `transferFrom` approval**: Users must `approve` the locker before calling `lock`. Document this clearly.
5. **Decimal mismatch**: USDC has 6 decimals; ensure the bridged token uses the same.

## See Also

- [Chainlink Oracle Integration](/docs/cookbook/integration/01-chainlink-oracle)
- [Example 15 -- Deploy to Sepolia](/docs/examples/15-deploy-to-sepolia)
- [ERC-8227 -- Encrypted Tokens](/docs/reference/ercs/02-erc-8227-fhe) -- for confidential bridges
