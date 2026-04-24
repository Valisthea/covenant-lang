---
title: "Private Identity (Anonymous Credentials)"
description: "Prove you belong to an eligible set without revealing which member you are, using ZK proofs."
section: cookbook
order: 5
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Private Identity (Anonymous Credentials)

## Problem

I run an airdrop, a DAO, or a gated forum, and I need to prove the caller belongs to an eligible set (KYC pass, past user, token holder, etc.) without revealing *which* member they are. Each credential must be single-use.

## Solution

```covenant
contract PrivateIdentity {
    field merkle_root: bytes32
    field admin: address = deployer
    field used: map<bytes32, bool>

    event RootUpdated(new_root: bytes32)
    event CredentialUsed(nullifier: bytes32 indexed)

    error InvalidProof()
    error NullifierAlreadyUsed()
    error Unauthorized()

    guard only_admin() { caller == admin }

    action set_root(new_root: bytes32) only only_admin {
        merkle_root = new_root
        emit RootUpdated(new_root)
    }

    // Caller proves:
    //   1. They know a secret `s` such that hash(s, addr_commit) is a leaf
    //      in the tree whose root is `merkle_root`.
    //   2. `nullifier == poseidon(s, context)` where `context` is the action
    //      being authorized (e.g. airdrop id, proposal id).
    action authenticate(nullifier: bytes32, context: bytes32, proof: bytes) -> bool {
        given !used[nullifier] or revert_with NullifierAlreadyUsed()

        let public_inputs = [merkle_root, nullifier, context]
        given zk_verify(eligibility_circuit, proof, public_inputs)
            or revert_with InvalidProof()

        used[nullifier] = true
        emit CredentialUsed(nullifier)
        return true
    }
}

// Composing with an airdrop:
contract PrivateAirdrop {
    field identity: PrivateIdentity
    field token: address
    field amount: amount
    field context: bytes32 = keccak256("airdrop:2026-Q2")

    action claim(nullifier: bytes32, recipient: address, proof: bytes) {
        identity.authenticate(nullifier, context, proof)
        transfer(token, recipient, amount)
    }
}
```

## Explanation

- The admin publishes a Merkle root `merkle_root` committing to the eligible set. Each leaf is `poseidon(identity_secret, commitment_to_address)`.
- The caller builds a Groth16 witness consisting of their secret, the Merkle path, and a freshly derived nullifier. The circuit checks the path and binds the nullifier to both the secret and the `context` input — so a credential used for airdrop A cannot be replayed on airdrop B.
- The `used` mapping enforces one-shot semantics. Once `used[nullifier] == true`, the proof cannot be accepted again, even by a different caller.
- The recipient address is *not* bound to the secret — the prover chooses it freely at claim time, which gives the anonymity (otherwise the tx origin would trivially deanonymize the claimant).

This is the standard *tornado-cash-style* anon-set with the addition of per-action contexts, which lets you reuse the same eligibility root across many gated actions without correlating them.

## Gas Estimate

| Operation | Gas (L1) | pGas (Aster) |
|-----------|---------|-------------|
| `set_root` | ~45,000 | ~4,000 |
| `authenticate` (Groth16, depth-20 tree) | ~280,000 | ~24,000 |
| `authenticate` (Plonk, depth-32 tree) | ~380,000 | ~33,000 |

## Common Pitfalls

1. **Forgetting `context` binding**: Without a context, a single credential can be replayed across every gated action. Always hash the action identifier into the nullifier.
2. **Address binding**: If the circuit binds the recipient address, tx.origin leaks the claimant. Leave recipient free inside the circuit and pass it as a public input only for the `transfer` call.
3. **Leaking through tx metadata**: Gas price, tip, and mempool timing can correlate to the original tree insertion. Use private relays or a meta-tx relayer.
4. **Root rotation**: When you publish a new root, old credentials stop working unless you keep a window of historical roots (`map<bytes32, bool> valid_roots`).
5. **Poseidon vs keccak**: The circuit dictates the hash. Using keccak in the contract but poseidon in the circuit is the most common bug we see in audits.

## Variations

- **Semaphore-compatible**: Replace `eligibility_circuit` with the Semaphore v4 verifier; `nullifier` and `context` map 1:1.
- **Revocable credentials**: Add a second Merkle tree `revoked_root` and require the circuit to prove non-membership.
- **Threshold credentials**: Require `k` different nullifiers before `authenticate` returns `true`; useful for "5 DAO members approve".

## See Also

- [Shielded Token Bridge](/docs/cookbook/privacy/06-shielded-token-bridge)
- [ZK Proof Primitives](/docs/reference/stdlib/02-zk)
- [Example 11 — Semaphore Integration](/docs/examples/11-semaphore)
