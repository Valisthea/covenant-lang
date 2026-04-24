---
title: "02 — Fields & Storage"
description: "Scalar fields, maps, lists, and storage layout in Covenant."
order: 2
section: "Fundamentals"
---

# 02 — Fields & Storage

Covenant maps every `field` declaration to one or more EVM storage slots. The compiler handles packing, hash-derived keys, and initialisation automatically.

## Scalar fields

```covenant
contract Scalars {
  field count:   u256   = 0
  field name:    String = ""
  field enabled: Bool   = true
  field owner:   Address
}
```

`Address` has no default — it is initialised to `msg.sender` at deployment automatically if omitted.

## Mappings

```covenant
contract Balances {
  field balances: Map<Address, u256>

  action balance_of(who: Address) -> u256 {
    return self.balances[who];
  }

  action credit(who: Address, amount: u256) {
    only(owner);
    self.balances[who] += amount;
  }
}
```

Maps compile to `keccak256(key . slot)` — identical to Solidity `mapping`.

## Nested maps

```covenant
field allowances: Map<Address, Map<Address, u256>>
```

Access: `self.allowances[owner][spender]`.

## Lists

```covenant
field voters: List<Address>
```

Lists expose `.push()`, `.len()`, and index access. They store length in slot N and elements at `keccak256(N) + i`.

## Storage packing

Fields smaller than 32 bytes are packed into a single slot when declared consecutively and their combined width ≤ 256 bits:

```covenant
field status: u8    // ─┐ packed into one slot
field flags:  u8    // ─┘
field value:  u256  //   next slot
```

## Initialisation order

Fields are initialised in declaration order at construction time. You may reference earlier fields:

```covenant
field cap:     u256 = 1_000_000
field minted:  u256 = 0
field remaining: u256 = self.cap   // legal — cap is already set
```
