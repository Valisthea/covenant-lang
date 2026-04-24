---
title: "Language Server Protocol"
description: "Covenant LSP capabilities: diagnostics, hover, completion, go-to-definition, and the 38 lint detectors. Setup for VS Code, Neovim, and IntelliJ."
section: reference
order: 1
level: reference
---

<!-- Source: doc10-lsp-specification.md -->
<!-- Last sync: 2026-04-23 -->

# Language Server Protocol

The Covenant language server (`covenant-lsp`) implements [LSP 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) and provides IDE intelligence for `.cvt` files. It ships inside the `covenant-cli` binary — no separate installation needed.

## Capabilities

| Capability | Status | Notes |
|-----------|--------|-------|
| Diagnostics (on save) | ✅ Full | All E/W/L codes |
| Diagnostics (on type) | ✅ Full | < 100ms latency |
| Hover | ✅ Full | Type + domain + docs |
| Go-to-definition | ✅ Full | Fields, actions, events, errors |
| Find references | ✅ Full | Cross-file |
| Rename symbol | ✅ Full | Safe rename with preview |
| Autocomplete | ✅ Full | Context-aware |
| Signature help | ✅ Full | FHE opcodes + stdlib |
| Code formatting | ✅ Full | `covenant fmt` |
| Inline hints | ✅ Full | Type + domain labels |
| Semantic tokens | ✅ Full | Full syntax theme |
| Code actions | ✅ Partial | 12 quick-fix actions |
| Inlay hints | ✅ Full | Domain P/E labels |
| Workspace symbols | ✅ Full | Search all contracts |
| Document outline | ✅ Full | Fields, actions, events tree |
| Folding ranges | ✅ Full | Block folding |
| Call hierarchy | 🔲 Planned | V0.8 |
| Type hierarchy | 🔲 Planned | V0.8 |

## Installation

### VS Code (Primary Support)

Install from the VS Code Marketplace:

```bash
# Via CLI
code --install-extension valisthea.covenant-lang

# Or search "Covenant" in the VS Code Extensions panel
```

The extension bundles `covenant-lsp` and starts it automatically when you open a `.cvt` file. No PATH configuration needed.

**Minimum requirements**: VS Code 1.85+, Node.js 18+ (for the extension host).

### Neovim

Install with your plugin manager, then configure with nvim-lspconfig:

```lua
-- lazy.nvim
{
  "neovim/nvim-lspconfig",
  config = function()
    require("lspconfig").covenant_lsp.setup({
      cmd = { "covenant", "lsp" },
      filetypes = { "covenant" },
      root_dir = require("lspconfig.util").root_pattern("covenant.toml"),
    })
  end,
}
```

Treesitter grammar for Covenant (syntax highlighting):
```bash
:TSInstall covenant
```

### IntelliJ / JetBrains IDEs

Install the "Covenant Language" plugin from JetBrains Marketplace. The plugin connects to `covenant lsp` via the LSP4IJ bridge. Requires IntelliJ 2024.1+ or any 2024+ JetBrains IDE.

**Note**: IntelliJ support is community-maintained. Feature parity with VS Code is ~80%. Code actions and quick-fixes have limited support.

## Lint Detectors

The LSP runs 38 lint detectors across four categories. These appear as squiggles in the editor and in the Problems panel. See [Diagnostics Catalog](/docs/reference/compiler/04-diagnostics) for the full list.

### Security lints (L-SEC-001 to L-SEC-010)

The most important category. `L-SEC-003` (reentrancy risk) detects the Checks-Effects-Interactions pattern violation — the pattern behind most DeFi exploits:

```covenant
// L-SEC-003: external call before state update
action withdraw(amount: amount) only owner {
    transfer(caller, amount)      // <- external call FIRST
    balances[caller] -= amount    // <- state update SECOND (reentrancy!)
}

// Correct: CEI pattern
action withdraw(amount: amount) only owner {
    balances[caller] -= amount    // 1. Effects
    transfer(caller, amount)      // 2. Interaction
}
```

### Privacy lints (L-PVT-001 to L-PVT-005)

`L-PVT-001` fires when an event emits an encrypted value without the `@confidential` flag. This is a common mistake: the event value is encrypted in storage but the event itself would leak the ciphertext to public indexers.

### Gas lints (L-GAS-001 to L-GAS-005)

`L-GAS-001` detects `map<address, bool>` used as a whitelist — the standard pattern wastes gas. The suggestion: use `set<address>` which stores membership via trie, not individual storage slots.

### Correctness lints (L-COR-001 to L-COR-008)

`L-COR-007` warns when a guard uses `block.timestamp`. Miners can manipulate `block.timestamp` by up to ~15 seconds, which is enough to break deadline-based mechanics in high-frequency trading or MEV-sensitive contracts.

## Hover

Hovering over any identifier shows:
- **Fields**: type, domain (P/E/A), storage slot, default value
- **Actions**: signature, guards, gas estimate
- **Events**: fields, indexed status
- **Errors**: parameters, common cause
- **FHE opcodes**: gas cost, domain requirements, precompile address
- **Built-ins**: description, type

Example hover for `fhe_add`:
```
fhe_add(a: encrypted<T>, b: encrypted<T>) -> encrypted<T>

Homomorphic addition. Domain: E -> E.
Precompile: 0x10. Gas: 8,000 (L1) / 400 pGas (Aster).
ERC-8227 §3.2.
```

## Autocomplete

Context-aware completion:
- After `only ` → suggests field names of type `address`
- After `fhe_` → shows all FHE opcodes with signatures
- After `event ` → shows declared events
- After `revert_with ` → shows declared errors
- After `emit ` → shows declared events
- Inside `amnesia { }` → shows `destroy()`, `on_destroy`
- After `@` → shows available annotations (`pq_signed`, `prove_offchain`, `amnesia_eligible`)

## Configuration

The LSP reads `covenant.toml` in the workspace root:

```toml
[lsp]
# Lint severity overrides (error/warning/hint/off)
L-GAS-003 = "off"          # disable string error lint
L-SEC-005 = "warning"       # downgrade PQ recommendation

# Inline hints
inlay_hints = true
domain_labels = true        # show P/E/A labels on expressions
gas_estimates = true        # show gas cost hints on FHE ops

# Formatting
indent = "4spaces"          # or "2spaces", "tabs"
trailing_newline = true
max_line_length = 100
```

## Performance

The LSP is designed for large workspaces:

| Metric | Target |
|--------|--------|
| First-open diagnostic latency | < 500ms |
| On-type diagnostic latency | < 100ms |
| Completion latency | < 50ms |
| Go-to-definition | < 20ms |
| Workspace indexing (100 files) | < 5s |

The LSP maintains an in-memory cache of all parsed contracts. Incremental re-parsing only re-analyzes the changed file and its dependents.

## Known Issues

- **V0.7**: Rename symbol does not work across external contract references (only within the same file/import tree). Fixed in V0.8.
- **V0.7**: IntelliJ integration does not show inline domain labels. Workaround: use hover.
- **V0.7**: Workspace symbols does not index contracts inside `node_modules`. By design; add `covenant.toml` to project root.

## Reporting Bugs

```bash
covenant lsp-report
```

This command generates a diagnostic bundle (LSP logs + contract snapshot) for filing issues at [github.com/Valisthea/covenant-lang/issues](https://github.com/Valisthea/covenant-lang/issues).

## See Also

- [Diagnostics Catalog](/docs/reference/compiler/04-diagnostics) — full L-code list
- [Compiler Pipeline](/docs/reference/compiler/01-pipeline) — how the LSP reuses compiler phases
- [Getting Started: CLI Reference](/docs/getting-started/03-cli-reference) — `covenant lsp` command
