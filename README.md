# İş İlanı Maaş Analizi: LLM ile Beceri Çıkarımı ve Maaş Tahmini

Veri Madenciliği ve İş Zekası dersi projesi.

ABD'deki LinkedIn iş ilanlarının metinlerinden becerileri iki yolla çıkarıyoruz (basit anahtar kelime araması ve bir LLM). Her yöntemin çıkardığı becerileri doğrusal regresyon modeline verip maaşı tahmin ediyoruz. Asıl soru: **LLM ile beceri çıkarımı, basit anahtar kelime aramasına göre maaş tahminine ek katkı sağlıyor mu?**

Ekip: (buraya ekip üyelerinin isimlerini ekleyin)

## Ana sonuç

2.499 ilan üzerinde 5 katlı × 4 tekrar çapraz doğrulama (toplam 20 deneme). Hedef: veri setindeki `normalized_salary` sütunu (USD). Model: log(maaş) üzerinde doğrusal regresyon.

| Model | Girdi | MAE (ortalama) | R² (ortalama) |
|---|---|---|---|
| A | Temel ilan bilgileri (deneyim seviyesi, çalışma türü, uzaktan çalışma, eyalet) | 34.402 $ | 0,214 |
| B | A + anahtar kelime ile çıkarılan beceriler | 31.045 $ | 0,314 |
| C | A + LLM ile çıkarılan beceriler | 29.873 $ | 0,352 |

- Beceri bilgisi hatayı yaklaşık %10 düşürüyor (A → B).
- LLM becerileri, anahtar kelimeye göre ek olarak yaklaşık %3,8 düşürüyor (B → C) ve 20 denemenin 19'unda daha düşük hata veriyor. Fark küçük ama tutarlı.
- Beceri katsayıları **nedensellik değil, ilişki** gösterir: modelde iş unvanı ve sektör yoktur, bu yüzden beceriler büyük ölçüde mesleğin göstergesi gibi davranır.

Ayrıntılı tablolar `raporlar/` klasöründeki CSV dosyalarındadır.

## Klasör yapısı

```
is-ilani-maas-analizi/
  data/                          ham veri ve ara dosyalar (ham veri repoda yoktur)
    postings.csv                 Kaggle'dan indirilir
    llm_cikti.jsonl              LLM'in beceri çıktısı (repoda; ilan metni içermez)
  src/
    01_veri_inceleme.py          veriye ilk bakış
    02_temizle_ornekle.py        temizleme, 2.500 ilanlık örneklem, train/test
    03_anahtar_kelime.py         anahtar kelime ile beceri çıkarımı
    04_llm_beceri.py             LLM ile beceri çıkarımı (API anahtarı gerekir)
    05_model_karsilastir.py      A / B / C modelleri, tek train/test bölmesi
    06_ilan_kontrol.py           bir ilanı ve iki yöntemin sonucunu yan yana gösterir
    07_tekrarli_karsilastirma.py 5x4 çapraz doğrulama
    beceriler.py                 ortak beceri listesi (41 beceri) ve anahtar kelime desenleri
  raporlar/                      sonuç CSV dosyaları
  requirements.txt
```

## Kurulum

Python 3 gerekir. Terminali **projenin ana klasöründe** açın (komutlardaki `data/...` yolları buna göre yazılmıştır).

```
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Windows'ta `python3` yerine `python` gerekebilir.

## Veri

Kaggle: [LinkedIn Job Postings (2023-2024)](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) (Kaggle hesabı gerekir). İndirdiğiniz ZIP'ten `postings.csv` dosyasını `data/` klasörüne koyun (yaklaşık 517 MB). Veri setinin lisans koşulları Kaggle sayfasında yazılıdır; ham veri bu repoda yer almaz.

## Çalıştırma sırası

| Adım | Komut | Ne yapar | API gerekir mi |
|---|---|---|---|
| 1 | `python3 src/01_veri_inceleme.py` | Sütunları, doluluğu, maaş dağılımını gösterir | Hayır |
| 2 | `python3 src/02_temizle_ornekle.py` | Temizler, 2.500 ilan örnekler (tohum 42), %80 / %20 ayırır. Çıktı: `data/ornek.csv` | Hayır |
| 3 | `python3 src/03_anahtar_kelime.py` | Anahtar kelime becerileri. Çıktı: `data/beceri_anahtar_kelime.csv` | Hayır |
| 4 | `python3 src/04_llm_beceri.py` | LLM becerileri. Çıktı: `data/llm_cikti.jsonl` | **Evet** |
| 5 | `python3 src/05_model_karsilastir.py` | A / B / C modelleri, katsayılar. Çıktı: `raporlar/` | Hayır |
| 6 | `python3 src/07_tekrarli_karsilastirma.py` | 20 denemelik karşılaştırma. Çıktı: `raporlar/` | Hayır |

Elle kontrol için: `python3 src/06_ilan_kontrol.py ILAN_NUMARASI` (örneğin `3887576385`).

### LLM adımı (04)

Anthropic API anahtarı ve bakiye gerekir. Anahtarı **ortam değişkeni** olarak verin, koda veya repoya yazmayın:

```
export ANTHROPIC_API_KEY="anahtarınız"           # macOS / Linux
$env:ANTHROPIC_API_KEY="anahtarınız"             # Windows PowerShell
```

Önce küçük bir denemeyle başlayın: `python3 src/04_llm_beceri.py --limit 30`. Tam çalıştırma 2.500 ilan içindir ve bizim çalıştırmamızda yaklaşık 1,1 $ tuttu (güncel fiyatları sağlayıcının sayfasından kontrol edin). Betik yarıda kesilirse aynı komutla kaldığı yerden devam eder, işlenmiş ilanlar tekrar işlenmez. Kullanılan model `04_llm_beceri.py` içindeki `MODEL` değişkeninde yazılıdır.

### API anahtarı olmadan yeniden üretme

`data/llm_cikti.jsonl` repoda olduğu için 4. adım atlanabilir: 1, 2, 3, 5 ve 6. adımları çalıştırmanız yeterlidir. 2. adım aynı tohumla çalışır; farklı bir pandas sürümünde örneklem değişirse `llm_cikti.jsonl` içindeki bazı ilanlar eşleşmeyebilir, bu durumda 05 ve 07 yalnızca ortak ilanlarla çalışır. Eşleşmeyen ilanlar için 4. adımı API anahtarıyla çalıştırabilirsiniz.

## Kapsam ve gelecek çalışma

**Kapsam**

- Veri ABD piyasasına aittir (maaşlı ilanların %99,96'sı USD), bulgular bu piyasa için geçerlidir. Veri neredeyse tamamen iş ilanlarından oluşur.
- Beceri katsayıları ilişki gösterir, nedensellik değil. İş unvanı ve sektör, becerilerin katkısını gizlemesin diye modele bilerek eklenmemiştir.
- Sonuçlar tek örneklem (2.499 ilan), tek LLM ve tek prompt ile elde edilmiştir. Anahtar kelime yöntemi, bizim yazdığımız basit bir beceri listesine dayanır.

**Gelecek çalışma**

- LLM çıktısının elle doğrulanması (precision / recall) ve LLM'in küçük üstünlüğünün kaynağının incelenmesi.
- Unvan veya sektör kontrolüyle beceri katsayılarının yeniden tahmini.
- Farklı LLM'ler, promptlar ve daha gelişmiş anahtar kelime desenleriyle karşılaştırma.

## Yapay zeka kullanımı

Kod ve analizler Claude (Anthropic) yardımıyla geliştirilmiştir. Becerileri çıkaran LLM de Claude'dur (Anthropic API üzerinden).
