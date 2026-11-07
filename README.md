# Akıllı Maaş Analizi ve Karar Destek Sistemi

LLM destekli iş ilanlarından beceri çıkarımı ve istatistiksel maaş tahmini. Veri Madenciliği ve İş Zekâsı dersi grup projesi.

## Proje Hakkında

İş ilanlarında maaş bilgisinin her zaman açıkça belirtilmemesi, iş arayan bireylerin pozisyonları ücret açısından karşılaştırmasını ve maaş beklentilerini değerlendirmesini zorlaştırmaktadır. Ayrıca ilanlarda talep edilen teknik ve mesleki becerilerin serbest metin içerisinde yer alması, bu becerilerin maaş düzeyleriyle ilişkisinin sistematik olarak incelenmesini güçleştirmektedir.

Bu proje, iş ilanı metinlerinden becerileri otomatik olarak çıkararak istatistiksel maaş tahmininde kullanmayı ve farklı beceri çıkarım yöntemlerinin tahmin başarısına katkısını değerlendirmeyi amaçlamaktadır.

Bu doğrultuda, LinkedIn iş ilanlarının açıklama metinlerinden 41 beceri, anahtar kelime (Regex) ve Büyük Dil Modeli (Claude) kullanılarak çıkarılmaktadır.

Elde edilen beceriler doğrusal regresyon modeliyle maaş tahmininde kullanılmakta ve üç yaklaşım karşılaştırılmaktadır:

- **Model A:** Temel ilan özellikleri
- **Model B:** Temel özellikler + anahtar kelime becerileri
- **Model C:** Temel özellikler + LLM becerileri

Projenin temel araştırma sorusu, LLM destekli beceri çıkarımının geleneksel anahtar kelime yöntemine kıyasla maaş tahminine ek katkı sağlayıp sağlamadığıdır. Ayrıca çıkarılan beceriler ile maaş düzeyleri arasındaki istatistiksel ilişkiler incelenmektedir. Ayrıntılı sonuçlar analiz raporunda bulunmaktadır.

## Kullanılan Teknolojiler

Python, pandas, NumPy, scikit-learn, Anthropic Claude API

## Klasör Yapısı

- `src/` — Python kaynak kodları
- `data/` — Veri dosyaları ve kaydedilmiş LLM çıktıları
- `raporlar/` — Model ve analiz sonuçları (CSV)
- `docs/` — Analiz raporu, gereksinimler, Use Case, kabul kriterleri ve test senaryoları
- `requirements.txt` — Gerekli Python kütüphaneleri

## Kurulum

```bash
git clone https://github.com/alisamaxd/is-ilani-maas-analizi.git
cd is-ilani-maas-analizi
pip install -r requirements.txt
```

Veri seti: [LinkedIn Job Postings (2023–2024)](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings)


## Çalıştırma

```bash
python src/01_veri_inceleme.py
python src/02_temizle_ornekle.py
python src/03_anahtar_kelime.py
python src/04_llm_beceri.py
python src/05_model_karsilastir.py
python src/07_tekrarli_karsilastirma.py
```


Tek bir ilanı kontrol etmek için:

```bash
python src/06_ilan_kontrol.py ILAN_NUMARASI
```

## Proje Ekibi

- Sevdenur Uçar — 95230004
- Beyza Başoğlu — 95230018
- Beyza Ulukaya — 95230016
- Ali Şener — 95230050

## Yapay Zekâ Kullanımı

Kod geliştirme ve analiz süreçlerinde Claude (Anthropic) desteğinden yararlanılmıştır. LLM tabanlı beceri çıkarımı Anthropic API aracılığıyla gerçekleştirilmiştir.
