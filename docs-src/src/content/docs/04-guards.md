---
title: "04 — Guards"
description: "Built-in and custom guards for access control in Covenant."
order: 4
section: "Fundamentals"
---

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
