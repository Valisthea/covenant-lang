---
title: "Diamond Storage Pattern"
description: "Isolate contract state into named storage slots for collision-free upgrades and facets."
section: cookbook
order: 3
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Diamond Storage Pattern

## Problem

I have multiple upgradeable modules (facets) sharing one proxy. Each facet needs its own isolated storage so adding or reordering fields in one module cannot corrupt another.

## Solution

```covenant
storage GovernanceStorage at 0xabc123 {
    field proposal_count: u256 = 0
    field proposals: mapping<u256, Proposal>
    field voting_delay: u64 = 1 days
}

storage TreasuryStorage at keccak256("covenant.storage.treasury") {
    field balance: amount = 0 tokens
    field receiver: address = address(0)
}

facet GovernanceFacet uses GovernanceStorage {
    event ProposalCreated(id: u256 indexed, proposer: address)

    error ZeroProposer()

    action propose(data: bytes) {
        given caller != address(0) or revert_with ZeroProposer()
        proposal_count = proposal_count + 1
        proposals[proposal_count] = Proposal { proposer: caller, data: data }
        emit ProposalCreated(proposal_count, caller)
    }
}

facet TreasuryFacet uses TreasuryStorage {
    event Deposited(amount: amount)

    action deposit(amount: amount) {
        balance = balance + amount
        emit Deposited(amount)
    }
}
```

## Explanation

- `storage Name at <slot>` declares a named storage region anchored to a deterministic slot
- The slot expression accepts a literal (`0xabc123`) or a compile-time call like `keccak256("...")`
- Each `facet` declares exactly one `uses StorageName` binding; field references in the facet body resolve through that binding
- The compiler emits an assembly `sstore(slot + offset, value)` for each field access, bypassing Solidity's sequential layout
- Two facets cannot share the same storage struct unless both declare `uses` the same name -- collisions are a compile error

This replaces Solidity's EIP-2535 boilerplate where developers hand-write:

```solidity
bytes32 constant STORAGE_SLOT = keccak256("covenant.storage.treasury");
function layout() internal pure returns (Layout storage l) {
    bytes32 slot = STORAGE_SLOT;
    assembly { l.slot := slot }
}
```

Covenant's `storage` block generates all of that from a single declarative line.

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| Field read (cold) | 2,100 |
| Field read (warm) | 100 |
| Field write (new) | 22,100 |
| Storage region init | ~3,000 |

Diamond storage imposes no runtime overhead versus sequential layout -- the slot is resolved at compile time.

## Common Pitfalls

1. **Slot collisions with literal addresses**: Using `at 0x...` with a human-chosen literal risks colliding with a future facet. Prefer `keccak256("covenant.storage.<module>")`.
2. **Renaming a storage region**: Renaming the string inside `keccak256(...)` changes the slot and strands all existing data. Treat storage names as permanent.
3. **Field insertion**: Unlike sequential layout, inserting a field in the middle of a `storage` block is safe because the compiler uses offsets within the region, but reordering still corrupts state. Only append.
4. **Cross-facet access**: A facet cannot reach into another facet's storage. If two modules need shared state, factor it into a third `storage` region both `uses`.
5. **Using `storage` in a non-upgradeable contract**: Legal, but overkill. Plain `field` declarations are cheaper to reason about unless you need upgrade isolation.

## Variations

### Shared read-only storage

```covenant
storage ConfigStorage at keccak256("covenant.storage.config") {
    field immutable chain_id: u256 = 1
    field immutable deployer: address
}

facet GovernanceFacet uses GovernanceStorage, ConfigStorage { /* ... */ }
facet TreasuryFacet uses TreasuryStorage, ConfigStorage { /* ... */ }
```

### Inline slot salt

```covenant
storage VaultStorage at keccak256("covenant.storage.vault.v1") {
    field balance: amount = 0 tokens
}
// v2 lives at keccak256("covenant.storage.vault.v2") -- fully isolated
```

## See Also

- [UUPS Upgradeable](/docs/cookbook/upgrades/01-uups-pattern)
- [Beacon Proxy Pattern](/docs/cookbook/upgrades/02-beacon-pattern)
- [Migration Scripts](/docs/cookbook/upgrades/04-migration-scripts)
