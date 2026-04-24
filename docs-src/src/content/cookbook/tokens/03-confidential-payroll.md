---
title: "Confidential Payroll"
description: "An encrypted payroll contract where salary amounts are hidden from all parties except the employee and authorized auditors."
section: cookbook
order: 3
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Confidential Payroll

## Problem

I need a payroll system where salary amounts are hidden on-chain. Only the employee can see their own salary; an auditor can see all salaries under a regulatory disclosure order.

## Solution

```covenant
encrypted token PayrollToken {
    name: "Payroll Credit"
    symbol: "PAY"
    decimals: 6
    supply: 0 tokens
    initial_holder: deployer

    field hr_admin: address = deployer
    field auditor: address

    event EmployeeRegistered(employee: address indexed)
    event SalaryPaid(employee: address indexed)
    event AuditDisclosureGranted(auditor: address indexed)

    error EmployeeNotFound()
    error ZeroAddress()

    action register_employee(employee: address, salary: encrypted<amount>)
        only hr_admin {
        given employee != address(0) or revert_with ZeroAddress()
        balances[employee] = salary
        emit EmployeeRegistered(employee)
    }

    action pay_salary(employee: address) only hr_admin {
        given balances[employee] != fhe_encrypt(0, network_key)
            or revert_with EmployeeNotFound()

        // Re-encrypt current balance as a new payment record
        let current = balances[employee]
        let doubled = fhe_add(current, current)   // simulate doubling on payday
        balances[employee] = doubled
        emit SalaryPaid(employee)
    }

    action view_my_salary() {
        // Employee-initiated: reveals only their own salary
        reveal balances[caller] to caller
    }

    action audit_disclosure(employee: address) only auditor {
        // Regulator-authorized disclosure
        reveal balances[employee] to auditor
    }
}
```

## Explanation

- `encrypted token` generates an ERC-8227-compliant contract -- all balances are BFV ciphertexts
- `register_employee` stores the salary as an encrypted value; HR sees the plaintext at time of registration but it is never stored plaintext on-chain
- `fhe_add(current, current)` performs homomorphic doubling without decrypting -- the operation happens on ciphertexts
- `reveal ... to caller` triggers the ERC-8227 threshold decryption protocol for the caller\'s own balance
- `reveal ... to auditor` requires the `only auditor` guard -- only the authorized auditor can request regulatory disclosure

The auditor field should be a multisig or DAO-controlled address to prevent unilateral disclosure.

## Gas Estimate

| Operation | Gas (L1) | pGas (Aster) |
|-----------|---------|-------------|
| `register_employee` | ~120,000 | ~12,000 |
| `pay_salary` | ~160,000 | ~16,000 |
| `view_my_salary` (initiate) | ~220,000 | ~22,000 |
| `audit_disclosure` | ~220,000 | ~22,000 |

FHE operations are 10x cheaper on Aster Chain. For payroll at scale, deploy on Aster.

## Common Pitfalls

1. **HR sees plaintext at registration**: The salary is plaintext in the `register_employee` transaction calldata. Use encrypted calldata (Aster feature) or a commit-reveal scheme if HR should not see individual salaries.
2. **Auditor address hardcoded at deploy**: Use a field + `hr_admin` guard to allow auditor rotation.
3. **No employee list**: The contract does not maintain a list of employees. Add a `field employees: set<address>` if you need to iterate.
4. **Homomorphic multiplication depth**: If your payroll logic has >6 levels of `fhe_mul`, you will hit BFV depth limits. Use `@prove_offchain` for complex calculations.
5. **Missing emit on disclosure**: Always emit an event when a disclosure happens for auditability.

## See Also

- [ERC-8227 -- Encrypted Tokens](/docs/reference/ercs/02-erc-8227-fhe)
- [Example 08 -- Encrypted Token](/docs/examples/08-encrypted-token)
- [Privacy: Private Voting](/docs/cookbook/privacy/02-private-voting)
