# ============================================================
# 03_chunk.py — Run this AFTER 02_clean.py
# Goal: Convert cleaned Q&A pairs into chunks ready for FAISS
# Each chunk = one document with text + metadata
# ============================================================

import pandas as pd
import json
import os

os.makedirs("data/processed", exist_ok=True)

# ── Load cleaned data ────────────────────────────────────────
df = pd.read_csv("data/processed/kcc_up_clean.csv")
print(f"Loaded: {len(df):,} rows")

# ── Build chunks ─────────────────────────────────────────────
# Each chunk = Query + Answer merged as one text block
# Metadata stays separate for FAISS filtering

chunks = []

for _, row in df.iterrows():
    # The actual text that will be embedded
    # Combining Q+A so semantic search works on full context
    text = f"Farmer query: {row['query']}\nExpert answer: {row['answer']}"

    # Metadata — used for filtering, NOT embedded
    metadata = {
        "crop"       : str(row['crop']),
        "category"   : str(row['category']),
        "query_type" : str(row['query_type']),
        "district"   : str(row['district']),
        "block"      : str(row['block']),
        "agro_zone"  : str(row['agro_zone']),
        "season"     : str(row['season']),
        "month"      : int(row['month']) if pd.notna(row['month']) else 0,
        "year"       : int(row['year'])  if pd.notna(row['year'])  else 0,
        # Store originals for SourceCard on frontend
        "original_query" : str(row['query']),
        "original_answer": str(row['answer']),
    }

    chunks.append({
        "text"    : text,
        "metadata": metadata,
    })

# ── Save as JSON ─────────────────────────────────────────────
output_path = "data/processed/kcc_chunks.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"\n✅ Chunks saved: {output_path}")
print(f"✅ Total chunks: {len(chunks):,}")
print(f"\nSample chunk:")
print(f"  Text   : {chunks[0]['text'][:150]}...")
print(f"  Metadata: {chunks[0]['metadata']}")
