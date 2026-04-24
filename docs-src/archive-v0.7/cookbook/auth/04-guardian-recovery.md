---
title: "Guardian Recovery"
description: "Recover control of a contract via a quorum of pre-registered guardians when the primary key is lost."
section: cookbook
order: 4
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Guardian Recovery

## Problem

The primary owner key of a critical contract could be lost, stolen, or compromised. I need a social-recovery mechanism where a quorum of trusted guardians (3-of-5) can rotate the owner -- but only after a 72-hour timelock that gives the real owner a chance to cancel a malicious recovery.

## Solution

```covenant
contract GuardianRecoverable {
    field owner: address = deployer
    field guardians: mapping<address, bool>
    field guardian_count: u8 = 0
    field quorum: u8 = 3
    field recovery_delay: u64 = 259200  // 72 hours in seconds

    // Pending recoveries
    field next_recovery_id: u64 = 0
    field recoveries: mapping<u64, Recovery>
    field approvals: mapping<u64, mapping<address, bool>>
    field approval_count: mapping<u64, u8>

    struct Recovery {
        proposed_owner: address
        proposed_at: timestamp
        executed: bool
        cancelled: bool
    }

    event GuardianAdded(guardian: address indexed)
    event RecoveryProposed(id: u64 indexed, proposer: address indexed, new_owner: address)
    event RecoveryConfirmed(id: u64 indexed, guardian: address indexed)
    event RecoveryExecuted(id: u64 indexed, new_owner: address)
    event RecoveryCancelled(id: u64 indexed)

    error NotOwner()
    error NotGuardian()
    error AlreadyGuardian()
    error RecoveryNotFound()
    error AlreadyConfirmed()
    error QuorumNotMet()
    error TimelockActive()
    error AlreadyFinalised()

    guard only_owner {
        given caller == owner or revert_with NotOwner()
    }

    guard only_guardian {
        given guardians[caller] or revert_with NotGuardian()
    }

    action add_guardian(g: address) only_owner {
        given !guardians[g] or revert_with AlreadyGuardian()
        guardians[g] = true
        guardian_count = guardian_count + 1
        emit GuardianAdded(g)
    }

    action propose_recovery(new_owner: address)
        only_guardian
        returns (id: u64) {

        let id = next_recovery_id
        recoveries[id] = Recovery {
            proposed_owner: new_owner,
            proposed_at: now,
            executed: false,
            cancelled: false
        }
        approvals[id][caller] = true
        approval_count[id] = 1
        next_recovery_id = next_recovery_id + 1

        emit RecoveryProposed(id, caller, new_owner)
        return id
    }

    action confirm_recovery(id: u64) only_guardian {
        given id < next_recovery_id or revert_with RecoveryNotFound()
        given !recoveries[id].executed and !recoveries[id].cancelled
            or revert_with AlreadyFinalised()
        given !approvals[id][caller] or revert_with AlreadyConfirmed()

        approvals[id][caller] = true
        approval_count[id] = approval_count[id] + 1
        emit RecoveryConfirmed(id, caller)
    }

    action execute_recovery(id: u64) only_guardian {
        let r = recoveries[id]
        given !r.executed and !r.cancelled or revert_with AlreadyFinalised()
        given approval_count[id] >= quorum or revert_with QuorumNotMet()
        given now >= r.proposed_at + recovery_delay or revert_with TimelockActive()

        recoveries[id].executed = true
        owner = r.proposed_owner
        emit RecoveryExecuted(id, r.proposed_owner)
    }

    action cancel_recovery(id: u64) only_owner {
        given !recoveries[id].executed or revert_with AlreadyFinalised()
        recoveries[id].cancelled = true
        emit RecoveryCancelled(id)
    }
}
```

## Explanation

- `guardians` is a `mapping<address, bool>` for O(1) membership checks; `guardian_count` tracks size for governance math.
- The proposer's own confirmation is counted at creation time -- no need for a separate `confirm` call from the proposer.
- `execute_recovery` enforces **both** quorum (3 confirmations) and timelock (72h elapsed) before rotating the owner.
- `cancel_recovery` gives the real owner an escape hatch -- if they still have their key they can veto a malicious recovery during the 72h window.
- The recovery ID monotonically increases, so old proposals cannot be replayed.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `add_guardian` | ~50,000 |
| `propose_recovery` | ~110,000 |
| `confirm_recovery` | ~45,000 |
| `execute_recovery` | ~35,000 |
| `cancel_recovery` | ~30,000 |

## Common Pitfalls

1. **No timelock**: Without the 72h delay, a colluding guardian majority can seize the contract instantly. The delay is what makes the scheme *recoverable* rather than *seizable*.
2. **Owner-is-guardian bootstrap**: If the owner registers themselves as a guardian, losing the owner key also burns one guardian slot. Keep guardian set disjoint from the owner.
3. **Quorum equal to count**: A 5-of-5 quorum means losing any single guardian permanently disables recovery. Use majority, not unanimity.
4. **Guardian collusion**: Pick guardians from independent trust domains (family, lawyer, hardware wallet in a safe) -- not all from the same team.
5. **Forgotten cancel**: The real owner must monitor `RecoveryProposed` events during the 72h window. Consider off-chain push notifications.

## Variations

### Weighted guardians

Some guardians count more than others (e.g., a hardware module counts as 2):

```covenant
field weights: mapping<address, u8>
field total_weight: u64

action confirm_recovery(id: u64) only_guardian {
    approvals[id][caller] = true
    approval_count[id] = approval_count[id] + weights[caller]
}
```

### Rotating guardian set

Let guardians themselves vote to replace a compromised peer, using the same quorum+timelock scheme applied to a `ProposeGuardianSwap` action.

## See Also

- [Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin)
- [Time-Locked Admin](/docs/cookbook/auth/02-time-locked-admin)
- [Role-Based Access Control](/docs/cookbook/auth/05-role-based-access)
