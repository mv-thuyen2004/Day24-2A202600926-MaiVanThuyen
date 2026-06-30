# scripts/anonymize_data.py
import sys
sys.modules["torch"] = None
import os
os.environ["PRESIDIO_DEVICE"] = "cpu"
import pandas as pd
from src.pii.anonymizer import MedVietAnonymizer

print("Loading raw patient records...")
df = pd.read_csv("data/raw/patients_raw.csv", dtype=str)

print("Anonymizing data...")
anonymizer = MedVietAnonymizer()
df_anon = anonymizer.anonymize_dataframe(df)

import os
os.makedirs("data/processed", exist_ok=True)
df_anon.to_csv("data/processed/patients_anonymized.csv", index=False)
print("Saved anonymized data to data/processed/patients_anonymized.csv")
