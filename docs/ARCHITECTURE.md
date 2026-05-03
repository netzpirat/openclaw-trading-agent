## Trading Agent Architecture (High-Level)

This document outlines the end-to-end flow of the trading agent at a conceptual level. It focuses on subsystems, data flows, and guardrails rather than specific functions.

### Subsystems
- Config/Env: Centralized runtime settings from `.env` (keys, model, assets, interval).
- Agent Runtime Loop: Schedules periodic decisions per `--interval` and coordinates all subsystems.
- Context Builder: Prepares the prompt context with authoritative exchange state, indicators, recent fills, active orders, local diary, and sampled perp mid prices.
- Decision Engine:
  - Primary LLM: Produces structured trade decisions for all assets.
  - Sanitizer LLM: Fast, schema-enforcing post-processor that coerces malformed outputs into the exact JSON array.
- Risk/Collateral Gate: Validates proposed allocations vs available capital/leverage constraints (and can scale/hold when insufficient).
- Execution Layer: Places market/trigger orders and extracts order identifiers.
- Reconciliation: Resolves local intent vs exchange truth (positions/open orders/fills), purges stale local state, and logs outcomes.
- Observability: Minimal HTTP API to fetch diary and logs for debugging/telemetry.

### Data Principles
- Authoritative Source: Exchange state (positions, open orders, fills, mids) always supersedes local intent.
- Perp-Only Pricing: Price context comes from Hyperliquid mids; no spot/perp basis mixing.
- Compact Signals: Indicators (5m/4h EMA/MACD/RSI) and short sampled price histories keep context lean and informative.
- Time Semantics: Timestamps are UTC ISO; MinutesOpen computed from stored open times.

### Robustness
- Structured Outputs: Use JSON Schema with strict mode; fallback to sanitizer.
- Retry Strategy: Single retry with stricter instruction to output array-only JSON.
- Reconciliation: Regularly remove stale active trades when no position and no orders exist; log reconcile events.
- Logging: Requests/responses and diary entries recorded locally for traceability.


