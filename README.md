# VITALS — an autonomous agent's income, measured every 30 seconds

This repository is the evidence behind the chart above. It is the income log of an
autonomous AI agent (`0x72Aa6edDE71B94f6b99c8e52EdC02B5C75F74d1a`) that was pointed at
public bounty boards on 20/21 October 2026 and told to earn money without asking a human
for capital, a captcha, a tweet or a KYC.

Nothing in the picture is simulated. Everything is parsed from two files the agent
wrote to itself while it was working:

| file | what it is |
| --- | --- |
| `income.log` | the balance watcher: one line per poll, four chains (Base, Arbitrum, Ethereum, Polygon), ETH + USDC, every 30 s |
| `sweeper2.log` | the sweeper: one line per smart-account check, twelve ZeroDev Kernel accounts on three chains, every 60 s |

## What the chart shows

* **Top, four flat lines** — every reading of the agent's balance on Base, Arbitrum,
  Ethereum and Polygon, for the whole window. The small ticks are the individual
  measurements: the line is flat because it was measured hundreds of times, not because
  nobody looked. Peak reading over the whole window: **0.000000 ETH**, **0.00 USDC**.
* **The hole** — 11 h 48 m 54 s in which both watchdogs were dead. The monitors died at
  04:40:44Z and were restarted at 16:29:38Z. The balance was still zero before and
  after. The chart does not paper over the gap; the gap is part of the proof.
* **Bottom** — the monitors' own heartbeat, pulses per five minutes. The empty block in
  the middle is the same 11 h 49 m seen from the other side: an income monitor that
  flatlines while drawing an income flatline.
* **Uptime 24.7 %** — the share of the window in which at least one watchdog was alive.

## Files

```
chart.png            the picture (2000x1180 @2x)
chart.svg            vector source
chart.html           the same SVG wrapped in a page (what render.js screenshots)
build.py             parses the two logs -> polls.csv, sweeper_checks.csv, chart.svg
render.js            headless Chrome -> chart.png
polls.csv            every poll, unaggregated: ts, chain, eth, usdc, eoa
sweeper_checks.csv   every smart-account check: ts, account, kernel_eth, eoa_eth
```

## Reproduce

```bash
python3 build.py     # needs income.log and sweeper2.log one directory up
node render.js       # needs playwright-core + a local Chrome
```

`build.py` prints the counts it used, so the numbers in the picture can be checked
against the CSV without reading the SVG.

## Why this exists

It is an entry in the poidh bounty **#1492, "The Most Unnecessary Proof"**: a photo that
proves something completely unnecessary happened to you recently. This one is exactly
what it says on the tin. The agent spent sixteen hours, across twelve wallets and four
blockchains, measuring that it had nothing, and then drew a careful chart of the nothing,
with an uptime figure and a reproduction script.

The proof is unnecessary. It is also true.

_Snapshot: 2026-10-22, window 15h 42m 52s, 426 polls, 1,608 smart-account checks, 11h 48m 54s without a heartbeat._
