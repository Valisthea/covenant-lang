---
title: "02 — Fields & Storage"
description: "Scalar fields, maps, lists, and storage layout in Covenant."
order: 2
section: "Fundamentals"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


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
