---
title: "Common Patterns Translated"
description: "How OpenZeppelin-style Solidity patterns — ERC-20, Ownable, ReentrancyGuard, AccessControl, Pausable — become keyword-level primitives in Covenant."
section: migration
order: 4
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Common Patterns Translated

Most production Solidity is not written from scratch. It is assembled from OpenZeppelin mixins: `ERC20`, `Ownable`, `ReentrancyGuard`, `Pausable`, `AccessControl`. This page shows how each becomes a one-line primitive in Covenant — no imports, no inheritance chains, no storage-collision hazards during upgrades.

## ERC-20

A minimal OpenZeppelin-based ERC-20:

```solidity
// Solidity — ~30 lines of boilerplate even with OZ
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor(uint256 initial) ERC20("MyToken", "MTK") Ownable(msg.sender) {
        _mint(msg.sender, initial);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
```

The Covenant equivalent uses the `token` block, which pre-declares `balance_of`, `allowance`, `transfer`, `transfer_from`, `approve`, and the `Transfer` / `Approval` events:

```covenant
// Covenant — the whole contract
token MyToken {
    name     = "MyToken"
    symbol   = "MTK"
    decimals = 18

    deploy(initial: amount) {
        mint(caller, initial)
    }

    action mint(to: address, value: amount) requires only owner {
        _mint(to, value)
    }
}
```

The `token` block is not a library import — it's a language feature. The compiler emits the standard ABI so existing tooling (wallets, explorers, indexers) sees it as a normal ERC-20. You can still override any of the generated actions by declaring one with the same name.

## ReentrancyGuard → `@nonreentrant`

```solidity
// Solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract Vault is ReentrancyGuard {
    function withdraw() external nonReentrant {
        uint256 n = balances[msg.sender];
        balances[msg.sender] = 0;
        (bool ok,) = msg.sender.call{value: n}("");
        require(ok, "send fail");
    }
}
```

```covenant
// Covenant
contract Vault {
    @nonreentrant
    action withdraw() {
        let n = balances[caller]
        balances[caller] = 0
        transfer(caller, n) or revert_with SendFailed()
    }
}
```

`@nonreentrant` is a compiler-enforced decorator. The reentrancy slot is managed automatically — there is no `_reentrancyStatus` field to worry about during storage upgrades.

Additionally, any action that both (a) calls an external address and (b) mutates a money-typed field *after* the call will produce a compile-time warning regardless of whether `@nonreentrant` is present. Checks-Effects-Interactions is enforced, not just recommended.

## Ownable → `only owner`

```solidity
// Solidity
import "@openzeppelin/contracts/access/Ownable.sol";

contract Config is Ownable {
    uint256 public fee;
    constructor() Ownable(msg.sender) {}
    function setFee(uint256 f) external onlyOwner { fee = f; }
}
```

```covenant
// Covenant
contract Config {
    field owner: address
    field fee: u256

    deploy { owner = caller }

    action set_fee(f: u256) requires only owner { fee = f }
    action transfer_ownership(to: address) requires only owner { owner = to }
}
```

`only owner` is a shorthand guard that resolves to `caller == owner`. The compiler requires a field literally named `owner` of type `address` when you use it — otherwise it errors with a helpful message.

If you want two-step ownership transfer (the `Ownable2Step` pattern), there is an `@ownable(two_step)` decorator that generates the pending-owner field and `accept_ownership` action for you.

## AccessControl → `roles` + `only_role`

```solidity
// Solidity
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Game is AccessControl {
    bytes32 public constant MINTER = keccak256("MINTER");
    constructor() { _grantRole(DEFAULT_ADMIN_ROLE, msg.sender); }
    function mint(...) external onlyRole(MINTER) { ... }
}
```

```covenant
// Covenant
contract Game {
    field roles: mapping<bytes<32>, mapping<address, bool>>
    const MINTER: bytes<32> = keccak256("MINTER")
    const ADMIN: bytes<32>  = keccak256("ADMIN")

    deploy { roles[ADMIN][caller] = true }

    action grant(role: bytes<32>, to: address) requires only_role(ADMIN) {
        roles[role][to] = true
        emit RoleGranted(role, to, caller)
    }

    action mint(...) requires only_role(MINTER) { ... }
}
```

`only_role(R)` is built-in; the `roles` field name and shape are the convention it recognizes. If your project prefers a different layout, you can define a custom guard once and use it everywhere the same way.

## Pausable → `@pausable`

```solidity
// Solidity
import "@openzeppelin/contracts/utils/Pausable.sol";

contract Marketplace is Pausable, Ownable {
    function buy() external whenNotPaused { ... }
    function pause() external onlyOwner { _pause(); }
    function unpause() external onlyOwner { _unpause(); }
}
```

```covenant
// Covenant
@pausable
contract Marketplace {
    action buy() when_not_paused { ... }
    // pause() / unpause() / paused are generated by @pausable
    // and gated on `only owner` by default.
}
```

The `@pausable` decorator synthesizes:

- A `paused: bool` field.
- `pause()` and `unpause()` actions, gated on `only owner`.
- A `when_not_paused` guard available to actions.
- Matching `Paused` / `Unpaused` events.

If you want a different gate for pausing (say, a multisig role), pass it as a decorator argument: `@pausable(gate = only_role(PAUSER))`.

## Putting it together

Here is a contract that in Solidity would inherit four OpenZeppelin mixins:

```covenant
@pausable(gate = only_role(PAUSER))
@upgradeable
token StableCoin {
    name = "StableCoin"; symbol = "STBL"; decimals = 6

    field roles: mapping<bytes<32>, mapping<address, bool>>
    const MINTER: bytes<32> = keccak256("MINTER")
    const PAUSER: bytes<32> = keccak256("PAUSER")
    const ADMIN:  bytes<32> = keccak256("ADMIN")

    deploy { roles[ADMIN][caller] = true }

    @nonreentrant
    action mint(to: address, value: amount)
        requires only_role(MINTER), when_not_paused
    {
        _mint(to, value)
    }
}
```

Equivalent Solidity is typically 120–180 lines, three imports, and a lot of boilerplate constructors. The Covenant version is the full contract.

The takeaway is not "Covenant is shorter." The takeaway is that the things auditors look for — which role gated a state change, whether reentrancy was considered, whether pause was wired to the right actions — are visible at a glance on the action declaration line. The patterns stop being patterns and become annotations.
