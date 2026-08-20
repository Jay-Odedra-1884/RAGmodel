"""
T2 — Download ai4bharat/MSMARCO-XI and save English passages to data/raw_passages.jsonl

Run once:  python load_dataset.py
"""

import os
import json
import pathlib
from collections import defaultdict

from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

HF_DATASET = os.getenv("HF_DATASET", "ai4bharat/MSMARCO-XI")
HF_SPLIT = os.getenv("HF_SPLIT", "train")
HF_MAX_PASSAGES = int(os.getenv("HF_MAX_PASSAGES", "50000"))
OUT_PATH = pathlib.Path("data/raw_passages.jsonl")


def extract_passages(example: dict) -> list[dict]:
    """
    MSMARCO-XI schema variants — handle both flat and nested layouts.
    Returns list of {passage_id, text, query, query_id, lang} dicts.
    """
    rows = []

    # Variant A: flat columns (passage_id, passage, query, query_id, language)
    if "passage" in example:
        rows.append({
            "passage_id": str(example.get("passage_id", example.get("id", ""))),
            "text": example["passage"].strip(),
            "query": example.get("query", ""),
            "query_id": str(example.get("query_id", "")),
            "lang": example.get("language", example.get("lang", "en")),
        })

    # Variant B: nested passages dict  {passage_text: [...], passage_id: [...]}
    elif "passages" in example:
        passages = example["passages"]
        texts = passages.get("passage_text", passages.get("text", []))
        ids = passages.get("passage_id", passages.get("id", range(len(texts))))
        for pid, text in zip(ids, texts):
            rows.append({
                "passage_id": str(pid),
                "text": text.strip(),
                "query": example.get("query", ""),
                "query_id": str(example.get("query_id", "")),
                "lang": example.get("language", example.get("lang", "en")),
            })

    return rows


def main() -> None:
    OUT_PATH.parent.mkdir(exist_ok=True)

    print(f"Loading {HF_DATASET} / {HF_SPLIT} ...")
    ds = load_dataset(HF_DATASET, split=HF_SPLIT, trust_remote_code=True)
    print(f"  Raw rows: {len(ds):,}")
    print(f"  Columns : {ds.column_names}")
    print(f"  Features: {ds.features}")

    seen_ids: set[str] = set()
    passages: list[dict] = []
    lang_counts: dict[str, int] = defaultdict(int)

    for example in ds:
        if len(passages) >= HF_MAX_PASSAGES:
            break
        for row in extract_passages(example):
            if not row["text"]:
                continue
            # deduplicate by passage_id
            uid = row["passage_id"] or row["text"][:64]
            if uid in seen_ids:
                continue
            seen_ids.add(uid)
            lang_counts[row["lang"]] += 1
            passages.append(row)
            if len(passages) >= HF_MAX_PASSAGES:
                break

    print(f"\n  Unique passages saved : {len(passages):,}")
    print(f"  Language distribution : {dict(sorted(lang_counts.items(), key=lambda x: -x[1]))}")

    lengths = [len(p["text"]) for p in passages]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    print(f"  Avg passage length    : {avg_len:.0f} chars")
    print(f"  Min / Max length      : {min(lengths)} / {max(lengths)} chars")

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"\nSaved → {OUT_PATH}  ({OUT_PATH.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
