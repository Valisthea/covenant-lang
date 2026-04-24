---
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

```toml
[project]
name    = "my-contract"
version = "0.1.0"
target  = "evm"

[networks.sepolia]
chain_id = 11155111
rpc_url  = "https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY"
```

## 2. Set your deployer key

Never commit private keys. Export as an environment variable:

```bash
export COVENANT_PRIVATE_KEY="0xYOUR_PRIVATE_KEY"
```

Or use a keystore file:

```bash
covenant keystore import --name deployer ./my-key.json
# Then reference it:
export COVENANT_KEYSTORE="deployer"
```

## 3. Build

```bash
covenant build
```

Emits `out/my-contract.abi` and `out/my-contract.bin`.

## 4. Deploy

```bash
covenant deploy --network sepolia --contract MyContract
```

Output:

```
Deploying MyContract to Sepolia...
Transaction: 0xabc123...
Block:       7843921
Gas used:    184,332
Contract:    0xDeployed...Address
```

## 5. Verify on Etherscan

```bash
covenant verify   --network  sepolia   --contract 0xDeployed...Address   --api-key  $ETHERSCAN_API_KEY
```

The CLI submits the source and ABI to Etherscan's verification API. Once verified, users can read the source and interact with the contract in the Etherscan UI.

## 6. Interact

```bash
# Call a read action
covenant call --network sepolia 0xDeployed...Address greet

# Send a write action
covenant send --network sepolia 0xDeployed...Address set_greeting "hello, Sepolia!"
```

## 7. Next: mainnet

Replace `--network sepolia` with `--network mainnet` (configured in `covenant.toml`). Mainnet deployments require real ETH for gas.

## Deploy to Aster Chain (ID 1996)

```toml
[networks.aster]
chain_id = 1996
rpc_url  = "https://tapi.asterdex.com/info"
```

```bash
covenant deploy --network aster --contract MyContract
```

Aster Chain contracts benefit from native FHE precompiles, ZK proof verification, and on-chain privacy primitives at a fraction of standard EVM gas costs.
