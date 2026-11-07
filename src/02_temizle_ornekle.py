"""
02_temizle_ornekle.py
Adim 2: Veriyi temizle, 2.500 ilanlik kontrollu orneklem cek, train/test ayir.

Kullanim:
    python src/02_temizle_ornekle.py

Girdi : data/postings.csv
Cikti : data/ornek.csv  ('set' sutunu: train / test)

Ayni orneklem ve ayni train/test ayrimi uc deneyde (A, B, C) de kullanilir.
"""

from pathlib import Path

import numpy as np
import pandas as pd

TOHUM = 42            # her calistirmada ayni orneklem cikmasi icin
ORNEKLEM = 2500       # LLM'e okutulacak ilan sayisi
TEST_ORANI = 0.20
MAAS_ALT = 15_000
MAAS_UST = 500_000

GEREKLI = ["job_id", "title", "description", "normalized_salary"]
ISTEGE_BAGLI = [
    "formatted_experience_level", "formatted_work_type", "work_type",
    "remote_allowed", "location", "company_name", "pay_period", "currency",
]


def main():
    girdi = Path("data/postings.csv")
    if not girdi.exists():
        raise SystemExit("data/postings.csv bulunamadi.")

    df = pd.read_csv(girdi)
    eksik = [s for s in GEREKLI if s not in df.columns]
    if eksik:
        raise SystemExit(f"Gerekli sutun(lar) yok: {eksik}. 01 raporundaki sutun adlarina bakin.")

    print(f"Baslangic ilan sayisi                      : {len(df):,}")

    df = df.dropna(subset=["description", "normalized_salary"])
    print(f"Maasi ve metni dolu olanlar                : {len(df):,}")

    df = df[df["normalized_salary"].between(MAAS_ALT, MAAS_UST)]
    print(f"{MAAS_ALT:,}-{MAAS_UST:,} araliginda kalanlar : {len(df):,}")

    # Ayni ilan hem train hem test'e dusmesin diye tekrarlari at
    df = df.drop_duplicates(subset="job_id")
    df = df.drop_duplicates(subset=["title", "description"])
    print(f"Tekrarlar atildiktan sonra                 : {len(df):,}")

    sutunlar = GEREKLI + [s for s in ISTEGE_BAGLI if s in df.columns]
    df = df[sutunlar]

    if len(df) > ORNEKLEM:
        df = df.sample(ORNEKLEM, random_state=TOHUM)
    df = df.reset_index(drop=True)
    print(f"Orneklem                                   : {len(df):,}")

    rng = np.random.default_rng(TOHUM)
    test_idx = rng.choice(len(df), size=int(len(df) * TEST_ORANI), replace=False)
    df["set"] = "train"
    df.loc[test_idx, "set"] = "test"
    print(f"Train: {(df['set'] == 'train').sum():,}   Test: {(df['set'] == 'test').sum():,}")

    print("\nMaas (normalized_salary) ozeti:")
    print(df["normalized_salary"].describe().round(0).to_string())

    print("\nEn sik 15 is unvani (ilan turu tek alanda mi, karisik mi gormek icin):")
    print(df["title"].value_counts().head(15).to_string())

    if "formatted_experience_level" in df.columns:
        print("\nDeneyim seviyesi dagilimi:")
        print(df["formatted_experience_level"].value_counts(dropna=False).to_string())

    cikti = Path("data/ornek.csv")
    df.to_csv(cikti, index=False)
    print(f"\nKaydedildi: {cikti}")


if __name__ == "__main__":
    main()
