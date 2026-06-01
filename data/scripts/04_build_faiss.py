
import json
import pickle
import os
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss

os.makedirs("data/vector_store", exist_ok=True)

# ── Load chunks ──────────────────────────────────────────────
print("Loading chunks...")
with open("data/processed/kcc_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)
print(f" Total chunks: {len(chunks):,}")

# ── Load embedding model (downloads once, then cached) ───────
print("\nLoading embedding model...")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
print(" Model loaded!")

# ── Extract texts ────────────────────────────────────────────
texts = [chunk["text"] for chunk in chunks]
metadatas = [chunk["metadata"] for chunk in chunks]

# ── Embed in batches ─────────────────────────────────────────
print(f"\nEmbedding {len(texts):,} chunks...")
print("(This will take 15-20 minutes — ek baar hota hai, phir save ho jayega)\n")

BATCH_SIZE = 64  

all_embeddings = []

for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Embedding"):
    batch = texts[i: i + BATCH_SIZE]
    embeddings = model.encode(batch, show_progress_bar=False)
    all_embeddings.append(embeddings)

# Stack all into one numpy array
all_embeddings = np.vstack(all_embeddings).astype("float32")
print(f"\n Embeddings shape: {all_embeddings.shape}")


print("\nBuilding FAISS index...")
dimension = all_embeddings.shape[1]  


faiss.normalize_L2(all_embeddings)   # normalize for cosine similarity
index = faiss.IndexFlatIP(dimension)
index.add(all_embeddings)

print(f" FAISS index built!")
print(f" Total vectors in index: {index.ntotal:,}")


print("\nSaving to disk...")

# Save FAISS index
faiss.write_index(index, "data/vector_store/kcc_index.faiss")


with open("data/vector_store/kcc_metadata.pkl", "wb") as f:
    pickle.dump(metadatas, f)

# Save original texts too (for SourceCard on frontend)
with open("data/vector_store/kcc_texts.pkl", "wb") as f:
    pickle.dump(texts, f)

print("Saved: data/vector_store/kcc_index.faiss")
print(" Saved: data/vector_store/kcc_metadata.pkl")
print(" Saved: data/vector_store/kcc_texts.pkl")


print("\n" + "=" * 50)
print("QUICK TEST — searching for wheat yellowing query")
print("=" * 50)

test_query = "wheat leaves turning yellow what to do"
test_vector = model.encode([test_query])
faiss.normalize_L2(test_vector)

scores, indices = index.search(test_vector.astype("float32"), k=3)

for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
    meta = metadatas[idx]
    print(f"\nResult {i+1} (score: {score:.3f})")
    print(f"  Crop     : {meta['crop']}")
    print(f"  Zone     : {meta['agro_zone']}")
    print(f"  District : {meta['district']}")
    print(f"  Query    : {meta['original_query'][:80]}...")
    print(f"  Answer   : {meta['original_answer'][:100]}...")

print("\n FAISS index ready! Ab RAG pipeline banana shuru karo.")
