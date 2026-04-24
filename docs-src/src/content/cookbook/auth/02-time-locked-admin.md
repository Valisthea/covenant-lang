---
title: "Time-Locked Admin"
description: "Admin actions that are queued and only executable after a minimum delay, giving users time to react."
section: cookbook
order: 2
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Time-Locked Admin

## Problem

I need critical admin actions (parameter changes, upgrades) to have a mandatory 48-hour delay between proposal and execution, so users have time to exit before any change takes effect.

## Solution

```covenant
contract TimelockController {
    field admin: address = deployer
    field min_delay: time = 48 hours
    field max_delay: time = 30 days

    field operation_count: uint = 0
    field operations: map<uint, Operation>

    struct Operation {
        target: address
        calldata: bytes
        value: amount
        eta: time
        executed: bool
        cancelled: bool
    }

    event OperationQueued(id: uint indexed, eta: time)
    event OperationExecuted(id: uint indexed)
    event OperationCancelled(id: uint indexed)
    event DelayUpdated(old_delay: time, new_delay: time)

    error NotAdmin()
    error DelayTooShort()
    error DelayTooLong()
    error NotReady()
    error Expired()
    error AlreadyExecuted()
    error AlreadyCancelled()

    action queue(target: address, calldata: bytes, value: amount, delay: time)
        only admin
        returns (id: uint) {

        given delay >= min_delay or revert_with DelayTooShort()
        given delay <= max_delay or revert_with DelayTooLong()

        let eta = block.timestamp + delay
        let id = operation_count

        operations[id] = Operation {
            target: target,
            calldata: calldata,
            value: value,
            eta: eta,
            executed: false,
            cancelled: false
        }
        operation_count = operation_count + 1

        emit OperationQueued(id, eta)
        return id
    }

    action execute(id: uint) only admin {
        let op = operations[id]

        given !op.executed or revert_with AlreadyExecuted()
        given !op.cancelled or revert_with AlreadyCancelled()
        given block.timestamp >= op.eta or revert_with NotReady()
        given block.timestamp < op.eta + 14 days or revert_with Expired()

        operations[id].executed = true
        external_call(op.target, op.value, op.calldata)

        emit OperationExecuted(id)
    }

    action cancel(id: uint) only admin {
        given !operations[id].executed or revert_with AlreadyExecuted()
        operations[id].cancelled = true
        emit OperationCancelled(id)
    }

    action update_delay(new_delay: time) only admin {
        given new_delay >= 1 hour or revert_with DelayTooShort()
        emit DelayUpdated(min_delay, new_delay)
        min_delay = new_delay
    }
}
```

## Explanation

- The 14-day expiry window prevents stale operations from being executed months later
- `only admin` on `execute` means the admin must manually trigger execution -- operations don\'t execute automatically at ETA
- `update_delay` itself should ideally go through the timelock (call `queue` with the update as calldata)

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `queue` | ~75,000 |
| `execute` | ~50,000 + execution cost |
| `cancel` | ~30,000 |

## Common Pitfalls

1. **No expiry**: Without a grace period, a queued operation can sit forever and execute after circumstances change.
2. **`update_delay` not timelocked**: Allowing instant delay changes defeats the purpose. Route delay updates through the timelock itself.
3. **block.timestamp manipulation**: Miners can shift `block.timestamp` by ~15s. For 48h delays, this is negligible. For very short delays (< 1 minute), use block numbers instead.
4. **Missing cancel**: Users watching the queue need a way to cancel a malicious operation before it executes (even if only admin can cancel -- governance or guardian).

## See Also

- [Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin)
- [PQ-Signed Admin](/docs/cookbook/auth/03-pq-signed-admin)
- [Example 04 -- Guards](/docs/examples/04-guards)
