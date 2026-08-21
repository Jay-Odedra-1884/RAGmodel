<div align="center">

> [!WARNING]
> 🚧 &nbsp;**UNDER ACTIVE DEVELOPMENT** &nbsp;·&nbsp; Not production-ready &nbsp;·&nbsp; Breaking changes expected &nbsp;🚧

# 🎙️ Voice RAG

### Voice-Enabled Retrieval-Augmented Generation Pipeline
#### HH Goa 2026 — Shortlisting Task 2

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC143C?style=for-the-badge)
![Claude](https://img.shields.io/badge/Claude-Haiku-7C3AED?style=for-the-badge)

</div>

---

## 📌 Overview

A production-grade voice-enabled RAG pipeline. Speak a question → pipeline transcribes it → retrieves relevant context from MSMARCO-XI → returns a grounded answer — all under **200ms**.

```
🎙️ Voice  →  📝 STT (Sarvam)  →  🔍 Retrieve (Qdrant)  →  🤖 Generate (Claude)  →  ✅ Answer
```

---

## ⚡ Latency Budget

| Stage | Budget |
|---|---|
| Query embed | ~5ms |
| Qdrant search | ~3ms |
| MMR re-rank | ~1ms |
| Claude Haiku | ~80ms |
| Guardrails | ~2ms |
| **Total (excl. STT)** | **~91ms ✓** |
| STT (Sarvam, network) | ~100ms (measured separately) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Next.js Frontend                     │
│         (Black/Purple UI · Port 3000)                    │
└────────────────────┬────────────────────────────────────┘
                     │ /api/* proxy
┌────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                        │
│                    (Port 8000)                           │
│                                                          │
│  POST /query/voice ──► STT ──► Guardrails ──► Retrieve  │
│  POST /query/text  ──────────► Guardrails ──► Retrieve  │
│                                                  │       │
│                                               Generate   │
│                                                  │       │
│                                             Guardrails   │
│                                          (post-gen check)│
└──────────────────────────────────────────────────────────┘
         │                        │
┌────────▼────────┐    ┌──────────▼──────────┐
│  Qdrant (local) │    │   Claude Haiku API   │
│  In-memory      │    │   (Anthropic)        │
│  3 chunk types  │    └─────────────────────┘
└─────────────────┘
```

---

## 🧠 Chunking Strategy

Three strategies run at index time — each chunk is tagged with its strategy as metadata:

| Strategy | Config | Use case |
|---|---|---|
| **Fixed-size** | 256 tokens, 32-token overlap | Broad coverage |
| **Semantic** | Sentence boundaries, ~512 token merge | Context coherence |
| **Metadata-aware** | Passage ID + query header prepended | Precision retrieval |

---

## 🛡️ Guardrails

| Check | When | Action |
|---|---|---|
| Off-topic detection | Pre-retrieval | Reject with message |
| Unsafe input | Pre-retrieval | Reject with message |
| Low retrieval score | Post-retrieval | "Not enough context" |
| Grounding check | Post-generation | Strip answer, return fallback |

---

## 📁 Project Structure

```
RAGmodel/
├── main.py                  # FastAPI app
├── load_dataset.py          # One-time dataset downloader
├── benchmark.py             # P50/P70/P100 latency runner
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pipeline/
│   ├── chunker.py           # 3-strategy chunking
│   ├── indexer.py           # Qdrant upsert + snapshot
│   ├── stt.py               # Sarvam STT wrapper
│   ├── retriever.py         # Embed → search → MMR
│   ├── generator.py         # Claude Haiku harness
│   └── guardrails.py        # Pre/post checks
├── frontend/                # Next.js 15 App Router
│   ├── src/app/
│   │   ├── page.tsx         # Main UI
│   │   ├── layout.tsx
│   │   └── globals.css      # Black/purple theme
│   └── package.json
└── data/
    ├── raw_passages.jsonl   # T2 output
    ├── chunks.jsonl         # T3 output
    └── qdrant_snapshot/     # T4 output
```

---

## 🚀 Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Sarvam API key → [console.sarvam.ai](https://console.sarvam.ai)
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)

### 1. Clone & configure

```bash
git clone <repo-url>
cd RAGmodel
copy .env.example .env
# Fill in SARVAM_API_KEY and ANTHROPIC_API_KEY in .env
```

### 2. Backend

```bash
pip install -r requirements.txt
python load_dataset.py          # one-time, downloads ~1GB
python -m pipeline.indexer      # one-time, builds vector index
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:3000
```

### 4. Benchmark

```bash
python benchmark.py
# Outputs latency_report.json with P50/P70/P100
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/query/text` | Text query → answer |
| `POST` | `/query/voice` | Audio file → answer |
| `GET` | `/health` | Pipeline status + index stats |
| `GET` | `/metrics` | Latest latency report |

**Request — `/query/text`**
```json
{ "query": "What is retrieval augmented generation?" }
```

**Response**
```json
{
  "answer": "RAG combines retrieval...",
  "sources": ["passage_001", "passage_042"],
  "grounded": true,
  "latency_ms": { "embed": 4.2, "search": 2.8, "generate": 78.3, "total": 91.1 }
}
```

---

## 📊 Dataset

**ai4bharat/MSMARCO-XI** — Multilingual MS MARCO  
Languages: `en`, `hi`, `bn`, `ta`, `te`, `ml`, `mr`, `pa`, `gu`, `or`  
Splits: `train` / `validation` / `test`  
Default: 50,000 English passages indexed

---

## 🐳 Docker

```bash
docker compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## 👥 Team

Built for **HH Goa 2026** · Deadline: August 22, 2026

---

<div align="center">

**#RAGInGoa**

</div>
