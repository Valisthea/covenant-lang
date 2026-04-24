---
title: "Tooling Equivalents"
description: "Mapping your Solidity workflow — Hardhat, Foundry, solc, slither, Remix — to the covenant CLI and its built-in tools."
section: migration
order: 5
level: reference
---

<!-- Last sync: 2026-04-23 -->

# Tooling Equivalents

You have muscle memory for a Solidity workflow. You know the shape of a Hardhat project, the feel of `forge test -vvv`, and the rhythm of running Slither before a PR. This page maps each of those to Covenant.

The short version: most of the Solidity ecosystem's separate tools are one binary in Covenant. You do not install a test runner, a linter, and a static analyzer separately.

## Tool-by-tool mapping

| Solidity | Covenant | Notes |
|---|---|---|
| Hardhat / Foundry (project mgmt) | `covenant` CLI | One binary; project layout is conventional, not configurable per-tool |
| `solc` (compiler) | `covenant build` | Compiler is a subcommand, not a separate binary |
| `forge test` / `hardhat test` | `covenant test` | Tests live inline in `test "name" { ... }` blocks |
| `forge fuzz` / Echidna | `covenant fuzz` | Property-based fuzzing built in; uses the same `invariant` syntax |
| Slither / Mythril | `covenant audit` | Static analyzer; runs by default in CI templates |
| Foundry `cast` | `covenant call` / `covenant send` | RPC calls and transactions |
| `forge script` (deploys) | `covenant deploy` | Deterministic deploy scripts declared in `deploy.cov` files |
| Remix IDE | `covenant init --example` (for now) | A hosted playground is on the roadmap — not yet shipped |
| OpenZeppelin Upgrades plugin | `covenant migrate` | Verifies storage-layout compatibility against the previous version |
| `abigen` / typechain | `covenant bindings --lang {ts,rs,py}` | Generates typed client bindings |

## The `covenant` CLI at a glance

```bash
covenant new my-project        # scaffold a new project
covenant build                 # compile
covenant test                  # run unit tests
covenant test --match deposit  # filter tests
covenant fuzz --runs 10000     # property-based fuzzing
covenant audit                 # static analysis (was: slither)
covenant bench                 # gas snapshots; diffs against previous run
covenant bindings --lang ts    # typed client bindings
covenant migrate               # storage-layout diff vs. previous deploy
covenant deploy --network mainnet
covenant call <addr> balance_of(0x...)
```

Every subcommand shares one config file: `covenant.toml`.

## `covenant.toml` — a minimal project file

This is roughly the Covenant equivalent of `hardhat.config.ts` + `foundry.toml` + `.slither.config.json` combined:

```toml
[project]
name    = "my-vault"
version = "0.1.0"
# Pin the language version explicitly — no ^ ranges.
language = "0.7"

[build]
# Output directory for compiled artifacts.
out = "target"
# Optimizer passes. 0 = debug, 3 = release.
optimize = 3
# Emit storage-layout JSON for upgrade checks.
emit_layout = true

[test]
# Default number of fuzz runs per property test.
fuzz_runs = 1000
# Fail the suite if any test exceeds this gas.
gas_ceiling = 2_000_000

[audit]
# Which rule families to run. "all" is the default.
rules = ["reentrancy", "oracle", "auth", "overflow", "fhe"]
# Rules whose findings should block CI.
deny  = ["reentrancy", "auth"]

[networks.mainnet]
rpc      = "https://rpc.covenant.network"
chain_id = 8443

[networks.testnet]
rpc      = "https://testnet-rpc.covenant.network"
chain_id = 84430
```

A fresh project from `covenant new` comes with sensible defaults — you usually only edit `[networks]` and `[audit]`.

## Project layout

```
my-project/
├── covenant.toml
├── src/
│   ├── Vault.cov
│   └── lib/
│       └── math.cov
├── tests/          # optional — tests can also live inline in src
│   └── integration.cov
├── scripts/
│   └── deploy.cov
└── target/         # build output (gitignored)
```

No separate `contracts/` and `test/` directories. Tests live wherever it is convenient — inline `test "..."` blocks in the same file as the contract, or in a `tests/` folder for multi-contract scenarios.

## Tests inline, not in a side file

A Foundry test file lives beside the contract. A Covenant test block lives *inside* the contract's source file (though a separate file also works). This is deliberate: tests are the contract's executable documentation.

```covenant
contract Vault {
    field balances: mapping<address, amount>

    action deposit(value: amount) payable { balances[caller] += value }

    test "deposit increments balance" {
        let alice = address(0xA11CE)
        impersonate(alice) { deposit(100) }
        assert balances[alice] == 100
    }

    fuzz "deposit is monotonic" (value: amount) {
        let before = balances[caller]
        deposit(value)
        assert balances[caller] >= before
    }

    invariant "total supply conserved" {
        balances.sum() == total_deposited
    }
}
```

Run them with `covenant test`. Fuzz and invariant blocks are picked up by `covenant fuzz` for longer runs in CI.

## `covenant audit` is not optional

Slither is a community tool you remember to run. `covenant audit` is a first-class subcommand wired into the default CI template. It runs:

- Reentrancy analysis (aware of `@nonreentrant`).
- Authorization gap detection (actions that mutate money-typed fields without a `guard`).
- Oracle price-freshness lints (for any field typed `price_feed`).
- Overflow / decimals-mismatch checks.
- FHE-specific checks (accidental plaintext leak via events, key-rotation staleness).

CI defaults to failing the build on findings in the `deny` list from `covenant.toml`.

## What about Remix?

A hosted playground is on the roadmap, but not yet shipped. Until then, the closest equivalent is:

```bash
covenant init --example erc20
covenant init --example vault
covenant init --example sealed-bid
```

Each spins up a ready-to-run project with tests already passing — useful for exploring a pattern without wiring up a full project.

## Moving an existing Foundry project

Pragmatic import path:

1. `covenant new --from-foundry ./my-foundry-project` — scaffolds a Covenant project with your Solidity sources copied into `legacy/`.
2. Port contracts one at a time into `src/`, starting with leaf contracts (no dependencies).
3. Use `covenant migrate --reference legacy/out/Foo.json` to check that storage layout matches, if you're preserving upgradeability.
4. Run `covenant audit` and `covenant test` at each step.

Most of the rest of this guide (especially the porting checklist on the next page) assumes this is how you're working: incrementally, with both codebases side by side.
