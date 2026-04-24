---
title: "Migration Scripts"
description: "Upgrade a deployed contract's state using migration scripts that run once per version."
section: cookbook
order: 4
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Migration Scripts

## Problem

I am upgrading my deployed contract from v1 to v2. The new version adds a field and renames another. I need the state transformation to run exactly once, atomically, during the upgrade.

## Solution

```covenant
upgradeable contract StakingVault {
    version 1 {
        field owner: address = deployer
        field total_staked: amount = 0 tokens
        field reward_rate: u256 = 100   // basis points, legacy name
    }

    version 2 {
        // inherits total_staked and owner unchanged
        field reward_rate_bps: u256         // renamed from reward_rate
        field fee_collector: address = address(0)   // new field
        field last_update: timestamp = 0            // new field

        migration to_v2 {
            run_once;

            // Rename: copy legacy value then clear the old slot
            reward_rate_bps = reward_rate;
            clear reward_rate;

            // Initialise new fields
            fee_collector = owner;
            last_update = now;

            emit Migrated(from: 1, to: 2, at: now);
        }
    }

    event Migrated(from: uint, to: uint, at: timestamp)
}
```

Deploy the upgrade:

```bash
covenant migrate --from 1.0.0 --to 2.0.0 --address 0xVault...
```

## Explanation

- `migration to_v2 { run_once; }` declares a block that the proxy executes exactly once, gated by a compiler-generated `__migrated_v2: bool` flag
- `run_once` is a mandatory directive -- without it, the compiler rejects the migration because a replay would double-apply transformations
- `clear` zeroes a storage slot so the renamed field no longer consumes gas on reads and returns its storage deposit
- `covenant migrate` on the CLI reads the on-chain version, checks the target matches the compiled artifact, deploys the new implementation, and calls the migration atomically in one transaction
- At compile time, the compiler diffs v1 and v2 storage layouts and refuses to build if any field was reordered or had its type narrowed without a migration block handling the change

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| Migration deploy (CLI) | ~1,200,000 |
| `migration to_v2` execution | ~95,000 |
| Storage slot clear (refund) | -4,800 |
| `__migrated_v2` flag set | 22,100 |

## Common Pitfalls

1. **Forgetting `run_once`**: Without it the compiler refuses to build. If you bypass the check with a custom flag you risk replay that double-applies transforms on a resumed upgrade.
2. **Reading cleared fields**: After `clear reward_rate`, any v2 action that still references `reward_rate` is a compile error because the field is removed from the v2 layout.
3. **Migration that reverts mid-way**: The upgrade transaction reverts atomically, but you must retry with corrected code. Test migrations on a fork first with `covenant migrate --dry-run`.
4. **Changing field types**: Widening (`u64` to `u256`) is safe. Narrowing loses data; the compiler blocks it unless the migration explicitly handles truncation.
5. **Skipping a version**: `--from 1.0.0 --to 3.0.0` runs `to_v2` then `to_v3` sequentially in one transaction. Each migration must be idempotent-safe because a failure between them leaves the contract at the intermediate version.

## Variations

### Migration with external data

Feed values from a JSON file at migration time:

```bash
covenant migrate --from 1.0.0 --to 2.0.0 \
    --input migration-v2.json \
    --address 0xVault...
```

```covenant
migration to_v2 {
    run_once;
    fee_collector = input.fee_collector;
    last_update = now;
}
```

### Dry-run on a fork

```bash
covenant migrate --dry-run \
    --from 1.0.0 --to 2.0.0 \
    --fork mainnet@latest \
    --address 0xVault...
```

Reports the state diff without broadcasting. Use this before every production migration.

## See Also

- [UUPS Upgradeable](/docs/cookbook/upgrades/01-uups-pattern)
- [Beacon Proxy Pattern](/docs/cookbook/upgrades/02-beacon-pattern)
- [Diamond Storage Pattern](/docs/cookbook/upgrades/03-diamond-storage)
