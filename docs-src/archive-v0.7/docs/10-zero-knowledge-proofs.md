---
title: "10 — Zero-Knowledge Proofs"
description: "zk_prove and zk_verify as language primitives."
order: 10
section: "Standards"
---

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
