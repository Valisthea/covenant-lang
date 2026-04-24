---
title: "Vesting Schedule"
description: "Lock tokens that unlock linearly over time with an optional cliff, typical for team/investor allocations."
section: cookbook
order: 5
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Vesting Schedule

## Problem

I need to grant tokens to team members or investors that unlock linearly over time, with an optional cliff before any tokens become claimable.

## Solution

```covenant
contract VestingVault {
    struct VestingInfo {
        total: amount
        released: amount
        start: timestamp
        cliff: u64
        duration: u64
    }

    field owner: address = deployer
    field token: address
    field schedules: mapping<address, VestingInfo>

    event ScheduleCreated(
        beneficiary: address indexed,
        total: amount,
        start: timestamp,
        cliff: u64,
        duration: u64
    )
    event Released(beneficiary: address indexed, amount: amount)
    event Revoked(beneficiary: address indexed, unvested: amount)

    error NoSchedule()
    error NothingToRelease()
    error InvalidDuration()
    error AlreadyExists()

    action grant(
        beneficiary: address,
        total: amount,
        start: timestamp,
        cliff: u64,
        duration: u64
    ) only owner {
        given duration > 0 or revert_with InvalidDuration()
        given schedules[beneficiary].total == 0 or revert_with AlreadyExists()
        schedules[beneficiary] = VestingInfo {
            total: total,
            released: 0,
            start: start,
            cliff: cliff,
            duration: duration
        }
        emit ScheduleCreated(beneficiary, total, start, cliff, duration)
    }

    action vested_amount(who: address) -> amount {
        let s = schedules[who]
        given s.total > 0 or revert_with NoSchedule()
        if now < s.start + s.cliff {
            return 0
        }
        if now >= s.start + s.duration {
            return s.total
        }
        return s.total * (now - s.start) / s.duration
    }

    action release() {
        let s = schedules[caller]
        given s.total > 0 or revert_with NoSchedule()
        let vested = vested_amount(caller)
        let claimable = vested - s.released
        given claimable > 0 or revert_with NothingToRelease()
        schedules[caller].released = s.released + claimable
        transfer(token, caller, claimable)
        emit Released(caller, claimable)
    }
}
```

## Explanation

- `VestingInfo` stores everything per-beneficiary in a single struct slot-packed by the compiler
- Linear unlock is `total * (now - start) / duration` after the cliff passes
- Before `start + cliff` the function short-circuits to `0`
- After `start + duration` it returns the full total (caps the formula)
- `released` tracks what has already been claimed so the beneficiary can `release()` incrementally

Under the hood, the compiler generates a single `SSTORE` per `grant` thanks to struct-packing and a single `SSTORE` on `release` (updating only `released`).

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `grant` | ~90,000 |
| `release` (partial) | ~55,000 |
| `release` (final) | ~60,000 |
| `vested_amount` (view) | ~4,500 |

## Common Pitfalls

1. **Cliff confusion**: `cliff` is a duration (seconds relative to `start`), not an absolute timestamp. Document this clearly in the UI.
2. **Re-granting**: The `AlreadyExists` guard prevents accidentally overwriting a schedule and zeroing `released`. Use a separate `top_up` action if you need additive grants.
3. **Revocation not implemented**: If the beneficiary leaves early, you need an explicit revoke path — see Variations.
4. **Zero `duration`**: Would cause a division-by-zero at `vested_amount`. The `InvalidDuration` guard blocks it at `grant` time.
5. **Token pulled from contract balance**: The vault must be funded separately before grants can be released. Consider a `fund` action that also emits an event for accounting.

## Variations

### Revocable vesting

```covenant
action revoke(beneficiary: address) only owner {
    let s = schedules[beneficiary]
    let vested = vested_amount(beneficiary)
    let unvested = s.total - vested
    schedules[beneficiary].total = vested   // freeze at vested
    transfer(token, owner, unvested)
    emit Revoked(beneficiary, unvested)
}
```

### Multi-tranche grant

Replace the single `VestingInfo` with `mapping<address, VestingInfo[]>` and iterate in `vested_amount`.

## See Also

- [Mintable Token](/docs/cookbook/tokens/01-mintable-token)
- [Capped Supply Token](/docs/cookbook/tokens/06-capped-supply)
- [Auth: Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin)
