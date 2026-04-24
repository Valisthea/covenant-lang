---
title: "Compiler Targets"
description: "The three compilation targets: EVM (default), Aster Chain, and WASM (experimental). Backend selection, output differences, and deployment workflows."
section: reference
order: 3
level: reference
---

<!-- Source: doc5-compiler-architecture.md §16-§18 -->
<!-- Last sync: 2026-04-23 -->

# Compiler Targets

The Covenant compiler supports three backends, selected via the `--target` flag:

```bash
covenant build --target evm    ./src/Contract.cvt   # default
covenant build --target aster  ./src/Contract.cvt   # Aster Chain
covenant build --target wasm   ./src/Contract.cvt   # experimental
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

### V0.8 Roadmap

The V0.7 Aster backend is a foundation. V0.8 plans:
- Full Aster SDK integration (native staking interaction)
- Aster Account Abstraction support
- pGas estimation in `covenant build --estimate-gas`
- Automatic Viewer Pass issuance for selective disclosure

## WASM Backend (experimental)

**Status**: Experimental. Not recommended for production use. Target V0.8 for stability.

The WASM backend compiles Covenant contracts to WebAssembly modules, enabling:
- Browser-side contract simulation (Covenant Playground, planned)
- Off-chain computation for `@prove_offchain` circuits
- Testing without an EVM node

### Current State

The WASM backend compiles 7 core IR opcodes to WASM instructions. FHE opcodes are stubbed (return dummy values). ZK opcodes generate real proofs via the embedded `snarkjs` WASM runtime.

```bash
covenant build --target wasm ./src/Contract.cvt
# Warning: WASM backend is experimental. FHE opcodes are stubbed.
```

### Planned Capabilities (V0.8+)

- Full FHE operation support via TFHE-rs compiled to WASM
- Browser-embeddable contracts
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
