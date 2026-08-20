# HH Goa 2026 — Voice-Enabled RAG Model: Build Plan

## Stack Decision

| Layer | Choice | Why |
|---|---|---|
| STT | Sarvam AI | Indian-focused, REST API, good Hindi/English |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Fast, local, 384-dim |
| Vector DB | **Qdrant** (in-memory mode) | <5ms search, no server needed for dev |
| LLM | Claude `claude-haiku-4-5-20251001` | Fastest Claude, structured output |
| Backend | FastAPI | Async, easy streaming |
| Frontend | **Next.js 15** (App Router) | Black/purple gradient theme, TypeScript |
| Dataset | `ai4bharat/MSMARCO-XI` | HuggingFace datasets |

---

## Tasks (implement one at a time)

### T1 — Project scaffold & env
- `requirements.txt`, `.env.example`, folder structure
- **No code logic yet** — just the skeleton

### T2 — Dataset loader
- Download `ai4bharat/MSMARCO-XI` (English split, passages column)
- Save raw passages to `data/raw_passages.jsonl`
- Quick stats print (count, avg length)

### T3 — Chunking pipeline (the hard part)
Three strategies, all run at index time, stored with `strategy` metadata:

| Strategy | Detail |
|---|---|
| **Fixed-size** | 256 tokens, 32-token overlap |
| **Semantic** | Split on sentence boundaries, merge until ~512 tokens |
| **Metadata-aware** | Keep passage ID + query context as a header chunk |

Output: `data/chunks.jsonl` — each chunk has `{id, text, strategy, passage_id, metadata}`

### T4 — Vector DB indexing
- Embed all chunks with `sentence-transformers`
- Upsert into Qdrant in-memory collection
- Save collection snapshot to `data/qdrant_snapshot/` for fast reload
- Target: full index load < 2s on startup

### T5 — Speech-to-text (Sarvam)
- `POST /v1/speech-to-text` with audio bytes
- Wrapper: `stt.py` → `transcribe(audio_bytes) -> str`
- Fallback: if Sarvam fails, raise `STTError` (no silent swallow)

### T6 — Retrieval pipeline
- Embed query → search Qdrant (top-k=5, all strategies)
- Re-rank by MMR (max marginal relevance) to avoid duplicate chunks
- Return `List[Chunk]` with scores

### T7 — Answer generation harness
- Claude call with structured tool output: `{answer: str, grounded: bool, sources: List[str]}`
- Retry up to 2x on malformed output
- Timeout: 3s hard cap per LLM call

### T8 — Guardrails
Four checks, run **before** LLM call:
1. **Off-topic**: cosine similarity of query embedding vs corpus centroid < threshold → reject
2. **Unsafe input**: keyword + regex blocklist
3. **Empty retrieval**: if top chunk score < 0.3 → "I don't have enough context"
4. **Post-generation grounding**: if `grounded=false` from LLM → strip answer, return fallback

### T9 — Latency analytics
- `LatencyTracker` class: wraps each pipeline stage with `time.perf_counter()`
- After N queries: print P50/P70/P100 per stage and end-to-end
- `benchmark.py` — runs 50 canned queries, dumps `latency_report.json`

### T10 — FastAPI backend
Endpoints:
- `POST /query/text` — text in, answer out (skips STT)
- `POST /query/voice` — audio file in, answer out (full pipeline)
- `GET /health` — pipeline status + index stats
- `GET /metrics` — latest latency report

### T11 — Frontend (single HTML)
- Mic button → `MediaRecorder` → WAV blob → `POST /query/voice`
- Shows: transcript, retrieved chunks (collapsible), answer, latency breakdown
- No framework, plain JS

### T12 — Docker + deployment
- `Dockerfile` — multi-stage, copies snapshot, no re-index on startup
- `docker-compose.yml` — single service
- Deploy target: Railway / Render (free tier, public URL for submission)

---

## File layout (end state)

```
RAGmodel/
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── main.py              # FastAPI app
├── pipeline/
│   ├── chunker.py       # T3
│   ├── indexer.py       # T4
│   ├── stt.py           # T5
│   ├── retriever.py     # T6
│   ├── generator.py     # T7
│   └── guardrails.py    # T8
├── benchmark.py         # T9
├── frontend/
│   └── index.html       # T11
└── data/
    ├── raw_passages.jsonl
    ├── chunks.jsonl
    └── qdrant_snapshot/
```

---

## Latency budget (200ms target)

| Stage | Budget |
|---|---|
| STT (Sarvam) | ~100ms (network, not counted in local pipeline) |
| Query embed | ~5ms |
| Qdrant search | ~3ms |
| Re-rank (MMR) | ~1ms |
| LLM (Haiku) | ~80ms |
| Guardrails | ~2ms |
| **Total (no STT)** | **~91ms** ✓ |

STT is a network call — budget it separately, document it in latency report.

---

## Implementation order

```
T1 → T2 → T3 → T4 → T6 → T9(partial) → T7 → T8 → T5 → T10 → T11 → T9(full) → T12
```

Tell me which task to start with (e.g. "implement T1").
