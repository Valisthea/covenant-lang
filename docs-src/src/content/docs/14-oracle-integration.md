---
title: "14 — Oracle Integration"
description: "Integrate price feeds and off-chain data with Covenant's oracle primitives."
order: 14
section: "Advanced"
---

<div style="border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;margin-bottom:24px;font-size:0.95em;color:#3d3d3d;">
  <strong style="color:#b45309;">⚠ This example is being rewritten against the verified V0.8 syntax.</strong>
  The code shown may use a pre-V0.8 sketch that will not compile as-is. For the canonical, compiler-verified V0.8 examples — every one of them derived from a compiler test fixture — see the <a href="https://playground.covenant-lang.org/examples" style="color:#7C3AED;">Playground Examples gallery</a>. The 4 reference examples already updated on this site: <a href="/docs/examples/01-hello-contract" style="color:#7C3AED;">Hello</a>, <a href="/docs/examples/06-erc20-token" style="color:#7C3AED;">ERC-20 Token</a>, <a href="/docs/examples/07-fhe-basics" style="color:#7C3AED;">FHE Basics</a>, <a href="/docs/examples/11-cryptographic-amnesia" style="color:#7C3AED;">Cryptographic Amnesia</a>. The remaining ones land in Sprint 29.
</div>


# 14 — Oracle Integration

Oracles bridge off-chain data (prices, randomness, weather, etc.) into your contracts. Covenant provides built-in interfaces for the most common oracle patterns.

## Chainlink-compatible price feed

```covenant
interface IAggregatorV3 {
  @view action latestRoundData() -> (
    roundId:       u80,
    answer:        i256,
    startedAt:     u256,
    updatedAt:     u256,
    answeredInRound: u80
  )
  @view action decimals() -> u8
}

contract PriceConsumer {
  field eth_usd_feed: Address

  init(feed: Address) {
    self.eth_usd_feed = feed;
  }

  @view
  action get_eth_price() -> u256 {
    let feed = IAggregatorV3(self.eth_usd_feed);
    let (_, answer, _, updatedAt, _) = feed.latestRoundData();
    // Staleness check: reject price older than 1 hour
    require(updatedAt >= block.timestamp - 3600, StalePrice);
    require(answer > 0, NegativePrice);
    let dec = feed.decimals();          // typically 8
    // Normalise to 18 decimals
    return u256(answer) * 10u256.pow(18 - u256(dec));
  }
}
```

## Aster Chain native oracle

Aster Chain's validator set posts a stake-weighted median price for all listed assets at every block. Access it via the built-in `oracle_price` primitive:

```covenant
action get_btc_price() -> u256 {
  // Built-in — no external call needed on Aster Chain
  return oracle_price("BTC/USD");
}
```

The oracle is sourced from a median of 14 CEXes, weighted by validator stake. Use `oracle_price_at(symbol, block)` for historical queries.

## Chainlink VRF (verifiable randomness)

```covenant
interface IVRFCoordinatorV2 {
  action requestRandomWords(
    keyHash:              Bytes32,
    subId:                u64,
    confirmations:        u16,
    callbackGasLimit:     u32,
    numWords:             u32
  ) -> u256
}

contract Lottery {
  field coordinator: Address
  field requests:    Map<u256, Address>   // requestId -> player

  action enter() {
    let coordinator = IVRFCoordinatorV2(self.coordinator);
    let requestId = coordinator.requestRandomWords(
      keyHash:          KEY_HASH,
      subId:            SUBSCRIPTION_ID,
      confirmations:    3,
      callbackGasLimit: 100000,
      numWords:         1
    );
    self.requests[requestId] = msg.sender;
  }

  // Called by VRF coordinator with the random result
  action fulfillRandomWords(requestId: u256, randomWords: List<u256>) {
    only(self.coordinator);
    let winner = self.requests[requestId];
    // Use randomWords[0] to pick outcome
    let outcome = randomWords[0] % 6;
    emit LotteryResult(winner, outcome);
  }
}
```

## Push oracle pattern

For custom off-chain data pushed by a trusted reporter:

```covenant
contract DataFeed {
  field reporter: Address
  field latest_value: u256
  field latest_ts:    u256

  action submit(value: u256) {
    only(self.reporter);
    self.latest_value = value;
    self.latest_ts    = block.timestamp;
    emit ValueUpdated(value, block.timestamp);
  }

  @view
  action get() -> (u256, u256) {
    return (self.latest_value, self.latest_ts);
  }
}
```
