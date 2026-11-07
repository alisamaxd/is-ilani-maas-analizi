"""
04_llm_beceri.py
Adim 4: LLM ile beceri cikarimi (Deney C icin).

ONCE kucuk bir denemeyle baslayin (maliyet ve calisip calismadigini gormek icin):
    python src/04_llm_beceri.py --limit 30

Sonuc iyiyse tamamini calistirin (yarida kesilirse kaldigi yerden devam eder):
    python src/04_llm_beceri.py

Gereken: pip install anthropic   ve   ANTHROPIC_API_KEY ortam degiskeni.
API anahtarini ASLA koda yazmayin ve GitHub'a koymayin.
  Windows (PowerShell): $env:ANTHROPIC_API_KEY="anahtar"
  Mac/Linux           : export ANTHROPIC_API_KEY="anahtar"

Baska bir saglayici (OpenAI, Gemini, yerel model) kullanacaksaniz sadece
llm_cagir() fonksiyonunu degistirmeniz yeterli, gerisi ayni kalir.

Girdi : data/ornek.csv
Cikti : data/llm_cikti.jsonl  (her satir: {"job_id":..., "beceriler":[...]})
        Cikti dosyasi onbellek gorevi gorur: ayni ilan icin tekrar para odenmez.
"""

import argparse
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from beceriler import BECERILER, BECERI_ADLARI

MODEL = "claude-haiku-5-5"   # kucuk/ucuz model. Fiyati saglayici sayfasindan kontrol edin.
ESZAMANLI = 5                # ayni anda kac istek
MAKS_KARAKTER = 6500         # cok uzun ilanlari kes (maliyet icin)
CIKTI = Path("data/llm_cikti.jsonl")

BECERI_LISTESI = "\n".join(f"- {ad}: {b['aciklama']}" for ad, b in BECERILER.items())


def prompt_olustur(metin):
    return f"""You will read a job posting and decide which skills from a fixed list it asks for.

Rules:
- Use ONLY skill names from the list below.
- Include a skill only if the posting clearly requires it or lists it as preferred.
- Do not include a skill just because the industry usually needs it. If unsure, leave it out.
- Answer with ONLY a JSON array of skill names, for example ["python","sql"]. If none apply, answer [].

Skill list:
{BECERI_LISTESI}

Job posting:
\"\"\"
{metin[:MAKS_KARAKTER]}
\"\"\""""


_istemci = None


def llm_cagir(istek):
    """LLM'e istegi gonderir, ham metin cevabi dondurur. Saglayici degisirse sadece burasi degisir."""
    global _istemci
    if _istemci is None:
        import anthropic  # ice aktarma: paket yoksa net hata versin
        _istemci = anthropic.Anthropic()  # anahtar ANTHROPIC_API_KEY'den okunur
    yanit = _istemci.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": istek}],
    )
    # Cevap bloklari arasinda 'thinking' olabilir, sadece 'text' bloklarini al
    return "".join(b.text for b in yanit.content if b.type == "text")


def cevabi_ayikla(cevap):
    """Cevaptaki JSON listesini bulur, sadece gecerli beceri adlarini tutar."""
    eslesme = re.search(r"\[.*?\]", cevap, flags=re.DOTALL)
    if not eslesme:
        return None
    try:
        liste = json.loads(eslesme.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(liste, list):
        return None
    gecerli = [str(x) for x in liste if str(x) in BECERI_ADLARI]
    return sorted(set(gecerli))


def tek_ilan(job_id, metin):
    istek = prompt_olustur(metin)
    for deneme in range(3):
        try:
            cevap = llm_cagir(istek)
            beceriler = cevabi_ayikla(cevap)
            if beceriler is not None:
                return job_id, beceriler
            print(f"UYARI (ilan {job_id}): cevap ayristirilamadi: {cevap[:200]!r}")
        except Exception as hata:
            print(f"HATA (ilan {job_id}): {type(hata).__name__}: {hata}")
            time.sleep(2 * (deneme + 1))
    return job_id, None


def onceki_sonuclar():
    yapilan = set()
    if CIKTI.exists():
        with open(CIKTI, encoding="utf-8") as f:
            for satir in f:
                try:
                    yapilan.add(json.loads(satir)["job_id"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return yapilan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="Sadece ilk N ilani isle (deneme icin)")
    args = ap.parse_args()

    df = pd.read_csv("data/ornek.csv")
    if args.limit:
        df = df.head(args.limit)

    yapilan = onceki_sonuclar()
    bekleyen = [(j, m) for j, m in zip(df["job_id"], df["description"]) if j not in yapilan]
    print(f"Toplam: {len(df):,}   Daha once yapilan: {len(yapilan):,}   Simdi islenecek: {len(bekleyen):,}")
    if not bekleyen:
        print("Yapilacak is yok.")
        return

    kilit = threading.Lock()
    basarisiz = 0
    tamam = 0
    CIKTI.parent.mkdir(parents=True, exist_ok=True)

    with open(CIKTI, "a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=ESZAMANLI) as havuz:
        isler = [havuz.submit(tek_ilan, j, m) for j, m in bekleyen]
        for is_ in as_completed(isler):
            job_id, beceriler = is_.result()
            if beceriler is None:
                basarisiz += 1
                continue
            with kilit:
                f.write(json.dumps({"job_id": int(job_id), "beceriler": beceriler}, ensure_ascii=False) + "\n")
                f.flush()
            tamam += 1
            if tamam % 50 == 0:
                print(f"  {tamam:,} / {len(bekleyen):,} tamamlandi")

    print(f"\nBitti. Basarili: {tamam:,}   Basarisiz: {basarisiz:,}")
    if basarisiz:
        print("Basarisiz olanlar kaydedilmedi; scripti tekrar calistirirsaniz sadece onlari dener.")
    print(f"Sonuclar: {CIKTI}")


if __name__ == "__main__":
    main()
