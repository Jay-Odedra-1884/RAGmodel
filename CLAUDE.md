# Voice RAG — Project Context for Claude

## What this is
HH Goa 2026 hackathon submission — a voice-enabled RAG pipeline.
Deadline: **August 22, 2026**.

Pipeline: `Voice → STT (Sarvam) → Chunking → Qdrant retrieval → Claude Haiku → Answer`

Full spec is in `PLAN.md`. This file tracks status, decisions, and constraints.

---

## Task Status

| Task | Status | File |
|---|---|---|
| T1 — Scaffold | ✅ Done | `requirements.txt`, `.env.example`, `main.py`, `pipeline/` stubs |
| T2 — Dataset loader | ✅ Code done, **needs manual run** | `load_dataset.py` |
| T3 — Chunking pipeline | ⏳ Next | `pipeline/chunker.py` |
| T4 — Vector DB indexing | ⏳ Pending | `pipeline/indexer.py` |
| T5 — STT wrapper | ⏳ Pending | `pipeline/stt.py` |
| T6 — Retrieval + MMR | ⏳ Pending | `pipeline/retriever.py` |
| T7 — Generator harness | ⏳ Pending | `pipeline/generator.py` |
| T8 — Guardrails | ⏳ Pending | `pipeline/guardrails.py` |
| T9 — Latency analytics | ⏳ Pending | `benchmark.py` |
| T10 — FastAPI backend | ⏳ Pending | `main.py` |
| T11 — Next.js UI | ⏳ Pending | `frontend/src/app/page.tsx` |
| T12 — Docker + deploy | ⏳ Pending | `Dockerfile`, `docker-compose.yml` |

**Manual run needed before T3:**
```bash
pip install -r requirements.txt
python load_dataset.py
# Creates data/raw_passages.jsonl (~50k passages)
```

---

## Key Decisions (don't revisit these)

| Decision | Choice | Reason |
|---|---|---|
| STT provider | Sarvam | Indian-focused, REST API |
| Vector DB | Qdrant in-memory | <5ms search, no server needed |
| LLM | Claude `claude-haiku-4-5-20251001` | Fastest Claude, fits 200ms budget |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Fast local, 384-dim |
| Frontend | **Next.js 15 App Router** | User explicitly requested (not single HTML) |
| UI theme | Black + purple gradient | `#0a0a0a` base, `#7c3aed` → `#4f46e5` |
| Backend | FastAPI on port 8000 | Async, easy streaming |
| Frontend port | 3000 | Proxies `/api/*` → FastAPI via `next.config.ts` |

---

## Constraints (hard requirements from spec)

- End-to-end latency **< 200ms** (STT measured separately)
- **3 chunking strategies** minimum: fixed-size, semantic, metadata-aware
- **P50 / P70 / P100** latency numbers required in submission
- LLM call must use a **harness** — structured output, retries, timeout
- **Guardrails** required: off-topic, unsafe input, low-score retrieval, post-gen grounding check
- Dataset: `ai4bharat/MSMARCO-XI` from HuggingFace

---

## Python Version Warning

**Use Python 3.12, not 3.14.**

Python 3.14 breaks `orjson` and `pydantic-core` (no pre-built wheels, requires MSVC linker to build from source). All packages have wheels for 3.12.

```bash
# If you have both installed:
py -3.12 -m pip install -r requirements.txt
py -3.12 load_dataset.py
```

---

## Implementation Order

```
T1 ✅ → T2 ✅ → T3 → T4 → T6 → T7 → T8 → T5 → T10 → T11 → T9 → T12
```

T5 (STT) comes after the core pipeline is working so it can be tested end-to-end.
T9 (latency) comes last so it benchmarks the full pipeline.

---

## File Layout (current)

```
RAGmodel/
├── CLAUDE.md               ← you are here
├── PLAN.md                 ← full task specs + latency budget
├── README.md               ← user-facing docs
├── requirements.txt        ← Python deps (use Python 3.12)
├── .env.example            ← copy to .env, fill API keys
├── main.py                 ← FastAPI stub (T10 fills this)
├── load_dataset.py         ← T2: run once to get data
├── benchmark.py            ← T9: latency runner stub
├── pipeline/
│   ├── chunker.py          ← T3 stub
│   ├── indexer.py          ← T4 stub
│   ├── stt.py              ← T5 stub
│   ├── retriever.py        ← T6 stub
│   ├── generator.py        ← T7 stub
│   └── guardrails.py       ← T8 stub
├── frontend/               ← Next.js 15 App Router
│   ├── next.config.ts      ← proxies /api/* → :8000
│   ├── tailwind.config.ts  ← black/purple design tokens
│   └── src/app/
│       ├── globals.css     ← glass cards, glow rings, gradient text
│       ├── layout.tsx
│       └── page.tsx        ← T11 stub
└── data/
    ├── raw_passages.jsonl  ← T2 output (run load_dataset.py)
    ├── chunks.jsonl        ← T3 output
    └── qdrant_snapshot/    ← T4 output
```

---

## API Keys Needed

| Key | Where to get |
|---|---|
| `SARVAM_API_KEY` | console.sarvam.ai |
| `ANTHROPIC_API_KEY` | console.anthropic.com |

Add both to `.env` (copy from `.env.example`).

---

## How to continue

User implements one task at a time by saying **"implement T[N]"**.
Always read `PLAN.md` for the full spec of a task before implementing it.
Update this file's task status table when a task is completed.
