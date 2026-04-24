---
title: "06 — ERC-20 Token"
description: "A complete ERC-20 implementation in Covenant."
order: 6
section: "Standards"
---

# 06 — ERC-20 Token

A full ERC-20 compliant token in Covenant — about 60 lines of readable code.

```covenant
contract ERC20Token {
  field name:        String
  field symbol:      String
  field decimals:    u8    = 18
  field total_supply: u256

  field balances:   Map<Address, u256>
  field allowances: Map<Address, Map<Address, u256>>

  event Transfer(from: indexed Address, to: indexed Address, value: u256)
  event Approval(owner: indexed Address, spender: indexed Address, value: u256)

  error InsufficientBalance(available: u256, requested: u256)
  error InsufficientAllowance(available: u256, requested: u256)

  // Constructor-equivalent: init block runs once at deployment
  init(name: String, symbol: String, initial_supply: u256) {
    self.name   = name;
    self.symbol = symbol;
    self.total_supply = initial_supply;
    self.balances[msg.sender] = initial_supply;
    emit Transfer(from: Address(0), to: msg.sender, value: initial_supply);
  }

  @view action name()         -> String { return self.name; }
  @view action symbol()       -> String { return self.symbol; }
  @view action decimals()     -> u8     { return self.decimals; }
  @view action totalSupply()  -> u256   { return self.total_supply; }

  @view
  action balanceOf(account: Address) -> u256 {
    return self.balances[account];
  }

  action transfer(to: Address, amount: u256) -> Bool {
    _transfer(msg.sender, to, amount);
    return true;
  }

  action approve(spender: Address, amount: u256) -> Bool {
    self.allowances[msg.sender][spender] = amount;
    emit Approval(owner: msg.sender, spender: spender, value: amount);
    return true;
  }

  @view
  action allowance(owner: Address, spender: Address) -> u256 {
    return self.allowances[owner][spender];
  }

  action transferFrom(from: Address, to: Address, amount: u256) -> Bool {
    let allowed = self.allowances[from][msg.sender];
    require(allowed >= amount, InsufficientAllowance(allowed, amount));
    self.allowances[from][msg.sender] -= amount;
    _transfer(from, to, amount);
    return true;
  }

  // Internal helper — not exposed in ABI
  internal action _transfer(from: Address, to: Address, amount: u256) {
    let bal = self.balances[from];
    require(bal >= amount, InsufficientBalance(bal, amount));
    self.balances[from] -= amount;
    self.balances[to]   += amount;
    emit Transfer(from: from, to: to, value: amount);
  }
}
```

## Minting & burning extension

Add to the contract body:

```covenant
action mint(to: Address, amount: u256) {
  only(owner);
  self.total_supply     += amount;
  self.balances[to]     += amount;
  emit Transfer(from: Address(0), to: to, value: amount);
}

action burn(amount: u256) {
  let bal = self.balances[msg.sender];
  require(bal >= amount, InsufficientBalance(bal, amount));
  self.balances[msg.sender] -= amount;
  self.total_supply         -= amount;
  emit Transfer(from: msg.sender, to: Address(0), value: amount);
}
```
