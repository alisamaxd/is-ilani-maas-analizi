"""
05_model_karsilastir.py
Adim 5: Uc deneyi kur ve karsilastir.

  A: sadece temel ilan ozellikleri
  B: temel ozellikler + anahtar kelime becerileri
  C: temel ozellikler + LLM becerileri

Ayni train/test ayrimi, ayni model (dogrusal regresyon), ayni olcutler.
Maas dagilimi carpik oldugu icin model log(maas) uzerinde egitilir;
hatalar (MAE, RMSE) tahminler tekrar dolara cevrilerek hesaplanir.

Kullanim:
    python src/05_model_karsilastir.py

Girdi : data/ornek.csv, data/beceri_anahtar_kelime.csv, data/llm_cikti.jsonl
Cikti : raporlar/sonuclar.csv, raporlar/beceri_katsayilari.csv, raporlar/beceri_karsilastirma.csv
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from beceriler import BECERI_ADLARI

EN_SIK_EYALET = 10


def llm_becerilerini_yukle():
    satirlar = []
    with open("data/llm_cikti.jsonl", encoding="utf-8") as f:
        for satir in f:
            kayit = json.loads(satir)
            s = {"job_id": kayit["job_id"]}
            for ad in BECERI_ADLARI:
                s[ad] = int(ad in kayit["beceriler"])
            satirlar.append(s)
    return pd.DataFrame(satirlar).drop_duplicates(subset="job_id")


def eyalet(konum):
    """'New York, NY' -> 'NY'. Parcalanamazsa 'Diger'."""
    if not isinstance(konum, str) or "," not in konum:
        return "Diger"
    son = konum.split(",")[-1].strip()
    return son.upper() if len(son) == 2 else "Diger"


def temel_ozellikler(df):
    """Deney A'nin girdisi: beceri icermeyen temel tablo bilgileri."""
    x = pd.DataFrame(index=df.index)
    x["deneyim"] = df.get("formatted_experience_level", pd.Series("Bilinmiyor", index=df.index)).fillna("Bilinmiyor")
    x["calisma_turu"] = df.get("formatted_work_type", pd.Series("Bilinmiyor", index=df.index)).fillna("Bilinmiyor")
    x["uzaktan"] = df.get("remote_allowed", pd.Series(0, index=df.index)).fillna(0).astype(int)

    eyaletler = df["location"].map(eyalet) if "location" in df.columns else pd.Series("Diger", index=df.index)
    sik = eyaletler[df["set"] == "train"].value_counts().head(EN_SIK_EYALET).index
    x["eyalet"] = eyaletler.where(eyaletler.isin(sik), "Diger")

    return pd.get_dummies(x, columns=["deneyim", "calisma_turu", "eyalet"], drop_first=True, dtype=int)


def degerlendir(ad, X, y_log, df):
    egitim = (df["set"] == "train").values
    test = ~egitim
    model = LinearRegression().fit(X[egitim], y_log[egitim])
    tahmin = np.exp(model.predict(X[test]))
    gercek = np.exp(y_log[test])
    sonuc = {
        "deney": ad,
        "ozellik_sayisi": X.shape[1],
        "MAE_usd": mean_absolute_error(gercek, tahmin),
        "RMSE_usd": mean_squared_error(gercek, tahmin) ** 0.5,
        "R2": r2_score(gercek, tahmin),
    }
    return sonuc, model


def main():
    ornek = pd.read_csv("data/ornek.csv")
    kw = pd.read_csv("data/beceri_anahtar_kelime.csv")
    llm = llm_becerilerini_yukle()

    # Uc deney de AYNI ilanlar uzerinde calissin diye LLM sonucu olan ilanlarla sinirla
    ortak = set(ornek["job_id"]) & set(kw["job_id"]) & set(llm["job_id"])
    df = ornek[ornek["job_id"].isin(ortak)].reset_index(drop=True)
    kw = kw.set_index("job_id").loc[df["job_id"], BECERI_ADLARI].reset_index(drop=True)
    llm = llm.set_index("job_id").loc[df["job_id"], BECERI_ADLARI].reset_index(drop=True)
    print(f"Kullanilan ilan: {len(df):,} (train {int((df['set'] == 'train').sum()):,}, "
          f"test {int((df['set'] == 'test').sum()):,})")
    if len(df) < len(ornek):
        print(f"Not: {len(ornek) - len(df):,} ilan LLM sonucu olmadigi icin disarida kaldi.")

    y_log = np.log(df["normalized_salary"].values)
    temel = temel_ozellikler(df)

    A = temel
    B = pd.concat([temel, kw.add_prefix("kw_")], axis=1)
    C = pd.concat([temel, llm.add_prefix("llm_")], axis=1)

    # Referans: egitim setinin medyan maasini herkes icin tahmin et
    test = (df["set"] == "test").values
    medyan = df.loc[df["set"] == "train", "normalized_salary"].median()
    gercek = df.loc[test, "normalized_salary"].values
    referans = {
        "deney": "0 (sadece medyan)", "ozellik_sayisi": 0,
        "MAE_usd": mean_absolute_error(gercek, np.full(len(gercek), medyan)),
        "RMSE_usd": mean_squared_error(gercek, np.full(len(gercek), medyan)) ** 0.5,
        "R2": 0.0,
    }

    sonuclar = [referans]
    modeller = {}
    for ad, X in [("A (temel)", A), ("B (temel + anahtar kelime)", B), ("C (temel + LLM)", C)]:
        s, m = degerlendir(ad, X, y_log, df)
        sonuclar.append(s)
        modeller[ad] = (m, X)

    tablo = pd.DataFrame(sonuclar)
    Path("raporlar").mkdir(exist_ok=True)
    tablo.to_csv("raporlar/sonuclar.csv", index=False)

    print("\n=== TEST SETI SONUCLARI (dusuk MAE/RMSE = iyi, yuksek R2 = iyi) ===")
    print(tablo.round({"MAE_usd": 0, "RMSE_usd": 0, "R2": 3}).to_string(index=False))

    # Beceri katsayilari (C modeli ve B modeli): log hedef oldugu icin yuzde etki olarak yorumlanir
    kat = []
    for ad, onek in [("C (temel + LLM)", "llm_"), ("B (temel + anahtar kelime)", "kw_")]:
        m, X = modeller[ad]
        for sutun, katsayi in zip(X.columns, m.coef_):
            if sutun.startswith(onek):
                kat.append({
                    "yontem": onek.rstrip("_"),
                    "beceri": sutun[len(onek):],
                    "yuzde_iliski": (np.exp(katsayi) - 1) * 100,
                    "ilan_sayisi": int(X[sutun].sum()),
                })
    kat = pd.DataFrame(kat).sort_values(["yontem", "yuzde_iliski"], ascending=[True, False])
    kat.to_csv("raporlar/beceri_katsayilari.csv", index=False)

    c = kat[(kat["yontem"] == "llm") & (kat["ilan_sayisi"] >= 20)]
    print("\n=== LLM becerileri: maasla iliski (diger ozellikler sabitken, yaklasik % fark) ===")
    print("(Sadece en az 20 ilanda gecen beceriler. Bu NEDENSELLIK degil, iliskidir.)")
    print("En yuksek 8:")
    print(c.head(8)[["beceri", "yuzde_iliski", "ilan_sayisi"]].round(1).to_string(index=False))
    print("En dusuk 8:")
    print(c.iloc[8:].tail(8)[["beceri", "yuzde_iliski", "ilan_sayisi"]].round(1).to_string(index=False))

    # Iki yontem hangi becerilerde ayriliyor
    kar = pd.DataFrame({
        "kw_ilan": kw.sum(),
        "llm_ilan": llm.sum(),
        "ikisi_de": (kw & llm).sum(),
    })
    kar["sadece_kw"] = kar["kw_ilan"] - kar["ikisi_de"]
    kar["sadece_llm"] = kar["llm_ilan"] - kar["ikisi_de"]
    kar["fark"] = (kar["sadece_kw"] + kar["sadece_llm"])
    kar = kar.sort_values("fark", ascending=False)
    kar.to_csv("raporlar/beceri_karsilastirma.csv")
    print("\n=== Anahtar kelime ve LLM en cok nerede ayriliyor (ilan sayisi) ===")
    print(kar.head(10).to_string())

    print("\nKaydedildi: raporlar/sonuclar.csv, beceri_katsayilari.csv, beceri_karsilastirma.csv")


if __name__ == "__main__":
    main()
