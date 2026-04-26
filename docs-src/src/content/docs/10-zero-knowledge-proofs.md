---
title: "10 — Zero-Knowledge Proofs"
description: "zk_prove and zk_verify as language primitives."
order: 10
section: "Standards"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


# 10 — Zero-Knowledge Proofs

Zero-knowledge proofs let a prover convince a verifier that a statement is true without revealing the witness (secret input). Covenant exposes ZK as `zk_prove` / `zk_verify` — scheme-agnostic, circuit-agnostic language primitives.

## Basic pattern

```covenant
contract AgeVerifier {
  // Anyone can verify a ZK proof that the caller is >= 18
  // without learning the actual birthdate.
  action prove_adult(proof: ZkProof, pub_inputs: Bytes) {
    let circuit = Circuit("age_18_plus_v1");   // circuit ID registered at deployment
    require(
      zk_verify(circuit, proof, pub_inputs),
      InvalidProof
    );
    emit AdultVerified(msg.sender);
  }
}
```

## Supported schemes

Configure in `covenant.toml`:

```toml
[zk]
scheme = "groth16"   # groth16 | plonk | halo2 | fflonk
```

| Scheme | Proof size | Verify gas | Trusted setup |
|--------|-----------|------------|---------------|
| Groth16 | ~200 B | ~280 K | Per-circuit |
| PLONK | ~800 B | ~600 K | Universal |
| Halo2 | ~1.2 KB | ~900 K | None |
| fflonk | ~256 B | ~350 K | Universal |

## Generating proofs off-chain

```js
import { CovenantProver } from "@covenant-lang/zk-sdk";

const prover  = new CovenantProver("age_18_plus_v1");
const witness = { birthdate: 19900101n, today: 20260101n };
const { proof, publicInputs } = await prover.prove(witness);

await contract.prove_adult(proof, publicInputs);
```

## Circuit registration

Circuits are deployed as precompile registrations at contract init time:

```covenant
init() {
  register_circuit("age_18_plus_v1", circuit_vk: AGE_VK_BYTES);
}
```

`AGE_VK_BYTES` is the verification key, embedded at compile time via `@embed("circuits/age.vk")`.

## `zk_prove` (on-chain proving)

For small circuits, Covenant can prove on-chain using the chain's native zkVM precompile:

```covenant
action commit(secret: u256) {
  let pub_hash = zk_prove(
    circuit: "pedersen_commit_v1",
    private_inputs: [secret],
    public_inputs: []
  );
  self.commitments[msg.sender] = pub_hash;
}
```

On-chain proving is only practical for circuits with < 2^16 constraints. For larger circuits, use off-chain proving + `zk_verify`.

## Recursive proofs

```covenant
action verify_rollup_batch(
  inner_proofs: List<ZkProof>,
  aggregated_proof: ZkProof,
  pub_inputs: Bytes
) {
  let agg_circuit = Circuit("plonk_aggregator_v2");
  require(zk_verify(agg_circuit, aggregated_proof, pub_inputs), BadAggregation);
  // Each inner proof is verified by the aggregator circuit itself
}
```
