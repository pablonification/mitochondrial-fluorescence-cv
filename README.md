# Kuantifikasi Fluoresensi Mitokondria dengan Computer Vision

Proyek ini dibuat untuk tugas besar IF3211 Domain-Specific Computation pada topik
**Respirasi Sel & Produksi ATP**. Fokus akhirnya adalah analisis citra fluoresensi
mitokondria, bukan estimasi ATP absolut. Program menghitung fitur citra seperti
intensitas fluoresensi, luas area foreground, jumlah komponen, dan integrated
density sebagai indikator tidak langsung keadaan struktur/sinyal mitokondria.

## Validasi Dataset

Dataset yang dipilih adalah **BBBC053: Murine Cath.a differentiated cells -
Mitochondria** dari Broad Bioimage Benchmark Collection.

- Sumber: https://bbbc.broadinstitute.org/BBBC053
- Koleksi BBBC: https://bbbc.broadinstitute.org/bbbc
- Biologi: mitochondria divisualisasi dengan antibodi TOM20 dan secondary
  antibody AlexaFluor 568.
- Format dataset penuh: TIFF 16-bit, 2048 x 2048 piksel.
- Ground truth: label biologis berdasarkan struktur direktori, termasuk kondisi
  kontrol DMSO dan perturbasi FCCP/CCCP-like.
- Sitasi yang direkomendasikan BBBC: Edwards, P. et al., BBBC053, Broad Bioimage
  Benchmark Collection; Ljosa et al., Nature Methods 2012.

BBBC dipilih karena langsung menyediakan dataset mitokondria fluoresensi dengan
sumber, format, label kondisi, dan sitasi yang jelas. Sumber bio-imaging lain
seperti Cell Image Library tidak dipakai pada implementasi ini karena BBBC053
sudah cukup spesifik untuk tujuan tugas.

Implementasi sekarang memakai archive resmi `FCCP-20220127T153841Z-001.zip`
dari BBBC053 dan mengekstrak **58 citra TIFF 16-bit full-resolution**:
29 citra kontrol DMSO dan 29 citra perturbasi FCCP. Dua PNG preview lama hanya
disimpan sebagai referensi ringan, bukan dataset analisis utama.

## Alasan Pendekatan

Dataset BBBC053 relevan untuk mitokondria dan fluoresensi, tetapi tidak menyediakan
label bounding box atau segmentation mask untuk training object detection lokal.
Karena itu proyek memakai classical computer vision:

1. load citra grayscale,
2. background subtraction sederhana,
3. Gaussian denoising,
4. threshold Otsu,
5. connected components,
6. ekstraksi fitur fluoresensi dan kualitas.

Pendekatan ini realistis untuk laptop tanpa GPU, mudah dijelaskan dalam laporan 6
halaman, dan tidak memaksa YOLO/ONNX tanpa label yang sesuai.

## Fitur Kuantitatif

Output utama:

- mean intensity,
- total fluorescence,
- foreground area,
- integrated density,
- object/component count,
- coverage fraction,
- background mean/std,
- signal-to-background score,
- quality flag.

Interpretasi biologis dibatasi: fitur tersebut dapat dibahas sebagai proksi
intensitas/luas sinyal mitokondria dan morfologi foreground, bukan pengukuran
langsung respirasi sel atau produksi ATP absolut.

## Struktur

```text
mitochondrial-fluorescence-cv/
  app.py
  run_analysis.py
  requirements.txt
  README.md
  data/
    raw/
      BBBC053_FCCP.zip
    bbbc053_full/
      FCCP/
        DMSO/
        FCCP/
    sample_manifest.csv
    sample_images/
      bbbc053_dmso_example.png
      bbbc053_fccp_example.png
  notebooks/
    bioenergetic_analysis.ipynb
  src/
    bioenergetics.py
  tests/
    test_bioenergetics.py
  outputs/
    figures/
```

## Instalasi

Jalankan dari root folder proyek ini:

```bash
python3 -m pip install -r requirements.txt
```

## Menjalankan Analisis Script

```bash
python3 run_analysis.py
```

Output yang dibuat:

- `outputs/image_metrics.csv`
- `outputs/condition_summary.csv`
- `outputs/dataset_validation.csv`
- `outputs/figures/*_preprocessed.png`
- `outputs/figures/*_mask.png`
- `outputs/figures/*_overlay.png`
- `outputs/figures/sample_metric_bars.png`

## Menjalankan Notebook

Buka atau eksekusi:

```text
notebooks/bioenergetic_analysis.ipynb
```

Notebook berisi validasi dataset, alasan metode, pemrosesan 58 citra TIFF
BBBC053, visualisasi mask/overlay, tabel fitur, ringkasan kondisi, dan kesimpulan
biologis yang tidak overclaim.

## Menjalankan Dashboard Streamlit

```bash
python3 -m streamlit run app.py
```

Dashboard menyediakan pilihan citra BBBC053 atau upload citra, tampilan original,
preprocessed, mask, overlay dengan bounding region, metrik fluoresensi, validasi
dataset, dan interpretasi.

## Menjalankan Test

```bash
python3 -m pytest tests -q
```

Test mencakup loader manifest 58 TIFF, segmentasi synthetic image, connected
components, output metrik finite dan tidak kosong, overlay visual, summary kondisi,
dan validasi dataset.

## Ringkasan Ide Final

Ide awal "estimasi produksi ATP dari citra fluoresensi" diframing ulang menjadi
**kuantifikasi fluoresensi dan area struktur mitokondria sebagai indikator tidak
langsung keadaan mitokondria**. Framing ini lebih aman karena citra TOM20/AlexaFluor
568 memperlihatkan struktur/sinyal mitokondria, tetapi tidak cukup untuk menghitung
ATP absolut tanpa data metabolik tambahan seperti OCR/ECAR, assay ATP, atau
kalibrasi eksperimen.
