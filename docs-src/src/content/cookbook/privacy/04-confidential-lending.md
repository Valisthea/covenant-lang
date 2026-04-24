---
title: "Confidential Lending Pool"
description: "A lending pool where collateral amounts and loan sizes are encrypted via FHE, visible only to the borrower."
section: cookbook
order: 4
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Confidential Lending Pool

## Problem

I want to run a lending market where the positions of individual borrowers are private. Competitors and MEV searchers should not be able to target a borrower for liquidation by reading their collateral ratio from storage. Only the borrower (and the protocol itself, homomorphically) should know the exact numbers.

## Solution

```covenant
sealed contract ConfidentialLending {
    field collateral_token: address
    field debt_token: address
    field oracle: address
    field liq_threshold: u256 = 8000  // 80.00% in basis points

    field collateral: map<address, encrypted<amount>>
    field debt: map<address, encrypted<amount>>

    event Borrowed(user: address indexed)
    event Repaid(user: address indexed)
    event Liquidated(user: address indexed, liquidator: address indexed)

    error InsufficientCollateral()
    error HealthyPosition()
    error InvalidProof()

    action deposit_collateral(encrypted_amount: encrypted<amount>) {
        collateral[caller] = fhe_add(collateral[caller], encrypted_amount)
        // ERC-20 pull happens via a matching plaintext receipt attached off-chain
    }

    action borrow(encrypted_amount: encrypted<amount>) {
        let new_debt = fhe_add(debt[caller], encrypted_amount)
        let price = oracle.price(collateral_token)
        let max_debt = fhe_mul(collateral[caller], price * liq_threshold / 10000)

        // fhe_cmp returns encrypted<bool>; reveal only the single bit
        let ok = fhe_cmp(new_debt, max_debt, op::LTE)
        given reveal_bit(ok) or revert_with InsufficientCollateral()

        debt[caller] = new_debt
        emit Borrowed(caller)
    }

    action repay(encrypted_amount: encrypted<amount>) {
        debt[caller] = fhe_sub(debt[caller], encrypted_amount)
        emit Repaid(caller)
    }

    // Liquidators submit a ZK proof that `user` is under-collateralized.
    // The circuit takes the ciphertexts as public inputs and the network
    // key share as a private witness, and outputs a single bit.
    action liquidate(user: address, proof: bytes) {
        let public_inputs = [
            hash(collateral[user]),
            hash(debt[user]),
            oracle.price(collateral_token),
            liq_threshold,
        ]
        given zk_verify(under_collateralized_circuit, proof, public_inputs)
            or revert_with InvalidProof()

        let seized = collateral[user]
        collateral[user] = encrypted_zero()
        debt[user] = encrypted_zero()
        transfer_encrypted(collateral_token, caller, seized)
        emit Liquidated(user, caller)
    }
}
```

## Explanation

- Balances live as BFV ciphertexts. `fhe_add` and `fhe_sub` are ~200k gas on L1 but only ~15k pGas on Aster Chain.
- `reveal_bit(ok)` uses threshold decryption to expose *only* the comparison outcome, never the underlying amounts.
- Liquidation cannot read the ciphertexts directly, so we require a ZK proof that the under-collateralized predicate holds. The circuit is `under_collateralized_circuit` — a Groth16 or Plonk circuit whose public inputs include the ciphertext hashes, price, and threshold.
- The liquidator runs the circuit off-chain after asking validators for a decryption share of the inequality bit via the `oracle.fhe_query` side-channel (ERC-8231).

## Gas Estimate

| Operation | Gas (L1) | pGas (Aster) |
|-----------|---------|-------------|
| `deposit_collateral` | ~210,000 | ~18,000 |
| `borrow` | ~950,000 | ~75,000 |
| `repay` | ~240,000 | ~21,000 |
| `liquidate` (Groth16) | ~310,000 | ~28,000 |

## Common Pitfalls

1. **Revealing too much**: `reveal_bit` is fine; `reveal(new_debt)` would leak the debt. Audit every `reveal*` call.
2. **Stale oracle price inside ciphertext**: `fhe_mul` with a plaintext price freezes that price into the ciphertext for the duration of that comparison. Refresh on every action.
3. **Liquidation race**: Two liquidators can submit proofs in the same block. Use `nonce` per user to make exactly one proof valid per block.
4. **Ciphertext bloat**: After ~1000 `fhe_add` calls, BFV noise overflows. Call `bootstrap(collateral[user])` periodically or bundle the whole position in an `amnesia { cleanup_phase: 1_000_000 }` block.
5. **Front-running via ciphertext size**: The encrypted amount has a fixed 4KB on-chain footprint, but the *transaction size* itself leaks whether this is a borrow vs repay. Use a unified `update_position` entrypoint in hostile environments.

## Variations

- **Interest accrual**: Multiply `debt[user]` by `fhe_mul(debt, rate_factor)` each block. Cheaper: accrue on the plaintext `rate_index` and let the user re-encrypt at repay time.
- **Multi-collateral**: Use `map<(address, address), encrypted<amount>>` keyed by `(user, token)` and sum the USD-valued collateral homomorphically.
- **Fixed-rate tranches**: Model the tranches as separate contracts and use `amnesia` to garbage-collect matured loans.

## See Also

- [Sealed-Bid Auction](/docs/cookbook/privacy/01-sealed-bid-auction)
- [ERC-8231 — FHE Oracle Queries](/docs/reference/ercs/03-erc-8231-fhe-oracle)
- [Example 09 — ZK Liquidation Proofs](/docs/examples/09-zk-liquidation)
