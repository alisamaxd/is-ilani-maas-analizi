"""
01_veri_inceleme.py
Adim 1: Veri setine ilk bakis.

Kullanim (proje klasorunun icinden):
    python src/01_veri_inceleme.py
    python src/01_veri_inceleme.py data/postings.csv

Beklenen girdi: Kaggle "LinkedIn Job Postings (2023-2024)" icindeki postings.csv
Bu script hicbir sey degistirmez, sadece ekrana rapor basar.
"""

import sys
from pathlib import Path

import pandas as pd

# Maaslari mantikli aralikta tutmak icin (proje planindaki karar, gerekirse degistirin)
MAAS_ALT = 15_000
MAAS_UST = 500_000

# Bizim isimize yarayacak sutunlar. Veri setinde adi farkliysa asagida "EKSIK" yazar.
ONEMLI_SUTUNLAR = [
    "job_id", "title", "description", "skills_desc",
    "formatted_experience_level", "formatted_work_type", "work_type",
    "location", "company_name",
    "min_salary", "med_salary", "max_salary",
    "pay_period", "currency", "compensation_type", "normalized_salary",
]


def baslik(metin):
    print("\n" + "=" * 70)
    print(metin)
    print("=" * 70)


def main():
    yol = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/postings.csv")
    if not yol.exists():
        print(f"Dosya bulunamadi: {yol}")
        print("Kaggle ZIP'ini acip postings.csv dosyasini data/ klasorune koyun.")
        sys.exit(1)

    df = pd.read_csv(yol)

    # 1) Genel gorunum
    baslik("1) GENEL GORUNUM")
    print(f"Toplam ilan (satir): {len(df):,}")
    print(f"Toplam sutun       : {df.shape[1]}")
    print("\nTum sutun adlari:")
    print(", ".join(df.columns))

    # 2) Onemli sutunlar var mi, ne kadari dolu
    baslik("2) ONEMLI SUTUNLAR VE DOLULUK ORANI")
    for sutun in ONEMLI_SUTUNLAR:
        if sutun not in df.columns:
            print(f"{sutun:30s} EKSIK (bu isimde sutun yok)")
        else:
            dolu = df[sutun].notna().mean() * 100
            print(f"{sutun:30s} %{dolu:5.1f} dolu")

    # 3) Maas bilgisi
    baslik("3) MAAS BILGISI")
    if "normalized_salary" in df.columns:
        maasli = df[df["normalized_salary"].notna()]
        print(f"normalized_salary dolu olan ilan: {len(maasli):,} "
              f"(toplamin %{len(maasli) / len(df) * 100:.1f}'i)")

        print("\nnormalized_salary ozet istatistik:")
        print(maasli["normalized_salary"].describe().round(0).to_string())

        mantikli = maasli[maasli["normalized_salary"].between(MAAS_ALT, MAAS_UST)]
        print(f"\n{MAAS_ALT:,} - {MAAS_UST:,} araliginda kalan ilan: {len(mantikli):,}")
        print(f"Bu aralik disinda kalan (elenecek) ilan  : {len(maasli) - len(mantikli):,}")
    else:
        print("normalized_salary sutunu yok. Yukaridaki sutun listesine bakip "
              "maas sutununu belirleyin.")
        maasli = df.iloc[0:0]

    for sutun in ["pay_period", "currency", "compensation_type"]:
        if sutun in df.columns:
            print(f"\n{sutun} dagilimi (maasi olan ilanlarda):")
            kaynak = maasli if len(maasli) else df
            print(kaynak[sutun].value_counts(dropna=False).head(10).to_string())

    # 4) Yinelenen kayitlar
    baslik("4) YINELENEN KAYITLAR")
    if "job_id" in df.columns:
        print(f"Ayni job_id tekrar eden satir: {df['job_id'].duplicated().sum():,}")
    if {"title", "description"}.issubset(df.columns):
        print(f"Ayni baslik + aciklama tekrar eden satir: "
              f"{df.duplicated(subset=['title', 'description']).sum():,}")

    # 5) Ilan metni
    baslik("5) ILAN METNI (description)")
    if "description" in df.columns:
        uzunluk = df["description"].dropna().astype(str).str.len()
        print("Karakter uzunlugu ozeti:")
        print(uzunluk.describe().round(0).to_string())
        print("\nMaasi olan ilanlardan bir ornek (ilk 600 karakter):")
        if len(maasli) and "description" in maasli.columns:
            ornek = maasli["description"].dropna().astype(str)
            if len(ornek):
                print(ornek.iloc[0][:600])
    else:
        print("description sutunu yok.")

    print("\nBitti. Bu ciktinin tamamini kopyalayip paylasabilirsiniz.")


if __name__ == "__main__":
    main()
