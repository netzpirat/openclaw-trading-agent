# Nocturne: AI Trading Agent on Hyperliquid

This project implements an AI-powered trading agent that leverages LLM models to analyze real-time market data from TAAPI, make informed trading decisions, and execute trades on the Hyperliquid decentralized exchange. The agent runs in a continuous loop, monitoring specified cryptocurrency assets at configurable intervals, using technical indicators to decide on buy/sell/hold actions, and manages positions with take-profit and stop-loss orders.

## Table of Contents

- [Disclaimer](#disclaimer)
- [Architecture](#architecture)
- [Nocturne Live Agents](#nocturne-live-agents)
- [Trading Tools & Infrastructure](#-trading-tools--infrastructure-recommended-stack)
- [Structure](#structure)
- [Env Configuration](#env-configuration)
- [Usage](#usage)
- [Tool Calling](#tool-calling)
- [Deployment to EigenCloud](#deployment-to-eigencloud)

## Disclaimer

There is no guarantee of any returns. This code has not been audited. Please use at your own risk.

## Architecture

See the full [Architecture Documentation](docs/ARCHITECTURE.md) for subsystems, data flow, and design principles.

Architecture Diagram

https://github.com/user-attachments/assets/d8f5110a-6401-42bd-b5f5-b154c7b0a418

## Nocturne Live Agents

- GPT-5 Pro: [Portfolio Dashboard](https://hypurrscan.io/address/0xa049db4b3dfcb25c3092891010a629d987d26113) | [Live Logs](https://35.190.43.182/logs/0xC0BE8E55f469c1a04c0F6d04356828C5793d8a9D) (Seeded with $200)
- DeepSeek R1: [Portfolio Dashboard](https://hypurrscan.io/address/0xa663c80d86fd7c045d9927bb6344d7a5827d31db) | [Live Logs](https://35.190.43.182/logs/0x4da68B78ef40D12f378b8498120f2F5A910Af1aD) (Seeded with $100) -- PAUSED
- Grok 4: [Portfolio Dashboard](https://hypurrscan.io/address/0x3c71f3cf324d0133558c81d42543115ef1a2be79) | [Live Logs](https://35.190.43.182/logs/0xe6a9f97f99847215ea5813812508e9354a22A2e0) (Seeded with $100) -- PAUSED

Trading tools & infrastructure

## 💡 Trading Tools & Infrastructure (Recommended Stack)

This bot is designed to work alongside a high-performance trading stack including **Solana trading bots, MEV tools, smart money trackers, and low-latency infrastructure**.

Using the right tools can significantly improve **execution speed, alpha detection, and profitability**.

> ⚡ Some links include fee discounts or access benefits.

---

### ⚡ Execution Layer (Fastest Trading Tools)

**Axiom Trade** — `solana trading bot / fast execution / low fees`

- Optimized for **on-chain trading & sniping**
- 10–30% lower trading fees
- Reliable for high-frequency execution
→ [Start using Axiom](https://axiom.trade/@423116)

**Odin Bot** — `automated trading bot / strategy execution`

- Fully automated trading strategies
- Low-latency execution engine
→ [Access Odin Bot](https://app.odinbot.io/join?code=b92mfb)

**Bloom (Telegram Bot)** — `ultra-fast solana trading bot`

- Lightweight + extremely fast execution
- Ideal for mobile + quick trades
→ [Launch Bloom](https://t.me/BloomSolana_bot?start=ref_541WLB0DZS)

---

### 📊 Alpha & Analytics (Edge Tools)

**GMGN** — `smart money tracker / early token discovery`

- Track **whales & insider activity**
- Discover tokens before they trend
→ [Explore GMGN](https://gmgn.ai/r/L53EOll4)

---

### 🧠 Advanced Trading Platforms

**Padre** — `advanced trading interface / pro tools`

- Enhanced execution controls
- Additional trading utilities
→ [Open Padre](https://trade.padre.gg/rk/423116)

**Polymarket** — `prediction market / trading signals`

- Trade on real-world outcomes
- Useful for **sentiment-driven strategies**
→ [Try Polymarket](https://polymarket.com/?r=cryptoking110600)

---

### 🖥️ Low-Latency Infrastructure (Critical for MEV)

**Recommended VPS Setup** — `low latency trading server / solana bot hosting`

For best performance, run the bot on a **New York-based VPS** (close to major trading infrastructure):
 → [Try Tradingvps.io](https://app.tradingvps.io/aff.php?aff=22)

- ⚡ Lower latency = faster execution
- 🔁 More reliable transaction inclusion
- 🧩 Better performance for MEV / sniping strategies

---

### 📈 Why This Stack Matters

Using this setup improves:

- Transaction speed (critical for sniping)
- Fill rates & execution reliability
- Access to early opportunities (alpha)

---

### ⚠️ Disclaimer

- These tools are optional and not required to run the bot
- Always test strategies before scaling
- Trading involves risk

## Structure

- `src/main.py`: Entry point, handles user input and main trading loop.
- `src/agent/decision_maker.py`: LLM logic for trade decisions (OpenRouter with tool calling for TAAPI indicators).
- `src/indicators/taapi_client.py`: Fetches indicators from TAAPI.
- `src/trading/hyperliquid_api.py`: Executes trades on Hyperliquid.
- `src/config_loader.py`: Centralized config loaded from `.env`.

## Env Configuration

Populate `.env` (use `.env.example` as reference):

- TAAPI_API_KEY
- HYPERLIQUID_PRIVATE_KEY (or LIGHTER_PRIVATE_KEY)
- OPENROUTER_API_KEY
- LLM_MODEL 
- Optional: OPENROUTER_BASE_URL (`https://openrouter.ai/api/v1`), OPENROUTER_REFERER, OPENROUTER_APP_TITLE

### Obtaining API Keys

- **TAAPI_API_KEY**: Sign up at [TAAPI.io](https://taapi.io/) and generate an API key from your dashboard.
- **HYPERLIQUID_PRIVATE_KEY**: Generate an Ethereum-compatible private key for Hyperliquid. Use tools like MetaMask or `eth_account` library. For security, never share this key.
- **OPENROUTER_API_KEY**: Create an account at [OpenRouter.ai](https://openrouter.ai/), then generate an API key in your account settings.
- **LLM_MODEL**: No key needed; specify a model name like "x-ai/grok-4" (see OpenRouter models list).

## Usage

Run: `poetry run python src/main.py --assets BTC ETH --interval 1h`

### Local API Endpoints

When the agent runs, it also serves a minimal API:

- `GET /diary?limit=200` — returns recent JSONL diary entries as JSON.
- `GET /logs?path=llm_requests.log&limit=2000` — tails the specified log file.

Configure bind host/port via env:

- `API_HOST` (default `0.0.0.0`)
- `API_PORT` or `APP_PORT` (default `3000`)

Docker:

```bash
docker build --platform linux/amd64 -t trading-agent .
docker run --rm -p 3000:3000 --env-file .env trading-agent
# Now: curl http://localhost:3000/diary
```

## Tool Calling

The agent can dynamically fetch any TAAPI indicator (e.g., EMA, RSI) via tool calls. See [TAAPI Indicators](https://taapi.io/indicators/) and [EMA Example](https://taapi.io/indicators/exponential-moving-average/) for details.

## Deployment to EigenCloud

EigenCloud (via EigenX CLI) allows deploying this trading agent in a Trusted Execution Environment (TEE) with secure key management.

### Prerequisites

- Allowlisted Ethereum account (Sepolia for testnet). Request onboarding at [EigenCloud Onboarding](https://onboarding.eigencloud.xyz).
- Docker installed.
- Sepolia ETH for deployments.

### Installation

#### macOS/Linux

```bash
curl -fsSL https://eigenx-scripts.s3.us-east-1.amazonaws.com/install-eigenx.sh | bash
```

#### Windows

```bash
curl -fsSL https://eigenx-scripts.s3.us-east-1.amazonaws.com/install-eigenx.ps1 | powershell -
```

### Initial Setup

```bash
docker login
eigenx auth login  # Or eigenx auth generate --store (if you don't have a eth account, keep this account separate from your trading account)
```

### Deploy the Agent

From the project directory:

```bash
cp .env.example .env
# Edit .env: set ASSETS, INTERVAL, API keys
eigenx app deploy
```

### Monitoring

```bash
eigenx app info --watch
eigenx app logs --watch
```

### Updates

Edit code or .env, then:

```bash
eigenx app upgrade <app-name>
```

For full CLI reference, see the [EigenX Documentation](https://github.com/Layr-Labs/eigenx-cli).
