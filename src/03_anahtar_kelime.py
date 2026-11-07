"""
03_anahtar_kelime.py
Adim 3: Anahtar kelime yontemiyle beceri cikarimi (Deney B icin).

Kullanim:
    python src/03_anahtar_kelime.py

Girdi : data/ornek.csv
Cikti : data/beceri_anahtar_kelime.csv  (job_id + beceri basina 0/1 sutun)
"""

from pathlib import Path

import pandas as pd

from beceriler import BECERI_ADLARI, anahtar_kelime_cikar


def main():
    df = pd.read_csv("data/ornek.csv")

    satirlar = []
    for job_id, metin in zip(df["job_id"], df["description"]):
        bulunan = set(anahtar_kelime_cikar(metin))
        satir = {"job_id": job_id}
        for ad in BECERI_ADLARI:
            satir[ad] = int(ad in bulunan)
        satirlar.append(satir)

    sonuc = pd.DataFrame(satirlar)
    sonuc.to_csv("data/beceri_anahtar_kelime.csv", index=False)

    print(f"{len(sonuc):,} ilan islendi.")
    print("\nEn cok bulunan 15 beceri (ilan sayisi):")
    print(sonuc[BECERI_ADLARI].sum().sort_values(ascending=False).head(15).to_string())
    print(f"\nIlan basina ortalama beceri sayisi: {sonuc[BECERI_ADLARI].sum(axis=1).mean():.2f}")
    print(f"Hic beceri bulunamayan ilan orani : %{(sonuc[BECERI_ADLARI].sum(axis=1) == 0).mean() * 100:.1f}")
    print("\nKaydedildi: data/beceri_anahtar_kelime.csv")


if __name__ == "__main__":
    main()
