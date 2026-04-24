---
title: "Known Pitfalls"
description: "Common mistakes and vulnerabilities to avoid when writing Covenant contracts."
order: 4
section: "Security"
---

# Known Pitfalls

This page documents known pitfalls in Covenant development — gotchas that are not caught by the compiler alone.

## 1. FHE key scope confusion

**Pitfall:** Encrypting values with `fhe_owner_key()` when the intended decryptor is the user.

`fhe_owner_key()` resolves to the contract deployer's public key. If users need to decrypt their own data, they must provide their own public key:

```covenant
// WRONG: user cannot decrypt this
self.user_secret[msg.sender] = fhe_encrypt(value, fhe_owner_key());

// CORRECT: encrypt under the caller's registered PQ/FHE key
self.user_secret[msg.sender] = fhe_encrypt(value, self.user_fhe_keys[msg.sender]);
```

## 2. Amnesia applied to event-indexed fields

Events are permanent — they live in the transaction receipt log, which is not part of state. If you `delete` a field and emit an event containing the old value, the value is preserved forever in the log:

```covenant
// DANGEROUS: old_value is now permanently in the event log
amnesia {
  let old_value = self.secret;
  delete self.secret;
  emit SecretRevoked(old_value);   // compiler error in v0.7 — catches this
}
```

The compiler emits an error if you reference an amnesia-deleted field in an `emit` statement.

## 3. Reentrancy in `@view` actions

`@view` actions cannot mutate state — but they **can** make external calls that trigger side effects in other contracts. This is not reentrancy in the classical sense but can cause issues with flash-loan-style attacks on downstream contracts.

Use `@staticcall` to enforce read-only external calls from `@view` actions.

## 4. Beacon proxy storage slot collisions

When adding fields to a beacon implementation, never insert new fields before existing ones. The proxy's stored data is a flat byte array indexed by slot number. Inserting a field shifts all subsequent slots, corrupting all existing proxy state.

Always **append** new fields or use a gap field from the start (see chapter 12).

## 5. `block.timestamp` manipulation

Validators can adjust `block.timestamp` by ±15 seconds. Never use it as the sole source of randomness or for fine-grained timing logic:

```covenant
// DANGEROUS for values < 15 seconds
require(block.timestamp >= self.unlock_time, NotYet);

// Use block numbers for more reliable sequencing on EVM
require(block.number >= self.unlock_block, NotYet);
```

## 6. `msg.value` in delegatecall context

If a contract uses `delegatecall` (proxy patterns), `msg.value` is available to the implementation. But if the proxy receives ETH in one call and delegates to the implementation without forwarding `msg.value`, the ETH is silently locked in the proxy.

Covenant's `deploy_beacon_proxy` built-in handles this correctly. Only use raw `delegatecall` if you understand the value-forwarding implications.

## 7. PQ signature replay

Dilithium3 signatures are deterministic — the same (message, key) always produces the same signature. Without a nonce, an observer who intercepts a signed transaction can replay it:

```covenant
// Include nonce in the signed message
action pq_withdraw(amount: u256, nonce: u256, pq_sig: Bytes) {
  verify_pq_sig_with_nonce(msg.sender, amount, nonce, pq_sig);
  require(!self.used_nonces[nonce], NonceReused);
  self.used_nonces[nonce] = true;
  // ...
}
```

## 8. ZK proof front-running

When a user submits a ZK proof transaction, an observer on the mempool can copy the proof and submit their own transaction with the same proof, claiming the reward before the original submitter. Bind the proof to `msg.sender`:

```covenant
// Public input must include msg.sender so the proof only works for the original caller
action claim_reward(proof: ZkProof, pub_inputs: Bytes) {
  // pub_inputs must encode msg.sender — enforced by the circuit
  require(decode_address(pub_inputs) == msg.sender, WrongCaller);
  require(zk_verify(REWARD_CIRCUIT, proof, pub_inputs), InvalidProof);
  // ...
}
```

## 9. Unchecked ERC-20 return values

Some ERC-20 tokens (USDT on mainnet) return no value from `transfer`. The Covenant interface definition requires a `-> Bool` return value — calling a non-returning token through this interface will revert. Use a safe-transfer wrapper for unknown tokens:

```covenant
action safe_transfer(token: Address, to: Address, amount: u256) {
  let ok = call(token, abi_encode("transfer(address,uint256)", to, amount), value: 0);
  require(ok.success && (ok.data.len == 0 || abi_decode<Bool>(ok.data)), TransferFailed);
}
```
