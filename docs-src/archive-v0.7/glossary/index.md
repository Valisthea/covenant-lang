---
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
