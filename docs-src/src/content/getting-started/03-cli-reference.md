---
title: "CLI Reference"
description: "Complete reference for the covenant command-line interface (V0.9 — Foundry-class with test, fmt, doctor, lint, init, explain)."
order: 3
---

# CLI Reference

The `covenant` CLI is the primary interface to the Covenant toolchain. All commands follow the pattern `covenant <command> [options] [args]`.

## What's new in V0.9

V0.9 brings Foundry-class developer ergonomics. Seven commands round out the CLI:

| Command | Purpose |
|---|---|
| `covenant test --watch / --coverage` | Per-test isolation, watch mode, name-heuristic coverage |
| `covenant fmt` | Canonical formatting, `--check` for CI gates |
| `covenant doctor` | 9 environment probes (Rust toolchain, network, helper bridge, …) |
| `covenant lint` | 6-rule linter for Solidity-isms (L001–L006) |
| `covenant init` | Scaffold from template (token, ceremony, defi) |
| `covenant explain <code>` | Long-form explanation of a diagnostic code |
| `covenant build --target-chain` | Per-chain helper-address embedding (mockchain · sepolia · aster) |

Install: `cargo install covenant-cli --version 0.9.0`

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

## `covenant fmt` <span style="font-size:0.75em;color:#7C3AED;">V0.9</span>

Canonical source formatter — opinionated, no configuration. Same role as `gofmt` / `cargo fmt`.

```bash
covenant fmt                # format all .cov files in src/
covenant fmt --check        # CI gate — non-zero exit if reformat needed
covenant fmt --diff         # show what would change without writing
covenant fmt path/to/file   # single file
```

Idempotent: running `fmt` twice on the same input produces identical output.

## `covenant doctor` <span style="font-size:0.75em;color:#7C3AED;">V0.9</span>

Diagnose your environment. Runs 9 probes covering Rust toolchain, Cargo registry, Foundry availability, helper-bridge connectivity, RPC endpoints, and more.

```bash
covenant doctor          # human-readable summary
covenant doctor --json   # machine-readable
covenant doctor --strict # exit non-zero on any warning (CI use)
```

Each probe reports `OK` / `WARN` / `FAIL` with a remediation hint. Useful as a first step when something breaks unexpectedly.

## `covenant init` <span style="font-size:0.75em;color:#7C3AED;">V0.9</span>

Scaffold a new project from a template. Replaces the older `covenant new` (which still works as an alias).

```bash
covenant init my-token                    # default: blank record contract
covenant init --template token my-token   # ERC-20 starter
covenant init --template ceremony my-cer  # amnesia ceremony starter
covenant init --template defi my-amm      # DeFi protocol scaffold
```

The scaffold creates `covenant.toml`, `src/`, `tests/`, a sample contract, and a CI workflow.

## `covenant explain` <span style="font-size:0.75em;color:#7C3AED;">V0.9</span>

Show the long-form explanation of any diagnostic code (E0xxx for compiler errors, W0xxx for warnings, L00x for linter, C100+ for security findings).

```bash
covenant explain E0421
covenant explain L003
covenant explain C100
```

Output includes: what the diagnostic means, why it fires, common causes, and how to fix or suppress it.

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
