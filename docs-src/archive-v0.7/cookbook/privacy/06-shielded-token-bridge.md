---
title: "Shielded Token Bridge"
description: "Bridge tokens between chains while hiding sender, receiver, and amount via ZK proofs."
section: cookbook
order: 6
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Shielded Token Bridge

## Problem

A standard lock-and-mint bridge leaks everything: source address, destination address, amount, timing. I want a bridge that preserves the invariant "tokens out == tokens in" while hiding sender, receiver, and amount from all observers, including the relayers.

## Solution

```covenant
sealed contract ShieldedBridge {
    field token: address
    field commitments_root: bytes32     // append-only Merkle root on this chain
    field nullifier_set: map<bytes32, bool>
    field total_shielded: encrypted<amount>

    event Deposit(commitment: bytes32 indexed, leaf_index: u64)
    event Withdraw(nullifier: bytes32 indexed, receiver: address)

    error InvalidProof()
    error AlreadySpent()
    error InvalidRoot()

    // Deposit: user burns `msg.value` tokens and adds a commitment
    // C = poseidon(encrypted_amount, secret, receiver_blinding)
    // to the append-only tree. The `encrypted_amount` is a BFV ciphertext
    // under the bridge's public key; total_shielded is kept in sync homomorphically.
    action shielded_deposit(
        note_commitment: bytes32,
        encrypted_amount: encrypted<amount>,
        range_proof: bytes,
    ) payable {
        // Prove encrypted_amount is in [0, msg.value] and matches the commitment
        given zk_verify(
            deposit_range_circuit,
            range_proof,
            [note_commitment, hash(encrypted_amount), msg.value],
        ) or revert_with InvalidProof()

        total_shielded = fhe_add(total_shielded, encrypted_amount)
        let leaf_index = tree_append(note_commitment)
        emit Deposit(note_commitment, leaf_index)
    }

    // Withdraw: user proves knowledge of a commitment in the tree whose
    // nullifier has not been spent, and that the disclosed amount matches.
    action shielded_withdraw(
        nullifier: bytes32,
        receiver: address,
        root: bytes32,
        amount_out: amount,
        proof: bytes,
    ) {
        given !nullifier_set[nullifier] or revert_with AlreadySpent()
        given is_known_root(root) or revert_with InvalidRoot()

        given zk_verify(
            withdraw_circuit,
            proof,
            [root, nullifier, receiver, amount_out],
        ) or revert_with InvalidProof()

        nullifier_set[nullifier] = true
        // Decrement the shielded supply homomorphically
        total_shielded = fhe_sub(total_shielded, encrypt(amount_out))
        transfer(token, receiver, amount_out)
        emit Withdraw(nullifier, receiver)
    }
}
```

## Explanation

The bridge has three moving parts:

1. **Commitment tree** — every deposit appends `poseidon(amount, secret, blinding)` to an append-only Merkle tree. The root is what provers prove membership against.
2. **Nullifier set** — spending a note publishes `nullifier = poseidon(secret, leaf_index)`. The circuit proves the nullifier is derived from a leaf in the tree without revealing which leaf.
3. **FHE-encrypted supply** — `total_shielded` is a BFV ciphertext of the total locked amount. The cross-chain relayer periodically proves (via another ZK circuit) that `decrypt(total_shielded) == locked_balance(token)`, catching bugs and insolvency without leaking individual amounts.

On the destination chain, the mirror contract mints against a proof that a given `(nullifier, receiver, amount)` tuple was finalized on the source chain. Combining commitments + nullifiers + FHE supply tracking closes the usual leakage channels:

- Sender hidden: the `shielded_withdraw` is called by a relayer, not the original depositor.
- Receiver hidden on deposit: only the commitment is stored; receiver is revealed at withdraw time.
- Amount hidden on both ends: only `amount_out` at withdraw leaks, and only to the receiver.

## Gas Estimate

| Operation | Gas (L1) | pGas (Aster) |
|-----------|---------|-------------|
| `shielded_deposit` | ~420,000 | ~36,000 |
| `shielded_withdraw` | ~390,000 | ~33,000 |
| Supply solvency proof | ~280,000 | ~24,000 |

## Common Pitfalls

1. **Historical roots**: Withdraw proofs are built against a root that was current at proof-generation time. Keep a ring buffer of the last ~100 roots and check membership with `is_known_root`.
2. **Nullifier collisions across chains**: If the destination chain uses the same nullifier namespace, a withdraw on chain A can be replayed on chain B. Include `chain_id` in the nullifier preimage.
3. **Frontrunning the withdraw**: A relayer can steal the fee by replacing the receiver. Fix `receiver` as a public input inside the circuit so replacing it invalidates the proof.
4. **FHE bootstrap cost**: After ~10,000 deposits the `total_shielded` ciphertext needs bootstrap. Schedule this via `amnesia { cleanup_phase: 1 day }`.
5. **Relayer censorship**: If only one relayer can publish withdraws, they can censor. Expose `shielded_withdraw` as permissionless and compensate the caller with a tip drawn from the note.

## Variations

- **Multi-asset**: Key the nullifier set by `(token, nullifier)` and add `token` to the circuit public inputs.
- **Shielded transfers (no withdraw)**: Use a join-split circuit that consumes two notes and produces two new notes, never revealing amounts.
- **Compliant shielding**: Include a viewing key per jurisdiction; regulators can decrypt flows but the public cannot.

## See Also

- [Private Identity](/docs/cookbook/privacy/05-private-identity)
- [Confidential Lending](/docs/cookbook/privacy/04-confidential-lending)
- [Example 14 — Cross-Chain ZK Bridges](/docs/examples/14-zk-bridge)
