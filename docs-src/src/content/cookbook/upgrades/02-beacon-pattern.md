---
title: "Beacon Proxy Pattern"
description: "Deploy many instances of a contract that can all be upgraded simultaneously by updating a single beacon."
section: cookbook
order: 2
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Beacon Proxy Pattern

## Problem

I need to deploy many instances of the same contract (e.g., per-user vaults, per-pool AMMs) that can all be upgraded to a new implementation in a single transaction.

## Solution

```covenant
// The beacon holds the current implementation address
contract VaultBeacon {
    field owner: address = deployer
    field implementation: address

    event Upgraded(new_impl: address indexed)
    error NotOwner()
    error ZeroAddress()

    action set_implementation(new_impl: address) only owner {
        given new_impl != address(0) or revert_with ZeroAddress()
        implementation = new_impl
        emit Upgraded(new_impl)
    }

    action get_implementation() returns (impl: address) {
        return implementation
    }
}

// Each vault instance is a beacon proxy
@proxy_compatible
contract UserVault {
    field owner: address
    field beacon: address
    field balance: amount = 0 tokens

    event Initialized(owner: address indexed)
    event Deposited(amount: amount)
    event Withdrawn(to: address indexed, amount: amount)

    error NotOwner()
    error InsufficientBalance()

    action initialize(vault_owner: address, beacon_addr: address) {
        owner = vault_owner
        beacon = beacon_addr
        emit Initialized(vault_owner)
    }

    action deposit(amount: amount) {
        balance = balance + amount
        emit Deposited(amount)
    }

    action withdraw(to: address, amount: amount) only owner {
        given amount <= balance or revert_with InsufficientBalance()
        balance = balance - amount
        transfer(to, amount)
        emit Withdrawn(to, amount)
    }
}
```

## Explanation

- The beacon stores the implementation address. All proxy instances query the beacon at runtime.
- `@proxy_compatible` annotates the implementation contract, enabling the compiler to generate the beacon proxy delegation code.
- Upgrading all vaults: call `beacon.set_implementation(new_impl_address)` once. All proxies immediately use the new implementation.
- Each proxy stores its own state (owner, balance) but delegates logic to the current implementation.

## Deployment Script

```bash
# 1. Deploy implementation
covenant deploy ./out/UserVault.artifact.json --network sepolia

# 2. Deploy beacon with implementation address
covenant deploy ./out/VaultBeacon.artifact.json   --constructor-args \'["<IMPL_ADDRESS>"]\'   --network sepolia

# 3. Deploy proxies for each user (in a factory)
covenant deploy ./out/VaultProxy.artifact.json   --constructor-args \'["<BEACON_ADDRESS>"]\'   --network sepolia
```

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| Beacon deployment | ~150,000 |
| Implementation deployment | ~300,000+ |
| Proxy deployment (per instance) | ~100,000 |
| `set_implementation` (upgrades all) | ~30,000 |

## Common Pitfalls

1. **Not using `@proxy_compatible`**: Without the annotation, the compiler does not generate the delegation jump table.
2. **Initializing via constructor**: Proxies cannot use constructors. Always use an `initialize` action.
3. **Beacon not access-controlled**: The beacon owner can upgrade all proxies. Use multisig or timelock.
4. **State layout changes**: V2 must not change field order -- beacon proxies share a delegatecall model where storage slot positions are fixed.

## See Also

- [UUPS Pattern](/docs/cookbook/upgrades/01-uups-pattern)
- [Example 13 -- Beacon Proxy](/docs/examples/13-beacon-proxy)
