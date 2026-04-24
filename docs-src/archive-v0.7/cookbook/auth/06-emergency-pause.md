---
title: "Emergency Pause"
description: "Global pause switch that halts mutating actions while allowing reads — the circuit breaker pattern."
section: cookbook
order: 6
level: beginner
---

<!-- Last sync: 2026-04-23 -->

# Emergency Pause

## Problem

When a bug or exploit is discovered in production, I need to halt every mutating action immediately -- but keep read-only views working so users can inspect their balances. The switch should be flippable by a low-trust "pauser" role (fast response) while only an admin can flip it back (prevents grief).

## Solution

```covenant
contract Pausable {
    field owner: address = deployer
    field pauser: address = deployer
    field paused: bool = false

    event Paused(by: address indexed)
    event Unpaused(by: address indexed)
    event PauserSet(previous: address, current: address)

    error NotOwner()
    error NotPauser()
    error ContractPaused()
    error NotPausedState()

    guard only_owner {
        given caller == owner or revert_with NotOwner()
    }

    guard only_pauser {
        given caller == pauser or caller == owner or revert_with NotPauser()
    }

    guard when_not_paused {
        given !paused or revert_with ContractPaused()
    }

    guard when_paused {
        given paused or revert_with NotPausedState()
    }

    action pause() only_pauser {
        given !paused or revert_with ContractPaused()
        paused = true
        emit Paused(caller)
    }

    action unpause() only_owner when_paused {
        paused = false
        emit Unpaused(caller)
    }

    action set_pauser(new_pauser: address) only_owner {
        let previous = pauser
        pauser = new_pauser
        emit PauserSet(previous, new_pauser)
    }

    // --- Every mutating action gets the when_not_paused guard ---

    action deposit(amount: amount) when_not_paused {
        // balance[caller] += amount
    }

    action withdraw(amount: amount) when_not_paused {
        // balance[caller] -= amount
    }

    action transfer(to: address, amount: amount) when_not_paused {
        // balance[caller] -= amount; balance[to] += amount
    }

    // Reads are intentionally NOT guarded -- users can always inspect state.
    action balance_of(a: address) returns (b: amount) {
        // return balance[a]
    }
}
```

## Explanation

- **Asymmetric trust**: `pause` is gated by `only_pauser` (a hot-key monitor bot or on-call engineer) so it can fire in seconds. `unpause` is gated by `only_owner` (the multisig) so the pause cannot be silently lifted.
- **Read-only paths stay open**: views like `balance_of` and any `returns`-only action without `when_not_paused` keep working under pause. This is essential for liquidator bots, frontends, and indexers.
- `only_pauser` also accepts `owner` -- admins never lose the ability to pause.
- The `when_not_paused` guard is applied uniformly to every mutating action. If you forget one, that action bypasses the circuit breaker -- consider a lint rule.
- Emitting `Paused(by)` and `Unpaused(by)` gives the on-chain audit trail needed for incident reports.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `pause` | ~28,000 |
| `unpause` | ~28,000 |
| `when_not_paused` guard (added to each action) | ~200 |
| View actions (balance_of) | unchanged |

## Common Pitfalls

1. **Forgetting a mutating action**: Any action without `when_not_paused` is a hole in the circuit breaker. Audit the full action list on every release.
2. **Pausing reads too**: Guarding views with `when_not_paused` breaks liquidators, explorers, and frontends. Pause should never affect reads.
3. **Pause as a rug**: Users are right to fear pauses -- they look indistinguishable from exit scams. Publish a pause policy: who can pause, under what conditions, and a maximum pause duration (e.g., 14 days before auto-unpause).
4. **Pauser = owner**: Defeats the asymmetry. A hot monitor bot should *not* be able to upgrade contracts, only pause.
5. **No auto-unpause**: A consider adding a `max_pause_duration` field and a permissionless `force_unpause_if_expired()` to prevent indefinite freeze.

## Variations

### Auto-expiring pause

```covenant
field pause_expiry: timestamp = 0
const MAX_PAUSE: u64 = 1209600  // 14 days

action pause() only_pauser {
    paused = true
    pause_expiry = now + MAX_PAUSE
    emit Paused(caller)
}

action force_unpause_if_expired() {
    given paused and now >= pause_expiry or revert_with NotPausedState()
    paused = false
    emit Unpaused(caller)
}
```

### Scoped pause (per-action)

Instead of a single `paused` bool, use `paused_actions: mapping<bytes4, bool>` keyed by selector -- pause only `withdraw` while leaving `deposit` open.

## See Also

- [Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin)
- [Role-Based Access Control](/docs/cookbook/auth/05-role-based-access)
- [Guardian Recovery](/docs/cookbook/auth/04-guardian-recovery)
