---
title: "First Contract"
description: "Create, compile, and test your first Covenant contract."
order: 2
---

# First Contract

In under five minutes, you'll have a working Covenant contract compiled to EVM bytecode.

## Create a project

```bash
covenant new my-contract
cd my-contract
```

This creates:

```
my-contract/
├── covenant.toml        # Project config
├── src/
│   └── main.cov         # Your contract source
└── tests/
    └── main_test.cov    # Test file
```

## Open the source file

`src/main.cov` contains a minimal counter contract:

```covenant
contract Counter {
  field count: U256 = 0
  field owner: Address

  event Incremented(new_value: U256)
  event Reset()

  action init(owner_addr: Address) {
    self.owner = owner_addr
    self.count = 0
  }

  action increment() {
    self.count += 1
    emit Incremented(new_value: self.count)
  }

  action reset() {
    only(self.owner)
    self.count = 0
    emit Reset()
  }

  @view action get_count() -> U256 {
    self.count
  }
}
```

## Compile

```bash
covenant build
```

Output:

```
✓ Parsed    src/main.cov
✓ Type check passed
✓ Guard analysis: all actions guarded
✓ CEI ordering: verified
✓ Compiled  target/counter.artifact  (1,204 bytes)
✓ ABI       target/counter.abi.json
```

The `.artifact` file is EVM-compatible bytecode. The `.abi.json` is a standard Ethereum ABI for use with ethers.js, viem, or any other tooling.

## Run tests

```bash
covenant test
```

```
Test suite: counter
✓ test_init
✓ test_increment
✓ test_reset_by_owner
✓ test_reset_fails_for_non_owner
Passed: 4 / 4
```

## Run the linter

```bash
covenant lint
```

```
✓ No issues found
Detectors run: 38
Files analyzed: 1
```

## Explore the ABI

```bash
cat target/counter.abi.json
```

The ABI is standard Ethereum JSON ABI format — paste it directly into Etherscan, Remix, or use it with ethers.js:

```js
import { ethers } from 'ethers';
import abi from './target/counter.abi.json';

const contract = new ethers.Contract(address, abi, signer);
await contract.increment();
const count = await contract.get_count();
```

## Next

→ [03 — CLI Reference](/getting-started/03-cli-reference)
