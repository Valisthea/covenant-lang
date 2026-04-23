---
title: "Installation"
description: "Install the Covenant CLI and VS Code extension."
order: 1
---

# Installation

Covenant ships as a single Rust binary published to crates.io. Installation takes under two minutes.

## Prerequisites

- **Rust** 1.75 or later — install via [rustup.rs](https://rustup.rs)
- **Cargo** (bundled with Rust)
- **Node.js** 18+ (optional — for the VS Code extension only)

Verify your Rust installation:

```bash
rustc --version
# rustc 1.75.0 (82e1608df 2023-12-21) or later
```

## Install the CLI

```bash
cargo install covenant-cli
```

This downloads and compiles the `covenant` binary from crates.io. First install takes 2–4 minutes (compiling ~19 crates).

Verify:

```bash
covenant --version
# covenant 0.7.0
```

## Install the VS Code Extension

1. Open VS Code
2. Open the Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`)
3. Search for **"Covenant"**
4. Click **Install** on the extension by *Kairos Lab*

The extension provides:
- Syntax highlighting for `.cov` files
- Real-time lint diagnostics (38+ detectors)
- Auto-complete for keywords, types, and built-ins
- Hover documentation
- Go-to-definition for contract fields and actions

The extension works on Windows, macOS, Linux, and via VS Code for the Web.

## Verify the language server

After installing the extension, open any `.cov` file. You should see syntax highlighting immediately. Within 2–3 seconds the language server starts and diagnostics appear in the Problems panel.

If the language server does not start, check the Output panel → "Covenant Language Server" for error messages. The most common cause is a missing or outdated `covenant-cli` in your PATH.

## Update

```bash
cargo install covenant-cli --force
```

The `--force` flag re-installs even if the version number matches, ensuring you have the latest build.

## Uninstall

```bash
cargo uninstall covenant-cli
```

Then uninstall the VS Code extension from the Extensions panel.

## Next

→ [02 — First Contract](/getting-started/02-first-contract)
