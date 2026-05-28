# ============================================================
# ============================================================
# 02_clean.py — Run this AFTER 01_explore.py
# Goal: Filter, clean, and save UP-specific agricultural data
# ============================================================

from datasets import load_dataset
import pandas as pd
import re
import os

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# ── Load ────────────────────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv("data/raw/merged_output.csv", low_memory=False)
print(f"Raw total: {len(df):,} rows")

# ── Step 1: Filter UP only ───────────────────────────────────
df = df[df['StateName'] == 'UTTAR PRADESH'].copy()
print(f"After UP filter: {len(df):,} rows")

# ── Step 2: Remove non-agricultural query types ──────────────
REMOVE_QUERY_TYPES = [
    'Government Schemes',
    'Market Information',
    'Weather',
    'Insurance',
]
df = df[~df['QueryType'].isin(REMOVE_QUERY_TYPES)]
print(f"After QueryType filter: {len(df):,} rows")

# ── Step 3: Remove non-specific categories ───────────────────
df = df[df['Category'] != 'Others']
df = df[df['Crop'] != 'Others']
print(f"After Category/Crop filter: {len(df):,} rows")

# ── Step 4: Drop null / empty Q&A pairs ─────────────────────
df = df.dropna(subset=['QueryText', 'KccAns'])
df = df[df['QueryText'].str.strip() != '']
df = df[df['KccAns'].str.strip() != '']
print(f"After null drop: {len(df):,} rows")

# ── Step 5: Clean text ───────────────────────────────────────
def clean_text(text):
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)       # multiple spaces → single
    text = re.sub(r'[^\w\s\u0900-\u097F.,?!%@/:-]', '', text)  # keep Hindi + basic punctuation
    return text

df['QueryText'] = df['QueryText'].apply(clean_text)
df['KccAns']    = df['KccAns'].apply(clean_text)

# ── Step 6: Keep only relevant columns ──────────────────────
df = df[[
    'QueryText',
    'KccAns',
    'Crop',
    'Category',
    'QueryType',
    'DistrictName',
    'BlockName',
    'Season',
    'month',
    'year',
]].copy()

# Rename for consistency
df.columns = [
    'query',
    'answer',
    'crop',
    'category',
    'query_type',
    'district',
    'block',
    'season',
    'month',
    'year',
]

# ── Step 7: Add agro zone mapping ───────────────────────────
# UP districts mapped to agro-climatic zones
# Source: ICAR agro-climatic zone classification
ZONE_MAP = {
    # Tarai zone
    'LAKHIMPUR KHERI': 'tarai', 'BAHRAICH': 'tarai', 'SHRAVASTI': 'tarai',
    'BALRAMPUR': 'tarai', 'SIDDHARTHNAGAR': 'tarai', 'MAHARAJGANJ': 'tarai',
    'GORAKHPUR': 'tarai', 'KUSHINAGAR': 'tarai', 'DEORIA': 'tarai',

    # Central plain zone
    'LUCKNOW': 'central_plain', 'UNNAO': 'central_plain', 'RAE BARELI': 'central_plain',
    'FATEHPUR': 'central_plain', 'KANPUR NAGAR': 'central_plain',
    'KANPUR DEHAT': 'central_plain', 'HARDOI': 'central_plain',
    'SITAPUR': 'central_plain', 'BARABANKI': 'central_plain',

    # Eastern plain zone
    'VARANASI': 'eastern_plain', 'JAUNPUR': 'eastern_plain', 'AZAMGARH': 'eastern_plain',
    'MAUNATH BHANJAN': 'eastern_plain', 'GHAZIPUR': 'eastern_plain',
    'BALLIA': 'eastern_plain', 'BASTI': 'eastern_plain', 'SANT KABIR NAGAR': 'eastern_plain',
    'AMBEDKAR NAGAR': 'eastern_plain', 'SULTANPUR': 'eastern_plain',

    # Western plain zone
    'AGRA': 'western_plain', 'MATHURA': 'western_plain', 'ETAH': 'western_plain',
    'MAINPURI': 'western_plain', 'FIROZABAD': 'western_plain', 'HATHRAS': 'western_plain',
    'ALIGARH': 'western_plain', 'BULANDSHAHR': 'western_plain',

    # Bundelkhand zone
    'JHANSI': 'bundelkhand', 'LALITPUR': 'bundelkhand', 'JALAUN': 'bundelkhand',
    'HAMIRPUR': 'bundelkhand', 'MAHOBA': 'bundelkhand', 'BANDA': 'bundelkhand',
    'CHITRAKOOT': 'bundelkhand',

    # Vindhyan zone
    'MIRZAPUR': 'vindhyan', 'SONBHADRA': 'vindhyan', 'ALLAHABAD': 'vindhyan',
}

def get_zone(district):
    if pd.isna(district):
        return 'central_plain'  # default
    return ZONE_MAP.get(str(district).upper().strip(), 'central_plain')

df['agro_zone'] = df['district'].apply(get_zone)

# ── Save ─────────────────────────────────────────────────────
output_path = "data/processed/kcc_up_clean.csv"
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n✅ Cleaned dataset saved: {output_path}")
print(f"✅ Final rows: {len(df):,}")
print(f"\nZone distribution:")
print(df['agro_zone'].value_counts())
print(f"\nTop crops:")
print(df['crop'].value_counts().head(10))
print(f"\nQuery types:")
print(df['query_type'].value_counts())
