---
title: "Multi-Sig Admin"
description: "A contract where critical admin actions require approval from 2 of 3 (or M of N) designated signers."
section: cookbook
order: 1
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Multi-Sig Admin

## Problem

I need a contract where critical actions (like withdrawals or upgrades) can only execute when at least 2 of 3 designated admins approve.

## Solution

```covenant
contract MultiSigVault {
    field admins: set<address> = {deployer}
    field threshold: uint = 2

    // Pending proposals
    field proposal_id: uint = 0
    field proposals: map<uint, Proposal>
    field approvals: map<uint, set<address>>

    struct Proposal {
        target: address
        value: amount
        data: bytes
        executed: bool
        deadline: time
    }

    event ProposalCreated(id: uint indexed, proposer: address indexed)
    event Approved(id: uint indexed, approver: address indexed)
    event Executed(id: uint indexed)
    event Revoked(id: uint indexed, revoker: address indexed)

    error NotAdmin()
    error AlreadyApproved()
    error AlreadyExecuted()
    error ThresholdNotMet()
    error Expired()

    guard is_admin {
        given admins.contains(caller) or revert_with NotAdmin()
    }

    action propose(target: address, value: amount, data: bytes)
        is_admin
        returns (id: uint) {

        let id = proposal_id
        proposals[id] = Proposal {
            target: target,
            value: value,
            data: data,
            executed: false,
            deadline: block.timestamp + 7 days
        }
        approvals[id] = {}
        proposal_id = proposal_id + 1

        emit ProposalCreated(id, caller)
        return id
    }

    action approve(id: uint) is_admin {
        given !proposals[id].executed or revert_with AlreadyExecuted()
        given block.timestamp <= proposals[id].deadline or revert_with Expired()
        given !approvals[id].contains(caller) or revert_with AlreadyApproved()

        approvals[id].add(caller)
        emit Approved(id, caller)
    }

    action execute(id: uint) is_admin {
        given !proposals[id].executed or revert_with AlreadyExecuted()
        given block.timestamp <= proposals[id].deadline or revert_with Expired()
        given approvals[id].size() >= threshold or revert_with ThresholdNotMet()

        proposals[id].executed = true
        external_call(proposals[id].target, proposals[id].value, proposals[id].data)
        emit Executed(id)
    }

    action revoke(id: uint) is_admin {
        given approvals[id].contains(caller) or revert_with NotAdmin()
        approvals[id].remove(caller)
        emit Revoked(id, caller)
    }
}
```

## Explanation

- `set<address>` for `admins` and `approvals` -- O(1) membership checks, no iteration needed
- `proposal_id` is a monotonically increasing counter (no reuse of IDs)
- `guard is_admin` is a reusable guard block -- more readable than repeating the check
- The 7-day deadline prevents stale proposals from accumulating
- CEI pattern in `execute`: mark `executed = true` before the external call

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `propose` | ~80,000 |
| `approve` | ~35,000 |
| `execute` (simple transfer) | ~50,000 |
| `revoke` | ~30,000 |

## Common Pitfalls

1. **Missing expiry**: Without a deadline, proposals accumulate indefinitely and could be executed long after they\'re relevant.
2. **No revoke**: Admins who change their mind need a way to withdraw approval.
3. **External call without CEI**: Mark `executed = true` before `external_call` to prevent reentrancy.
4. **Threshold of 1**: A threshold of 1 is functionally equivalent to a single owner. Enforce minimum threshold of 2.
5. **Admin set not updatable**: This recipe has immutable admins. For admin rotation, add a `add_admin`/`remove_admin` action (also gated by multisig).

## Variations

### Simple M-of-N without data

For simpler cases (just "approve this specific operation"):

```covenant
field pending_action: address = address(0)
field action_approvals: set<address>

action initiate_withdrawal(to: address) is_admin {
    pending_action = to
    action_approvals = {}
}

action approve_withdrawal() is_admin {
    action_approvals.add(caller)
    if action_approvals.size() >= threshold {
        transfer(pending_action, balance)
        pending_action = address(0)
    }
}
```

## See Also

- [Time-Locked Admin](/docs/cookbook/auth/02-time-locked-admin)
- [PQ-Signed Admin](/docs/cookbook/auth/03-pq-signed-admin)
- [Example 04 -- Guards](/docs/examples/04-guards)
