---
title: "Compiler Pipeline"
description: "The ten phases of the Covenant compiler: from source text to verified bytecode."
section: reference
order: 1
level: reference
---

<!-- Source: doc5-compiler-architecture.md chapters 1-19 -->
<!-- Last sync: 2026-04-23 -->

# Compiler Pipeline

The Covenant compiler (`covc`) transforms source files through ten sequential phases. Each phase has a well-defined input, output, and error class.

## The Ten Phases

| # | Phase | Input | Output | Error range |
|---|-------|-------|--------|-------------|
| 1 | Lexer | UTF-8 source | Token stream | E100–E199 |
| 2 | Parser | Tokens | AST | E200–E299 |
| 3 | Resolver | Unresolved AST | Bound AST | E300–E399 |
| 4 | Typechecker | Bound AST | Typed AST | E400–E499 |
| 5 | Privacy Flow | Typed AST | Domain-annotated AST | E500–E599 |
| 6 | IR Builder | Annotated AST | SSA IR | E600–E699 |
| 7 | Optimizer | SSA IR | Optimized IR | W700–W799 |
| 8 | Backend | Optimized IR | Backend IR | E800–E899 |
| 9 | Codegen | Backend IR | Bytecode + ABI | E800–E899 |
| 10 | Metadata | Bytecode + ABI | .artifact.json | — |

## Phase 1 — Lexer

**Input**: Raw UTF-8 source text  
**Output**: Token stream  
**Error codes**: E100–E199

The lexer handles keywords, numeric literals (decimal, hex `0x…`, underscore separators), string literals, comments (`//` and `/* */`), and FHE type tokens (`encrypted<`, `sealed`).

Common errors:
- `E101 UnexpectedCharacter` — invalid byte in source
- `E102 UnterminatedString` — missing closing `"`
- `E103 InvalidEscape` — unknown escape sequence
- `E104 OverflowLiteral` — integer literal exceeds any Covenant type

## Phase 2 — Parser

**Input**: Token stream  
**Output**: AST (after desugaring)  
**Error codes**: E200–E299

A hand-written recursive-descent PEG parser. Desugaring rules:

- `token Foo { }` → `contract Foo extends __ERC20Token { }`
- `encrypted token Foo { }` → `contract Foo extends __ERC8227Token { }`
- `only owner` → `given caller == owner or revert_with Unauthorized()`
- `when condition` → `given condition or revert_with PreconditionFailed()`

Common errors:
- `E201 UnexpectedToken`
- `E202 MissingClosingBrace`
- `E203 InvalidFieldType`

## Phase 3 — Resolver

**Input**: AST with unresolved names  
**Output**: AST with all names bound  
**Error codes**: E300–E399

Builds a scope tree, resolves imports (`use covenant::stdlib::*`), detects circular dependencies, and binds built-ins (`caller`, `block.timestamp`, `deployer`).

Common errors:
- `E301 UndefinedName`
- `E302 AmbiguousName`
- `E303 CircularDependency`
- `E310 PrivateFieldAccess`

## Phase 4 — Typechecker

**Input**: Resolved AST  
**Output**: Typed AST  
**Error codes**: E400–E499

Hindley-Milner extended for Covenant domain types: `amount` (non-negative, unit-tracked), `encrypted<T>` (FHE ciphertext), `pq_key` (2,592-byte opaque blob), `address`.

Key type rules:
- `encrypted<T>` cannot flow to plaintext without explicit `reveal`
- `pq_key` is immutable once assigned
- Constant `amount` arithmetic is overflow-checked at compile time

Common errors:
- `E401 TypeMismatch`
- `E402 EncryptedToPlaintext` — implicit ciphertext coercion
- `E410 AmountOverflow`
- `E420 UnitMismatch`

## Phase 5 — Privacy Flow Analyzer

**Input**: Typed AST  
**Output**: Domain-annotated AST  
**Error codes**: E500–E599

Enforces the two-domain model:
- **P domain** — public, visible on-chain
- **E domain** — encrypted FHE ciphertext
- **A domain** — amnesia-eligible (inside `amnesia { }` blocks)

E-domain values cannot flow to P-domain outputs without an authorized `reveal`. Amnesia-eligible fields cannot be read after the ceremony reaches DESTROYED.

Common errors:
- `E501 DomainViolation`
- `E502 RevealWithoutAuth`
- `E503 AmnesiaEscapeAttempt`
- `E510 CrossContractDomainLeak`

## Phase 6 — IR Builder

**Input**: Annotated typed AST  
**Output**: SSA IR  
**Error codes**: E600–E699

Lowers AST to Static Single Assignment form. Each variable assigned exactly once; control flow uses phi nodes. See [Intermediate Representation](/docs/reference/compiler/02-ir).

## Phase 7 — Optimizer

**Input**: SSA IR  
**Output**: Optimized SSA IR  
**Warning codes**: W700–W799

22 passes (not errors, cannot break compilation):

1. Constant folding
2. Dead code elimination
3. Common subexpression elimination
4. Guard inlining
5. Bounded loop unrolling
6. FHE operation batching
7. Storage slot packing
8. Event deduplication
9. Revert string deduplication
10. Gas cost canonicalization
11–22. Backend-specific peephole passes

Key warnings:
- `W701 UnreachableCode`
- `W702 ConstantField`
- `W710 FHEDepthExceeded` — multiplication depth will require bootstrapping

## Phase 8 — Backend Selection

**Input**: Optimized IR  
**Output**: Backend-lowered IR  
**Error codes**: E800–E899

Available backends: `evm` (default), `aster`, `wasm` (experimental V0.8+). See [Compiler Targets](/docs/reference/compiler/03-targets).

## Phase 9 — Codegen

Produces raw EVM bytecode. Handles the selector dispatcher, constructor, PUSH/JUMPDEST layout. Aster backend emits Aster VM opcodes instead.

## Phase 10 — Metadata Emission

Emits `.artifact.json`:

```json
{
  "compiler": "covc 0.7.4",
  "contract": "MyContract",
  "abi": [],
  "bytecode": "0x608060...",
  "metadata": {
    "erc_compliance": ["8227"],
    "compliance_profile": "CL2",
    "optimizer": {"passes": 22},
    "audit": {"report": "OMEGA V4", "findings": 41, "resolved": 41}
  }
}
```

## Running Individual Phases

```bash
covenant inspect ast ./src/Contract.cvt   # stop after parsing
covenant check ./src/Contract.cvt          # stop after typechecking
covenant inspect ir ./src/Contract.cvt    # emit optimized IR
covenant build ./src/Contract.cvt          # full build
```

## Performance Targets

| Phase | Target (1000-line contract) |
|-------|----------------------------|
| Lexer + Parser | < 50ms |
| Resolver | < 30ms |
| Typechecker | < 100ms |
| Privacy flow | < 80ms |
| IR + Optimizer | < 250ms |
| Codegen + Metadata | < 140ms |
| **Total** | **< 650ms** |

## See Also

- [Intermediate Representation](/docs/reference/compiler/02-ir)
- [Compiler Targets](/docs/reference/compiler/03-targets)
- [Diagnostics Catalog](/docs/reference/compiler/04-diagnostics)
- [LSP Reference](/docs/reference/lsp/01-lsp-overview)
