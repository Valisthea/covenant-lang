---
title: "13 — Beacon Proxy"
description: "One-to-many upgrades with ERC-1967 Beacon Proxy in Covenant."
order: 13
section: "Advanced"
---

# 13 — Beacon Proxy

The Beacon Proxy pattern (EIP-1967) lets you upgrade **many proxy instances** by pointing a single beacon contract to a new implementation. This is ideal for factory-deployed contracts (e.g. per-user vaults, per-pool AMM pairs).

## Architecture

```
 ┌──────────────┐     points to     ┌─────────────────┐
 │  Beacon      │ ──────────────►   │  Implementation  │
 │  (upgradeable│                   │  (logic contract)│
 │   by owner)  │                   └─────────────────┘
 └──────────────┘
        ▲ reads implementation()
        │
 ┌──────┴──────┐  ┌─────────────┐  ┌─────────────┐
 │ BeaconProxy │  │ BeaconProxy │  │ BeaconProxy │  ...
 │  (instance) │  │  (instance) │  │  (instance) │
 └─────────────┘  └─────────────┘  └─────────────┘
```

## Beacon contract

```covenant
contract VaultBeacon {
  field implementation: Address

  init(impl: Address) {
    self.implementation = impl;
  }

  @view
  action get_implementation() -> Address {
    return self.implementation;
  }

  action upgrade(new_impl: Address) {
    only(owner);
    self.implementation = new_impl;
    emit Upgraded(new_impl);
  }
}
```

## Implementation contract

```covenant
@upgradeable(beacon)
contract UserVault {
  field balance: u256

  action deposit() {
    self.balance += msg.value;
  }

  @nonreentrant
  action withdraw(amount: u256) {
    require(self.balance >= amount, InsufficientBalance);
    self.balance -= amount;
    transfer_eth(msg.sender, amount);
  }
}
```

## Factory pattern

```covenant
contract VaultFactory {
  field beacon:  Address
  field vaults:  Map<Address, Address>

  init(beacon: Address) {
    self.beacon = beacon;
  }

  action create_vault() -> Address {
    require(self.vaults[msg.sender] == Address(0), AlreadyHasVault);
    // Deploy a new BeaconProxy pointing at self.beacon
    let proxy = deploy_beacon_proxy(self.beacon);
    self.vaults[msg.sender] = proxy;
    emit VaultCreated(msg.sender, proxy);
    return proxy;
  }
}
```

## Upgrading all vaults

Because all proxies query the same beacon, upgrading is a single call:

```bash
covenant deploy UserVaultV2 --out impl_v2.json
covenant call $BEACON_ADDR upgrade $(cat impl_v2.json | jq -r .address)
```

All existing proxies immediately delegate to `UserVaultV2` — zero per-proxy transactions needed.

## When to use Beacon vs UUPS

| Use case | Recommended pattern |
|----------|-------------------|
| Single upgradeable contract | UUPS |
| Many identical contract instances | Beacon |
| Contracts that need independent upgrade schedules | UUPS per contract |
| Factory-deployed per-user contracts | Beacon |
