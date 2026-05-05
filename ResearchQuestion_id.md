# Pertanyaan Penelitian & Hipotesis untuk BI-AI Engine

Dihasilkan dari kode BI-AI Engine: pipeline analisis saham otomatis yang mengintegrasikan harga yfinance, scraping berita CNBC, sentimen FinBERT, penilaian gabungan (40% kuantitatif + 60% kualitatif), dan rekomendasi.

## RQ1: Akurasi Model
**Hipotesis**: Skor sentimen FinBERT berkorelasi >70% dengan return harga maju 7 hari aktual (lebih baik daripada baseline kata kunci).

**Pengumpulan Data**:
- Jalankan pipeline pada 100 ticker S&P500 (harian, 30 hari).
- Kumpulkan: headline, skor FinBERT (1-10), %perubahan aktual (hari+7).
- Sumber: Existing (yfinance, CNBC), perluas ke multiple tanggal.

**Metode Analisis**:
1. Korelasi Pearson (skor vs return maju).
2. Regresi: skor ~ return + kontrol (volatilitas).
3. Baseline: hitung kata kunci (POSITIVE_KEYWORDS vs NEGATIVE_KEYWORDS).

**Penyelesaian**:
| Hasil | Interpretasi |
|-------|--------------|
| Korelasi >0.7 | Kekuatan prediktif kuat |
| 0.4-0.7 | Utilitas sedang |
| <0.4 | Perlu fine-tuning |

**Metrik Sukses**: p-value <0.01, R²>0.25.

---

## RQ2: Keandalan Sumber Data
**Hipotesis**: Tingkat keberhasilan scraping CNBC >90% selama jam pasar, dengan headline mengandung rata-rata ≥2 kata kunci bisnis.

**Pengumpulan Data**:
- 500 scraping (waktu acak, hari kerja 09:00-16:00 ET).
- Log: status HTTP, jumlah headline, densitas kata kunci (BUSINESS_KEYWORDS).
- Bypass cache (`force_refresh=True`).

**Metode Analisis**:
1. Tingkat keberhasilan (200 OK / total percobaan).
2. Statistik deskriptif (headline/scrape, kata kunci/headline).
3. Time-series: keberhasilan per jam.

**Penyelesaian**:
- Uji-t: jam pasar vs non-jam pasar.
- Jika <90%, tambah fallback (Reuters, Yahoo News).

**Metrik Sukses**: Keberhasilan ≥90%, kata kunci ≥1.5 rata-rata.

---

## RQ3: Efektivitas Skor Gabungan
**Hipotesis**: Pembobotan optimal (60% sentimen + 40% harga) mengungguli pembobotan sama (50/50) atau hanya harga dalam backtesting return.

**Pengumpulan Data**:
- Run historis: 50 ticker × 60 hari.
- Hitung skor: saat ini (60/40), alt1 (50/50), alt2 (100% harga).
- Simulasi: Beli jika skor≥7, Jual ≤4, Tahan lainnya; lacak return portofolio.

**Metode Analisis**:
1. Rasio Sharpe, max drawdown per strategi.
2. ANOVA: return ~ strategi.
3. Kurva ROC (threshold skor vs akurasi beli/jual).

**Penyelesaian**:
| Pembobotan | Sharpe Diharapkan |
|------------|-------------------|
| 60/40      | >1.2             |
| 50/50      | >1.0             |
| Hanya Harga| <0.8             |

**Metrik Sukses**: Sharpe 60/40 > lainnya (p<0.05).

---

## RQ4: Generalisasi Lintas Pasar
**Hipotesis**: Model berkinerja konsisten (std dev skor <1.5) di US (S&P500), Asia (Nikkei), Eropa (DAX).

**Pengumpulan Data**:
- 20 ticker/region (contoh: AAPL/NKEI/DAX).
- Jalankan pipeline, ekstrak volatilitas sentimen, relevansi kata kunci.

**Metode Analisis**:
1. ANOVA: varians skor ~ region.
2. Uji-t: performa US vs non-US.
3. PCA: dekomposisi driver skor (harga vs sentimen).

**Penyelesaian**:
- Jika varians tinggi, tuning kata kunci spesifik region.

**Metrik Sukses**: F-stat p>0.05 (tidak ada efek region).

---

## RQ5: Kegunaan Rekomendasi
**Hipotesis**: Rekomendasi prioritas 'Tinggi' menghasilkan rata-rata return 7 hari +2% vs 'Rendah' (-0.5%).

**Pengumpulan Data**:
- 200 analisis, label rekomendasi berdasarkan prioritas.
- Lacak return maju 7 hari pasca-rekomendasi.

**Metode Analisis**:
1. Uji-t: return ~ prioritas.
2. Logistik: outperform pasar ~ sinyal rekomendasi.
3. Survival: waktu ke +2% pasca-rekomendasi.

**Penyelesaian**:
| Prioritas | Return Diharapkan |
|-----------|-------------------|
| Tinggi    | ≥+2%             |
| Sedang    | 0-2%             |
| Rendah    | ≤0%              |

**Metrik Sukses**: t-stat >2, effect size >0.5.

## Catatan Implementasi
- **Manfaatkan Kode**: Perluas `BIEngine.run()` dengan loop/batch.
- **Penyimpanan**: Simpan hasil ke Supabase (`stock_data`, `sentiment_score`).
- **Visualisasi**: Gunakan Recharts frontend untuk hasil.
- **Ekstensi**: Tambah panggilan `batch_analyze` via API.

**Selanjutnya**: Jalankan eksperimen via loop `python bi_engine.py` atau batching API.

---
*Dihasilkan oleh BLACKBOXAI dari analisis kode*

