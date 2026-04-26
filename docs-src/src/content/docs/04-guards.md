---
title: "04 — Guards"
description: "Built-in and custom guards for access control in Covenant."
order: 4
section: "Fundamentals"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


# 04 — Guards

Guards are boolean conditions that gate action execution. Covenant ships with three built-in guards and lets you define custom ones.

## Built-in guards

| Guard | Meaning |
|-------|---------|
| `only(owner)` | `msg.sender == owner()` |
| `only(self)` | Internal call from the contract itself |
| `only(role: ROLE_NAME)` | Caller holds `ROLE_NAME` in the built-in role registry |

```covenant
action pause() {
  only(owner);
  self.paused = true;
}
```

## Custom guards

Declare a `guard` block — it must evaluate to a `Bool`:

```covenant
guard is_member(addr: Address) -> Bool {
  return self.members[addr];
}

guard not_paused() -> Bool {
  return !self.paused;
}
```

Use them in actions with `only()`:

```covenant
action vote(proposal: u256) {
  only(is_member(msg.sender));
  only(not_paused());
  // ...
}
```

## Composing guards

Guards are ordinary boolean expressions — combine with `&&` and `||`:

```covenant
guard admin_or_operator(addr: Address) -> Bool {
  return self.admins[addr] || self.operators[addr];
}
```

## Role-based access control

```covenant
contract Vault {
  role MANAGER
  role AUDITOR

  action withdraw(amount: u256) {
    only(role: MANAGER);
    // ...
  }

  action read_balance() -> u256 {
    only(role: AUDITOR);
    return self.balance;
  }
}
```

Roles are managed via the built-in `grant_role(role, addr)` and `revoke_role(role, addr)` actions (owner-only by default).

## Guards as modifiers

If you declare a guard with `@before`, it runs automatically before every action in the contract:

```covenant
@before
guard check_not_paused() -> Bool {
  return !self.paused;
}
```
