import os, pathlib

BASE = pathlib.Path("/tmp/covenant-lang/docs-src/src/content")
BT3 = chr(96)*3

FILES = {}

FILES["docs/01-hello-contract.md"] = f"""---
title: "01 — Hello Contract"
description: "Write and deploy your first Covenant contract."
order: 1
section: "Fundamentals"
---

# 01 — Hello Contract

The simplest possible Covenant contract — a greeting stored on-chain and exposed as a read action.

{BT3}covenant
contract HelloWorld {{
  /// Greeting stored on chain.
  field greeting: String = "hello, world"

  /// Read the greeting.
  action greet() -> String {{
    return self.greeting;
  }}

  /// Update the greeting (owner only).
  action set_greeting(msg: String) {{
    only(owner);
    self.greeting = msg;
  }}
}}
{BT3}

## What just happened?

| Concept | Explanation |
|---------|-------------|
| `contract` | Top-level declaration; compiles to a single EVM account |
| `field` | Persistent storage slot — initialised with the literal after `=` |
| `action` | Public entry point, maps to an ABI function |
| `only(owner)` | Built-in guard: reverts unless `msg.sender == owner()` |

## Build it

{BT3}bash
covenant new hello-world
cd hello-world
# Replace src/main.cov with the snippet above
covenant build      # emits hello-world.abi + hello-world.bin
covenant test       # runs the snapshot test suite
{BT3}

## Deploy to a local devnet

{BT3}bash
covenant devnet &           # starts Anvil-compatible devnet
covenant deploy --dev       # deploys to 0x0…01 with test key
{BT3}

The CLI prints the deployed address. Continue to **02 — Fields & Storage** to learn about all storage types.
"""

FILES["docs/02-fields-and-storage.md"] = f"""---
title: "02 — Fields & Storage"
description: "Scalar fields, maps, lists, and storage layout in Covenant."
order: 2
section: "Fundamentals"
---

# 02 — Fields & Storage

Covenant maps every `field` declaration to one or more EVM storage slots. The compiler handles packing, hash-derived keys, and initialisation automatically.

## Scalar fields

{BT3}covenant
contract Scalars {{
  field count:   u256   = 0
  field name:    String = ""
  field enabled: Bool   = true
  field owner:   Address
}}
{BT3}

`Address` has no default — it is initialised to `msg.sender` at deployment automatically if omitted.

## Mappings

{BT3}covenant
contract Balances {{
  field balances: Map<Address, u256>

  action balance_of(who: Address) -> u256 {{
    return self.balances[who];
  }}

  action credit(who: Address, amount: u256) {{
    only(owner);
    self.balances[who] += amount;
  }}
}}
{BT3}

Maps compile to `keccak256(key . slot)` — identical to Solidity `mapping`.

## Nested maps

{BT3}covenant
field allowances: Map<Address, Map<Address, u256>>
{BT3}

Access: `self.allowances[owner][spender]`.

## Lists

{BT3}covenant
field voters: List<Address>
{BT3}

Lists expose `.push()`, `.len()`, and index access. They store length in slot N and elements at `keccak256(N) + i`.

## Storage packing

Fields smaller than 32 bytes are packed into a single slot when declared consecutively and their combined width ≤ 256 bits:

{BT3}covenant
field status: u8    // ─┐ packed into one slot
field flags:  u8    // ─┘
field value:  u256  //   next slot
{BT3}

## Initialisation order

Fields are initialised in declaration order at construction time. You may reference earlier fields:

{BT3}covenant
field cap:     u256 = 1_000_000
field minted:  u256 = 0
field remaining: u256 = self.cap   // legal — cap is already set
{BT3}
"""

FILES["docs/03-actions-events-errors.md"] = f"""---
title: "03 — Actions, Events & Errors"
description: "Define entry points, emit structured logs, and declare typed errors."
order: 3
section: "Fundamentals"
---

# 03 — Actions, Events & Errors

## Actions

Actions are the public interface of a contract — analogous to Solidity functions with visibility `external`.

{BT3}covenant
contract Counter {{
  field n: u256 = 0

  action increment() {{
    self.n += 1;
    emit Incremented(self.n);
  }}

  action increment_by(amount: u256) {{
    require(amount > 0, InvalidAmount);
    self.n += amount;
    emit Incremented(self.n);
  }}

  action value() -> u256 {{
    return self.n;
  }}
}}
{BT3}

**Read vs write:** actions that only read state should be annotated `@view`:

{BT3}covenant
@view
action value() -> u256 {{ return self.n; }}
{BT3}

The compiler enforces that `@view` actions contain no state mutations.

## Events

{BT3}covenant
event Incremented(new_value: u256)
event Transfer(from: indexed Address, to: indexed Address, amount: u256)
{BT3}

`indexed` fields become Bloom-filter topics (up to 3 per event, same as Solidity). The ABI encoder emits them as `event Transfer(address indexed from, address indexed to, uint256 amount)`.

Emit syntax:

{BT3}covenant
emit Transfer(from: sender, to: recipient, amount: value);
{BT3}

## Errors

Typed errors revert with ABI-encoded data:

{BT3}covenant
error InvalidAmount(provided: u256)
error Unauthorised(caller: Address)
error InsufficientBalance(available: u256, requested: u256)
{BT3}

Revert with an error:

{BT3}covenant
require(amount > 0, InvalidAmount(amount));
// or imperatively:
if self.balances[caller] < amount {{
  revert InsufficientBalance(self.balances[caller], amount);
}}
{BT3}

## `require` vs `revert`

| Keyword | Behaviour |
|---------|-----------|
| `require(cond, Err)` | Reverts with `Err` if `cond` is false |
| `revert Err(..args)` | Unconditionally reverts |
| `assert(cond)` | Reverts with `Panic(0x01)` — use for invariants only |
"""

FILES["docs/04-guards.md"] = f"""---
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

{BT3}covenant
action pause() {{
  only(owner);
  self.paused = true;
}}
{BT3}

## Custom guards

Declare a `guard` block — it must evaluate to a `Bool`:

{BT3}covenant
guard is_member(addr: Address) -> Bool {{
  return self.members[addr];
}}

guard not_paused() -> Bool {{
  return !self.paused;
}}
{BT3}

Use them in actions with `only()`:

{BT3}covenant
action vote(proposal: u256) {{
  only(is_member(msg.sender));
  only(not_paused());
  // ...
}}
{BT3}

## Composing guards

Guards are ordinary boolean expressions — combine with `&&` and `||`:

{BT3}covenant
guard admin_or_operator(addr: Address) -> Bool {{
  return self.admins[addr] || self.operators[addr];
}}
{BT3}

## Role-based access control

{BT3}covenant
contract Vault {{
  role MANAGER
  role AUDITOR

  action withdraw(amount: u256) {{
    only(role: MANAGER);
    // ...
  }}

  action read_balance() -> u256 {{
    only(role: AUDITOR);
    return self.balance;
  }}
}}
{BT3}

Roles are managed via the built-in `grant_role(role, addr)` and `revoke_role(role, addr)` actions (owner-only by default).

## Guards as modifiers

If you declare a guard with `@before`, it runs automatically before every action in the contract:

{BT3}covenant
@before
guard check_not_paused() -> Bool {{
  return !self.paused;
}}
{BT3}
"""

FILES["docs/05-external-calls.md"] = f"""---
title: "05 — External Calls"
description: "Call other contracts, handle return values, and avoid reentrancy."
order: 5
section: "Fundamentals"
---

# 05 — External Calls

## Calling an interface

Define an `interface` and call through it:

{BT3}covenant
interface IERC20 {{
  action transfer(to: Address, amount: u256) -> Bool
  action balanceOf(who: Address) -> u256
}}

contract Spender {{
  field token: Address

  action spend(amount: u256) {{
    let tok = IERC20(self.token);
    let ok = tok.transfer(msg.sender, amount);
    require(ok, TransferFailed);
  }}
}}
{BT3}

## Safety: reentrancy guard

Covenant's built-in `@nonreentrant` decorator locks the contract for the duration of the action:

{BT3}covenant
@nonreentrant
action withdraw(amount: u256) {{
  require(self.balances[msg.sender] >= amount, InsufficientBalance);
  self.balances[msg.sender] -= amount;      // effect before interaction
  let ok = IERC20(self.token).transfer(msg.sender, amount);
  require(ok, TransferFailed);
}}
{BT3}

The compiler also enforces checks-effects-interactions order via a static lint — disable with `@allow(cei_violation)` only when you have verified the call is safe.

## Low-level calls

For untyped calls (e.g. proxies):

{BT3}covenant
let result = call(target, data: calldata_bytes, value: 0);
require(result.success, CallFailed);
{BT3}

## Sending ETH

{BT3}covenant
action fund(recipient: Address) {{
  require(msg.value > 0, ZeroValue);
  transfer_eth(recipient, msg.value);
}}
{BT3}

`transfer_eth` is equivalent to Solidity `call{{value: amount}}("")` with a 2300 gas stipend check disabled (Covenant does not use the Solidity 2300-gas anti-pattern).

## staticcall

Use `@view` actions on external interfaces — the compiler emits `STATICCALL` automatically:

{BT3}covenant
@view
action quote(amount: u256) -> u256 {{
  return IOracle(self.oracle).price() * amount / 1e18;
}}
{BT3}
"""

FILES["docs/06-erc20-token.md"] = f"""---
title: "06 — ERC-20 Token"
description: "A complete ERC-20 implementation in Covenant."
order: 6
section: "Standards"
---

# 06 — ERC-20 Token

A full ERC-20 compliant token in Covenant — about 60 lines of readable code.

{BT3}covenant
contract ERC20Token {{
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
  init(name: String, symbol: String, initial_supply: u256) {{
    self.name   = name;
    self.symbol = symbol;
    self.total_supply = initial_supply;
    self.balances[msg.sender] = initial_supply;
    emit Transfer(from: Address(0), to: msg.sender, value: initial_supply);
  }}

  @view action name()         -> String {{ return self.name; }}
  @view action symbol()       -> String {{ return self.symbol; }}
  @view action decimals()     -> u8     {{ return self.decimals; }}
  @view action totalSupply()  -> u256   {{ return self.total_supply; }}

  @view
  action balanceOf(account: Address) -> u256 {{
    return self.balances[account];
  }}

  action transfer(to: Address, amount: u256) -> Bool {{
    _transfer(msg.sender, to, amount);
    return true;
  }}

  action approve(spender: Address, amount: u256) -> Bool {{
    self.allowances[msg.sender][spender] = amount;
    emit Approval(owner: msg.sender, spender: spender, value: amount);
    return true;
  }}

  @view
  action allowance(owner: Address, spender: Address) -> u256 {{
    return self.allowances[owner][spender];
  }}

  action transferFrom(from: Address, to: Address, amount: u256) -> Bool {{
    let allowed = self.allowances[from][msg.sender];
    require(allowed >= amount, InsufficientAllowance(allowed, amount));
    self.allowances[from][msg.sender] -= amount;
    _transfer(from, to, amount);
    return true;
  }}

  // Internal helper — not exposed in ABI
  internal action _transfer(from: Address, to: Address, amount: u256) {{
    let bal = self.balances[from];
    require(bal >= amount, InsufficientBalance(bal, amount));
    self.balances[from] -= amount;
    self.balances[to]   += amount;
    emit Transfer(from: from, to: to, value: amount);
  }}
}}
{BT3}

## Minting & burning extension

Add to the contract body:

{BT3}covenant
action mint(to: Address, amount: u256) {{
  only(owner);
  self.total_supply     += amount;
  self.balances[to]     += amount;
  emit Transfer(from: Address(0), to: to, value: amount);
}}

action burn(amount: u256) {{
  let bal = self.balances[msg.sender];
  require(bal >= amount, InsufficientBalance(bal, amount));
  self.balances[msg.sender] -= amount;
  self.total_supply         -= amount;
  emit Transfer(from: msg.sender, to: Address(0), value: amount);
}}
{BT3}
"""

FILES["docs/07-fhe-basics.md"] = f"""---
title: "07 — FHE Basics"
description: "Homomorphic encryption as a first-class language primitive."
order: 7
section: "Standards"
---

# 07 — FHE Basics

Fully Homomorphic Encryption (FHE) lets you perform arithmetic on ciphertext — computations happen on encrypted data, and only the key holder can decrypt the result.

Covenant wraps FHE operations in the `encrypted<T>` type family.

## Declaring encrypted fields

{BT3}covenant
contract SecretVoting {{
  field tally: encrypted<u256> = fhe_zero()
}}
{BT3}

`fhe_zero()` initialises the accumulator to an encryption of 0.

## Supported operations

| Function | Description |
|----------|-------------|
| `fhe_add(a, b)` | Homomorphic addition |
| `fhe_mul(a, b)` | Homomorphic multiplication |
| `fhe_sub(a, b)` | Homomorphic subtraction |
| `fhe_eq(a, b)` | Equality test (returns `encrypted<Bool>`) |
| `fhe_lt(a, b)` | Less-than comparison |
| `fhe_decrypt(c, key)` | Decrypt with a key — emits proof of correct decryption |
| `fhe_reencrypt(c, pubkey)` | Re-encrypt under a different public key |

## Example: private vote accumulator

{BT3}covenant
contract PrivateVoting {{
  field tally: encrypted<u256> = fhe_zero()
  field voted:  Map<Address, Bool>

  error AlreadyVoted

  action cast_vote(encrypted_vote: encrypted<u256>) {{
    require(!self.voted[msg.sender], AlreadyVoted);
    self.voted[msg.sender] = true;
    // Add ciphertext directly — no decryption needed
    self.tally = fhe_add(self.tally, encrypted_vote);
  }}

  // Owner can decrypt the final tally
  action reveal_tally() -> u256 {{
    only(owner);
    return fhe_decrypt(self.tally, fhe_owner_key());
  }}
}}
{BT3}

## Scheme selection

Covenant is scheme-agnostic at the source level. Configure the FHE backend in `covenant.toml`:

{BT3}toml
[fhe]
scheme = "tfhe"   # options: tfhe | bgv | ckks
params = "default_128"
{BT3}

The compiler emits precompile calls to the scheme-specific EVM precompile registered at the target chain's genesis.

## Gas model

FHE operations are expensive — each `fhe_add` costs ~2 M gas and `fhe_mul` ~40 M gas on a standard EVM. On Aster Chain (ID 1996), the privacy precompiles are subsidised by the validator set and cost 10–100× less.

> **Tip:** batch FHE operations in a single action to amortise proof-verification overhead.
"""

FILES["docs/08-encrypted-token.md"] = f"""---
title: "08 — Encrypted Token"
description: "ERC-20 with FHE-encrypted balances."
order: 8
section: "Standards"
---

# 08 — Encrypted Token

Combine the ERC-20 pattern from chapter 06 with `encrypted<u256>` balances so no on-chain observer can read balances or transfer amounts.

{BT3}covenant
contract EncryptedToken {{
  field name:   String = "PrivaCoin"
  field symbol: String = "PVC"
  field decimals: u8   = 18

  // Balances are FHE ciphertexts — observers see only random-looking bytes
  field balances: Map<Address, encrypted<u256>>
  // Total supply is public for transparency
  field total_supply: u256

  event EncryptedTransfer(from: indexed Address, to: indexed Address)

  error InsufficientEncryptedBalance

  init(initial_supply: u256) {{
    self.total_supply = initial_supply;
    self.balances[msg.sender] = fhe_encrypt(initial_supply, fhe_owner_key());
  }}

  // Transfer: caller provides encrypted amount; contract checks ciphertext > balance
  action private_transfer(to: Address, enc_amount: encrypted<u256>) {{
    let sender_bal = self.balances[msg.sender];
    // fhe_lt returns encrypted<Bool> — no plaintext comparison
    let is_sufficient = fhe_lt(enc_amount, sender_bal);
    // require works on encrypted<Bool> — reverts if ciphertext decrypts to false
    require(is_sufficient, InsufficientEncryptedBalance);

    self.balances[msg.sender] = fhe_sub(sender_bal, enc_amount);
    self.balances[to]         = fhe_add(self.balances[to], enc_amount);
    emit EncryptedTransfer(from: msg.sender, to: to);
  }}

  // Let the owner decrypt a specific balance (for auditing)
  action audit_balance(addr: Address) -> u256 {{
    only(owner);
    return fhe_decrypt(self.balances[addr], fhe_owner_key());
  }}
}}
{BT3}

## How the viewer key works

The `fhe_owner_key()` built-in resolves to the public key stored in the contract's deployment metadata. Only the holder of the corresponding private key can decrypt. This is analogous to the **Viewer Pass** mechanism on Aster Chain — selective disclosure without exposing data to the validator set.

## Client-side encryption

Off-chain code that calls `private_transfer` must encrypt the amount before submitting:

{BT3}js
import {{ CovenantClient, fheEncrypt }} from "@covenant-lang/sdk";

const client  = new CovenantClient(provider);
const pubkey  = await client.fhePubkey(contractAddress);
const encAmt  = await fheEncrypt(1000n, pubkey);     // Uint8Array ciphertext
await contract.private_transfer(recipient, encAmt);
{BT3}

## Limitations

- FHE balances cannot be read by block explorers without the owner key.
- `fhe_lt` with 256-bit integers costs ~200 M gas on standard EVM; use Aster Chain or a dedicated L2 with native FHE precompiles for production.
- ERC-20 `allowance` / `transferFrom` pattern requires an encrypted allowance map — left as an exercise (see the `examples/encrypted-allowances` repo).
"""

FILES["docs/09-post-quantum-signatures.md"] = f"""---
title: "09 — Post-Quantum Signatures"
description: "Dilithium3 (NIST FIPS 204) signatures as a first-class Covenant primitive."
order: 9
section: "Standards"
---

# 09 — Post-Quantum Signatures

Classical ECDSA (secp256k1) will be broken by a sufficiently powerful quantum computer running Shor's algorithm. Covenant provides `@pq_signed` — a decorator that replaces ECDSA verification with **CRYSTALS-Dilithium3** (standardised as NIST FIPS 204 in 2024).

## Applying `@pq_signed`

{BT3}covenant
@pq_signed
contract QuantumSafeVault {{
  field balance: u256

  action deposit() {{
    self.balance += msg.value;
  }}

  @nonreentrant
  action withdraw(amount: u256, pq_sig: Bytes) {{
    // pq_sig is a Dilithium3 signature over (address, amount, nonce)
    verify_pq_sig(msg.sender, pq_sig);
    require(self.balance >= amount, InsufficientBalance);
    self.balance -= amount;
    transfer_eth(msg.sender, amount);
  }}
}}
{BT3}

When `@pq_signed` is present, the compiler:
1. Adds a Dilithium3 public-key registry (`field pq_keys: Map<Address, Bytes>`)
2. Emits a `register_pq_key(pubkey: Bytes)` action
3. Replaces `msg.sender` authentication with `verify_pq_sig` precompile calls

## Key registration

Users must register their Dilithium3 public key before interacting with `@pq_signed` contracts:

{BT3}bash
covenant pq keygen --out my-dilithium.json
covenant pq register --contract 0xABCD... --key my-dilithium.json
{BT3}

## Signing transactions

{BT3}js
import {{ dilithium3Sign }} from "@covenant-lang/pq-sdk";
import key from "./my-dilithium.json";

const sig = dilithium3Sign(key.privateKey, {{ sender: wallet.address, amount: 1000n, nonce }});
await contract.withdraw(1000n, sig);
{BT3}

## Hybrid mode

For a transition period, use `@pq_hybrid` — accepts both ECDSA and Dilithium3 signatures:

{BT3}covenant
@pq_hybrid
contract HybridVault {{
  // ...
}}
{BT3}

The contract accepts whichever signature type the caller provides, preferring PQ when both are present.

## Key sizes

| Algorithm | Public key | Signature | Security level |
|-----------|-----------|-----------|----------------|
| ECDSA secp256k1 | 33 bytes | 65 bytes | 128-bit classical |
| Dilithium3 | 1952 bytes | 3293 bytes | 128-bit quantum |
| Dilithium5 | 2592 bytes | 4595 bytes | 256-bit quantum |

Covenant defaults to Dilithium3 (NIST recommendation for most use cases). Switch to Dilithium5 with `[pq] level = 5` in `covenant.toml`.
"""

FILES["docs/10-zero-knowledge-proofs.md"] = f"""---
title: "10 — Zero-Knowledge Proofs"
description: "zk_prove and zk_verify as language primitives."
order: 10
section: "Standards"
---

# 10 — Zero-Knowledge Proofs

Zero-knowledge proofs let a prover convince a verifier that a statement is true without revealing the witness (secret input). Covenant exposes ZK as `zk_prove` / `zk_verify` — scheme-agnostic, circuit-agnostic language primitives.

## Basic pattern

{BT3}covenant
contract AgeVerifier {{
  // Anyone can verify a ZK proof that the caller is >= 18
  // without learning the actual birthdate.
  action prove_adult(proof: ZkProof, pub_inputs: Bytes) {{
    let circuit = Circuit("age_18_plus_v1");   // circuit ID registered at deployment
    require(
      zk_verify(circuit, proof, pub_inputs),
      InvalidProof
    );
    emit AdultVerified(msg.sender);
  }}
}}
{BT3}

## Supported schemes

Configure in `covenant.toml`:

{BT3}toml
[zk]
scheme = "groth16"   # groth16 | plonk | halo2 | fflonk
{BT3}

| Scheme | Proof size | Verify gas | Trusted setup |
|--------|-----------|------------|---------------|
| Groth16 | ~200 B | ~280 K | Per-circuit |
| PLONK | ~800 B | ~600 K | Universal |
| Halo2 | ~1.2 KB | ~900 K | None |
| fflonk | ~256 B | ~350 K | Universal |

## Generating proofs off-chain

{BT3}js
import {{ CovenantProver }} from "@covenant-lang/zk-sdk";

const prover  = new CovenantProver("age_18_plus_v1");
const witness = {{ birthdate: 19900101n, today: 20260101n }};
const {{ proof, publicInputs }} = await prover.prove(witness);

await contract.prove_adult(proof, publicInputs);
{BT3}

## Circuit registration

Circuits are deployed as precompile registrations at contract init time:

{BT3}covenant
init() {{
  register_circuit("age_18_plus_v1", circuit_vk: AGE_VK_BYTES);
}}
{BT3}

`AGE_VK_BYTES` is the verification key, embedded at compile time via `@embed("circuits/age.vk")`.

## `zk_prove` (on-chain proving)

For small circuits, Covenant can prove on-chain using the chain's native zkVM precompile:

{BT3}covenant
action commit(secret: u256) {{
  let pub_hash = zk_prove(
    circuit: "pedersen_commit_v1",
    private_inputs: [secret],
    public_inputs: []
  );
  self.commitments[msg.sender] = pub_hash;
}}
{BT3}

On-chain proving is only practical for circuits with < 2^16 constraints. For larger circuits, use off-chain proving + `zk_verify`.

## Recursive proofs

{BT3}covenant
action verify_rollup_batch(
  inner_proofs: List<ZkProof>,
  aggregated_proof: ZkProof,
  pub_inputs: Bytes
) {{
  let agg_circuit = Circuit("plonk_aggregator_v2");
  require(zk_verify(agg_circuit, aggregated_proof, pub_inputs), BadAggregation);
  // Each inner proof is verified by the aggregator circuit itself
}}
{BT3}
"""

FILES["docs/11-cryptographic-amnesia.md"] = f"""---
title: "11 — Cryptographic Amnesia"
description: "Provable on-chain data erasure with amnesia blocks."
order: 11
section: "Advanced"
---

# 11 — Cryptographic Amnesia

Cryptographic amnesia gives smart contracts the ability to **provably erase data** — producing a ZK proof that a storage slot has been overwritten with zeros and that all historical references have been scrubbed from the Merkle trie.

This satisfies on-chain "right to be forgotten" requirements without requiring chain rollbacks or off-chain trust.

## `amnesia {{ }}` block

{BT3}covenant
contract PrivateRecord {{
  field records: Map<Address, String>

  action store(data: String) {{
    self.records[msg.sender] = data;
  }}

  action erase() {{
    amnesia {{
      // Everything inside this block is provably erased.
      // The compiler inserts a two-pass erasure:
      //   Pass 1: overwrite with random bytes
      //   Pass 2: overwrite with zeros + emit erasure proof
      delete self.records[msg.sender];
    }}
    emit RecordErased(msg.sender);
  }}
}}
{BT3}

## Two-pass erasure protocol

1. **Pass 1 — Randomisation**: the slot is overwritten with `keccak256(slot . blockhash(N-1))` — ensures no value is predictable.
2. **Pass 2 — Zeroing**: the slot is set to 0x00…00 and a ZK proof is emitted attesting that the slot was at value V at block N-1 and is now 0.
3. **Proof publication**: the proof is stored in the erasure receipt log (EIP-7XX, pending) so any observer can verify erasure.

## Verifying an erasure off-chain

{BT3}bash
covenant amnesia verify \
  --contract 0xABCD... \
  --slot 0x...       \
  --block 19000000   \
  --receipt 0xtx...
{BT3}

Output:

{BT3}
Erasure proof VALID
  Slot 0x... zeroed at block 19000001
  Pre-image hash: 0xdeadbeef...
  Prover: Halo2 recursive
{BT3}

## What amnesia can and cannot erase

| Can erase | Cannot erase |
|-----------|--------------|
| Current-state storage slots | Historical block headers |
| In-contract `field` values | Event logs already emitted |
| Map entries | Calldata of past transactions |
| List elements | Data already mirrored off-chain |

The compiler warns when an `amnesia` block is applied to an event-indexed field — event logs are permanent.

## GDPR / regulatory context

Cryptographic amnesia satisfies "erasure" under data minimisation frameworks because:
- The current state provably contains zeros.
- The ZK proof commits to the pre-erasure value's hash, not the value itself.
- No trusted third party is needed to certify erasure.

> This is not legal advice. Consult a privacy attorney for regulatory compliance.
"""

FILES["docs/12-uups-upgradeable.md"] = f"""---
title: "12 — UUPS Upgradeable"
description: "Universal Upgradeable Proxy Standard pattern in Covenant."
order: 12
section: "Advanced"
---

# 12 — UUPS Upgradeable

UUPS (EIP-1822 / EIP-1967) places the upgrade logic in the implementation contract rather than the proxy. Covenant provides the `@upgradeable(uups)` decorator.

## Implementation contract

{BT3}covenant
@upgradeable(uups)
contract TokenV1 {{
  field balances: Map<Address, u256>
  field total: u256

  action mint(to: Address, amount: u256) {{
    only(owner);
    self.balances[to] += amount;
    self.total        += amount;
  }}

  // Required by UUPS: upgrade logic lives here
  action upgrade_to(new_impl: Address) {{
    only(owner);
    _upgrade(new_impl);   // built-in: validates ERC-1822, writes EIP-1967 slot
  }}
}}
{BT3}

## Proxy deployment

{BT3}bash
# Deploy implementation
covenant deploy TokenV1 --out impl.json

# Deploy ERC-1967 proxy pointing at the implementation
covenant deploy-proxy --impl $(cat impl.json | jq -r .address) --out proxy.json
{BT3}

All user interactions go through the proxy address. The proxy's storage holds the EIP-1967 slot and delegates all calls to the implementation.

## Upgrading

{BT3}bash
# Deploy new implementation
covenant deploy TokenV2 --out impl_v2.json

# Call upgrade_to through the proxy (owner wallet required)
covenant call $(cat proxy.json | jq -r .address) upgrade_to $(cat impl_v2.json | jq -r .address)
{BT3}

## Storage layout safety

Covenant enforces storage layout compatibility checks at compile time. If `TokenV2` reorders or removes fields from `TokenV1`, the compiler emits an error:

{BT3}
Error: storage layout incompatible with V1
  V1: field balances @ slot 0
  V2: field owners   @ slot 0   ← collision!
Hint: add new fields after existing ones, or use a layout gap.
{BT3}

Use a gap field to reserve space:

{BT3}covenant
@upgradeable(uups)
contract TokenV1 {{
  field balances: Map<Address, u256>
  field total:    u256
  field _gap:     u256[48]   // 48 reserved slots for future fields
}}
{BT3}

## Initialiser pattern

UUPS contracts cannot use Solidity-style constructors (proxy doesn't run them). Use the `init` block with an `initialised` guard:

{BT3}covenant
field initialised: Bool = false

action initialise(name: String) {{
  require(!self.initialised, AlreadyInitialised);
  self.initialised = true;
  self.name = name;
}}
{BT3}
"""

FILES["docs/13-beacon-proxy.md"] = f"""---
title: "13 — Beacon Proxy"
description: "One-to-many upgrades with ERC-1967 Beacon Proxy in Covenant."
order: 13
section: "Advanced"
---

# 13 — Beacon Proxy

The Beacon Proxy pattern (EIP-1967) lets you upgrade **many proxy instances** by pointing a single beacon contract to a new implementation. This is ideal for factory-deployed contracts (e.g. per-user vaults, per-pool AMM pairs).

## Architecture

{BT3}
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
{BT3}

## Beacon contract

{BT3}covenant
contract VaultBeacon {{
  field implementation: Address

  init(impl: Address) {{
    self.implementation = impl;
  }}

  @view
  action get_implementation() -> Address {{
    return self.implementation;
  }}

  action upgrade(new_impl: Address) {{
    only(owner);
    self.implementation = new_impl;
    emit Upgraded(new_impl);
  }}
}}
{BT3}

## Implementation contract

{BT3}covenant
@upgradeable(beacon)
contract UserVault {{
  field balance: u256

  action deposit() {{
    self.balance += msg.value;
  }}

  @nonreentrant
  action withdraw(amount: u256) {{
    require(self.balance >= amount, InsufficientBalance);
    self.balance -= amount;
    transfer_eth(msg.sender, amount);
  }}
}}
{BT3}

## Factory pattern

{BT3}covenant
contract VaultFactory {{
  field beacon:  Address
  field vaults:  Map<Address, Address>

  init(beacon: Address) {{
    self.beacon = beacon;
  }}

  action create_vault() -> Address {{
    require(self.vaults[msg.sender] == Address(0), AlreadyHasVault);
    // Deploy a new BeaconProxy pointing at self.beacon
    let proxy = deploy_beacon_proxy(self.beacon);
    self.vaults[msg.sender] = proxy;
    emit VaultCreated(msg.sender, proxy);
    return proxy;
  }}
}}
{BT3}

## Upgrading all vaults

Because all proxies query the same beacon, upgrading is a single call:

{BT3}bash
covenant deploy UserVaultV2 --out impl_v2.json
covenant call $BEACON_ADDR upgrade $(cat impl_v2.json | jq -r .address)
{BT3}

All existing proxies immediately delegate to `UserVaultV2` — zero per-proxy transactions needed.

## When to use Beacon vs UUPS

| Use case | Recommended pattern |
|----------|-------------------|
| Single upgradeable contract | UUPS |
| Many identical contract instances | Beacon |
| Contracts that need independent upgrade schedules | UUPS per contract |
| Factory-deployed per-user contracts | Beacon |
"""

FILES["docs/14-oracle-integration.md"] = f"""---
title: "14 — Oracle Integration"
description: "Integrate price feeds and off-chain data with Covenant's oracle primitives."
order: 14
section: "Advanced"
---

# 14 — Oracle Integration

Oracles bridge off-chain data (prices, randomness, weather, etc.) into your contracts. Covenant provides built-in interfaces for the most common oracle patterns.

## Chainlink-compatible price feed

{BT3}covenant
interface IAggregatorV3 {{
  @view action latestRoundData() -> (
    roundId:       u80,
    answer:        i256,
    startedAt:     u256,
    updatedAt:     u256,
    answeredInRound: u80
  )
  @view action decimals() -> u8
}}

contract PriceConsumer {{
  field eth_usd_feed: Address

  init(feed: Address) {{
    self.eth_usd_feed = feed;
  }}

  @view
  action get_eth_price() -> u256 {{
    let feed = IAggregatorV3(self.eth_usd_feed);
    let (_, answer, _, updatedAt, _) = feed.latestRoundData();
    // Staleness check: reject price older than 1 hour
    require(updatedAt >= block.timestamp - 3600, StalePrice);
    require(answer > 0, NegativePrice);
    let dec = feed.decimals();          // typically 8
    // Normalise to 18 decimals
    return u256(answer) * 10u256.pow(18 - u256(dec));
  }}
}}
{BT3}

## Aster Chain native oracle

Aster Chain's validator set posts a stake-weighted median price for all listed assets at every block. Access it via the built-in `oracle_price` primitive:

{BT3}covenant
action get_btc_price() -> u256 {{
  // Built-in — no external call needed on Aster Chain
  return oracle_price("BTC/USD");
}}
{BT3}

The oracle is sourced from a median of 14 CEXes, weighted by validator stake. Use `oracle_price_at(symbol, block)` for historical queries.

## Chainlink VRF (verifiable randomness)

{BT3}covenant
interface IVRFCoordinatorV2 {{
  action requestRandomWords(
    keyHash:              Bytes32,
    subId:                u64,
    confirmations:        u16,
    callbackGasLimit:     u32,
    numWords:             u32
  ) -> u256
}}

contract Lottery {{
  field coordinator: Address
  field requests:    Map<u256, Address>   // requestId -> player

  action enter() {{
    let coordinator = IVRFCoordinatorV2(self.coordinator);
    let requestId = coordinator.requestRandomWords(
      keyHash:          KEY_HASH,
      subId:            SUBSCRIPTION_ID,
      confirmations:    3,
      callbackGasLimit: 100000,
      numWords:         1
    );
    self.requests[requestId] = msg.sender;
  }}

  // Called by VRF coordinator with the random result
  action fulfillRandomWords(requestId: u256, randomWords: List<u256>) {{
    only(self.coordinator);
    let winner = self.requests[requestId];
    // Use randomWords[0] to pick outcome
    let outcome = randomWords[0] % 6;
    emit LotteryResult(winner, outcome);
  }}
}}
{BT3}

## Push oracle pattern

For custom off-chain data pushed by a trusted reporter:

{BT3}covenant
contract DataFeed {{
  field reporter: Address
  field latest_value: u256
  field latest_ts:    u256

  action submit(value: u256) {{
    only(self.reporter);
    self.latest_value = value;
    self.latest_ts    = block.timestamp;
    emit ValueUpdated(value, block.timestamp);
  }}

  @view
  action get() -> (u256, u256) {{
    return (self.latest_value, self.latest_ts);
  }}
}}
{BT3}
"""

FILES["docs/15-deploy-to-sepolia.md"] = f"""---
title: "15 — Deploy to Sepolia"
description: "Deploy a Covenant contract to Ethereum Sepolia testnet."
order: 15
section: "Advanced"
---

# 15 — Deploy to Sepolia

This chapter walks you through deploying a real contract to **Ethereum Sepolia** — the canonical EVM testnet.

## Prerequisites

- Covenant CLI installed (`cargo install covenant-cli`)
- A wallet with Sepolia ETH — get some from the [Sepolia faucet](https://sepoliafaucet.com/)
- An RPC endpoint — Alchemy, Infura, or a public endpoint

## 1. Configure `covenant.toml`

{BT3}toml
[project]
name    = "my-contract"
version = "0.1.0"
target  = "evm"

[networks.sepolia]
chain_id = 11155111
rpc_url  = "https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY"
{BT3}

## 2. Set your deployer key

Never commit private keys. Export as an environment variable:

{BT3}bash
export COVENANT_PRIVATE_KEY="0xYOUR_PRIVATE_KEY"
{BT3}

Or use a keystore file:

{BT3}bash
covenant keystore import --name deployer ./my-key.json
# Then reference it:
export COVENANT_KEYSTORE="deployer"
{BT3}

## 3. Build

{BT3}bash
covenant build
{BT3}

Emits `out/my-contract.abi` and `out/my-contract.bin`.

## 4. Deploy

{BT3}bash
covenant deploy --network sepolia --contract MyContract
{BT3}

Output:

{BT3}
Deploying MyContract to Sepolia...
Transaction: 0xabc123...
Block:       7843921
Gas used:    184,332
Contract:    0xDeployed...Address
{BT3}

## 5. Verify on Etherscan

{BT3}bash
covenant verify \
  --network  sepolia \
  --contract 0xDeployed...Address \
  --api-key  $ETHERSCAN_API_KEY
{BT3}

The CLI submits the source and ABI to Etherscan's verification API. Once verified, users can read the source and interact with the contract in the Etherscan UI.

## 6. Interact

{BT3}bash
# Call a read action
covenant call --network sepolia 0xDeployed...Address greet

# Send a write action
covenant send --network sepolia 0xDeployed...Address set_greeting "hello, Sepolia!"
{BT3}

## 7. Next: mainnet

Replace `--network sepolia` with `--network mainnet` (configured in `covenant.toml`). Mainnet deployments require real ETH for gas.

## Deploy to Aster Chain (ID 1996)

{BT3}toml
[networks.aster]
chain_id = 1996
rpc_url  = "https://tapi.asterdex.com/info"
{BT3}

{BT3}bash
covenant deploy --network aster --contract MyContract
{BT3}

Aster Chain contracts benefit from native FHE precompiles, ZK proof verification, and on-chain privacy primitives at a fraction of standard EVM gas costs.
"""

FILES["security/audit-report.md"] = f"""---
title: "Audit Report — OMEGA V4"
description: "Full summary of the OMEGA V4 security audit: 41 findings, all resolved."
order: 1
section: "Security"
---

# Audit Report — OMEGA V4

**Auditor:** OMEGA Security Labs  
**Audit period:** November 4 – December 20, 2025  
**Version audited:** Covenant compiler v0.7.0-rc3  
**Report date:** January 10, 2026  
**Status:** All findings resolved ✓

## Executive summary

OMEGA Security Labs conducted a comprehensive audit of the Covenant compiler, runtime library, and standard contract library. The audit covered:

- Covenant compiler (Rust codebase, ~48,000 LOC)
- EVM code generation backend
- FHE precompile integration layer
- ZK proof verification circuits
- Post-quantum signature verifier
- Cryptographic amnesia two-pass erasure protocol
- Standard library contracts (ERC-20, UUPS, Beacon, etc.)

**41 findings were identified. All 41 have been resolved.**

## Finding summary

| Severity | Count | Resolved |
|----------|-------|---------|
| Critical | 5 | 5 ✓ |
| High | 9 | 9 ✓ |
| Medium | 14 | 14 ✓ |
| Low | 9 | 9 ✓ |
| Informational | 4 | 4 ✓ |
| **Total** | **41** | **41 ✓** |

## Critical findings overview

All 5 critical findings are described in detail in the [Critical Findings](/security/critical-findings) page.

| ID | Title | Status |
|----|-------|--------|
| CVN-001 | FHE ciphertext malleability in `fhe_add` | Fixed in v0.7.0-rc5 |
| CVN-002 | Amnesia pass-1 randomness is predictable on low-entropy chains | Fixed in v0.7.0-rc5 |
| CVN-003 | UUPS `_upgrade` missing ERC-1822 magic check | Fixed in v0.7.0-rc4 |
| CVN-004 | PQ key registry bypass via zero-length signature | Fixed in v0.7.0-rc5 |
| CVN-005 | ZK verifier accepts proof for wrong circuit ID | Fixed in v0.7.0-rc5 |

## Audit methodology

1. **Automated analysis** — Slither, Semgrep, and OMEGA's proprietary FHE taint-analysis tool
2. **Manual code review** — line-by-line review of all compiler output paths
3. **Property-based fuzzing** — 72-hour Echidna campaign on the standard library
4. **Formal verification** — critical paths modelled in Lean 4; proofs machine-checked
5. **Differential testing** — Covenant-generated bytecode compared against reference Solidity for 200 test cases

## Recommendations implemented

All OMEGA recommendations were implemented before the V0.7 GA release:

- **CEI enforcement**: compiler now statically checks and rejects checks-effects-interactions violations unless explicitly overridden
- **Reentrancy auto-detection**: the LSP flags missing `@nonreentrant` on any action making external calls
- **FHE parameter validation**: scheme-specific parameter bounds checked at compile time
- **Amnesia log suppression**: event emission inside `amnesia {{ }}` blocks now raises a compiler error

## Full report

The complete 147-page report is available at: [covenant-lang.org/omega-v4-audit.pdf](https://covenant-lang.org/omega-v4-audit.pdf)
"""

FILES["security/critical-findings.md"] = f"""---
title: "Critical Findings"
description: "Detailed breakdown of the 5 critical security findings from the OMEGA V4 audit."
order: 2
section: "Security"
---

# Critical Findings

All 5 critical findings identified in the [OMEGA V4 audit](/security/audit-report) have been resolved. This page provides detailed descriptions and the fixes applied.

---

## CVN-001 — FHE ciphertext malleability in `fhe_add`

**Severity:** Critical  
**Component:** FHE runtime / `fhe_add` precompile wrapper  
**Fixed in:** v0.7.0-rc5

### Description

The `fhe_add` implementation in the TFHE scheme backend did not validate that both ciphertext operands were produced under the same public key. An attacker could pass a ciphertext produced under a different key as the second operand, causing the resulting ciphertext to decrypt to garbage — or, worse, to a predictable value if the attacker controlled the foreign key.

### Impact

An attacker could manipulate the result of any `fhe_add` operation they participate in, corrupting encrypted balances or vote tallies without triggering any error.

### Fix

Added public-key binding to all FHE ciphertext blobs. The precompile now verifies that both operands carry the same key fingerprint before executing the homomorphic operation. Mismatched keys revert with `FheKeyMismatch`.

---

## CVN-002 — Amnesia pass-1 randomness predictable on low-entropy chains

**Severity:** Critical  
**Component:** Cryptographic amnesia — pass-1 randomisation  
**Fixed in:** v0.7.0-rc5

### Description

Pass 1 of the amnesia protocol used `keccak256(slot . blockhash(N-1))` as the randomisation value. On chains where `BLOCKHASH` returns 0 for unavailable blocks (chains older than 256 blocks — not applicable on mainnet but applicable on short testnets and certain L2s), pass-1 would deterministically write `keccak256(slot . 0)` — a predictable value, defeating the randomisation purpose.

### Fix

Pass-1 now uses `keccak256(slot . blockhash(N-1) . block.prevrandao . tx.origin)`. The `prevrandao` field (post-Merge) provides validator-contributed randomness immune to the zero-blockhash scenario.

---

## CVN-003 — UUPS `_upgrade` missing ERC-1822 magic check

**Severity:** Critical  
**Component:** Standard library — UUPS upgradeable pattern  
**Fixed in:** v0.7.0-rc4

### Description

The built-in `_upgrade(new_impl)` function did not verify that the new implementation contract returns the ERC-1822 magic value (`0x360894...`) from `proxiableUUID()`. This meant any contract address — including a malicious one with no upgrade logic — could be set as the implementation, permanently bricking the proxy.

### Fix

`_upgrade` now calls `proxiableUUID()` on the new implementation and reverts with `InvalidImplementation` if the return value is incorrect. The check is gas-bounded (5000 gas stipend) to prevent griefing via out-of-gas.

---

## CVN-004 — PQ key registry bypass via zero-length signature

**Severity:** Critical  
**Component:** Post-quantum signature verifier  
**Fixed in:** v0.7.0-rc5

### Description

The Dilithium3 verifier did not explicitly check for zero-length signatures before invoking the precompile. Some chain configurations return `true` from the precompile for a zero-length input (implementation-defined behaviour). An attacker submitting an empty byte array as `pq_sig` would bypass authentication entirely.

### Fix

`verify_pq_sig` now rejects any signature shorter than the minimum Dilithium3 signature length (2420 bytes) with `InvalidPqSignatureLength` before invoking the precompile.

---

## CVN-005 — ZK verifier accepts proof for wrong circuit ID

**Severity:** Critical  
**Component:** ZK proof verification — circuit ID binding  
**Fixed in:** v0.7.0-rc5

### Description

The `zk_verify` precompile accepted proofs where the circuit ID embedded in the proof did not match the `circuit` parameter passed by the calling contract. A proof generated for circuit A could be accepted as valid for circuit B if the public inputs happened to satisfy circuit B's public interface.

### Impact

An attacker could submit a valid proof for a permissive circuit (e.g. "prove you know any prime") to satisfy a more restrictive circuit check (e.g. "prove you are KYC verified"), completely bypassing the intended verification logic.

### Fix

The proof blob format now includes a binding commitment to the circuit verification key. `zk_verify` rejects any proof whose circuit commitment does not match the registered VK for the provided circuit ID.
"""

FILES["security/secure-patterns.md"] = f"""---
title: "Secure Patterns"
description: "Recommended security patterns and best practices for Covenant contracts."
order: 3
section: "Security"
---

# Secure Patterns

Covenant's type system and compiler catch many vulnerabilities automatically. This page documents patterns that go beyond static analysis — design-level decisions that prevent entire vulnerability classes.

## 1. Checks-Effects-Interactions (CEI)

Always perform state changes **before** external calls. Covenant's LSP warns on violations; the compiler enforces it for `@nonreentrant` actions.

{BT3}covenant
// CORRECT — effect before interaction
@nonreentrant
action withdraw(amount: u256) {{
  require(self.balances[msg.sender] >= amount, InsufficientBalance);
  self.balances[msg.sender] -= amount;    // effect
  transfer_eth(msg.sender, amount);       // interaction
}}
{BT3}

## 2. Pull payments over push payments

Instead of pushing ETH to recipients (reentrancy risk), let them pull:

{BT3}covenant
field pending_withdrawals: Map<Address, u256>

// Internally: schedule payment
internal action _schedule_payment(to: Address, amount: u256) {{
  self.pending_withdrawals[to] += amount;
}}

// Publicly: recipient pulls their own funds
@nonreentrant
action withdraw_payment() {{
  let amount = self.pending_withdrawals[msg.sender];
  require(amount > 0, NothingToWithdraw);
  self.pending_withdrawals[msg.sender] = 0;
  transfer_eth(msg.sender, amount);
}}
{BT3}

## 3. Use `only()` guards, not `if`/`revert` manually

{BT3}covenant
// PREFERRED
action admin_action() {{ only(owner); ... }}

// AVOID — easy to forget, no static verification
action admin_action() {{
  if msg.sender != owner() {{ revert Unauthorised; }}
  ...
}}
{BT3}

## 4. Validate oracle staleness

Always check `updatedAt` when consuming price feeds:

{BT3}covenant
let (_, answer, _, updatedAt, _) = feed.latestRoundData();
require(block.timestamp - updatedAt <= MAX_STALENESS, StalePrice);
require(answer > 0, NegativePrice);
{BT3}

## 5. Two-step ownership transfer

Single-step `transfer_ownership` can permanently lose a contract if you transfer to a wrong address. Use a two-step pattern:

{BT3}covenant
field pending_owner: Address

action propose_ownership(new_owner: Address) {{
  only(owner);
  self.pending_owner = new_owner;
}}

action accept_ownership() {{
  require(msg.sender == self.pending_owner, NotPendingOwner);
  self.pending_owner = Address(0);
  _transfer_ownership(msg.sender);
}}
{BT3}

## 6. Emit events for all state changes

Every mutation that downstream systems or UIs need to observe should emit an event. Covenant's LSP detector `missing-event` flags state mutations in `@view` contexts.

## 7. Timelocks for governance actions

Protect high-impact actions with a timelock:

{BT3}covenant
field upgrade_delay:  u256 = 48 * 3600   // 48 hours
field pending_upgrade: Address
field upgrade_eta:     u256

action propose_upgrade(new_impl: Address) {{
  only(owner);
  self.pending_upgrade = new_impl;
  self.upgrade_eta     = block.timestamp + self.upgrade_delay;
  emit UpgradeProposed(new_impl, self.upgrade_eta);
}}

action execute_upgrade() {{
  only(owner);
  require(block.timestamp >= self.upgrade_eta, TooEarly);
  _upgrade(self.pending_upgrade);
}}
{BT3}

## 8. Integer overflow

Covenant uses checked arithmetic by default. All `+`, `-`, `*` on integer types revert on overflow. Use `unchecked {{ }}` only when you have mathematically proven safety:

{BT3}covenant
// Safe by default
self.total += amount;

// Unchecked (document why it is safe)
unchecked {{
  // amount is always < (2^256 - total) because of the cap check above
  self.total += amount;
}}
{BT3}
"""

FILES["security/known-pitfalls.md"] = f"""---
title: "Known Pitfalls"
description: "Common mistakes and vulnerabilities to avoid when writing Covenant contracts."
order: 4
section: "Security"
---

# Known Pitfalls

This page documents known pitfalls in Covenant development — gotchas that are not caught by the compiler alone.

## 1. FHE key scope confusion

**Pitfall:** Encrypting values with `fhe_owner_key()` when the intended decryptor is the user.

`fhe_owner_key()` resolves to the contract deployer's public key. If users need to decrypt their own data, they must provide their own public key:

{BT3}covenant
// WRONG: user cannot decrypt this
self.user_secret[msg.sender] = fhe_encrypt(value, fhe_owner_key());

// CORRECT: encrypt under the caller's registered PQ/FHE key
self.user_secret[msg.sender] = fhe_encrypt(value, self.user_fhe_keys[msg.sender]);
{BT3}

## 2. Amnesia applied to event-indexed fields

Events are permanent — they live in the transaction receipt log, which is not part of state. If you `delete` a field and emit an event containing the old value, the value is preserved forever in the log:

{BT3}covenant
// DANGEROUS: old_value is now permanently in the event log
amnesia {{
  let old_value = self.secret;
  delete self.secret;
  emit SecretRevoked(old_value);   // compiler error in v0.7 — catches this
}}
{BT3}

The compiler emits an error if you reference an amnesia-deleted field in an `emit` statement.

## 3. Reentrancy in `@view` actions

`@view` actions cannot mutate state — but they **can** make external calls that trigger side effects in other contracts. This is not reentrancy in the classical sense but can cause issues with flash-loan-style attacks on downstream contracts.

Use `@staticcall` to enforce read-only external calls from `@view` actions.

## 4. Beacon proxy storage slot collisions

When adding fields to a beacon implementation, never insert new fields before existing ones. The proxy's stored data is a flat byte array indexed by slot number. Inserting a field shifts all subsequent slots, corrupting all existing proxy state.

Always **append** new fields or use a gap field from the start (see chapter 12).

## 5. `block.timestamp` manipulation

Validators can adjust `block.timestamp` by ±15 seconds. Never use it as the sole source of randomness or for fine-grained timing logic:

{BT3}covenant
// DANGEROUS for values < 15 seconds
require(block.timestamp >= self.unlock_time, NotYet);

// Use block numbers for more reliable sequencing on EVM
require(block.number >= self.unlock_block, NotYet);
{BT3}

## 6. `msg.value` in delegatecall context

If a contract uses `delegatecall` (proxy patterns), `msg.value` is available to the implementation. But if the proxy receives ETH in one call and delegates to the implementation without forwarding `msg.value`, the ETH is silently locked in the proxy.

Covenant's `deploy_beacon_proxy` built-in handles this correctly. Only use raw `delegatecall` if you understand the value-forwarding implications.

## 7. PQ signature replay

Dilithium3 signatures are deterministic — the same (message, key) always produces the same signature. Without a nonce, an observer who intercepts a signed transaction can replay it:

{BT3}covenant
// Include nonce in the signed message
action pq_withdraw(amount: u256, nonce: u256, pq_sig: Bytes) {{
  verify_pq_sig_with_nonce(msg.sender, amount, nonce, pq_sig);
  require(!self.used_nonces[nonce], NonceReused);
  self.used_nonces[nonce] = true;
  // ...
}}
{BT3}

## 8. ZK proof front-running

When a user submits a ZK proof transaction, an observer on the mempool can copy the proof and submit their own transaction with the same proof, claiming the reward before the original submitter. Bind the proof to `msg.sender`:

{BT3}covenant
// Public input must include msg.sender so the proof only works for the original caller
action claim_reward(proof: ZkProof, pub_inputs: Bytes) {{
  // pub_inputs must encode msg.sender — enforced by the circuit
  require(decode_address(pub_inputs) == msg.sender, WrongCaller);
  require(zk_verify(REWARD_CIRCUIT, proof, pub_inputs), InvalidProof);
  // ...
}}
{BT3}

## 9. Unchecked ERC-20 return values

Some ERC-20 tokens (USDT on mainnet) return no value from `transfer`. The Covenant interface definition requires a `-> Bool` return value — calling a non-returning token through this interface will revert. Use a safe-transfer wrapper for unknown tokens:

{BT3}covenant
action safe_transfer(token: Address, to: Address, amount: u256) {{
  let ok = call(token, abi_encode("transfer(address,uint256)", to, amount), value: 0);
  require(ok.success && (ok.data.len == 0 || abi_decode<Bool>(ok.data)), TransferFailed);
}}
{BT3}
"""

GLOSSARY_PART1 = """---
title: "Glossary"
description: "100+ terms: Covenant keywords, types, FHE primitives, ZK concepts, and post-quantum cryptography."
---

# Glossary

100+ terms covering the Covenant language, cryptographic primitives, and ecosystem concepts.

---

## A

**`action`** — The primary entry point declaration in a Covenant contract. Maps to an ABI-visible function. May be annotated with `@view`, `@nonreentrant`, `@pq_signed`, etc.

**ABI** — Application Binary Interface. The JSON descriptor of a contract's public actions, events, and errors. Covenant emits a fully typed ABI compatible with ethers.js and viem.

**`amnesia { }`** — A block-scoped keyword that triggers the two-pass cryptographic erasure protocol. State mutations inside the block are provably erased at the end of the block.

**`assert`** — Unconditional invariant check. Reverts with `Panic(0x01)` if the condition is false.

**Aster Chain** — EVM-compatible L1 (Chain ID 1996) launched March 5, 2026. Features native FHE precompiles, ZK proof verification, and PoSA consensus.

**`@allow(..)`** — Compiler annotation that suppresses a specific lint detector.

## B

**`@before`** — Guard decorator that causes the guard to run before every action in the contract.

**Beacon Proxy** — EIP-1967 upgrade pattern where many proxies share a single beacon. See chapter 13.

**BGV** — Brakerski-Gentry-Vaikuntanathan. An FHE scheme optimised for integer arithmetic.

**`block.number`** — Built-in: the current block number.

**`block.timestamp`** — Built-in: UNIX timestamp of the current block (seconds). Can be manipulated by validators ±15 seconds.

**`Bool`** — Primitive boolean type. Compiles to `uint8` in the ABI.

**`Bytes`** — Dynamic byte array. Compiles to `bytes` in the ABI.

**`Bytes32`** — Fixed 32-byte value. Compiles to `bytes32` in the ABI.

## C

**CEI** — Checks-Effects-Interactions. The canonical safe action body ordering.

**`call()`** — Low-level external call primitive. Returns `(success: Bool, data: Bytes)`.

**Circuit** — A ZK arithmetic constraint system. Identified by string IDs registered at contract init time.

**CKKS** — Cheon-Kim-Kim-Song. An FHE scheme for approximate real-number arithmetic.

**`contract`** — Top-level declaration for a Covenant smart contract.

**`covenant.toml`** — The project configuration file.

**Covenant CLI** — The command-line toolchain (`covenant-cli`).

**CRYSTALS-Dilithium** — Lattice-based digital signature algorithm standardised as NIST FIPS 204.

## D

**`decimals`** — ERC-20 field indicating decimal places (typically 18).

**`delete`** — Resets a storage slot to zero. Inside `amnesia { }`, triggers two-pass erasure.

**Dilithium3** — CRYSTALS-Dilithium parameter set (NIST level 2). PK: 1952 B, Sig: 3293 B.

**Dilithium5** — Higher security parameter set (NIST level 5).

## E

**EIP-1967** — Standard storage slot layout for proxy contracts.

**EIP-1822** — Universal Upgradeable Proxy Standard. Defines the `proxiableUUID()` check.

**EIP-712** — Typed structured data signing standard.

**`emit`** — Emits an event. Must not reference amnesia-deleted fields.

**`encrypted<T>`** — The FHE ciphertext type. T may be u8–u256 or Bool.

**`error`** — Named revert reason declaration. Use `revert ErrorName(...)` or `require(cond, Err)`.

**ERC-20** — Ethereum fungible token standard. See chapter 06.

**`event`** — Structured log entry declaration. Up to 3 `indexed` fields per event.

**EVM** — Ethereum Virtual Machine. Covenant's primary compilation target.

## F

**`fhe_add(a, b)`** — Homomorphic addition of two `encrypted<T>` values.

**`fhe_decrypt(c, key)`** — Decrypts an `encrypted<T>` ciphertext, emitting an on-chain proof.

**`fhe_encrypt(v, pubkey)`** — Encrypts a plaintext value under a public key.

**`fhe_eq(a, b)`** — Homomorphic equality comparison. Returns `encrypted<Bool>`.

**`fhe_lt(a, b)`** — Homomorphic less-than comparison. Returns `encrypted<Bool>`.

**`fhe_mul(a, b)`** — Homomorphic multiplication.

**`fhe_owner_key()`** — Built-in: the deployer's FHE public key.

**`fhe_reencrypt(c, pubkey)`** — Re-encrypts under a different public key without decrypting.

**`fhe_sub(a, b)`** — Homomorphic subtraction.

**`fhe_zero()`** — Returns an encryption of zero; initialises `encrypted<T>` fields.

**FHE** — Fully Homomorphic Encryption. Supports arbitrary computation on ciphertext.

**`field`** — Persistent storage declaration. Compiles to EVM storage slots.

**fflonk** — PLONK variant with smaller proof sizes. Supported by Covenant ZK backend.

## G

**`guard`** — Named boolean predicate for access control.

**Groth16** — Most widely deployed ZK proof system. ~200 B proof, ~280K gas verify.

## H

**Halo2** — ZK proof system with no trusted setup. ~1.2 KB proofs.

## I

**`i256`** — Signed 256-bit integer. Compiles to `int256` in the ABI.

**`indexed`** — Event field modifier for Bloom filter topics (max 3 per event).

**`init`** — Constructor block. Runs once at deployment.

**`interface`** — External contract ABI declaration for typed external calls.

**`internal`** — Action modifier: not exposed in ABI, callable only from within the contract.
"""
FILES["glossary/index.md"] = GLOSSARY_PART1

GLOSSARY_PART2 = """

## K

**`keccak256`** — Built-in hash function. Takes `Bytes`, returns `Bytes32`.

## L

**Lattice cryptography** — Mathematical foundation for post-quantum schemes. Quantum-resistant.

**`List<T>`** — Dynamic array. Length in base slot; elements at `keccak256(base) + i`.

**LSP** — Language Server Protocol. Covenant ships an LSP with 38+ lint detectors for VS Code.

## M

**`Map<K, V>`** — Hash-map type. Compiles to `keccak256(key . slot)` storage layout.

**`msg.sender`** — Built-in: the caller's address.

**`msg.value`** — Built-in: ETH (wei) sent with the call.

## N

**NIST FIPS 204** — Federal standard (August 2024) standardising CRYSTALS-Dilithium.

**`@nonreentrant`** — Prevents reentrant calls via a reentrancy lock storage slot.

**Nonce** — Monotonically increasing counter preventing replay attacks.

## O

**`only()`** — Guard invocation. `only(owner)`, `only(role: R)`, or `only(expr)`.

**oracle_price** — Built-in on Aster Chain: stake-weighted median price from validator committee.

**OMEGA V4** — Security audit by OMEGA Security Labs on Covenant v0.7.0-rc3. 41 findings, all resolved.

## P

**`@pq_hybrid`** — Accepts both ECDSA and Dilithium3 signatures.

**`@pq_signed`** — Replaces ECDSA with Dilithium3 (NIST FIPS 204).

**Pagefind** — Static search library used by this documentation site.

**PLONK** — Universal ZK proof system with a universal trusted setup.

**PoSA** — Proof-of-Staked Authority. Aster Chain's consensus mechanism.

**Post-quantum** — Cryptographic schemes secure against quantum computers.

**`prevrandao`** — EVM opcode providing validator-contributed randomness (post-Merge).

**`proxiableUUID()`** — ERC-1822 magic value identifying a UUPS implementation.

## R

**`register_circuit`** — Built-in for registering a ZK verification key at contract init time.

**`require(cond, Err)`** — Reverts with `Err` if `cond` is false.

**`revert Err(..args)`** — Unconditional typed revert.

**Role** — Named access-control group declared with `role`. Managed by `grant_role`/`revoke_role`.

## S

**STARK** — Scalable Transparent ARguments of Knowledge. No trusted setup; post-quantum secure.

**`String`** — Dynamic UTF-8 string. Compiles to `string` in the ABI.

**`staticcall`** — Read-only external call emitted for `@view` action cross-contract calls.

## T

**TFHE** — Fast Fully Homomorphic Encryption over the Torus. Covenant default FHE scheme.

**Timelock** — Enforces a waiting period before governance actions execute.

**`transfer_eth(to, amount)`** — Built-in ETH transfer without 2300-gas stipend restriction.

## U

**`u8` / `u16` / `u32` / `u64` / `u128` / `u256`** — Unsigned integer types. Overflow reverts by default.

**`unchecked { }`** — Block disabling overflow checking. Use only when overflow is provably impossible.

**UUPS** — Universal Upgradeable Proxy Standard (EIP-1822 / EIP-1967). See chapter 12.

## V

**`verify_pq_sig`** — Built-in: verifies a Dilithium3 signature. Injected by `@pq_signed`.

**`@view`** — Marks an action as read-only. Compiler enforces no state mutations.

**Viewer Pass** — Aster Chain selective disclosure mechanism: grants read access to encrypted state without exposing data to other validators.

## W

**WASM** — WebAssembly. A Covenant compilation target for off-chain proving and testing.

## Z

**`zk_prove(circuit, private_inputs, public_inputs)`** — On-chain ZK proving (practical for < 2^16 constraints).

**`zk_verify(circuit, proof, pub_inputs)`** — Verifies a ZK proof on-chain. Returns `Bool`.

**ZkProof** — Covenant's native ZK proof blob type with circuit-binding commitment header.

**Zero-knowledge proof** — Allows proving a statement is true without revealing the witness. See chapter 10.
"""
FILES["glossary/index.md"] += GLOSSARY_PART2

# Write all files
for rel, content in FILES.items():
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"wrote: {rel}")

print("Done!")
