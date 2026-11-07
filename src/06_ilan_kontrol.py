"""
06_ilan_kontrol.py
Bir ilanin metnini, LLM'in ve anahtar kelime yonteminin buldugu becerilerle yan yana gosterir.

Kullanim:
    python3 src/06_ilan_kontrol.py 3887576385
"""

import json
import sys

import pandas as pd

from beceriler import anahtar_kelime_cikar

if len(sys.argv) < 2:
    raise SystemExit("Kullanim: python3 src/06_ilan_kontrol.py ILAN_NUMARASI")

job_id = int(sys.argv[1])
df = pd.read_csv("data/ornek.csv")
bulunan = df[df["job_id"] == job_id]
if bulunan.empty:
    raise SystemExit(f"{job_id} numarali ilan data/ornek.csv icinde yok.")
satir = bulunan.iloc[0]

llm = {}
with open("data/llm_cikti.jsonl", encoding="utf-8") as f:
    for s in f:
        k = json.loads(s)
        llm[k["job_id"]] = k["beceriler"]

print("BASLIK:", satir["title"])
print("\n" + "=" * 70)
print("ILAN METNI (ilk 8000 karakter):")
print("=" * 70)
print(satir["description"][:8000])
print("\n" + "=" * 70)
print("LLM'IN BULDUGU BECERILER      :", ", ".join(llm.get(job_id, ["(bu ilan icin sonuc yok)"])))
print("ANAHTAR KELIMENIN BULDUKLARI  :", ", ".join(anahtar_kelime_cikar(satir["description"])) or "(yok)")
print("=" * 70)
