---
title: "CLI Reference"
description: "Complete reference for the covenant command-line interface."
order: 3
---

# CLI Reference

The `covenant` CLI is the primary interface to the Covenant toolchain. All commands follow the pattern `covenant <command> [options] [args]`.

## Global flags

| Flag | Description |
|------|-------------|
| `--version` | Print compiler version |
| `--verbose` | Verbose output |
| `--quiet` | Suppress all output except errors |
| `--no-color` | Disable ANSI color output |
| `--config <path>` | Path to `covenant.toml` (default: project root) |

## `covenant new`

Create a new project.

```bash
covenant new <name> [--template <template>]
```

| Template | Description |
|----------|-------------|
| `default` | Counter contract (default) |
| `erc20` | ERC-20 token |
| `fhe` | Encrypted counter with FHE |
| `upgradeable` | UUPS upgradeable contract |

## `covenant build`

Compile source files to EVM bytecode.

```bash
covenant build [source.cov] [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--target <chain>` | `evm` | Target chain: `evm`, `aster`, `wasm` |
| `--optimize` | off | Enable IR optimizer |
| `--output <dir>` | `target/` | Output directory |
| `--emit-ir` | off | Also emit typed IR (.cov.ir) |
| `--strict` | off | Treat warnings as errors |

## `covenant test`

Run the test suite.

```bash
covenant test [--filter <pattern>] [--verbose]
```

Tests are defined in `tests/*.cov` or inline in source with `#[test]`.

## `covenant lint`

Run all static analysis detectors.

```bash
covenant lint [source.cov] [--fix] [--strict]
```

38+ detectors cover: reentrancy, integer overflow, unchecked external calls, missing guards, CEI violations, FHE reveal without guard, PQ signature misconfiguration, and more.

## `covenant deploy`

Deploy a compiled artifact to a network.

```bash
covenant deploy <artifact> --network <network> [options]
```

| Option | Description |
|--------|-------------|
| `--network <name>` | Network from `covenant.toml` |
| `--constructor-args <args...>` | Constructor arguments (ABI-encoded) |
| `--value <amount>` | ETH to send with deployment |
| `--gas-limit <n>` | Override gas limit |
| `--dry-run` | Simulate without broadcasting |

## `covenant call`

Call a view action (no transaction).

```bash
covenant call <address> <action> [args...] --network <network>
```

## `covenant send`

Send a transaction to a contract.

```bash
covenant send <address> <action> [args...] --network <network> [--value <eth>]
```

## `covenant verify`

Verify source on a block explorer.

```bash
covenant verify <address> --network <network> --source <file> --compiler-version <ver>
```

## `covenant upgrade-check`

Check storage layout compatibility between two artifacts.

```bash
covenant upgrade-check <old.artifact> <new.artifact>
```

Exits 0 if safe, non-zero on collision with a human-readable diff.

## `covenant zk prove`

Generate a ZK proof off-chain.

```bash
covenant zk prove --circuit <circuit-id> --private <key=val...> --public <key=val...>
```

## `covenant.toml` reference

```toml
[project]
name    = "my-contract"
version = "0.1.0"

[compiler]
target  = "evm"         # default target
strict  = false
optimize = true

[networks.sepolia]
rpc_url    = "https://rpc.sepolia.org"
chain_id   = 11155111
explorer   = "https://sepolia.etherscan.io"

[networks.aster]
rpc_url    = "https://tapi.asterdex.com"
chain_id   = 1996
explorer   = "https://explorer.asterdex.com"

[deploy]
private_key_env = "DEPLOYER_PRIVATE_KEY"
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `DEPLOYER_PRIVATE_KEY` | Private key for signing transactions |
| `COVENANT_RPC_URL` | Override network RPC URL |
| `COVENANT_LOG` | Log level: `error`, `warn`, `info`, `debug`, `trace` |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Compile error |
| 2 | Test failure |
| 3 | Lint error (with `--strict`) |
| 4 | Deployment failure |
| 5 | Upgrade storage collision |
