# ============================================================
# 01_explore.py — Run this FIRST after download
# Goal: Understand the dataset before cleaning
# ============================================================

from datasets import load_dataset
import pandas as pd

# ── Load ────────────────────────────────────────────────────
print("Loading dataset from HuggingFace...")
import pandas as pd
df = pd.read_csv("data/raw/merged_output.csv")

print(f"\n✅ Total rows: {len(df):,}")
print(f"✅ Columns: {list(df.columns)}\n")

# ── Basic stats ─────────────────────────────────────────────
print("=" * 50)
print("STATE DISTRIBUTION (top 10):")
print(df['StateName'].value_counts().head(10))

print("\n" + "=" * 50)
print("UP ROWS:")
df_up = df[df['StateName'] == 'UTTAR PRADESH']
print(f"  Total UP rows: {len(df_up):,}")

print("\n" + "=" * 50)
print("QUERY TYPES in UP:")
print(df_up['QueryType'].value_counts())

print("\n" + "=" * 50)
print("CATEGORIES in UP:")
print(df_up['Category'].value_counts())

print("\n" + "=" * 50)
print("TOP 20 CROPS in UP:")
print(df_up['Crop'].value_counts().head(20))

print("\n" + "=" * 50)
print("SAMPLE ROW (Wheat, UP):")
sample = df_up[df_up['Crop'] == 'Wheat'].iloc[0]
print(f"  Query : {sample['QueryText']}")
print(f"  Answer: {sample['KccAns'][:200]}...")

print("\n" + "=" * 50)
print("NULL CHECK:")
print(df_up[['QueryText', 'KccAns', 'Crop', 'District']].isnull().sum())
