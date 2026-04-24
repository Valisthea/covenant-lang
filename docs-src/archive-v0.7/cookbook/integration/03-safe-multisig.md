---
title: "Safe (Gnosis) Multisig Integration"
description: "Use a deployed Safe multisig as the contract owner, receiving and executing transactions through it."
section: cookbook
order: 3
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Safe (Gnosis) Multisig Integration

## Problem

I want a deployed [Safe](https://safe.global) multisig (formerly Gnosis Safe) to be the *owner* of my Covenant contract. Protocol upgrades, treasury disbursements, and parameter changes should all route through the Safe's M-of-N signer set. I also want the contract itself to be able to execute transactions *as* the Safe when a proposal is approved off-chain and submitted on-chain.

## Solution

```covenant
// External ABI for the Safe contract
external contract ISafe {
    action execTransaction(
        to: address,
        value: u256,
        data: bytes,
        operation: u8,       // 0 = CALL, 1 = DELEGATECALL
        safe_tx_gas: u256,
        base_gas: u256,
        gas_price: u256,
        gas_token: address,
        refund_receiver: address,
        signatures: bytes
    ) returns (success: bool)

    action getThreshold() returns (t: u256)
    action isOwner(a: address) returns (b: bool)
    action nonce() returns (n: u256)
}

contract SafeOwnedTreasury {
    field owner: address            // Set to the Safe address at deploy
    field safe: ISafe               // Typed reference to the Safe
    field total_received: amount = 0
    field spend_limit_per_tx: amount = 100 ether

    event Received(from: address indexed, amount: amount)
    event Disbursed(to: address indexed, amount: amount, safe_nonce: u256)
    event SafeRotated(previous: address, current: address)

    error NotOwner()
    error OverLimit()
    error SafeCallFailed()

    action init(safe_address: address) {
        given owner == address(0)  // one-shot init
        owner = safe_address
        safe = ISafe(safe_address)
    }

    guard only_safe {
        given caller == owner or revert_with NotOwner()
    }

    // Anyone can deposit; only the Safe can disburse.
    action receive() payable {
        total_received = total_received + msg.value
        emit Received(caller, msg.value)
    }

    action disburse(to: address, amount: amount) only_safe {
        given amount <= spend_limit_per_tx or revert_with OverLimit()
        let n = safe.nonce()
        transfer(to, amount)
        emit Disbursed(to, amount, n)
    }

    action set_spend_limit(new_limit: amount) only_safe {
        spend_limit_per_tx = new_limit
    }

    action rotate_safe(new_safe: address) only_safe {
        let previous = owner
        owner = new_safe
        safe = ISafe(new_safe)
        emit SafeRotated(previous, new_safe)
    }

    // Let the treasury forward an arbitrary call AS ITSELF when the Safe says so.
    // The Safe has already verified M-of-N signatures before reaching this call.
    action execute_from_safe(target: address, value: u256, data: bytes)
        only_safe
        returns (result: bytes) {

        let result = external_call(target, value, data)
            or revert_with SafeCallFailed()
        return result
    }
}
```

## Explanation

- The Safe deploys independently (via the Safe UI or `SafeProxyFactory`). Its address becomes the `owner` of the Covenant contract -- no special integration code needed for the auth path.
- Because `caller == owner` means `caller == safe_address`, every `only_safe` action is automatically gated by the Safe's full M-of-N signature check -- the Safe validates signatures in `execTransaction` *before* calling into our contract.
- The treasury never verifies signatures itself. All signature logic lives in the Safe, which is already audited and battle-tested.
- `execute_from_safe` is a generic escape hatch: the Safe proposes a call, collects signatures off-chain, submits via `execTransaction`, which `call`s the treasury's `execute_from_safe`, which then forwards to `target`. The treasury's own address appears as `msg.sender` to `target`.
- `rotate_safe` lets the current Safe hand ownership to a migrated Safe (e.g., when upgrading signer sets or migrating to a new Safe version).

## Off-chain Flow

```
1. Signer A drafts a tx in the Safe UI: treasury.disburse(alice, 10 ether)
2. Signers A, B sign the SafeTx hash (EIP-712) off-chain
3. Anyone submits safe.execTransaction(...) with both signatures
4. Safe verifies sigs, increments nonce, calls treasury.disburse(alice, 10 ether)
5. treasury.disburse runs with caller == safe_address -> only_safe passes
6. Disbursed event emits with the Safe's nonce for traceability
```

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `receive` (deposit) | ~30,000 |
| `disburse` via Safe (2-of-3) | ~95,000 (Safe overhead) + ~40,000 (disburse) |
| `rotate_safe` via Safe | ~50,000 |
| Reading `safe.nonce()` | ~3,000 |

## Common Pitfalls

1. **Setting owner to a non-Safe EOA by mistake**: Always verify at deploy that `safe_address.code.length > 0` and `ISafe(safe_address).getThreshold() >= 2`.
2. **Forgetting to check `caller == owner`**: The pattern only works because the Safe's address *is* the owner. If you check `isOwner(caller)` instead, you're asking whether the *caller* is a Safe signer -- which lets a single signer act unilaterally. Don't do that.
3. **Ignoring the Safe nonce**: Replays are impossible thanks to the nonce increment in `execTransaction`, but logging the nonce in `Disbursed` helps incident reconstruction.
4. **Using `delegatecall` (operation=1) casually**: A `DELEGATECALL` from the Safe into your contract runs *in the Safe's storage*. Use only when you intentionally want to mutate the Safe itself (e.g., module installation).
5. **Modules vs. ownership**: For frequent programmatic actions (streaming payments, auto-compound), consider installing a Safe Module instead of routing every call through `execTransaction` -- cheaper and doesn't require N signatures per action.

## Variations

### Safe Module instead of Owner

Instead of making the Safe the *owner*, register this contract as a *Module* on the Safe. Modules can call `Safe.execTransactionFromModule` without signatures. Useful for automations where signature overhead is prohibitive.

### Hybrid: Safe + Timelock

Route Safe transactions through a Timelock contract first: `Safe -> Timelock -> Treasury`. Adds a 48h delay on top of M-of-N approval. See [Time-Locked Admin](/docs/cookbook/auth/02-time-locked-admin).

## See Also

- [Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin) -- for a native Covenant multisig implementation
- [Chainlink Oracle Integration](/docs/cookbook/integration/01-chainlink-oracle)
- [Safe documentation](https://docs.safe.global)
