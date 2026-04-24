---
title: "Porting Checklist"
description: "Step-by-step checklist for porting a Solidity contract to Covenant, with a full worked example: a staking contract in both languages."
section: migration
order: 6
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Porting Checklist

This page assumes you've read the previous five. You understand the syntax, the types, the pattern translations, and the tooling. Now you are staring at a real Solidity file and wondering where to start.

The checklist below is the order we recommend. It is written to be followed linearly the first time you port a contract; later ports will compress steps.

## The eight-step checklist

### 1. Translate state variables and events

Start with the data model. Do not think about logic yet. Walk top-to-bottom through the Solidity contract and write the equivalent `field` and `event` declarations. Replace `uint256`-holding-a-balance with `amount`. Replace `mapping` syntax. Replace `uint256`-holding-a-timestamp with `timestamp`.

If a field is set only in the constructor, mark it immutable by assigning it in the `deploy` block and never reassigning. The compiler will enforce this.

### 2. Convert functions into actions with explicit guards

For each function, write an empty `action` with the same name and parameters. Attach the guards it needs: `only owner`, `only_role(R)`, `@nonreentrant`, `when_not_paused`. Do not copy the body yet — just get the signatures and gating right.

This step alone often surfaces authorization gaps. If a Solidity function had no modifier but mutated state an external caller should not control, you will notice now because you have nothing to put on the `requires` line.

### 3. Replace `require` with `given`

Now walk each function body. Every `require(cond, "msg")` becomes `given cond or revert_with Err()`. Declare the error types at the top of the contract. Group related guards into a single `given { ... }` block where it reads better.

This is also the right time to delete defensive `require`s that the type system now handles for you — a non-zero address check against `address` parameters that the type narrows, or an overflow check against arithmetic that is already checked.

### 4. Map custom modifiers to `guard` blocks

Any project-specific modifier (e.g. `whenSaleOpen`, `onlyAfter(x)`) becomes a named `guard` block. Because guards are boolean predicates, not wrappers, the translation is usually two lines shorter than the Solidity modifier.

Parametrized modifiers become guards that take arguments: `guard after(t: timestamp) { now > t or revert_with TooEarly() }`.

### 5. Translate tests to `test {}` blocks

Copy each Foundry or Hardhat test into a `test "name" { ... }` block in the same file as the contract. Solidity tests that used `vm.prank(...)` become `impersonate(...) { ... }`. Tests that used `vm.warp(...)` become `warp(to: timestamp) { ... }`.

Fuzz tests (`testFuzz_*`) become `fuzz "name" (args) { ... }`. Invariant tests become `invariant "name" { ... }`.

### 6. Run `covenant audit`

Once the contract compiles and tests pass, run `covenant audit` and read every finding. Do not silence findings you do not understand. The auditor's output is less noisy than Slither's by design — a flagged issue usually reflects a real oversight in the port.

### 7. Compare gas estimates

`covenant bench` produces a gas snapshot per action. Run it and compare against the Solidity gas report from `forge snapshot` (or equivalent). Ports are usually cheaper because of cleaner storage packing and fewer dead branches — but a significant regression is a signal you may have introduced an accidentally hot loop or a redundant guard.

### 8. Diff storage layout for upgradeability

If the contract is upgradeable and you are preserving an existing deployment, run:

```bash
covenant migrate --reference path/to/previous-layout.json
```

This checks that the storage layout of your Covenant port is compatible with the prior Solidity layout — same slots, same types, no surprise reorderings. A mismatch here is a live upgrade hazard.

## Worked example: a staking contract

Here is a small-but-realistic Solidity staking contract (50 lines) and its Covenant port (about 30 lines). Neither is production-hardened — they exist to make the translation concrete.

### Solidity version

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract Staking is Ownable, ReentrancyGuard {
    IERC20 public immutable stakeToken;
    uint256 public rewardRate;             // rewards per sec per token staked
    mapping(address => uint256) public staked;
    mapping(address => uint256) public stakedAt;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount, uint256 reward);

    error ZeroAmount();
    error NothingStaked();

    constructor(address token, uint256 rate) Ownable(msg.sender) {
        stakeToken = IERC20(token);
        rewardRate = rate;
    }

    function setRate(uint256 rate) external onlyOwner { rewardRate = rate; }

    function stake(uint256 amount) external nonReentrant {
        if (amount == 0) revert ZeroAmount();
        require(stakeToken.transferFrom(msg.sender, address(this), amount), "xfer");
        staked[msg.sender] += amount;
        stakedAt[msg.sender] = block.timestamp;
        emit Staked(msg.sender, amount);
    }

    function unstake() external nonReentrant {
        uint256 n = staked[msg.sender];
        if (n == 0) revert NothingStaked();
        uint256 dt = block.timestamp - stakedAt[msg.sender];
        uint256 reward = n * rewardRate * dt;
        staked[msg.sender] = 0;
        stakedAt[msg.sender] = 0;
        require(stakeToken.transfer(msg.sender, n + reward), "xfer");
        emit Unstaked(msg.sender, n, reward);
    }
}
```

### Covenant port

```covenant
// staking.cov
contract Staking {
    field stake_token: address           // immutable after deploy
    field reward_rate: u256              // rewards per sec per token
    field staked:      mapping<address, amount>
    field staked_at:   mapping<address, timestamp>
    field owner:       address

    event Staked(user: address indexed, value: amount)
    event Unstaked(user: address indexed, value: amount, reward: amount)

    error ZeroAmount()
    error NothingStaked()

    deploy(token: address, rate: u256) {
        stake_token = token
        reward_rate = rate
        owner       = caller
    }

    action set_rate(rate: u256) requires only owner { reward_rate = rate }

    @nonreentrant
    action stake(value: amount) {
        given value > 0 or revert_with ZeroAmount()
        erc20(stake_token).transfer_from(caller, self, value)
            or revert_with TransferFailed()
        staked[caller]    += value
        staked_at[caller]  = now
        emit Staked(caller, value)
    }

    @nonreentrant
    action unstake() {
        let n = staked[caller]
        given n > 0 or revert_with NothingStaked()
        let dt      = now - staked_at[caller]          // duration
        let reward  = n * reward_rate * dt.seconds     // amount
        staked[caller]    = 0
        staked_at[caller] = timestamp::zero
        erc20(stake_token).transfer(caller, n + reward)
            or revert_with TransferFailed()
        emit Unstaked(caller, n, reward)
    }

    test "stake then unstake returns principal + reward" {
        let alice = address(0xA11CE)
        deal(stake_token, alice, 100)
        impersonate(alice) { stake(100) }
        warp(now + 10.seconds)
        impersonate(alice) { unstake() }
        assert erc20(stake_token).balance_of(alice) >= 100
    }

    invariant "staked_at is zero iff staked is zero" {
        forall addr in touched_addresses:
            (staked[addr] == 0) == (staked_at[addr] == timestamp::zero)
    }
}
```

Things worth pointing at:

- **Ownable and ReentrancyGuard disappeared.** They are a field declaration and a decorator now.
- **`block.timestamp - stakedAt`** returned a `uint256` in Solidity, giving you no hint that it's a duration. In Covenant the subtraction returns `duration`, and the multiplication has a `.seconds` call to lower it back to a scalar — the compiler would have rejected the naive `n * reward_rate * dt` form.
- **`transferFrom` and `transfer`** return `Result` rather than `bool`. The `or revert_with` makes the failure branch explicit.
- **Tests and invariants live in the same file.** The invariant catches the class of bug where one of the two parallel maps gets out of sync.

Running the full loop:

```bash
covenant build
covenant test
covenant fuzz --runs 10000
covenant audit
covenant bench --diff previous.snap
```

If all five are green and clean, the port is done.

## When to stop

You will sometimes be tempted to introduce FHE, ZK, or multi-chain features "while you're in there." Resist that urge for the first port. Get a faithful translation running and audited first; layer on new capabilities as a follow-up change. Migrations that try to do two things at once are the migrations that stall.
