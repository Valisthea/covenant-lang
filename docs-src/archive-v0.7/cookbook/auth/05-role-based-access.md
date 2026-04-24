---
title: "Role-Based Access Control"
description: "OpenZeppelin-style RBAC: grant, revoke, and enforce roles across multiple actions."
section: cookbook
order: 5
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Role-Based Access Control

## Problem

My contract has several privileged operations -- minting, pausing, upgrading -- and I want to hand each of them to a different address (or set of addresses) without creating N independent owner fields. I want the familiar OpenZeppelin `AccessControl` model: roles as `bytes32` identifiers, admin roles that can grant/revoke, and a single uniform guard.

## Solution

```covenant
contract RBAC {
    // role id => (holder => granted?)
    field roles: mapping<bytes32, mapping<address, bool>>
    field role_admin: mapping<bytes32, bytes32>

    // Canonical role identifiers (keccak256 of the string)
    const ADMIN_ROLE: bytes32 = 0x0000000000000000000000000000000000000000000000000000000000000000
    const MINTER_ROLE: bytes32 = keccak256("MINTER_ROLE")
    const PAUSER_ROLE: bytes32 = keccak256("PAUSER_ROLE")
    const UPGRADER_ROLE: bytes32 = keccak256("UPGRADER_ROLE")

    event RoleGranted(role: bytes32 indexed, account: address indexed, sender: address indexed)
    event RoleRevoked(role: bytes32 indexed, account: address indexed, sender: address indexed)
    event RoleAdminChanged(role: bytes32 indexed, previous: bytes32, current: bytes32)

    error MissingRole(role: bytes32, account: address)
    error CannotRenounceForOther()

    // Deployer bootstraps as ADMIN_ROLE; ADMIN_ROLE is its own admin.
    action init() {
        roles[ADMIN_ROLE][deployer] = true
        role_admin[ADMIN_ROLE] = ADMIN_ROLE
        role_admin[MINTER_ROLE] = ADMIN_ROLE
        role_admin[PAUSER_ROLE] = ADMIN_ROLE
        role_admin[UPGRADER_ROLE] = ADMIN_ROLE
        emit RoleGranted(ADMIN_ROLE, deployer, deployer)
    }

    guard only_role(r: bytes32) {
        given roles[r][caller] or revert_with MissingRole(r, caller)
    }

    action grant_role(role: bytes32, a: address)
        only_role(role_admin[role]) {

        given !roles[role][a]  // idempotent no-op if already granted
        roles[role][a] = true
        emit RoleGranted(role, a, caller)
    }

    action revoke_role(role: bytes32, a: address)
        only_role(role_admin[role]) {

        given roles[role][a]
        roles[role][a] = false
        emit RoleRevoked(role, a, caller)
    }

    // Holders can voluntarily drop their own role (cannot be used to kick others).
    action renounce_role(role: bytes32, a: address) {
        given a == caller or revert_with CannotRenounceForOther()
        given roles[role][a]
        roles[role][a] = false
        emit RoleRevoked(role, a, caller)
    }

    action set_role_admin(role: bytes32, new_admin: bytes32)
        only_role(ADMIN_ROLE) {

        let previous = role_admin[role]
        role_admin[role] = new_admin
        emit RoleAdminChanged(role, previous, new_admin)
    }

    // --- Example privileged actions using the guard ---

    action mint(to: address, amount: u256) only_role(MINTER_ROLE) {
        // ... mint logic
    }

    action pause() only_role(PAUSER_ROLE) {
        // ... pause logic
    }

    action upgrade(new_impl: address) only_role(UPGRADER_ROLE) {
        // ... upgrade logic
    }
}
```

## Explanation

- `bytes32` role identifiers mirror OpenZeppelin so the same off-chain tooling (Etherscan role dashboards, Defender) works unchanged.
- `ADMIN_ROLE` is the zero hash by convention -- easy to spot in logs and matches `DEFAULT_ADMIN_ROLE`.
- `role_admin[role]` is itself a role, meaning you can delegate: e.g., set `MINTER_ROLE`'s admin to `MINTER_ADMIN_ROLE` to separate the "who mints" from "who appoints minters."
- `renounce_role` requires `a == caller` so a compromised admin cannot use it to remove honest operators.
- The `only_role(r)` guard takes a parameter -- this is the idiomatic way to reuse one guard across many actions.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `grant_role` | ~48,000 |
| `revoke_role` | ~30,000 |
| `renounce_role` | ~28,000 |
| `has_role` (view) | ~3,000 |
| Guard check on action | ~2,500 |

## Common Pitfalls

1. **Single admin bootstrap**: If `deployer` is the only `ADMIN_ROLE` holder and loses their key, nobody can grant roles ever again. Always grant `ADMIN_ROLE` to at least a 2-of-3 multisig at deploy.
2. **Using `owner == caller` alongside RBAC**: Mixing the two models creates ambiguity. Pick RBAC and migrate legacy owner checks to `only_role(ADMIN_ROLE)`.
3. **Role id collisions**: Always compute ids with `keccak256("ROLE_NAME")` at compile time. Do not type them manually.
4. **Forgetting `set_role_admin`**: By default every role is gated by `ADMIN_ROLE`. If you want a more granular hierarchy, call `set_role_admin` during init.
5. **Renounce semantics**: OpenZeppelin changed renounce semantics in v5 to require self; match it here to avoid migration surprises.

## Variations

### Timelocked role grants

Wrap `grant_role` in a 48h timelock so a compromised admin cannot immediately appoint an attacker. Combine with [Time-Locked Admin](/docs/cookbook/auth/02-time-locked-admin).

### Enumerable roles

Add a `mapping<bytes32, address[]> members` alongside the bool map so UIs can list every holder. Push on grant, swap-and-pop on revoke.

## See Also

- [Multi-Sig Admin](/docs/cookbook/auth/01-multi-sig-admin)
- [Guardian Recovery](/docs/cookbook/auth/04-guardian-recovery)
- [Emergency Pause](/docs/cookbook/auth/06-emergency-pause)
