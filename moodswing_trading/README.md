# MoodSwing Trading API

**MoodSwing Trading (MST)** is a real-time market insight platform that ingests financial news, processes sentiment, and produces probabilistic price forecasts for a curated set of tickers.

The service exposes a well-structured **FastAPI** backend, backed by **PostgreSQL** with partitioned storage and **Redis** for both caching and real-time event streaming. It supports both **REST** and **WebSocket** delivery to serve dashboards, analytical clients, and automated trading workflows.

---

## 📌 Overview

**Core capabilities:**

* **Live market data** — OHLC history, intraday quotes, WebSocket tick streaming
* **Enriched news** — Hourly ingestion, sentiment classification, source weighting
* **Sentiment metrics** — Aggregated MoodScore (0–100) blended with prior day, optional LLM rationale
* **Probabilistic forecasts** — Hourly & EOD μ/σ projections via ONNX-optimised models

**Technology stack:**

* **FastAPI** (async I/O) under **Uvicorn**
* **Redis** for caching & Pub/Sub
* **PostgreSQL 15+** (validated on 17) with list partitioning by ticker
* **Celery** for scheduled/background jobs
* **ONNX Runtime** for prediction inference
* **Docker** for containerisation
* **Prometheus** for metrics and observability

---

## 📊 Data Flow

The following diagram shows how data moves from external providers to API consumers.

```text
            ┌───────────────┐
            │  External APIs│
            │ (AV, yfinance,│
            │  GoogleNews)  │
            └───────┬───────┘
                    │
     [Hourly/5s]    │
                    ▼
             ┌─────────────┐
             │ Celery Tasks│
             │  - NewsIngest
             │  - Sentiment
             │  - Predict
             └──────┬──────┘
                    │
         Writes to  ▼
           ┌─────────────────┐
           │ PostgreSQL (R/W)│
           │  article        │
           │  sentiment_day  │
           │  prediction     │
           └───────┬─────────┘
                   │
        Publishes  ▼
          ┌───────────────────┐
          │ Redis (cache+WS)  │
          └────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │ FastAPI Endpoints  │
         │ REST + WebSockets  │
         └────────┬───────────┘
                  │
        Serves    ▼
      ┌───────────────────────┐
      │ Dashboards / Clients  │
      └───────────────────────┘
```

---

## 📂 Repository Structure

```
moodswing_trading/
├─ api/              # FastAPI routers
├─ core/             # Config, logging, scheduler, Celery app
├─ db/               # SQLAlchemy models, CRUD helpers
├─ services/         # External API integrations, business logic
├─ tasks/            # Celery scheduled jobs
├─ utils/            # Shared utilities
└─ main.py           # FastAPI app factory
```

---

## 🚀 Quickstart

### Requirements

* **Docker** & **Docker Compose**
* **Alpha Vantage API key** (for live market data)
* Optional: **OpenAI API key** (for LLM rationale generation)

### Local Development

```bash
git clone https://github.com/your-org/moodswing-trading.git
cd moodswing-trading
cp .env.example .env  # Configure API keys and settings
docker-compose up --build
```

The API will be available at:

```
http://localhost:8000/api/v1
```

---

## 📡 Example Usage

### Latest sentiment

```bash
curl http://localhost:8000/api/v1/sentiment/TSLA/latest
```

### Subscribe to live price ticks

```bash
wscat -c ws://localhost:8000/api/v1/stocks/TSLA/stream
```

---

## 📜 Appendix A — Implementation Notes

* **WebSocket rate limits:** Implemented via WS control frames (not HTTP headers)
* **Prediction TTL:** Dynamic TTL aligns to the next hourly run (minimum 60 s)
* **Partition management:** Native partitioned parents with DEFAULT partitions; hygiene task only
* **Cold export:** Optional, disabled by default
* **LLM rationale:** Feature-flagged; MVP may fall back to summariser (non-LLM)
* **Logging:** Minimal JSON formatter; trace IDs planned for later
* **Latency targets:** HTTP p95 ≤ 400 ms, WS ≤ 200 ms (excluding upstream provider latency)

---

**Full API reference:** See [`docs/api-spec.md`](../docs/api-spec.md)
