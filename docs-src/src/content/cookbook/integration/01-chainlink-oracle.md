---
title: "Chainlink Oracle Integration"
description: "Fetch price data from a Chainlink aggregator and use it to trigger on-chain actions."
section: cookbook
order: 1
level: intermediate
---

<!-- Last sync: 2026-04-23 -->

# Chainlink Oracle Integration

## Problem

I need my contract to use real-world price data (e.g., ETH/USD) from Chainlink to trigger actions like liquidations or pricing.

## Solution

```covenant
contract PriceTriggeredVault {
    field owner: address = deployer
    field price_feed: address          // Chainlink AggregatorV3Interface
    field liquidation_threshold: uint  // e.g., 150 = 150% collateral ratio
    field collateral: map<address, amount>
    field debt: map<address, amount>

    struct RoundData {
        round_id: uint80
        answer: int256
        started_at: uint256
        updated_at: uint256
        answered_in_round: uint80
    }

    event Deposited(user: address indexed, amount: amount)
    event Liquidated(user: address indexed, collateral: amount)

    error StalePrice()
    error InsufficientCollateral()
    error PriceFeedError()

    action deposit_collateral(amount: amount) {
        collateral[caller] = collateral[caller] + amount
        emit Deposited(caller, amount)
    }

    action liquidate(user: address) {
        let price_data = get_price()
        let col = collateral[user]
        let dbt = debt[user]

        // collateral_ratio = (collateral * price) / debt
        // liquidate if ratio < threshold
        let ratio = (col * price_data) / dbt
        given ratio < liquidation_threshold or revert_with InsufficientCollateral()

        let seized = collateral[user]
        collateral[user] = 0
        debt[user] = 0

        // Reward liquidator with 5% bonus
        transfer(caller, seized * 105 / 100)
        emit Liquidated(user, seized)
    }

    action get_price() returns (price: uint256) {
        let round = static_call(price_feed, "latestRoundData()")
            as RoundData
            or revert_with PriceFeedError()

        // Stale price check: reject if updated > 1 hour ago
        given block.timestamp - round.updated_at <= 3600 or revert_with StalePrice()
        given round.answer > 0 or revert_with PriceFeedError()

        return round.answer as uint256
    }
}
```

## Explanation

- `static_call(price_feed, "latestRoundData()")` calls the Chainlink aggregator read-only
- The stale price check (1 hour) is critical -- stale prices can cause incorrect liquidations
- Chainlink returns an `int256` (can be negative during errors) -- always check `> 0`
- The 5% liquidation bonus incentivizes keepers to call `liquidate`

## Chainlink Price Feed Addresses

| Pair | Sepolia | Ethereum Mainnet |
|------|---------|-----------------|
| ETH/USD | `0x694AA1769357215DE4FAC081bf1f309aDC325306` | `0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419` |
| BTC/USD | `0x1b44F3514812d835EB1BDB0acB33d3fA3351Ee43` | `0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88b` |
| LINK/USD | `0xc59E3633BAAC79493d908e63626716e204a45EdF` | `0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c` |

## Gas Estimate

| Operation | Gas |
|-----------|-----|
| `deposit_collateral` | ~35,000 |
| `liquidate` | ~85,000 |
| `get_price` (static call) | ~5,000 |

## Common Pitfalls

1. **Missing stale price check**: Always verify `updated_at` is recent. A 1-hour window is common; adjust for the asset\'s heartbeat.
2. **Using `answer` as price directly**: Chainlink returns 8 decimal places for USD pairs. Divide by `1e8` or scale appropriately.
3. **No fallback oracle**: If Chainlink goes down, your contract is stuck. Consider a secondary oracle or circuit breaker.
4. **Liquidation with stale price**: A stale price can allow underwater positions to remain open or force-liquidate healthy ones.
5. **Integer overflow in ratio calculation**: Multiply before divide. Use `uint256` throughout.

## See Also

- [Example 14 -- Oracle Integration](/docs/examples/14-oracle-integration)
- [Time-Locked Admin](/docs/cookbook/auth/02-time-locked-admin) -- for circuit breakers
