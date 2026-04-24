---
title: "Compiler Targets"
description: "The three compilation targets in Covenant V0.8 GA: EVM (default), Aster Chain, and WebAssembly. Backend selection, output differences, and deployment workflows."
section: reference
order: 3
level: reference
---

<!-- Source: doc5-compiler-architecture.md §16-§18 -->
<!-- Last sync: 2026-04-24 · Covenant 0.8.0 GA -->

# Compiler Targets

The Covenant compiler supports three first-class backends as of V0.8 GA, selected via the `--target-chain` flag:

```bash
covenant build --target-chain evm    ./src/Contract.cov   # default
covenant build --target-chain aster  ./src/Contract.cov   # Aster Chain
covenant build --target-chain wasm   ./src/Contract.cov   # V0.8 GA — deterministic
```

## EVM Backend (default)

The EVM backend produces standard EVM bytecode deployable on Ethereum mainnet, all major L2s (Arbitrum, Optimism, Base, Scroll), and any EVM-compatible chain.

### IR to EVM Opcode Mapping

Key mappings (IR opcode → EVM opcodes):

| IR Opcode | EVM Opcodes |
|-----------|-------------|
| `Load slot` | `PUSH32 slot SLOAD` |
| `Store slot value` | `PUSH32 slot SVALUE SSTORE` |
| `Call fn` | `JUMP` (internal) / `CALL` (external) |
| `FheAdd a b` | `PUSH20 0x10 STATICCALL` (precompile) |
| `Emit Event(...)` | `LOG1/LOG2/LOG3/LOG4` |
| `Revert msg` | `REVERT` with ABI-encoded error |
| `PqVerify pk msg sig` | `PUSH20 0x41 STATICCALL` |

### Gas Model

The EVM backend generates gas-optimal code for the standard EVM pricing model (EIP-1559, EIP-3529). The optimizer's storage slot packing pass is particularly impactful: packing `bool` fields saves 15,000 gas per cold read.

FHE precompile costs on L1 are high (see [ERC-8227 gas table](/docs/reference/ercs/02-erc-8227-fhe)). For FHE-heavy contracts, use the Aster backend.

### Metadata Format

The EVM artifact includes a CBOR-encoded metadata blob appended to the deployed bytecode (following Solidity convention). This blob contains:
- Compiler version
- Source hash
- ERC compliance profile (CL1–CL5)
- Audit report reference (OMEGA V4)
- IPFS hash of the full artifact JSON

Block explorers that understand Covenant contracts (AsterScan, etc.) use this CBOR blob for source verification.

### Deployment Workflow

```bash
# Build
covenant build --target evm ./src/Token.cvt

# Deploy to Sepolia
covenant deploy   --network sepolia   --rpc https://rpc.sepolia.org   --private-key $DEPLOYER_KEY   ./out/Token.artifact.json
```

The `covenant deploy` command is a thin wrapper around `cast send` from Foundry. It reads the artifact, encodes the constructor call, and broadcasts the deployment transaction.

## Aster Backend

The Aster backend targets **Aster Chain** (Chain ID 1996), a purpose-built L1 with native FHE and ZK hardware acceleration.

### Key Differences from EVM

| Feature | EVM | Aster |
|---------|-----|-------|
| FHE operations | Via precompile calls (expensive) | Native opcodes (single-instruction) |
| ZK verification | Via precompile (~200k gas) | Native (~20k gas equivalent) |
| Block time | 12s (Ethereum) / 2s (most L2s) | 500ms (with ms pre-confirmation) |
| Privacy | Off by default | On by default (Account Privacy) |
| Gas model | ETH gas | Dual: compute gas + pGas (privacy gas) |
| FHE batch | 3 precompile calls | 1 native instruction |

### Aster-Specific IR Lowering

When targeting Aster, the IR lowering transforms:

```
; EVM: FheAdd calls precompile 0x10
%result = FheAdd %a %b
  -> PUSH20 0x10  PUSH args  GAS  STATICCALL

; Aster: FheAdd is a single native opcode
%result = FheAdd %a %b
  -> ASTER_FHEADD  (1 opcode, ~400 pGas)
```

The Aster backend also enables:
- **Account Privacy by default**: Balance reads return ciphertexts unless the caller has a Viewer Pass
- **Single-instruction batch FHE**: The `FheBatch` IR opcode maps to a single Aster native opcode
- **ZK proof generation via hardware**: Off-chip ZK accelerators reduce proof time from seconds to milliseconds

### Aster Deployment Workflow

```bash
covenant build --target aster ./src/Contract.cvt

covenant deploy   --network aster   --rpc https://tapi.asterdex.com/info   --chain-id 1996   --private-key $DEPLOYER_KEY   ./out/Contract.artifact.json
```

### Current state in V0.8 GA and V0.8.x roadmap

V0.8 GA ships the Aster foundation: chain ID 1996, precompile registry wiring, and placeholder artifacts with `COV7\x01` magic. The `--target-chain aster` flag is a first-class target — it parses, type-checks, and emits auditable placeholder bytecode. Full Aster SDK lowering lands in V0.8.x:

- Full Aster SDK integration (native staking interaction, real per-opcode lowering)
- Aster Account Abstraction support
- pGas estimation in `covenant build --estimate-gas`
- Automatic Viewer Pass issuance for selective disclosure

## WebAssembly Backend

**Status**: Stable as of **V0.8 GA (April 2026)**. Deterministic, `wasmparser::validate`-clean output suitable for browsers and server-side sandboxes (`wasmtime`, `wasmer`).

The WASM backend compiles Covenant contracts to WebAssembly modules, enabling:

- Browser-side contract simulation (Covenant Playground)
- Off-chain computation for `@prove_offchain` circuits
- Deterministic server-side sandboxing via `wasmtime` / `wasmer`
- Testing without an EVM node

```bash
covenant build contract.cov --target-chain wasm
#   → contract.wasm (deterministic)
#   → contract.metadata.json (ABI, imports, exports, storage layout)
```

### Determinism guarantees

The WASM backend emits byte-identical output for byte-identical inputs. No threads, no non-deterministic intrinsics, no floats in hot paths. Host-imports are narrow (storage get/put, keccak256, log emission) and fully enumerated in the `metadata.json` imports table.

### FHE on WASM

V0.8 ships types and trap behavior for FHE operations on the WASM target. Real TFHE key-switching on WASM is gated on the `0x0128` precompile (or its WASM-host equivalent) and lands in V0.8.x. Until then, FHE ops in a WASM build will return a `KeySwitchError::NotImplemented` when exercised.

### V0.8.x follow-ups

- Real TFHE key-switching on WASM (via `0x0128` precompile or host-import)
- Integration with the Covenant Playground (in-browser IDE)
- WASM contracts deployable to WASM-compatible chains (Cosmos CosmWasm, etc.)

## Future Backends

The following backends are under consideration for V0.9+:

| Backend | Status | Notes |
|---------|--------|-------|
| zkEVM | Researching | Type-1 zkEVM compatibility |
| Solana SVM | Researching | Requires significant IR changes |
| StarkVM | Not planned | Different memory model |

## See Also

- [Compiler Pipeline](/docs/reference/compiler/01-pipeline)
- [Diagnostics Catalog](/docs/reference/compiler/04-diagnostics)
- [Example 15 — Deploy to Sepolia](/docs/examples/15-deploy-to-sepolia)
