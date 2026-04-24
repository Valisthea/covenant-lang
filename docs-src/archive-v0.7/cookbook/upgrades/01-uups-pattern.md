---
title: "UUPS Upgradeable"
description: "A contract that can be upgraded while keeping a single stable address, using the UUPS proxy pattern with automatic re-init protection."
section: cookbook
order: 1
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# UUPS Upgradeable

## Problem

I need my contract to be upgradeable (fix bugs, add features) while keeping the same address. I also need protection against the re-initialization vulnerability.

## Solution

```covenant
upgradeable contract UpgradeableVault {
    version 1 {
        field owner: address = deployer
        field balance: amount = 0 tokens
        field initialized: bool = false

        event Initialized(version: uint)
        event Upgraded(new_impl: address indexed)
        event Deposited(from: address indexed, amount: amount)
        event Withdrawn(to: address indexed, amount: amount)

        error AlreadyInitialized()
        error NotOwner()
        error InsufficientBalance()

        action initialize(new_owner: address) {
            given !initialized or revert_with AlreadyInitialized()
            initialized = true
            owner = new_owner
            emit Initialized(1)
        }

        action deposit(amount: amount) {
            balance = balance + amount
            emit Deposited(caller, amount)
        }

        action withdraw(to: address, amount: amount) only owner {
            given amount <= balance or revert_with InsufficientBalance()
            balance = balance - amount
            transfer(to, amount)
            emit Withdrawn(to, amount)
        }

        action upgrade_to(new_impl: address) only owner {
            emit Upgraded(new_impl)
            proxy_upgrade(new_impl)
        }
    }
}
```

## Explanation

The `upgradeable contract` keyword generates:
1. A proxy contract deployed to the stable address (stores state)
2. An implementation contract (stores logic)
3. A `__initialized` guard that prevents re-initialization after upgrade (OMEGA V4 finding resolved automatically)

The `version 1 { }` block marks this as the first implementation. When V2 is written:

```covenant
upgradeable contract UpgradeableVault {
    version 2 {
        // inherits all V1 fields
        field fee_bps: uint = 30   // new field

        // V2 overrides withdraw with fee
        action withdraw(to: address, amount: amount) only owner {
            let fee = amount * fee_bps / 10000
            let net = amount - fee
            balance = balance - amount
            transfer(to, net)
            transfer(fee_collector, fee)
        }

        // V2 initializer runs once after upgrade
        action initialize_v2(fee_collector: address) {
            // compiler generates: given !__v2_initialized
            fee_collector_addr = fee_collector
        }
    }
}
```

## OMEGA V4 Context

The OMEGA V4 audit (Critical finding **KSR-CVN-002**) identified that upgradeable contracts without automatic re-init guards could be re-initialized after upgrade, transferring ownership. The Covenant compiler\'s `upgradeable contract` construct generates a `__initialized_vN` flag for each version, preventing re-initialization automatically.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| Proxy deployment | ~200,000 |
| `initialize` | ~55,000 |
| `deposit` | ~30,000 |
| `withdraw` | ~45,000 |
| `upgrade_to` | ~35,000 (+ new impl deploy) |

## Common Pitfalls

1. **Manual re-init guard**: Don\'t add your own `initialized` check -- the compiler generates one. Two checks create a logic conflict.
2. **Storage collisions**: New fields in V2 must be appended, never inserted. The compiler enforces this.
3. **Upgrade without time-lock**: Combine with [Time-Locked Admin](/docs/cookbook/auth/02-time-locked-admin) for production protocols.
4. **Upgrading implementation without proxy**: `upgrade_to` updates the proxy\'s implementation pointer. Never redeploy the proxy.

## See Also

- [Beacon Proxy Pattern](/docs/cookbook/upgrades/02-beacon-pattern)
- [Example 12 -- UUPS Upgradeable](/docs/examples/12-uups-upgradeable)
- [Security: OMEGA V4 Findings](/docs/security/critical-findings)
