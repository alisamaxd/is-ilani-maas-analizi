"""
07_tekrarli_karsilastirma.py
Adim 6: A, B, C karsilastirmasini TEK bir train/test ayrimina bagli birakmadan,
tekrarli capraz dogrulama (5 katli x 4 tekrar = 20 deneme) ile yap.

Neden: 05'teki sonuc tek bir test setine (yaklasik 500 ilan) dayaniyor. B ile C arasindaki
kucuk fark sans olabilir. 20 farkli bolmede ortalamaya ve tutarliliga bakmak daha guvenilir.

Kullanim:
    python3 src/07_tekrarli_karsilastirma.py

Girdi : 05'tekiyle ayni (data/ornek.csv, data/beceri_anahtar_kelime.csv, data/llm_cikti.jsonl)
Cikti : raporlar/tekrarli_sonuclar.csv, raporlar/tekrarli_ozet.csv
"""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold

from beceriler import BECERI_ADLARI

KAT = 5
TEKRAR = 4
TOHUM = 42


def modul_yukle(yol, ad):
    """05 dosyasinin adi rakamla basladigi icin normal import calismaz, bu yolla yukleriz."""
    spec = importlib.util.spec_from_file_location(ad, yol)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def main():
    m05 = modul_yukle(Path(__file__).with_name("05_model_karsilastir.py"), "model05")

    ornek = pd.read_csv("data/ornek.csv")
    kw = pd.read_csv("data/beceri_anahtar_kelime.csv")
    llm = m05.llm_becerilerini_yukle()

    ortak = set(ornek["job_id"]) & set(kw["job_id"]) & set(llm["job_id"])
    df = ornek[ornek["job_id"].isin(ortak)].reset_index(drop=True)
    kw = kw.set_index("job_id").loc[df["job_id"], BECERI_ADLARI].reset_index(drop=True)
    llm = llm.set_index("job_id").loc[df["job_id"], BECERI_ADLARI].reset_index(drop=True)

    # Capraz dogrulamada tum ilanlar kullanilir; "en sik eyaletler" listesi tum veriden cikar
    # (kucuk bir sizinti, sonucu etkilemez ama raporda belirtin)
    df["set"] = "train"
    temel = m05.temel_ozellikler(df)
    deneyler = {
        "A (temel)": temel,
        "B (temel + anahtar kelime)": pd.concat([temel, kw.add_prefix("kw_")], axis=1),
        "C (temel + LLM)": pd.concat([temel, llm.add_prefix("llm_")], axis=1),
    }
    y_log = np.log(df["normalized_salary"].values)
    y = df["normalized_salary"].values

    satirlar = []
    for tekrar in range(TEKRAR):
        kf = KFold(n_splits=KAT, shuffle=True, random_state=TOHUM + tekrar)
        for kat, (egitim, test) in enumerate(kf.split(df)):
            for ad, X in deneyler.items():
                model = LinearRegression().fit(X.iloc[egitim], y_log[egitim])
                tahmin = np.exp(model.predict(X.iloc[test]))
                satirlar.append({
                    "tekrar": tekrar, "kat": kat, "deney": ad,
                    "MAE_usd": mean_absolute_error(y[test], tahmin),
                    "R2": r2_score(y[test], tahmin),
                })

    sonuc = pd.DataFrame(satirlar)
    Path("raporlar").mkdir(exist_ok=True)
    sonuc.to_csv("raporlar/tekrarli_sonuclar.csv", index=False)

    ozet = sonuc.groupby("deney").agg(
        MAE_ortalama=("MAE_usd", "mean"), MAE_std=("MAE_usd", "std"),
        R2_ortalama=("R2", "mean"), R2_std=("R2", "std"),
    )
    ozet.to_csv("raporlar/tekrarli_ozet.csv")

    print(f"Ilan sayisi: {len(df):,}   Deneme sayisi: {KAT * TEKRAR} ({KAT} kat x {TEKRAR} tekrar)")
    print("\n=== ORTALAMA SONUCLAR (std = denemeler arasi dagilim) ===")
    print(ozet.round({"MAE_ortalama": 0, "MAE_std": 0, "R2_ortalama": 3, "R2_std": 3}).to_string())

    # Ayni bolmede iki yontemi birebir karsilastir
    p = sonuc.pivot_table(index=["tekrar", "kat"], columns="deney", values="MAE_usd")
    a, b, c = "A (temel)", "B (temel + anahtar kelime)", "C (temel + LLM)"
    print("\n=== AYNI BOLMEDE BIREBIR KARSILASTIRMA (MAE, dolar) ===")
    for ad, x, y_ in [("B, A'dan iyi mi?", b, a), ("C, A'dan iyi mi?", c, a), ("C, B'den iyi mi?", c, b)]:
        fark = p[y_] - p[x]          # pozitif = x daha dusuk hata = x daha iyi
        print(f"{ad:20s} ortalama fark: {fark.mean():8.0f} $   "
              f"ilk yontem {int((fark > 0).sum())}/{len(fark)} denemede daha iyi")
    print("\nOkuma: 'C, B'den iyi mi?' satirinda fark kucukse ve 20 denemenin yaklasik yarisinda "
          "C kazaniyorsa, iki yontem pratikte esit demektir.")


if __name__ == "__main__":
    main()
