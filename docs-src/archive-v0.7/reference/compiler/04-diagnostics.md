---
title: "Diagnostics Catalog"
description: "Complete catalog of Covenant compiler error codes (E), warning codes (W), and LSP lint codes (L)."
section: reference
order: 4
level: reference
---

<!-- Source: doc5-compiler-architecture.md §19, doc9-cli-ux-spec.md §12 -->
<!-- Last sync: 2026-04-23 -->

# Diagnostics Catalog

The Covenant compiler uses a unified diagnostic system with three categories:

- **E-codes** — errors that halt compilation
- **W-codes** — warnings (compilation continues, but output may be suboptimal or risky)
- **L-codes** — LSP lint detectors (IDE-only, 38+ rules, do not affect CLI build)

## Diagnostic Format

All diagnostics follow the [ariadne](https://github.com/zesterer/ariadne) format — color-coded spans with source context:

```
error[E401]: type mismatch
  --> src/Token.cvt:14:20
   |
14 |     let payout = salary + bonus
   |                          ^^^^^ expected `encrypted<uint256>`, found `uint256`
   |
   = note: use `fhe_add(salary, bonus)` for homomorphic addition
```

All diagnostics include:
- Code (`E401`, `W702`, `L-UNR-001`)
- Message
- Source span(s)
- Optional `note` with fix suggestion
- Optional `help` with documentation link

## JSON Format (for tooling)

```bash
covenant check --format json ./src/Token.cvt
```

```json
{
  "diagnostics": [
    {
      "code": "E401",
      "severity": "error",
      "message": "type mismatch",
      "span": { "file": "src/Token.cvt", "start": [14, 20], "end": [14, 25] },
      "note": "use fhe_add(salary, bonus) for homomorphic addition"
    }
  ]
}
```

## E-Codes — Errors

### E100–E199: Lexer Errors

| Code | Name | Description |
|------|------|-------------|
| E101 | UnexpectedCharacter | Invalid byte in source file |
| E102 | UnterminatedString | String literal not closed before end of line |
| E103 | InvalidEscape | Unrecognized escape sequence in string |
| E104 | OverflowLiteral | Integer literal too large for any Covenant type |
| E105 | InvalidHexLiteral | Malformed hex literal (odd number of digits) |
| E110 | InvalidUnicodeCodepoint | `\u{...}` escape out of valid Unicode range |

### E200–E299: Parser Errors

| Code | Name | Description |
|------|------|-------------|
| E201 | UnexpectedToken | Token not valid at current parse position |
| E202 | MissingClosingBrace | Unmatched `{` |
| E203 | InvalidFieldType | Type expression could not be parsed |
| E204 | DuplicateField | Two fields with the same name in one contract |
| E205 | DuplicateAction | Two actions with the same name |
| E206 | InvalidGuardPlacement | Guard clause not at start of action |
| E207 | EmptyContract | Contract body has no fields or actions |
| E210 | DesugarFailed | Desugaring rule precondition not met |
| E220 | InvalidAmnesiaBlock | `amnesia { }` contains non-destructible constructs |

### E300–E399: Resolver Errors

| Code | Name | Description |
|------|------|-------------|
| E301 | UndefinedName | Identifier not declared in any enclosing scope |
| E302 | AmbiguousName | Name resolves to multiple declarations |
| E303 | CircularDependency | Import cycle detected |
| E304 | UnresolvedImport | `use` path not found |
| E305 | SelfImport | Contract imports itself |
| E310 | PrivateFieldAccess | External access to private field |
| E311 | ImmutableWrite | Write to an immutable (`const`) field |
| E320 | BuiltinShadow | User-defined name shadows a built-in |

### E400–E499: Typechecker Errors

| Code | Name | Description |
|------|------|-------------|
| E401 | TypeMismatch | Expression type incompatible with context |
| E402 | EncryptedToPlaintext | Implicit E-domain to P-domain coercion |
| E403 | PlaintextToEncryptedContext | Unencrypted value in encrypted-only context |
| E404 | InvalidFHEOperand | FHE opcode applied to non-encrypted value |
| E405 | PQKeyImmutable | Attempt to reassign a `pq_key` field |
| E406 | AddressZero | Literal `address(0)` used where disallowed |
| E410 | AmountOverflow | Constant amount arithmetic overflows uint256 |
| E411 | NegativeAmount | `amount` type cannot be negative |
| E420 | UnitMismatch | Mixing incompatible amount units |
| E430 | InvalidEventField | Event field type cannot be indexed (too large) |
| E440 | ReturnTypeMismatch | Action return type does not match declaration |

### E500–E599: Privacy Flow Errors

| Code | Name | Description |
|------|------|-------------|
| E501 | DomainViolation | E-domain value flows to P-domain output |
| E502 | RevealWithoutAuth | `reveal` missing authorization guard |
| E503 | AmnesiaEscapeAttempt | A-domain field accessed after DESTROYED phase |
| E504 | UnauthorizedDecrypt | `fhe_decrypt` called without validator auth |
| E505 | SelectiveDisclosureScope | `selective_disclosure` used outside authorized action |
| E510 | CrossContractDomainLeak | External call passes E-domain to non-ERC-8227 contract |
| E511 | EventDataLeak | E-domain value emitted in event data |

### E600–E699: IR Builder Errors

| Code | Name | Description |
|------|------|-------------|
| E601 | InfiniteLoop | Unbounded loop without exit condition |
| E602 | StackOverflow | Estimated stack depth exceeds EVM limit (1024) |
| E603 | ContractSizeExceeded | Generated bytecode exceeds 24 KB (EIP-170) |
| E604 | InvalidPhi | Phi node has wrong number of predecessors |
| E610 | FHEDepthLimit | Multiplication depth exceeds BFV capacity (requires bootstrapping) |
| E620 | AmnesiaPhaseViolation | A-domain operation outside valid ceremony phase |

### E800–E899: Backend / Codegen Errors

| Code | Name | Description |
|------|------|-------------|
| E801 | UnsupportedOpcode | IR opcode not supported by selected backend |
| E802 | PrecompileUnavailable | Required precompile not available on target chain |
| E803 | ABIEncodingError | ABI encoding of type not possible |
| E810 | AsterFeatureUnavailable | Feature requires Aster Chain (not EVM) |
| E811 | WASMUnsupported | Feature not yet supported in WASM backend |

### E900–E999: Internal Compiler Errors

| Code | Name | Description |
|------|------|-------------|
| E999 | InternalError | Compiler bug — please report with `covenant bug-report` |

## W-Codes — Warnings

### W300–W399: Resolver Warnings

| Code | Name | Description |
|------|------|-------------|
| W301 | Shadowing | Name shadows an outer scope declaration |
| W302 | UnusedImport | Imported name never used |
| W303 | UnusedField | Field declared but never read or written |

### W400–W499: Typechecker Warnings

| Code | Name | Description |
|------|------|-------------|
| W401 | ImplicitConversion | Widening conversion applied implicitly |
| W410 | UnusedReturnValue | Action return value discarded at call site |

### W500–W599: Privacy Warnings

| Code | Name | Description |
|------|------|-------------|
| W501 | RevealToAll | `reveal field to all` exposes encrypted state globally |
| W502 | AmnesiaExternalCall | External call inside `on_destroy` hook (reentrancy risk) |
| W503 | PartialDestruction | `amnesia` block has fields not listed in any `destroy()` |

### W700–W799: Optimizer Warnings

| Code | Name | Description |
|------|------|-------------|
| W701 | UnreachableCode | Branch that can never be taken |
| W702 | ConstantField | Field only ever assigned once (consider `const`) |
| W703 | ExpensiveGasPattern | Detected pattern with known high gas cost |
| W710 | FHEDepthExceeded | Multiplication depth near BFV limit |
| W711 | FHEBatchMissed | Adjacent FHE ops not batched (optimizer limitation) |

## L-Codes — LSP Lint Detectors

The LSP runs 38 lint detectors in the IDE. These never block compilation but appear as squiggles/hints.

### Security Lints (L-SEC-*)

| Code | Description |
|------|-------------|
| L-SEC-001 | Missing `only` guard on state-modifying action |
| L-SEC-002 | Unchecked external call return value |
| L-SEC-003 | Reentrancy risk: external call before state update |
| L-SEC-004 | Unrestricted `destroy()` outside ceremony |
| L-SEC-005 | `pq_signed` missing on high-value action (> 1M token threshold) |
| L-SEC-006 | `admin` field can be changed by `admin` itself (no 2-step transfer) |
| L-SEC-007 | FHE multiplication depth > 6 (bootstrapping cost warning) |
| L-SEC-008 | Hardcoded address (should use a field) |
| L-SEC-009 | Missing `ReentrancyGuard` on action with external call |
| L-SEC-010 | Integer division before multiplication (precision loss) |

### Privacy Lints (L-PVT-*)

| Code | Description |
|------|-------------|
| L-PVT-001 | Event emits encrypted value without confidential flag |
| L-PVT-002 | `reveal` without time-lock or deadline |
| L-PVT-003 | Selective disclosure to `all` (defeats privacy) |
| L-PVT-004 | Map key (address) exposed in events |
| L-PVT-005 | Cross-contract domain leak potential |

### Style Lints (L-STY-*)

| Code | Description |
|------|-------------|
| L-STY-001 | Action name should be `snake_case` |
| L-STY-002 | Field name should be `snake_case` |
| L-STY-003 | Contract name should be `PascalCase` |
| L-STY-004 | Missing `description` on public action |
| L-STY-005 | Magic number (use named constant) |
| L-STY-006 | Redundant `given true` guard |
| L-STY-007 | Empty `amnesia { }` block |

### Gas Lints (L-GAS-*)

| Code | Description |
|------|-------------|
| L-GAS-001 | `map<address, bool>` for whitelists (use `set<address>`) |
| L-GAS-002 | Unnecessary storage read in loop |
| L-GAS-003 | String error message (use typed error instead) |
| L-GAS-004 | Event emission in loop (high gas risk) |
| L-GAS-005 | `fhe_encrypt` inside loop |

### Correctness Lints (L-COR-*)

| Code | Description |
|------|-------------|
| L-COR-001 | Comparison with `address(0)` without null check |
| L-COR-002 | Overflow-unsafe arithmetic in `unchecked` block |
| L-COR-003 | Missing zero-check on `amount` parameter |
| L-COR-004 | Action callable during ceremony DESTROYED phase |
| L-COR-005 | `on_destroy` hook modifies state after `destroy()` |
| L-COR-006 | `total_supply` updated but not mirroring `balances` sum |
| L-COR-007 | Guard relies on `block.timestamp` (miner-manipulable, ±15s) |
| L-COR-008 | Self-transfer allowed (may inflate event logs) |

## Suppressing Diagnostics

```covenant
// Suppress a specific warning for one line
#[allow(W301)]
let shadow = outer_name

// Suppress for an entire action
#[allow(W702, L-GAS-001)]
action expensive_init() only deployer { ... }
```

Using `#[allow(...)]` on an E-code is a compile error — errors cannot be suppressed.

## See Also

- [Compiler Pipeline](/docs/reference/compiler/01-pipeline) — which phase emits which codes
- [LSP Reference](/docs/reference/lsp/01-lsp-overview) — how lint codes appear in the IDE
- [Security: Known Pitfalls](/docs/security/known-pitfalls) — common patterns behind L-SEC-* lints
