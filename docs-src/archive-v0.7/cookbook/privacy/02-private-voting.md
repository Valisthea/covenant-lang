---
title: "Private Voting"
description: "A DAO voting system where ballots are confidential until the tally, preventing vote manipulation based on early results."
section: cookbook
order: 2
level: advanced
---

<!-- Last sync: 2026-04-23 -->

# Private Voting

## Problem

I need a DAO where members vote on proposals but ballots are kept secret until the voting period ends, preventing "follow the whale" dynamics.

## Solution

```covenant
contract PrivateVoting {
    field admin: address = deployer
    field proposal_count: uint = 0

    field proposals: map<uint, Proposal>
    field votes: map<uint, map<address, encrypted<bool>>>
    field has_voted: map<uint, map<address, bool>>

    struct Proposal {
        title: text
        deadline: time
        yes_count: encrypted<uint>
        no_count: encrypted<uint>
        finalized: bool
        result: bool
    }

    event ProposalCreated(id: uint indexed, title: text, deadline: time)
    event VoteCast(proposal_id: uint indexed, voter: address indexed)
    event ProposalFinalized(id: uint indexed, passed: bool)

    error ProposalNotFound()
    error VotingClosed()
    error AlreadyVoted()
    error NotFinalized()
    error AlreadyFinalized()

    action create_proposal(title: text, duration: time) only admin returns (id: uint) {
        let id = proposal_count
        proposals[id] = Proposal {
            title: title,
            deadline: block.timestamp + duration,
            yes_count: fhe_encrypt(0, network_key),
            no_count: fhe_encrypt(0, network_key),
            finalized: false,
            result: false
        }
        proposal_count = proposal_count + 1
        emit ProposalCreated(id, title, block.timestamp + duration)
        return id
    }

    action vote(proposal_id: uint, encrypted_vote: encrypted<bool>) {
        let p = proposals[proposal_id]
        given block.timestamp < p.deadline or revert_with VotingClosed()
        given !has_voted[proposal_id][caller] or revert_with AlreadyVoted()

        has_voted[proposal_id][caller] = true
        votes[proposal_id][caller] = encrypted_vote

        // Homomorphic tally update (no decryption)
        proposals[proposal_id].yes_count = fhe_add(
            p.yes_count,
            fhe_mul(encrypted_vote, fhe_encrypt(1, network_key))
        )
        proposals[proposal_id].no_count = fhe_add(
            p.no_count,
            fhe_mul(fhe_sub(fhe_encrypt(1, network_key), encrypted_vote), fhe_encrypt(1, network_key))
        )

        emit VoteCast(proposal_id, caller)
    }

    action finalize(proposal_id: uint) only admin {
        let p = proposals[proposal_id]
        given block.timestamp >= p.deadline or revert_with VotingClosed()
        given !p.finalized or revert_with AlreadyFinalized()

        // Threshold decryption reveals tally
        let yes = reveal proposals[proposal_id].yes_count to all
        let no = reveal proposals[proposal_id].no_count to all

        proposals[proposal_id].finalized = true
        proposals[proposal_id].result = yes > no
        emit ProposalFinalized(proposal_id, yes > no)
    }
}
```

## Explanation

- Votes are `encrypted<bool>` -- `true` = yes, `false` = no
- The running tally is updated homomorphically in each `vote` call -- no one can read the partial tally during voting
- `finalize` triggers threshold decryption only after the deadline -- both yes and no counts are revealed simultaneously
- `has_voted` is a plaintext map (addresses are not private in this design -- only vote contents are)

## Gas Estimate

| Operation | Gas (L1) | pGas (Aster) |
|-----------|---------|-------------|
| `create_proposal` | ~100,000 | ~10,000 |
| `vote` | ~280,000 | ~28,000 |
| `finalize` | ~250,000 | ~25,000 |

## Common Pitfalls

1. **Plaintext vote addresses**: `VoteCast` events reveal who voted. If voter anonymity is required, use a commitment scheme (commit-reveal) instead.
2. **Single admin finalizes**: For trustless finalization, allow anyone to call `finalize` after the deadline.
3. **Tally during voting**: The encrypted yes/no counts are visible as ciphertexts -- they don\'t leak vote totals but do leak "number of votes cast" indirectly via event count.
4. **FHE depth**: The `fhe_mul(encrypted_vote, ...)` adds a multiplication level. Keep vote logic simple to stay within BFV depth limits.

## See Also

- [ZK Airdrop](/docs/cookbook/privacy/03-zk-airdrop)
- [ERC-8227 -- Encrypted Tokens](/docs/reference/ercs/02-erc-8227-fhe)
- [ERC-8229 -- FHE Verification Standard](/docs/reference/ercs/04-erc-8229-fhe-verify)
