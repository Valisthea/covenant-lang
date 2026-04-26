---
title: "08 — Encrypted Token"
description: "ERC-20 with FHE-encrypted balances."
order: 8
section: "Standards"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


# 08 — Encrypted Token

Combine the ERC-20 pattern from chapter 06 with `encrypted<u256>` balances so no on-chain observer can read balances or transfer amounts.

```covenant
contract EncryptedToken {
  field name:   String = "PrivaCoin"
  field symbol: String = "PVC"
  field decimals: u8   = 18

  // Balances are FHE ciphertexts — observers see only random-looking bytes
  field balances: Map<Address, encrypted<u256>>
  // Total supply is public for transparency
  field total_supply: u256

  event EncryptedTransfer(from: indexed Address, to: indexed Address)

  error InsufficientEncryptedBalance

  init(initial_supply: u256) {
    self.total_supply = initial_supply;
    self.balances[msg.sender] = fhe_encrypt(initial_supply, fhe_owner_key());
  }

  // Transfer: caller provides encrypted amount; contract checks ciphertext > balance
  action private_transfer(to: Address, enc_amount: encrypted<u256>) {
    let sender_bal = self.balances[msg.sender];
    // fhe_lt returns encrypted<Bool> — no plaintext comparison
    let is_sufficient = fhe_lt(enc_amount, sender_bal);
    // require works on encrypted<Bool> — reverts if ciphertext decrypts to false
    require(is_sufficient, InsufficientEncryptedBalance);

    self.balances[msg.sender] = fhe_sub(sender_bal, enc_amount);
    self.balances[to]         = fhe_add(self.balances[to], enc_amount);
    emit EncryptedTransfer(from: msg.sender, to: to);
  }

  // Let the owner decrypt a specific balance (for auditing)
  action audit_balance(addr: Address) -> u256 {
    only(owner);
    return fhe_decrypt(self.balances[addr], fhe_owner_key());
  }
}
```

## How the viewer key works

The `fhe_owner_key()` built-in resolves to the public key stored in the contract's deployment metadata. Only the holder of the corresponding private key can decrypt. This is analogous to the **Viewer Pass** mechanism on Aster Chain — selective disclosure without exposing data to the validator set.

## Client-side encryption

Off-chain code that calls `private_transfer` must encrypt the amount before submitting:

```js
import { CovenantClient, fheEncrypt } from "@covenant-lang/sdk";

const client  = new CovenantClient(provider);
const pubkey  = await client.fhePubkey(contractAddress);
const encAmt  = await fheEncrypt(1000n, pubkey);     // Uint8Array ciphertext
await contract.private_transfer(recipient, encAmt);
```

## Limitations

- FHE balances cannot be read by block explorers without the owner key.
- `fhe_lt` with 256-bit integers costs ~200 M gas on standard EVM; use Aster Chain or a dedicated L2 with native FHE precompiles for production.
- ERC-20 `allowance` / `transferFrom` pattern requires an encrypted allowance map — left as an exercise (see the `examples/encrypted-allowances` repo).
