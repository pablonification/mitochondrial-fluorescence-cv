**Brainstorm**  
**Nama: Arqila Surya Putra**

**Topik:**

1. Respirasi Sel & Produksi ATP 

**Judul Solusi:**

Analisis Pergeseran Profil Bioenergetik Makrofag Berdasarkan Data OCR dan ECAR pada Stimulasi LPS dan IL-4

**Latar Belakang & Motivasi:**  
(Kenapa masalah ini penting?)

Respirasi sel merupakan proses penting dalam produksi energi seluler. Selain melalui respirasi mitokondria, sel juga dapat menghasilkan energi melalui glikolisis. Pada sel imun seperti makrofag, pola penggunaan jalur energi dapat berubah ketika sel menerima stimulasi tertentu. Stimulasi LPS umumnya berkaitan dengan respons inflamasi dan peningkatan aktivitas glikolitik, sedangkan stimulasi IL-4 berkaitan dengan aktivasi alternatif makrofag.

Perubahan metabolisme energi ini dapat diamati melalui data Seahorse XF, yaitu Oxygen Consumption Rate (OCR) sebagai indikator respirasi mitokondria dan Extracellular Acidification Rate (ECAR) sebagai indikator aktivitas glikolisis. Oleh karena itu, analisis komputasi terhadap data OCR dan ECAR dapat membantu memahami bagaimana makrofag mengubah strategi produksi energinya setelah stimulasi biologis.

**Rumusan Pertanyaan Penelitian:**  
(Contoh: "Seberapa akurat metode X dalam memprediksi Y?")

Bagaimana stimulasi LPS dan IL-4 memengaruhi profil bioenergetik makrofag berdasarkan perubahan OCR dan ECAR?

**Permasalahan Spesifik:**

1. Perubahan metabolisme energi pada makrofag sulit diamati hanya dari penjelasan biologis kualitatif.
2. Data OCR dan ECAR berbentuk time-series sehingga membutuhkan pengolahan komputasional untuk membandingkan kondisi kontrol dan stimulasi.
3. Diperlukan metode analisis yang dapat menunjukkan apakah stimulasi tertentu lebih berkaitan dengan peningkatan aktivitas glikolisis atau respirasi mitokondria.

**Usulan Solusi & Metode Komputasi:**  
(Algoritma / pendekatan apa yang akan dipakai?)

Solusi yang diusulkan adalah program Python untuk menganalisis data OCR dan ECAR makrofag dari file Excel supplementary dataset. Program akan melakukan parsing data, pemisahan kondisi kontrol dan perlakuan, analisis pre-injection dan post-injection, serta visualisasi perubahan profil bioenergetik.

Metode komputasi yang digunakan:

1. Data preprocessing untuk membaca dan merapikan data OCR/ECAR dari file `.xlsx`.
2. Feature extraction, meliputi rata-rata OCR dan ECAR sebelum serta sesudah stimulasi, perubahan nilai post-injection terhadap kontrol, rasio ECAR/OCR, dan area under curve (AUC) sederhana.
3. Comparative analysis untuk membandingkan profil Control, LPS, dan IL-4.
4. Visualisasi data menggunakan line plot, bar chart, dan scatter plot OCR vs ECAR.
5. Interpretasi biologis untuk menilai kecenderungan glycolytic shift atau perubahan respirasi mitokondria.

**Dataset yang Diusulkan:**  
(Termasuk sumber, format, ketersediaan)

Dataset yang digunakan berasal dari supplementary data artikel:

Glycolytic Stimulation is not a Requirement for M2 Macrophage Differentiation.

Sumber: https://pmc.ncbi.nlm.nih.gov/articles/PMC6449248/

File dataset:

1. `NIHMS1505771-supplement-2.xlsx`: Table S1, dataset real-time ECAR dan OCR pada bone marrow-derived macrophages yang distimulasi LPS. Format Excel, tersedia sebagai supplementary material.
2. `NIHMS1505771-supplement-3.xlsx`: Table S2, dataset real-time ECAR dan OCR pada bone marrow-derived macrophages yang distimulasi IL-4. Format Excel, tersedia sebagai supplementary material.

Kedua dataset berisi data time-series dalam bentuk persentase OCR dan ECAR, dengan 5 replicate reads, nilai rata-rata, dan standar deviasi untuk setiap timepoint.

**Fitur Utama Program:**

1. Membaca dataset OCR dan ECAR dari file Excel.
2. Menampilkan ringkasan statistik untuk kondisi Control, LPS, dan IL-4.
3. Menghitung perubahan ECAR dan OCR sebelum serta sesudah stimulasi.
4. Menghitung rasio ECAR/OCR sebagai indikator kecenderungan penggunaan glikolisis relatif terhadap respirasi mitokondria.
5. Membuat visualisasi line plot OCR/ECAR terhadap waktu, bar chart perubahan rata-rata, dan scatter plot OCR vs ECAR.
6. Menghasilkan interpretasi sederhana mengenai apakah suatu kondisi menunjukkan peningkatan aktivitas glikolitik atau perubahan respirasi mitokondria.

**Analisis SWOT**

| Indikator | Penjelasan |
| :---- | :---- |
| Strengths | Dataset nyata tersedia dalam format Excel, topik sesuai dengan respirasi sel dan produksi energi, serta hasil dapat dianalisis secara kuantitatif dan divisualisasikan dengan jelas. |
| Weakness | Dataset menggunakan nilai OCR dan ECAR dalam bentuk persentase ter-normalisasi, sehingga tidak dapat digunakan untuk menghitung produksi ATP absolut secara langsung. |
| Opportunities | Analisis dapat dikembangkan menjadi klasifikasi profil bioenergetik, misalnya glycolysis-dominant, OXPHOS-dominant, atau balanced, serta dapat dikaitkan dengan respons imun makrofag. |
| Threats | Interpretasi biologis harus berhati-hati karena OCR dan ECAR merupakan indikator tidak langsung dari produksi energi, sehingga kesimpulan perlu dibatasi pada profil bioenergetik, bukan klaim ATP absolut. |
