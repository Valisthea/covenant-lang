---
title: "12 — UUPS Upgradeable"
description: "Universal Upgradeable Proxy Standard pattern in Covenant."
order: 12
section: "Advanced"
---

# 12 — UUPS Upgradeable

UUPS (EIP-1822 / EIP-1967) places the upgrade logic in the implementation contract rather than the proxy. Covenant provides the `@upgradeable(uups)` decorator.

## Implementation contract

```covenant
@upgradeable(uups)
contract TokenV1 {
  field balances: Map<Address, u256>
  field total: u256

  action mint(to: Address, amount: u256) {
    only(owner);
    self.balances[to] += amount;
    self.total        += amount;
  }

  // Required by UUPS: upgrade logic lives here
  action upgrade_to(new_impl: Address) {
    only(owner);
    _upgrade(new_impl);   // built-in: validates ERC-1822, writes EIP-1967 slot
  }
}
```

## Proxy deployment

```bash
# Deploy implementation
covenant deploy TokenV1 --out impl.json

# Deploy ERC-1967 proxy pointing at the implementation
covenant deploy-proxy --impl $(cat impl.json | jq -r .address) --out proxy.json
```

All user interactions go through the proxy address. The proxy's storage holds the EIP-1967 slot and delegates all calls to the implementation.

## Upgrading

```bash
# Deploy new implementation
covenant deploy TokenV2 --out impl_v2.json

# Call upgrade_to through the proxy (owner wallet required)
covenant call $(cat proxy.json | jq -r .address) upgrade_to $(cat impl_v2.json | jq -r .address)
```

## Storage layout safety

Covenant enforces storage layout compatibility checks at compile time. If `TokenV2` reorders or removes fields from `TokenV1`, the compiler emits an error:

```
Error: storage layout incompatible with V1
  V1: field balances @ slot 0
  V2: field owners   @ slot 0   ← collision!
Hint: add new fields after existing ones, or use a layout gap.
```

Use a gap field to reserve space:

```covenant
@upgradeable(uups)
contract TokenV1 {
  field balances: Map<Address, u256>
  field total:    u256
  field _gap:     u256[48]   // 48 reserved slots for future fields
}
```

## Initialiser pattern

UUPS contracts cannot use Solidity-style constructors (proxy doesn't run them). Use the `init` block with an `initialised` guard:

```covenant
field initialised: Bool = false

action initialise(name: String) {
  require(!self.initialised, AlreadyInitialised);
  self.initialised = true;
  self.name = name;
}
```
