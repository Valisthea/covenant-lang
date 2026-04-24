---
title: "PQ-Signed Admin"
description: "Admin actions protected by post-quantum Dilithium-5 signatures in addition to standard ECDSA authentication."
section: cookbook
order: 3
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# PQ-Signed Admin

## Problem

I need critical admin actions (treasury withdrawals, protocol upgrades) to be protected against quantum attackers who may be able to break ECDSA in the future.

## Solution

```covenant
contract QuantumSafeAdmin {
    field admin: address = deployer
    field admin_pq_key: pq_key

    field treasury: amount = 0 tokens

    event PQKeyRegistered(admin: address indexed)
    event WithdrawalExecuted(to: address indexed, amount: amount)
    event UpgradeProposed(new_impl: address indexed)

    error PQKeyNotSet()
    error ZeroAddress()
    error InsufficientFunds()

    action register_pq_key(pk: pq_key) only admin {
        admin_pq_key = pk
        emit PQKeyRegistered(admin)
    }

    action withdraw(to: address, amount: amount)
        only admin
        @pq_signed(admin_pq_key) {

        given admin_pq_key != pq_key(0) or revert_with PQKeyNotSet()
        given to != address(0) or revert_with ZeroAddress()
        given amount <= treasury or revert_with InsufficientFunds()

        treasury = treasury - amount
        transfer(to, amount)
        emit WithdrawalExecuted(to, amount)
    }

    action propose_upgrade(new_impl: address)
        only admin
        @pq_signed(admin_pq_key) {

        given new_impl != address(0) or revert_with ZeroAddress()
        emit UpgradeProposed(new_impl)
        // Actual upgrade logic would go here (see UUPS recipe)
    }

    // Standard ECDSA-only action for low-value operations
    action update_config(key: bytes32, value: bytes32) only admin {
        // No PQ required for non-critical config
        config[key] = value
    }
}
```

## Explanation

- `@pq_signed(admin_pq_key)` causes the compiler to inject a `PqVerify` check before the action body
- The transaction must include a Dilithium-5 signature over the transaction hash as extra calldata
- `register_pq_key` is deliberately ECDSA-only -- the PQ key must be registered before it can be used for PQ signing
- Non-critical actions (`update_config`) use only ECDSA -- PQ adds ~74 KB of calldata overhead per transaction

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `register_pq_key` | ~180,000 (2,600 bytes storage) |
| `withdraw` (with PQ sig) | ~155,000 |
| `propose_upgrade` (with PQ sig) | ~90,000 |
| PQ signature calldata overhead | 4,627 x 16 = 74,032 gas |

## Common Pitfalls

1. **No PQKeyNotSet check**: If admin_pq_key is zero and @pq_signed is used, the action reverts with an opaque error. Add an explicit check with a clear error.
2. **Register before use**: The PQ key must be registered in a separate transaction before any @pq_signed action is called.
3. **Key rotation**: If the PQ key is compromised, you need an escape hatch (e.g., multisig without PQ) to rotate it.
4. **Calldata cost**: Each PQ-signed transaction uses ~74 KB extra calldata. On Ethereum L1 this is ~-50 depending on gas price. Use Aster Chain for frequent PQ-signed operations.
5. **Signing off-chain**: PQ signatures must be generated off-chain using the Covenant SDK. The on-chain contract only verifies.

## Variations

### Hybrid mode (ECDSA OR PQ)

```covenant
action critical_action()
    given (caller == admin OR pq_verify(pq_sig, msg_hash, admin_pq_key)) {
    // ...
}
```

## See Also

- [ERC-8231 -- Post-Quantum Key Registry](/docs/reference/ercs/05-erc-8231-pq)
- [Example 09 -- Post-Quantum Signatures](/docs/examples/09-post-quantum-signatures)
- [Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin)
