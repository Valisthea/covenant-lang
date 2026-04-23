#!/usr/bin/env python3
"""Write all 15 example docs + 3 getting-started + 4 security + 1 glossary files."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE, "src", "content", "docs")
GS_DIR   = os.path.join(BASE, "src", "content", "getting-started")
SEC_DIR  = os.path.join(BASE, "src", "content", "security")
GL_DIR   = os.path.join(BASE, "src", "content", "glossary")

for d in [DOCS_DIR, GS_DIR, SEC_DIR, GL_DIR]:
    os.makedirs(d, exist_ok=True)

def w(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  {os.path.basename(path)}")

print("Writing getting-started...")
w(os.path.join(GS_DIR, "01-install.md"), """\
---
title: "Installation"
description: "Install the Covenant CLI and VS Code extension."
order: 1
---

# Installation

## Prerequisites

- **Rust** 1.75 or later — install via [rustup.rs](https://rustup.rs)
- **Cargo** (bundled with Rust)

## Install the CLI

```bash
cargo install covenant-cli
covenant --version
# covenant 0.7.0
```

## VS Code Extension

1. Open Extensions (`Ctrl+Shift+X`)
2. Search **"Covenant"**
3. Install extension by *Kairos Lab*

Provides: syntax highlighting, 38+ real-time lint diagnostics, auto-complete, hover docs, go-to-definition.
Works on Windows, macOS, Linux, and VS Code for the Web.

## Update

```bash
cargo install covenant-cli --force
```

## Next

[02 — First Contract](/getting-started/02-first-contract)
""")

w(os.path.join(GS_DIR, "02-first-contract.md"), """\
---
title: "First Contract"
description: "Create, compile, and test your first Covenant contract."
order: 2
---

# First Contract

## Create a project

```bash
covenant new my-contract
cd my-contract
```

## The source (`src/main.cov`)

```covenant
contract Counter {
  field count: U256 = 0
  field owner: Address

  event Incremented(new_value: U256)

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
  }

  @view action get_count() -> U256 {
    self.count
  }
}
```

## Build, test, lint

```bash
covenant build
# target/counter.artifact  (1,204 bytes)
# target/counter.abi.json

covenant test
# Passed: 4 / 4

covenant lint
# No issues — 38 detectors run
```

## Use with ethers.js

```js
import { ethers } from 'ethers';
import abi from './target/counter.abi.json';

const contract = new ethers.Contract(address, abi, signer);
await contract.increment();
const count = await contract.get_count();
```

## Next

[03 — CLI Reference](/getting-started/03-cli-reference)
""")

w(os.path.join(GS_DIR, "03-cli-reference.md"), """\
---
title: "CLI Reference"
description: "Complete reference for the covenant command-line interface."
order: 3
---

# CLI Reference

All commands: `covenant <command> [options] [args]`

## Commands

| Command | Description |
|---------|-------------|
| `covenant new <name>` | Create a new project |
| `covenant build [file]` | Compile to EVM bytecode |
| `covenant test` | Run test suite |
| `covenant lint` | Run 38+ static analysis detectors |
| `covenant deploy <artifact>` | Deploy to network |
| `covenant call <addr> <action>` | Call a view action |
| `covenant send <addr> <action>` | Send a transaction |
| `covenant verify <addr>` | Verify source on Etherscan |
| `covenant upgrade-check <v1> <v2>` | Check storage layout compatibility |
| `covenant zk prove` | Generate ZK proof off-chain |

## `covenant build` flags

```bash
covenant build [source.cov] [--target evm|aster|wasm] [--optimize] [--strict] [--emit-ir]
```

## `covenant.toml`

```toml
[project]
name    = "my-contract"
version = "0.1.0"

[compiler]
target   = "evm"
optimize = true
strict   = false

[networks.sepolia]
rpc_url  = "https://rpc.sepolia.org"
chain_id = 11155111
explorer = "https://sepolia.etherscan.io"

[networks.aster]
rpc_url  = "https://tapi.asterdex.com"
chain_id = 1996
explorer = "https://explorer.asterdex.com"

[deploy]
private_key_env = "DEPLOYER_PRIVATE_KEY"
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Compile error |
| 2 | Test failure |
| 3 | Lint error (`--strict`) |
| 4 | Deploy failure |
| 5 | Upgrade storage collision |
""")

print("Writing docs examples...")

examples = {
"01-hello-contract.md": """\
---
title: "01 — Hello Contract"
description: "Your first Covenant contract: structure, fields, and a simple action."
order: 1
section: "Fundamentals"
---

# 01 — Hello Contract

Every Covenant contract begins with the `contract` keyword.

```covenant
contract HelloWorld {
  field greeting: String = "hello, world"
  field owner: Address

  event GreetingChanged(old: String, new: String)

  action init(owner_addr: Address) {
    self.owner    = owner_addr
    self.greeting = "hello, world"
  }

  action set_greeting(msg: String) {
    only(self.owner)
    require(msg.len() > 0, "greeting cannot be empty")
    emit GreetingChanged(old: self.greeting, new: msg)
    self.greeting = msg
  }

  @view action get_greeting() -> String {
    self.greeting
  }
}
```

## Line-by-line

- **`field greeting: String`** — persistent storage. Survives across transactions.
- **`field owner: Address`** — 20-byte Ethereum address.
- **`event GreetingChanged`** — on-chain log entry.
- **`action init`** — constructor, called once at deployment.
- **`only(self.owner)`** — access guard: reverts if `msg.sender != self.owner`.
- **`require(...)`** — assertion that reverts on failure.
- **`emit GreetingChanged(...)`** — fires the event.
- **`@view action`** — read-only, no gas cost for direct EOA calls.

## Key concepts

| Covenant | Solidity |
|----------|----------|
| `field name: Type` | state variable |
| `action init(...)` | `constructor(...)` |
| `only(self.owner)` | `require(msg.sender == owner)` |
""",

"02-fields-and-storage.md": """\
---
title: "02 — Fields & Storage"
description: "Persistent storage types: primitives, maps, lists, and structs."
order: 2
section: "Fundamentals"
---

# 02 — Fields & Storage

`field` declarations persist across transactions and map to EVM storage slots.

```covenant
contract StorageDemo {
  field count:    U256  = 0
  field flag:     Bool  = false
  field owner:    Address
  field balances: Map<Address, U256>
  field members:  List<Address>

  struct Profile {
    name:   String
    score:  U256
    active: Bool
  }
  field profiles: Map<Address, Profile>

  action set_profile(name: String, score: U256) {
    self.profiles[msg.sender] = Profile {
      name: name, score: score, active: true,
    }
    if !self.members.contains(msg.sender) {
      self.members.push(msg.sender)
    }
  }

  action increment() { self.count += 1 }

  @view action get_profile(addr: Address) -> Profile {
    self.profiles[addr]
  }
}
```

## Storage types

| Type | Description |
|------|-------------|
| `U8`–`U256` | Unsigned integers (packed) |
| `Bool` | Boolean (bit-packed) |
| `Address` | 20-byte address |
| `String`, `Bytes` | Dynamic |
| `Map<K, V>` | Lazy key-value mapping |
| `List<T>` | Dynamic array |

## Key concepts

- **Fields vs locals** — `field` = storage (expensive), `let` = memory (cheap).
- **Maps** — missing key returns zero value, never reverts.
- **Lists** — out-of-range index reverts with `IndexOutOfBounds`.
""",

"03-actions-events-errors.md": """\
---
title: "03 — Actions, Events & Errors"
description: "Callable actions, structured events, and typed errors."
order: 3
section: "Fundamentals"
---

# 03 — Actions, Events & Errors

```covenant
contract Vault {
  field owner:   Address
  field balance: U256

  event Deposited(from: Address, amount: U256)
  event Withdrawn(to: Address, amount: U256)

  error InsufficientFunds(requested: U256, available: U256)
  error ZeroAmount()

  action init(owner_addr: Address) {
    self.owner = owner_addr
    self.balance = 0
  }

  action deposit(amount: U256) {
    require(amount > 0, ZeroAmount {})
    self.balance += amount
    emit Deposited(from: msg.sender, amount: amount)
  }

  action withdraw(amount: U256) {
    only(self.owner)
    if amount > self.balance {
      revert InsufficientFunds { requested: amount, available: self.balance }
    }
    self.balance -= amount
    emit Withdrawn(to: msg.sender, amount: amount)
  }

  @view action get_balance() -> U256 { self.balance }
}
```

## Action visibility

- **`@pure`** — no state reads or writes
- **`@view`** — reads state, no writes; no gas from EOA
- **`@payable`** — accepts ETH (`msg.value`)
- **`internal`** — not in ABI; not externally callable

## Events

```covenant
event Transfer(#[indexed] from: Address, #[indexed] to: Address, value: U256)
```

`#[indexed]` fields can be filtered in log queries.

## Typed errors

Compile to EVM custom errors (EIP-838) — less gas than string reverts.
""",

"04-guards.md": """\
---
title: "04 — Guards"
description: "Access control with only(), require(), and custom guards."
order: 4
section: "Fundamentals"
---

# 04 — Guards

Guards are compile-time-verified access control primitives. Tagged `#[side_effect = "access_control"]` — cannot be eliminated by optimization passes (audit fix KSR-CVN-011).

```covenant
contract MultiOwner {
  field owners: Map<Address, Bool>
  field paused: Bool

  error NotOwner(caller: Address)
  error ContractPaused()

  action init(initial_owners: List<Address>) {
    for addr in initial_owners { self.owners[addr] = true }
    self.paused = false
  }

  guard is_owner() {
    if !self.owners[msg.sender] {
      revert NotOwner { caller: msg.sender }
    }
  }

  guard not_paused() {
    if self.paused { revert ContractPaused {} }
  }

  action pause() {
    only(is_owner)
    self.paused = true
  }

  action sensitive_action(amount: U256) {
    only(is_owner)
    only(not_paused)
    require(amount > 0, "must be positive")
  }
}
```

## Guard types

| Guard | Behavior |
|-------|---------|
| `only(addr_field)` | Caller must equal stored address |
| `only(guard_fn)` | Calls named guard function |
| `require(cond, msg)` | Asserts condition |
| `require(cond, Error {})` | Asserts with typed error |

## Key concepts

- Guards stack — all checks before any state change.
- `only(addr)` compiles to: `CALLER` + `EQ` + `JUMPI`.
- LSP warns if an action touches sensitive storage without a guard.
""",

"05-external-calls.md": """\
---
title: "05 — External Calls"
description: "Calling other contracts safely: interfaces, CEI, and reentrancy."
order: 5
section: "Fundamentals"
---

# 05 — External Calls

Covenant enforces Checks-Effects-Interactions ordering by default and prevents reentrancy.

```covenant
interface IERC20 {
  action transfer(to: Address, amount: U256) -> Bool
  action balanceOf(owner: Address) -> U256
}

contract TokenSweeper {
  field owner:    Address
  field treasury: Address

  error TransferFailed(token: Address, amount: U256)
  event Swept(token: Address, amount: U256)

  action init(owner_addr: Address, treasury_addr: Address) {
    self.owner    = owner_addr
    self.treasury = treasury_addr
  }

  action sweep(token_addr: Address) {
    only(self.owner)
    let token  = IERC20 at token_addr
    let amount = token.balanceOf(address(self))
    require(amount > 0, "nothing to sweep")

    emit Swept(token: token_addr, amount: amount)  # Effect first

    let ok = token.transfer(self.treasury, amount)  # Interaction last
    if !ok { revert TransferFailed { token: token_addr, amount: amount } }
  }
}
```

## CEI pattern

1. **Checks** — `require`, `only`, guards
2. **Effects** — state mutations, `emit`
3. **Interactions** — external calls

Compiler warns (or errors in `--strict`) if an external call precedes state mutation.

## Reentrancy guard

```covenant
action flash_loan(amount: U256) @nonreentrant {
  # storage-slot mutex — blocks reentrant calls
}
```
""",

"06-erc20-token.md": """\
---
title: "06 — ERC-20 Token"
description: "A complete ERC-20 implementation in Covenant."
order: 6
section: "Standards"
---

# 06 — ERC-20 Token

Full ERC-20 with `internal action`, nested maps, and `Address::zero()`.

```covenant
contract CovenantToken {
  field name:         String = "Covenant Token"
  field symbol:       String = "CVT"
  field decimals:     U8     = 18
  field total_supply: U256   = 0
  field balances:     Map<Address, U256>
  field allowances:   Map<Address, Map<Address, U256>>
  field owner:        Address

  event Transfer(#[indexed] from: Address, #[indexed] to: Address, value: U256)
  event Approval(#[indexed] owner: Address, #[indexed] spender: Address, value: U256)

  error InsufficientBalance(have: U256, need: U256)
  error InsufficientAllowance(have: U256, need: U256)

  action init(owner_addr: Address, initial_supply: U256) {
    self.owner = owner_addr
    self._mint(owner_addr, initial_supply)
  }

  action transfer(to: Address, amount: U256) -> Bool {
    require(to != Address::zero(), "zero address")
    self._transfer(msg.sender, to, amount)
    true
  }

  action approve(spender: Address, amount: U256) -> Bool {
    self.allowances[msg.sender][spender] = amount
    emit Approval(owner: msg.sender, spender: spender, value: amount)
    true
  }

  action transfer_from(from: Address, to: Address, amount: U256) -> Bool {
    let allowed = self.allowances[from][msg.sender]
    if allowed < amount { revert InsufficientAllowance { have: allowed, need: amount } }
    self.allowances[from][msg.sender] -= amount
    self._transfer(from, to, amount)
    true
  }

  action mint(to: Address, amount: U256) {
    only(self.owner)
    self._mint(to, amount)
  }

  internal action _transfer(from: Address, to: Address, amount: U256) {
    let bal = self.balances[from]
    if bal < amount { revert InsufficientBalance { have: bal, need: amount } }
    self.balances[from] -= amount
    self.balances[to]   += amount
    emit Transfer(from: from, to: to, value: amount)
  }

  internal action _mint(to: Address, amount: U256) {
    self.balances[to] += amount
    self.total_supply  += amount
    emit Transfer(from: Address::zero(), to: to, value: amount)
  }

  @view action balance_of(owner: Address) -> U256 { self.balances[owner] }
  @view action total_supply() -> U256 { self.total_supply }
}
```

## Key concepts

- `internal action` — not in ABI; compiler enforces non-external access.
- Nested maps — `Map<Address, Map<Address, U256>>` for allowances.
- `Address::zero()` — null address constant.
- Mint/burn events use `Address::zero()` as from/to.
""",

"07-fhe-basics.md": """\
---
title: "07 — FHE Basics"
description: "encrypted<T>, fhe_add, fhe_mul, fhe_reveal as language primitives."
order: 7
section: "Standards"
---

# 07 — FHE Basics

Operate on encrypted values without decrypting them. FHE ops compile to `STATICCALL` to chain precompiles.

```covenant
contract EncryptedCounter {
  field owner: Address
  field count: encrypted<U64>

  event CountUpdated(new_count: encrypted<U64>)

  action init(owner_addr: Address) {
    self.owner = owner_addr
    self.count = fhe_encrypt(0_u64, owner_addr)
  }

  action increment(encrypted_one: encrypted<U64>) {
    self.count = fhe_add(self.count, encrypted_one)
    emit CountUpdated(new_count: self.count)
  }

  action reveal_count() -> U64 {
    only(self.owner)
    fhe_reveal(self.count)
  }

  @view action get_encrypted_count() -> encrypted<U64> { self.count }
}
```

## Precompile table

| Function | Address | Operation |
|---------|---------|-----------|
| `fhe_add` | `0x0300` | Homomorphic addition |
| `fhe_mul` | `0x0301` | Multiplication (widening) |
| `fhe_cmp` | `0x0302` | Encrypted equality |
| `fhe_reveal` | `0x0303` | Authorized decryption |
| `fhe_encrypt` | `0x0304` | Client-side encryption |
| `fhe_sub` | `0x0305` | Homomorphic subtraction |
| `fhe_cmp_gte` | `0x0306` | Encrypted >= comparison |
| `fhe_reveal_for` | `0x0307` | Address-targeted reveal |

## Scheme agnosticism

Covenant has zero dependency on any FHE library. Chains implement precompiles using TFHE (Apache 2.0), OpenFHE (BSD-2), SEAL (MIT), or Lattigo (Apache 2.0). See `LICENSE_CLARIFICATION.md`.

## Key concepts

- `encrypted<T>` — ciphertext on-chain; `fhe_reveal` produces plaintext.
- FHE ops are type-safe — mismatch = compile error.
- `fhe_mul` is widening: `fhe_mul<U64> -> encrypted<U128>` (audit fix KSR-CVN-038).
- `fhe_reveal` must be behind `only()` — LSP enforces this.
""",

"08-encrypted-token.md": """\
---
title: "08 — Encrypted Token"
description: "ERC-20-style token with FHE-encrypted balances."
order: 8
section: "Standards"
---

# 08 — Encrypted Token

Balances stored as `encrypted<U256>`. No observer including validators can learn balances or transfer amounts.

```covenant
contract EncryptedToken {
  field name:     String = "Encrypted CVT"
  field symbol:   String = "eCVT"
  field decimals: U8     = 18
  field owner:    Address
  field balances: Map<Address, encrypted<U256>>

  event Transfer(#[indexed] from: Address, #[indexed] to: Address)

  action init(owner_addr: Address, initial_supply_enc: encrypted<U256>) {
    self.owner = owner_addr
    self.balances[owner_addr] = initial_supply_enc
  }

  action transfer(to: Address, enc_amount: encrypted<U256>) {
    let new_from     = fhe_sub(self.balances[msg.sender], enc_amount)
    let non_negative = fhe_cmp_gte(new_from, fhe_encrypt(0_u256, msg.sender))
    zk_verify(non_negative, "balance_non_negative")

    self.balances[msg.sender] = new_from
    self.balances[to]         = fhe_add(self.balances[to], enc_amount)
    emit Transfer(from: msg.sender, to: to)
  }

  action mint(to: Address, enc_amount: encrypted<U256>) {
    only(self.owner)
    self.balances[to] = fhe_add(self.balances[to], enc_amount)
  }

  action reveal_balance(account: Address) -> U256 {
    only(self.owner)
    fhe_reveal(self.balances[account])
  }

  action reveal_my_balance() -> U256 {
    fhe_reveal_for(self.balances[msg.sender], msg.sender)
  }
}
```

## ZK + FHE composition

`zk_verify(non_negative, ...)` proves the encrypted balance is non-negative **without revealing the balance**. FHE computes on ciphertext; ZK proves a property of that ciphertext.

## Key concepts

- Transfer amount is never revealed on-chain.
- `fhe_reveal_for(val, addr)` — only `addr` can learn the plaintext.
- `zk_verify` result is a regular `Bool` — composable with other expressions.
""",

"09-post-quantum-signatures.md": """\
---
title: "09 — Post-Quantum Signatures"
description: "@pq_signed decorator and Dilithium3 signature verification."
order: 9
section: "Standards"
---

# 09 — Post-Quantum Signatures

`@pq_signed` replaces ECDSA with NIST FIPS 204 post-quantum signatures. Default: Dilithium3.

```covenant
@pq_signed(scheme: "dilithium3")
contract QuantumSafeVault {
  field owner:     Address
  field pq_pubkey: Bytes
  field balance:   U256

  error InvalidSignature()
  error InsufficientFunds(have: U256, need: U256)

  action init(owner_addr: Address, pubkey: Bytes) {
    require(pubkey.len() == 1952, "invalid Dilithium3 key")
    self.owner     = owner_addr
    self.pq_pubkey = pubkey
    self.balance   = 0
  }

  @payable action deposit() {
    self.balance += msg.value
  }

  action withdraw(to: Address, amount: U256, message: Bytes, signature: Bytes) {
    let valid = pq_verify(
      pubkey: self.pq_pubkey, message: message,
      signature: signature, scheme: "dilithium3",
    )
    if !valid { revert InvalidSignature {} }
    if amount > self.balance {
      revert InsufficientFunds { have: self.balance, need: amount }
    }
    self.balance -= amount
    transfer_eth(to, amount)
  }
}
```

## Why post-quantum?

ECDSA is broken by Shor's algorithm on a quantum computer. Dilithium3 is lattice-based, NIST FIPS 204 (2024), quantum-resistant.

## Scheme table

| Scheme | Precompile | Pub key | Sig size |
|--------|-----------|---------|---------|
| Dilithium3 | `0x0400` | 1952 B | 3293 B |
| Falcon-512 | `0x0401` | 897 B | 666 B |

## Key concepts

- `@pq_signed` applies to all actions including `internal` (audit fix KSR-CVN-023).
- Validate key length in `init` to prevent uninitialized-key pitfall.
- V0.8: `@hybrid_signed` adds ECDSA + Dilithium3 for migration periods.
""",

"10-zero-knowledge-proofs.md": """\
---
title: "10 — Zero-Knowledge Proofs"
description: "zk_prove and zk_verify as first-class language primitives."
order: 10
section: "Standards"
---

# 10 — Zero-Knowledge Proofs

Prove statements about private data without revealing it. `zk_verify` is a language keyword.

```covenant
contract AgeVerifier {
  field owner:        Address
  field verifier_key: Bytes

  event AgeVerified(user: Address)
  error ProofInvalid()
  error VerifierNotSet()

  action init(owner_addr: Address) { self.owner = owner_addr }

  action set_verifier_key(vk: Bytes) {
    only(self.owner)
    self.verifier_key = vk
  }

  action prove_age(proof: Bytes, public_age_floor: U256) -> Bool {
    require(self.verifier_key.len() > 0, VerifierNotSet {})

    let statement = zk_statement {
      circuit:       "age_check_v1",
      public_inputs: [public_age_floor],
    }

    let valid = zk_verify(proof: proof, statement: statement, vk: self.verifier_key)
    if !valid { revert ProofInvalid {} }

    emit AgeVerified(user: msg.sender)
    true
  }
}
```

## Workflow

1. **Circuit** — defines what is proved.
2. **Off-chain proof** — `covenant zk prove --circuit age_check_v1 --private age=25 --public age_floor=18`.
3. **On-chain verify** — `zk_verify` dispatches to the precompile.

## Proof systems

| System | Precompile | Proof size | Setup |
|--------|-----------|-----------|-------|
| Groth16 | `0x0500` | ~200 B | Trusted setup |
| PLONK | `0x0501` | ~500 B | Universal SRS |
| Halo2 | `0x0502` | ~1 KB | Transparent |
""",

"11-cryptographic-amnesia.md": """\
---
title: "11 — Cryptographic Amnesia"
description: "Provable two-pass data erasure with amnesia {} blocks."
order: 11
section: "Advanced"
---

# 11 — Cryptographic Amnesia

`amnesia { }` performs provable two-pass erasure of storage fields, producing an on-chain Merkle proof that data no longer exists.

```covenant
contract SensitiveDataVault {
  field owner:       Address
  field secret_data: Bytes
  field data_hash:   Bytes32
  field committed:   Bool

  event DataCommitted(hash: Bytes32)
  event DataErased(proof: Bytes32)

  error AlreadyCommitted()
  error NothingToErase()

  action init(owner_addr: Address) {
    self.owner     = owner_addr
    self.committed = false
  }

  action commit(data: Bytes) {
    only(self.owner)
    require(!self.committed, AlreadyCommitted {})
    self.secret_data = data
    self.data_hash   = keccak256(data)
    self.committed   = true
    emit DataCommitted(hash: self.data_hash)
  }

  action erase() {
    only(self.owner)
    require(self.committed, NothingToErase {})
    amnesia { self.secret_data }
    self.committed = false
    emit DataErased(proof: erasure_proof())
  }

  @view action get_commitment() -> Bytes32 { self.data_hash }
}
```

## How it works

1. **Random overwrite** — slot := `keccak256(blockhash || slot || nonce)`.
2. **Zero overwrite** — slot := `0x00...00`.
3. **Merkle proof** — precompile `0x0600` records a witness.

`erasure_proof()` returns a 32-byte commitment that anyone can verify independently.

> **Audit fix KSR-CVN-031** — V0.6 had single-pass (zero-only). V0.7 adds the mandatory random overwrite first pass.

## Use cases

GDPR-compliant PII deletion · Ephemeral voting (erase ballots post-tally) · Provable key rotation.
""",

"12-uups-upgradeable.md": """\
---
title: "12 — UUPS Upgradeable"
description: "Universal Upgradeable Proxy Standard pattern in Covenant."
order: 12
section: "Advanced"
---

# 12 — UUPS Upgradeable

`@upgradeable(uups)` generates a UUPS proxy. Upgrade authorization lives in the implementation contract.

```covenant
@upgradeable(uups)
contract UpgradeableToken {
  field name:         String = "Upgradeable Token"
  field symbol:       String = "UPT"
  field decimals:     U8     = 18
  field total_supply: U256   = 0
  field balances:     Map<Address, U256>
  field admin:        Address
  field __gap:        [U256; 50]

  event Upgraded(new_impl: Address)
  error ZeroAddress()

  action init(admin_addr: Address, initial_supply: U256) {
    require(admin_addr != Address::zero(), ZeroAddress {})
    self.admin = admin_addr
    self.balances[admin_addr] = initial_supply
    self.total_supply          = initial_supply
  }

  action authorize_upgrade(new_impl: Address) {
    only(self.admin)
    require(new_impl != Address::zero(), ZeroAddress {})
    emit Upgraded(new_impl: new_impl)
  }

  action transfer(to: Address, amount: U256) -> Bool {
    require(to != Address::zero(), ZeroAddress {})
    require(self.balances[msg.sender] >= amount, "insufficient")
    self.balances[msg.sender] -= amount
    self.balances[to]         += amount
    true
  }

  @view action balance_of(addr: Address) -> U256 { self.balances[addr] }
}
```

## Upgrade workflow

```bash
covenant build token-v2.cov
covenant upgrade-check v1.artifact v2.artifact
covenant deploy v2.artifact --network sepolia
covenant send PROXY_ADDR authorize_upgrade NEW_IMPL --network sepolia
```

## Key concepts

- Never reorder fields — storage slots are position-based.
- Add new fields at the end only (or use `__gap`).
- `authorize_upgrade` must be guarded — LSP warns if unguarded.
""",

"13-beacon-proxy.md": """\
---
title: "13 — Beacon Proxy"
description: "Upgrade many contracts at once with the beacon proxy pattern."
order: 13
section: "Advanced"
---

# 13 — Beacon Proxy

One beacon contract points all proxies to the same implementation. One `upgrade()` updates all proxies.

```covenant
contract ImplementationBeacon {
  field admin: Address
  field impl:  Address

  event Upgraded(old_impl: Address, new_impl: Address)

  action init(admin_addr: Address, initial_impl: Address) {
    self.admin = admin_addr
    self.impl  = initial_impl
  }

  action upgrade(new_impl: Address) {
    only(self.admin)
    emit Upgraded(old_impl: self.impl, new_impl: new_impl)
    self.impl = new_impl
  }

  @view action get_implementation() -> Address { self.impl }
}

@upgradeable(beacon)
contract TokenFactory {
  field admin:  Address
  field beacon: Address
  field tokens: Map<Address, Address>

  event TokenCreated(owner: Address, proxy: Address)

  action init(admin_addr: Address, beacon_addr: Address) {
    self.admin  = admin_addr
    self.beacon = beacon_addr
  }

  action create_token(name: String, symbol: String) {
    require(self.tokens[msg.sender] == Address::zero(), "already exists")
    let proxy = deploy_beacon_proxy(
      beacon: self.beacon,
      init_calldata: encode_call("init", [msg.sender, name, symbol]),
    )
    self.tokens[msg.sender] = proxy
    emit TokenCreated(owner: msg.sender, proxy: proxy)
  }

  @view action get_token(owner: Address) -> Address { self.tokens[owner] }
}
```

## Beacon vs UUPS

| | UUPS | Beacon |
|-|------|--------|
| Upgrade scope | One proxy | All proxies |
| Gas | Per-proxy | One tx |
| Best for | Singletons | Factories |
""",

"14-oracle-integration.md": """\
---
title: "14 — Oracle Integration"
description: "Price feeds with typed interfaces and staleness validation."
order: 14
section: "Advanced"
---

# 14 — Oracle Integration

```covenant
interface IChainlinkAggregator {
  @view action latestRoundData() -> (roundId: U80, answer: I256, startedAt: U256, updatedAt: U256, answeredInRound: U80)
  @view action decimals() -> U8
}

contract PriceFeedConsumer {
  field owner:         Address
  field eth_feed:      Address
  field max_staleness: U256

  struct Price { value: U256, decimals: U8, updated_at: U256 }

  error StalePrice(age: U256, max: U256)
  error NegativePrice(raw: I256)
  error OracleNotSet()

  action init(owner_addr: Address, feed_addr: Address) {
    self.owner        = owner_addr
    self.eth_feed     = feed_addr
    self.max_staleness = 3600
  }

  @view action get_eth_price() -> Price {
    require(self.eth_feed != Address::zero(), OracleNotSet {})
    let feed = IChainlinkAggregator at self.eth_feed
    let (_, answer, _, updated_at, _) = feed.latestRoundData()

    if answer < 0 { revert NegativePrice { raw: answer } }
    let age = block.timestamp - updated_at
    if age > self.max_staleness { revert StalePrice { age: age, max: self.max_staleness } }

    Price { value: answer as U256, decimals: feed.decimals(), updated_at: updated_at }
  }
}
```

## Security checklist

| Check | Pattern |
|-------|---------|
| Staleness | `block.timestamp - updatedAt <= maxStaleness` |
| Negative price | `if answer < 0 { revert }` |
| Zero address | `require(feed != Address::zero())` |
| Round completeness | `require(answeredInRound >= roundId)` |

## Aster Chain oracle

```covenant
@view action get_price(symbol: String) -> U256 {
  aster_oracle_price(symbol)  # STATICCALL -> precompile 0x0700
}
```
""",

"15-deploy-to-sepolia.md": """\
---
title: "15 — Deploy to Sepolia"
description: "End-to-end: compile, test, deploy to Ethereum Sepolia testnet."
order: 15
section: "Advanced"
---

# 15 — Deploy to Sepolia

Complete workflow: compile → test → lint → deploy → verify.

## 1. Install

```bash
cargo install covenant-cli
covenant --version  # covenant 0.7.0
```

## 2–4. Build, test, lint

```bash
covenant build quantum-vault.cov --target evm
# Compiled  quantum-vault.artifact  (4,821 bytes)

covenant test quantum-vault.cov
# Passed: 5 / 5

covenant lint quantum-vault.cov
# No issues — 38 detectors run
```

## 5. Configure `covenant.toml`

```toml
[networks.sepolia]
rpc_url    = "https://rpc.sepolia.org"
chain_id   = 11155111
explorer   = "https://sepolia.etherscan.io"

[deploy]
private_key_env = "DEPLOYER_PRIVATE_KEY"
```

```bash
export DEPLOYER_PRIVATE_KEY="0x..."
```

## 6. Deploy

```bash
covenant deploy quantum-vault.artifact \\
  --network sepolia \\
  --constructor-args "0xYOUR_ADDR" "0xDILITHIUM3_PUBKEY"

# Contract: 0xdef456...   Gas: 312,500
# https://sepolia.etherscan.io/address/0xdef456
```

## 7. Verify

```bash
covenant verify 0xdef456 \\
  --network sepolia \\
  --source quantum-vault.cov \\
  --compiler-version 0.7.0
# Status: Verified
```

## 8. Interact

```bash
covenant call 0xdef456 get_balance --network sepolia
covenant send 0xdef456 deposit --value 0.01eth --network sepolia
```

## Congratulations — all 15 chapters complete!

**[Security section](/security/audit-report)** · **[Glossary](/glossary)**
""",
}

for filename, content in examples.items():
    w(os.path.join(DOCS_DIR, filename), content)

print("Writing security pages...")

w(os.path.join(SEC_DIR, "audit-report.md"), """\
---
title: "OMEGA V4 Audit Report"
description: "Full audit report for Covenant V0.7.0 — 41 findings, 5 Critical, all resolved."
order: 1
---

# OMEGA V4 Audit Report

Covenant V0.7.0 was audited by OMEGA V4 before public release. The audit targeted the compiler itself — not just contracts. 41 findings were identified. All are resolved in V0.7 GA.

## Summary

| Severity | Count | Resolved |
|----------|-------|---------|
| Critical | 5 | 5 |
| High | 8 | 8 |
| Medium | 14 | 14 |
| Low | 9 | 9 |
| Informational | 5 | 5 |
| **Total** | **41** | **41** |

## Scope

All 19 workspace crates: `covenant-parser`, `covenant-ir`, `covenant-codegen`, `covenant-optimizer`, `covenant-lsp`, `covenant-cli`, `covenant-stdlib`.

Focus areas:
1. Compiler correctness — does bytecode faithfully execute source semantics?
2. Guard preservation — are access guards preserved through optimization?
3. FHE type safety — are `encrypted<T>` values never accidentally revealed?
4. PQ signature enforcement — does `@pq_signed` apply to all protected actions?
5. Cryptographic amnesia — does `amnesia { }` produce correct two-pass erasure?

## Critical Findings

| ID | Title | Status |
|----|-------|--------|
| KSR-CVN-011 | `only(owner)` guards silently dropped in optimizer | Resolved |
| KSR-CVN-019 | FHE encrypted values leaked in dead-store pass | Resolved |
| KSR-CVN-023 | `@pq_signed` missing on `internal action` paths | Resolved |
| KSR-CVN-031 | `amnesia {}` single-pass erasure (no random overwrite) | Resolved |
| KSR-CVN-038 | Integer overflow in `fhe_mul` type width computation | Resolved |

See [Critical Findings](/security/critical-findings) for full write-ups.

## High Findings (summary)

| ID | Title | Status |
|----|-------|--------|
| KSR-CVN-004 | Reentrancy in `@delegatecall` context | Resolved |
| KSR-CVN-007 | `zk_verify` bypass when `vk` is zero-length | Resolved |
| KSR-CVN-012 | Uninitialized padding bytes in struct storage | Resolved |
| KSR-CVN-015 | `Map` default corrupted for `String` type | Resolved |
| KSR-CVN-022 | Beacon proxy init can be front-run | Resolved |
| KSR-CVN-027 | Oracle timestamp manipulation in 12-second window | Resolved |
| KSR-CVN-033 | LSP guard detector false negative on nested calls | Resolved |
| KSR-CVN-039 | WASM: `encrypted<T>` not zeroed after `fhe_reveal` | Resolved |

## Methodology

- **Fuzzing** — 72 hours coverage-guided fuzzing against compiler and runtime
- **Formal verification** — key IR passes verified against Coq specifications
- **Manual review** — line-by-line review of all codegen passes
- **Differential testing** — against a reference Solidity implementation for EVM equivalence

## Post-audit

Every critical/high finding has an associated regression test. Test suite grew from 312 to 550+ tests.

```bash
covenant test --suite regression
# Passed: 238 / 238
```

Full report: `github.com/Valisthea/covenant-audits`
""")

w(os.path.join(SEC_DIR, "critical-findings.md"), """\
---
title: "Critical Findings"
description: "Deep-dive on the 5 critical findings from the OMEGA V4 audit."
order: 2
---

# Critical Findings

Five critical severity findings from OMEGA V4. All resolved in V0.7 GA.

---

## KSR-CVN-011 — Guards Silently Dropped

**Severity**: Critical | **Component**: `covenant-optimizer` | **Status**: Resolved in V0.7.0-rc3

### Root cause

The IR dead-code elimination pass classified `only(owner)` calls as "pure side-effect-free" when the guard argument was an `Address` field. Guards were removed if the optimizer determined the guarded variable was "always true" in an optimized trace. **Every `only(owner)` guard compiled to zero bytes.**

### Impact

Any caller could invoke any `only(owner)`-guarded action on any pre-V0.7 contract. Full access control bypass.

### Resolution

1. Guard calls tagged `#[side_effect = "access_control"]` in the IR.
2. Dead-code pass never eliminates `access_control`-tagged nodes.
3. New mandatory `guard-preservation-check` pass runs after all optimizations.
4. LSP displays a warning if an action touches sensitive storage without a detectable guard.

---

## KSR-CVN-019 — FHE Value Leaked to Storage

**Severity**: Critical | **Component**: `covenant-optimizer` | **Status**: Resolved in V0.7.0-rc4

### Root cause

The dead-store pass eliminated storage writes for `encrypted<T>` assignments when the temporary variable was not read again in the same basic block. A subtler variant materialized intermediate plaintext values into memory accessible via `MLOAD`.

### Resolution

`encrypted<T>` assignments marked `#[side_effect = "fhe_store"]` — excluded from dead-store elimination. FHE temporaries zeroed immediately after use.

---

## KSR-CVN-023 — @pq_signed Missing on Internal Paths

**Severity**: Critical | **Component**: `covenant-codegen` | **Status**: Resolved in V0.7.0-rc4

### Root cause

`@pq_signed` was applied only to actions reachable from the external ABI selector dispatch. `internal action` functions were not in the dispatch table and received no PQ check. An attacker using a crafted `delegatecall` could bypass PQ verification entirely.

### Resolution

`@pq_signed` now applies recursively to all actions in a decorated contract, including `internal` ones.

---

## KSR-CVN-031 — Amnesia Single-Pass Erasure

**Severity**: Critical | **Component**: `covenant-codegen` | **Status**: Resolved in V0.7.0-rc5

### Root cause

`amnesia { }` was implemented as a single zero-overwrite. Archive nodes retain storage history — without the random overwrite pass, "erasure" was cosmetic.

### Resolution

Two-pass sequence:
1. Random overwrite: `keccak256(blockhash(block.number - 1) || slot || nonce)`.
2. Zero overwrite: `0x00...00`.

Precompile `0x0600` records a Merkle witness proving both passes executed.

---

## KSR-CVN-038 — FHE Multiply Type Width Overflow

**Severity**: Critical | **Component**: `covenant-ir` | **Status**: Resolved in V0.7.0-rc5

### Root cause

`fhe_mul(a: encrypted<U64>, b: encrypted<U64>)` should return `encrypted<U128>` (doubling width). The type inference pass returned `encrypted<U64>`, silently truncating the high bits. Incorrect computation results, no runtime error.

### Resolution

FHE multiplication uses widening semantics: `fhe_mul<T, T> -> encrypted<Widen<T>>`. `Widen<U64> = U128`, `Widen<U128> = U256`.
""")

w(os.path.join(SEC_DIR, "secure-patterns.md"), """\
---
title: "Secure Patterns"
description: "Recommended security patterns for Covenant smart contracts."
order: 3
---

# Secure Patterns

Patterns vetted during the OMEGA V4 audit. Use these as defaults.

## 1. Always guard admin actions

```covenant
# Bad — no guard
action set_fee(new_fee: U256) { self.fee = new_fee }

# Good — guarded
action set_fee(new_fee: U256) {
  only(self.owner)
  self.fee = new_fee
}
```

## 2. CEI ordering — always

```covenant
# Bad — external call before state update
action withdraw(amount: U256) {
  token.transfer(msg.sender, amount)
  self.balances[msg.sender] -= amount  # Too late — reentrancy possible
}

# Good — CEI
action withdraw(amount: U256) {
  require(self.balances[msg.sender] >= amount, "insufficient")
  self.balances[msg.sender] -= amount  # Effect first
  token.transfer(msg.sender, amount)   # Interaction last
}
```

## 3. Use typed errors

```covenant
# Bad
require(amount > 0, "amount must be positive")

# Good
error ZeroAmount()
require(amount > 0, ZeroAmount {})
```

## 4. Validate all external inputs

```covenant
action set_oracle(addr: Address) {
  only(self.owner)
  require(addr != Address::zero(), "zero address")
  self.oracle = addr
}
```

## 5. Guard FHE reveals

```covenant
# Bad — anyone can reveal
action reveal_balance(account: Address) -> U256 {
  fhe_reveal(self.balances[account])
}

# Good — owner only
action reveal_balance(account: Address) -> U256 {
  only(self.owner)
  fhe_reveal(self.balances[account])
}
```

## 6. Validate ZK verifier keys

```covenant
action verify_proof(proof: Bytes) -> Bool {
  require(self.vk.len() > 0, "verifier key not set")
  let ok = zk_verify(proof, self.statement, self.vk)
  require(ok, "invalid proof")
  true
}
```

## 7. Storage gaps in upgradeable contracts

```covenant
@upgradeable(uups)
contract MyContract {
  field owner:  Address
  field paused: Bool
  field __gap:  [U256; 50]  # Reserve 50 slots for future fields
}
```

## 8. Oracle staleness checks

```covenant
let age = block.timestamp - updated_at
require(age <= self.max_staleness, StalePrice { age: age })
```

## 9. Two-step ownership transfer

```covenant
field owner:         Address
field pending_owner: Address

action transfer_ownership(new_owner: Address) {
  only(self.owner)
  self.pending_owner = new_owner
}

action accept_ownership() {
  require(msg.sender == self.pending_owner, "not pending owner")
  self.owner         = self.pending_owner
  self.pending_owner = Address::zero()
}
```

## 10. @nonreentrant on flash-loan paths

```covenant
action flash_loan(amount: U256, callback: Address) @nonreentrant {
  let before = self.balance
  token.transfer(callback, amount)
  require(self.balance >= before + self.fee, "fee not paid")
}
```
""")

w(os.path.join(SEC_DIR, "known-pitfalls.md"), """\
---
title: "Known Pitfalls"
description: "Common mistakes and anti-patterns in Covenant smart contracts."
order: 4
---

# Known Pitfalls

Common mistakes with bad/good code examples and LSP detection status.

## 1. Map returns zero for missing keys

```covenant
# Pitfall — assumes missing key is an error
let score = self.scores[addr]  # Returns 0, not an error

# Fix — add existence check if needed
require(self.members[addr], "not a member")
let score = self.scores[addr]
```

**LSP**: Warning if Map access result is used without a membership guard.

## 2. U256 underflow

```covenant
# Pitfall
self.balance -= amount  # Wraps/panics on underflow

# Fix
require(self.balance >= amount, InsufficientFunds {})
self.balance -= amount
```

**LSP**: Warning on unchecked subtraction of `U256` fields.

## 3. Plaintext secrets

```covenant
field api_key: Bytes       # Pitfall — visible to anyone with a node
field api_key: encrypted<Bytes>  # Fix
```

**LSP**: Info hint if field named `secret`, `key`, `password` is not `encrypted<T>`.

## 4. Emitting events after external calls

```covenant
# Pitfall — reentrancy can skip the emit
action withdraw(amount: U256) {
  token.transfer(msg.sender, amount)
  emit Withdrawn(amount)  # Too late
}

# Fix — emit before external call
action withdraw(amount: U256) {
  emit Withdrawn(amount)
  token.transfer(msg.sender, amount)
}
```

## 5. block.timestamp for randomness

```covenant
# Pitfall — manipulable within ~12 seconds
let winner = block.timestamp % self.participants.len()

# Fix — use VRF or commit-reveal
let winner = vrf_random() % self.participants.len()
```

**LSP**: Error if `block.timestamp` used in modulo arithmetic.

## 6. Uninitialized pq_pubkey

```covenant
# Pitfall — pq_pubkey never set; all calls fail signature check
@pq_signed
contract BadPQ {
  field pq_pubkey: Bytes  # Never initialized!
}

# Fix — validate in init
action init(pk: Bytes) {
  require(pk.len() == 1952, "invalid Dilithium3 key size")
  self.pq_pubkey = pk
}
```

**LSP**: Error if `@pq_signed` contract's `init` does not assign `pq_pubkey`.

## 7. Proxy storage collision

```covenant
# V1 layout: owner=slot0, balance=slot1
# V2 BAD — new field inserted before existing:
field version: U8       # slot 0 — collides with owner!
field owner:   Address  # slot 1
```

**Detection**: `covenant upgrade-check v1.artifact v2.artifact`.

## 8. fhe_reveal in a loop

```covenant
# Expensive — 100 precompile calls
for addr in self.members {
  let bal = fhe_reveal(self.balances[addr])
}

# Better — batch reveal
let revealed = fhe_reveal_batch(self.members.map(|a| self.balances[a]))
```

## 9. Missing zk_verify after fhe_cmp

```covenant
# Pitfall — trusting encrypted<Bool> without ZK proof
let non_negative = fhe_cmp_gte(new_bal, fhe_encrypt(0))
# non_negative is encrypted<Bool> — we cannot trust it without verification

# Fix
zk_verify(non_negative, "balance_non_negative")
```

## 10. Missing __gap in upgradeable contracts

```covenant
# Pitfall — no way to add fields later without storage collision
@upgradeable(uups)
contract NoGap {
  field owner: Address
  # No __gap!
}

# Fix
field __gap: [U256; 50]
```
""")

print("Writing glossary...")
w(os.path.join(GL_DIR, "index.md"), """\
---
title: "Glossary"
description: "Complete reference for every Covenant keyword, type, primitive, and concept."
order: 1
---

# Glossary

Complete reference for every Covenant keyword, built-in type, decorator, cryptographic primitive, and compiler concept.

---

## Language Keywords

**`action`** — A callable function. Compiles to an EVM function selector. Analogous to Solidity's `function`.

**`amnesia`** — A block performing provable two-pass erasure: `amnesia { field1, field2 }`. Compiles to random overwrite then zero overwrite, with a Merkle erasure proof.

**`contract`** — Top-level declaration. Contains fields, actions, events, errors, and guards.

**`emit`** — Fires a declared event: `emit EventName(field: value)`.

**`error`** — Declares a typed revert reason: `error Name(field: Type)`. Compiles to EVM custom errors (EIP-838).

**`event`** — Declares a structured log entry. Fields annotated `#[indexed]` are indexed.

**`field`** — Declares persistent storage: `field name: Type = default`. Occupies EVM storage slots.

**`for`** — Loop over a `List<T>`: `for item in list { ... }`.

**`guard`** — A reusable access control function: `guard name() { ... }`. Called via `only(guard_name)`.

**`if`** — Conditional expression: `if cond { ... } else { ... }`. Expression-oriented — returns a value.

**`interface`** — Declares an external contract's ABI: `interface IName { action foo(...) }`. Used with `IName at address`.

**`internal`** — Visibility modifier for actions not callable externally: `internal action foo()`.

**`let`** — Declares a local variable in EVM memory: `let name = expr`.

**`only`** — Access guard: `only(self.owner)` reverts if `msg.sender != self.owner`. `only(guard_fn)` calls a named guard.

**`require`** — Asserts a condition: `require(cond, "message")` or `require(cond, ErrorName {})`.

**`revert`** — Reverts with a typed error: `revert ErrorName { field: value }`.

**`self`** — Reference to the current contract. `self.field_name` accesses storage.

**`struct`** — Defines a composite value type: `struct Name { field: Type, ... }`. Value types (copied, not referenced).

---

## Built-in Types

**`Address`** — 20-byte Ethereum address. `Address::zero()` is the null address.

**`Bool`** — Boolean: `true` or `false`. Bit-packed in storage.

**`Bytes`** — Dynamically sized raw bytes. Dynamic storage.

**`Bytes32`** — Fixed 32-byte value. Common for hashes and Merkle leaves.

**`I256`** — Signed 256-bit integer.

**`List<T>`** — Dynamic array: `push`, `[i]`, `len()`, `contains()`. Out-of-bounds reverts.

**`Map<K, V>`** — Key-value mapping. Missing key returns zero value (never reverts). Not iterable — use a `List<K>` to track keys.

**`String`** — UTF-8 string. Dynamic storage.

**`U8`, `U32`, `U64`, `U128`, `U256`** — Unsigned integers. Smaller types packed in storage. `U256` is the native EVM word.

**`encrypted<T>`** — FHE wrapper type. Values are ciphertext on-chain. Only `fhe_reveal` or `fhe_reveal_for` produces plaintext.

---

## Decorators

**`@delegatecall`** — Marks an action as delegatecall-compatible. Only in upgradeable contracts.

**`@hybrid_signed`** *(V0.8, upcoming)* — Applies both ECDSA and post-quantum signature checks. Transition mode.

**`@nonreentrant`** — Storage-slot mutex. Reverts if called while already executing.

**`@packed`** — On a struct. Pack fields as tightly as possible.

**`@payable`** — Allows an action to receive ETH (`msg.value`).

**`@pq_signed`** — Contract-level. Injects post-quantum signature verification into every action. Default: Dilithium3.

**`@pure`** — No state reads or writes. Evaluable off-chain.

**`@upgradeable(uups)`** — UUPS upgradeable proxy. Generates `authorize_upgrade` hook.

**`@upgradeable(transparent)`** — Transparent proxy. Admin-controlled upgrade via proxy.

**`@upgradeable(beacon)`** — Beacon proxy. Single beacon points all proxies to one implementation.

**`@view`** — Reads state, no writes. No gas cost for direct EOA calls.

---

## FHE Primitives

**`fhe_add(a, b)`** — Homomorphic addition. Precompile `0x0300`.

**`fhe_cmp(a, b)`** — Encrypted equality. Returns `encrypted<Bool>`. Precompile `0x0302`.

**`fhe_cmp_gte(a, b)`** — Encrypted `>=`. Returns `encrypted<Bool>`. Precompile `0x0306`.

**`fhe_encrypt(val, for_addr)`** — Client-side encryption helper. Precompile `0x0304`.

**`fhe_mul(a, b)`** — Homomorphic multiplication with widening: `fhe_mul<U64> -> encrypted<U128>`. Precompile `0x0301`.

**`fhe_reveal(ciphertext)`** — Decrypts `encrypted<T>`. Requires `only()` guard. Precompile `0x0303`.

**`fhe_reveal_batch(list)`** — Decrypts a list in one precompile call.

**`fhe_reveal_for(ciphertext, addr)`** — Decrypts only for `addr`. Precompile `0x0307`.

**`fhe_sub(a, b)`** — Homomorphic subtraction. Precompile `0x0305`.

---

## ZK Primitives

**`zk_prove(statement)`** — Generates a ZK proof off-chain. CLI: `covenant zk prove`.

**`zk_statement { circuit, public_inputs }`** — Declares the circuit ID and public inputs for verification.

**`zk_verify(proof, statement, vk)`** — On-chain ZK proof verification. Returns `Bool`. Dispatches to Groth16 (`0x0500`), PLONK (`0x0501`), or Halo2 (`0x0502`).

---

## Post-Quantum Primitives

**`pq_verify(pubkey, message, signature, scheme)`** — Verifies a post-quantum signature. Returns `Bool`.

**Dilithium3** — CRYSTALS-Dilithium level 3. NIST FIPS 204. Pub key: 1952 B. Sig: 3293 B. Precompile `0x0400`.

**Falcon-512** — NIST FIPS 206. Smaller signatures. Pub key: 897 B. Sig: 666 B. Precompile `0x0401`.

**SPHINCS+** — Hash-based post-quantum scheme. No lattice math. Stateless. Larger sigs (~8 KB).

---

## Cryptographic Primitives

**`amnesia { }`** — Two-pass provable erasure block. See `amnesia` keyword.

**`erasure_proof()`** — Available after `amnesia { }`. Returns 32-byte Merkle commitment. Precompile `0x0600`.

**`keccak256(data)`** — Built-in Keccak-256 hash. Returns `Bytes32`.

**`sha256(data)`** — Built-in SHA-256. Returns `Bytes32`. Precompile `0x02`.

---

## Global Variables

**`block.timestamp`** — Current block timestamp (Unix seconds). Manipulable by validators within ~12 seconds. Never use for randomness.

**`block.number`** — Current block number.

**`block.hash`** — Previous block hash.

**`msg.sender`** — Address of the direct caller.

**`msg.value`** — ETH sent with the current call (wei). Non-zero only in `@payable` actions.

**`tx.origin`** — Transaction originator. **Never use for authorization** — phishing vulnerable.

**`address(self)`** — This contract's own address.

---

## Compiler Concepts

**ABI** — External interface of a compiled contract. Covenant ABIs are Ethereum ABI spec-compatible.

**CEI (Checks-Effects-Interactions)** — Ordering rule enforced by default: checks → state mutations → external calls.

**Dead-code elimination** — Optimizer pass that removes unreachable code. Never eliminates `access_control`-tagged guards (audit fix KSR-CVN-011).

**Guard** — Access control function. Tagged at IR level; cannot be eliminated by optimization passes.

**IR (Intermediate Representation)** — Typed form between Covenant source and EVM bytecode. Inspect with `covenant build --emit-ir`.

**LSP (Language Server Protocol)** — Powers the VS Code extension. Real-time diagnostics, auto-complete, hover docs.

**Precompile** — Chain-native built-in at a fixed address. Covenant dispatches FHE, PQ, ZK, and amnesia ops to precompiles.

**Scheme-agnostic** — Covenant has no dependency on any specific FHE or PQ library. The chain implements the precompiles.

**Selector** — 4-byte function ID: `keccak256(name(types))[0:4]`. Identical to Ethereum's function selector.

**Storage slot** — 32-byte unit of EVM persistent storage.

---

## Security Concepts

**Reentrancy** — Attack where a malicious contract calls back during an external call. Mitigated by CEI and `@nonreentrant`.

**Front-running** — Attacker submits a tx with higher gas to execute first. Mitigated by commit-reveal patterns.

**Flash loan attack** — Uses flash loans to transiently manipulate protocol state. Mitigated by `@nonreentrant`.

**Storage collision** — Two contract versions map different fields to the same slot. Detected by `covenant upgrade-check`.

**Staleness** — Using oracle data that is too old. Check `block.timestamp - updatedAt <= maxStaleness`.

**Selector clash** — Two action signatures hash to the same 4-byte selector. Covenant compiler detects and rejects clashes.

---

## Aster Chain Specifics

**Chain ID 1996** — Aster Chain mainnet. Use `covenant build --target-chain aster`.

**FHE precompiles (Aster)** — Precompiles `0x0300–0x0308` implemented by Aster Foundation.

**PQ precompiles (Aster)** — Dilithium3 (`0x0400`), Falcon-512 (`0x0401`).

**ZK precompiles (Aster)** — Groth16 (`0x0500`), PLONK (`0x0501`), Halo2 (`0x0502`).

**PoSA** — Proof-of-Staked Authority. Aster Chain consensus.

**Privacy mode** — Account Privacy ON by default. Balances and positions hidden. Compatible with `encrypted<T>`.

**Viewer Pass** — Selective disclosure on Aster Chain. Share a pass to reveal data to a specific observer.

---

## Cryptographic Background

**CRYSTALS-Dilithium** — Lattice-based digital signature. NIST FIPS 204 (2024). Quantum-resistant.

**FHE (Fully Homomorphic Encryption)** — Encryption scheme allowing computation on ciphertext. Results stay encrypted until explicitly decrypted.

**Groth16** — Pairing-based ZK-SNARK. Small proofs (~200 B), fast verification. Requires trusted setup per circuit.

**Halo2** — ZK proof system by Zcash. No trusted setup. Transparent SRS.

**Lattice cryptography** — Based on hard lattice problems (LWE, RLWE). Basis for Dilithium, Falcon, Kyber. Quantum-resistant.

**PLONK** — Universal ZK-SNARK. Universal trusted setup (one per field, reusable). Larger proofs than Groth16 but more flexible.

**Shor's algorithm** — Quantum algorithm breaking RSA and ECDSA in polynomial time. Motivates post-quantum cryptography.

**TFHE** — Fast FHE over the Torus. Chillotti et al. (ASIACRYPT 2016). Reference scheme for Covenant's FHE semantic model.

**ZK-SNARK** — Zero-Knowledge Succinct Non-Interactive Argument of Knowledge. Short proof, fast verification.

**ZK-STARK** — Zero-Knowledge Scalable Transparent Argument of Knowledge. No trusted setup, post-quantum secure.
""")

print("\nAll files written successfully!")
print(f"  {len(examples)} example docs")
print(f"  3 getting-started pages")
print(f"  4 security pages")
print(f"  1 glossary")
