# 🐾 OpenClaw — AI Trading Agent for Hyperliquid

OpenClaw is an **AI-powered trading agent** that uses LLMs to analyze real-time market data, generate trading decisions, and execute trades on the Hyperliquid decentralized exchange.

Built for **automation, low-latency execution, and strategy experimentation**, OpenClaw continuously monitors markets, evaluates technical indicators, and manages positions with risk controls.

---

## 🚀 Features

* 🤖 LLM-driven trading decisions (multi-model support)
* 📊 Real-time technical analysis via TAAPI
* ⚡ Automated trade execution on Hyperliquid
* 🔁 Continuous trading loop with configurable intervals
* 🛡️ Built-in risk management (TP / SL logic)
* 🔌 Tool-calling support for dynamic indicator queries
* 📡 Lightweight API for logs & trade diary

---

## 📚 Table of Contents

* [Disclaimer](#disclaimer)
* [Architecture](#architecture)
* [Live Agents](#live-agents)
* [Trading Stack](#-trading-stack-recommended-tools--infrastructure)
* [Project Structure](#project-structure)
* [Environment Setup](#environment-setup)
* [Usage](#usage)
* [Tool Calling](#tool-calling)
* [Deployment (EigenCloud)](#deployment-eigencloud)

---

## ⚠️ Disclaimer

This project is experimental and unaudited.
There is **no guarantee of profitability**. Use at your own risk.

---

## 🏗️ Architecture

See full documentation:
→ `docs/ARCHITECTURE.md`

Architecture diagram:

https://github.com/user-attachments/assets/d8f5110a-6401-42bd-b5f5-b154c7b0a418

---

## 📡 Live Agents

* **GPT-5 Pro** — Portfolio + Logs (active)
* **DeepSeek R1** — paused
* **Grok 4** — paused

*(Replace with your updated endpoints if needed)*

---

# 💡 Trading Stack (Recommended Tools & Infrastructure)

OpenClaw is designed to integrate with a high-performance stack including **trading bots, MEV tools, analytics platforms, and low-latency infrastructure**.

Using the right stack improves:

* ⚡ Execution speed
* 📈 Alpha discovery
* 🎯 Trade accuracy

---

## ⚡ Execution Layer

**Axiom Trade**

* Fast on-chain execution
* Reduced fees (10–30%)
  → [Access](https://axiom.trade/@423116)

**Odin Bot**

* Automated strategies
* Low-latency execution
  → [Access](https://app.odinbot.io/join?code=b92mfb)

**Bloom (Telegram Bot)**

* Ultra-fast trading interface
  → [Launch](https://t.me/BloomSolana_bot?start=ref_541WLB0DZS)

---

## 📊 Analytics & Alpha

**GMGN**

* Smart money tracking
* Early token discovery
  → [Explore](https://gmgn.ai/r/L53EOll4)

---

## 🧠 Advanced Platforms

**Padre**

* Advanced execution tools
  → [Open](https://trade.padre.gg/rk/423116)

**Polymarket**

* Prediction-based trading
  → [Try](https://polymarket.com/?r=cryptoking110600)

---

## 🖥️ Infrastructure

**Low-Latency VPS (New York Recommended)**

* Faster transaction propagation
* Better execution reliability
* Ideal for bots & MEV strategies

→ [Get VPS](https://app.tradingvps.io/aff.php?aff=22)

---

## 📁 Project Structure

```
src/
├── main.py                  # Entry point / trading loop
├── agent/
│   └── decision_maker.py   # LLM decision engine
├── indicators/
│   └── taapi_client.py     # TAAPI integration
├── trading/
│   └── hyperliquid_api.py  # Trade execution
└── config_loader.py        # Env config loader
```

---

## ⚙️ Environment Setup

Create `.env` (see `.env.example`):

```
TAAPI_API_KEY=
HYPERLIQUID_PRIVATE_KEY=
OPENROUTER_API_KEY=
LLM_MODEL=
```

Optional:

```
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
API_PORT=3000
```

---

## ▶️ Usage

```bash
poetry run python src/main.py --assets BTC ETH --interval 1h
```

---

## 🌐 Local API

* `/diary` → trade history
* `/logs` → runtime logs

---

## 🧠 Tool Calling

Supports dynamic indicator fetching via TAAPI:

* EMA
* RSI
* Custom indicators

---

## ☁️ Deployment (EigenCloud)

Run inside a **TEE (Trusted Execution Environment)** for secure key handling.

### Install

```bash
curl -fsSL https://eigenx-scripts.s3.us-east-1.amazonaws.com/install-eigenx.sh | bash
```

### Deploy

```bash
eigenx app deploy
```

### Monitor

```bash
eigenx app logs --watch
```

---

## ⚠️ Notes

* Tools listed are optional
* Performance depends on latency + strategy quality
* Always test before scaling

---
