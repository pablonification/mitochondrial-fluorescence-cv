# Goal: Tugas Besar KDS - Mitochondrial Fluorescence Computer Vision

Bantu selesaikan end-to-end tugas besar IF3211 Domain-Specific Computation untuk ide milik M Zidni Alkindi dengan topik **Respirasi Sel & Produksi ATP** dan judul awal **Kuantifikasi Aktivitas Respirasi Mitokondria melalui Analisis Citra Fluoresensi Menggunakan Computer Vision**.

Mulai dari tahap riset kelayakan karena ide ini belum tervalidasi. Cek apakah dataset publik yang sesuai benar-benar tersedia, terutama dari Broad Bioimage Benchmark Collection, Cell Image Library, atau sumber bio-imaging publik lain yang dapat diunduh dan dikutip. Jangan mengarang dataset. Semua dataset yang dipakai harus memiliki sumber jelas, format jelas, ukuran yang masuk akal, dan bisa diproses dengan Python. Evaluasi apakah data tersebut benar-benar relevan untuk mitokondria, fluoresensi, potensial membran mitokondria, respirasi sel, atau proksi aktivitas bioenergetik. Jika klaim awal tentang estimasi produksi ATP terlalu kuat untuk data citra yang tersedia, ubah framing ilmiahnya menjadi lebih aman, misalnya kuantifikasi intensitas fluoresensi mitokondria sebagai indikator tidak langsung aktivitas atau keadaan mitokondria, bukan pengukuran ATP absolut.

Perhatikan keterbatasan storage lokal. Mac saat ini hanya tersisa sekitar 1 GB, jadi kelola ruang disk secara aman dan iteratif selama bekerja. Sebelum mengunduh dataset atau dependency besar, cek ukuran file dan ketersediaan storage. Hindari mengunduh dataset raksasa jika tidak perlu. Prioritaskan subset kecil, sample images, file yang sudah tersedia lokal, atau data yang bisa diproses streaming. Jika storage hampir habis atau proses membutuhkan ruang tambahan, lakukan safe cleaning secara bertahap: identifikasi cache, build artifact, temp file, atau output yang jelas aman dihapus; jelaskan apa yang akan dibersihkan; hapus hanya file sementara atau output yang dihasilkan oleh proses ini; lalu cek ulang storage sebelum lanjut. Jangan menghapus file user, dataset penting, kode proyek lain, dokumen, foto, atau folder yang tidak jelas kepemilikannya. Hindari destructive cleanup seperti menghapus folder besar secara membabi buta. Semua cleaning harus konservatif, dapat dijelaskan, dan dilakukan hanya bila diperlukan untuk menyelesaikan tugas.

Setelah riset dataset, tentukan pendekatan komputasi yang realistis untuk tugas kuliah ini. Jangan memaksakan YOLO atau ONNX jika dataset tidak memiliki label bounding box/segmentation mask atau jika training object detection tidak realistis. Pilih pendekatan yang paling feasible berdasarkan data yang ditemukan. Pendekatan dapat berupa classical computer vision dengan OpenCV atau scikit-image untuk thresholding, denoising, segmentation, connected components, intensity quantification, dan feature extraction; atau model ringan/pretrained jika dataset dan label mendukung. Prioritaskan solusi yang bisa berjalan di laptop tanpa GPU dan dapat dijelaskan dalam laporan maksimal 6 halaman. Buat keputusan teknis secara eksplisit dalam README atau notebook: mengapa metode dipilih, apa keterbatasannya, dan bagaimana hubungannya dengan konsep respirasi sel, mitokondria, potensial membran, dan produksi energi.

Implementasikan solusi lengkap dengan format proyek yang rapi:

1. Modul Python reusable untuk loading dataset citra, preprocessing, segmentasi atau identifikasi area mitokondria/area fluoresensi relevan, ekstraksi fitur, dan interpretasi ringkas.
2. Fitur kuantitatif minimal: mean intensity, total fluorescence, area, integrated density, jumlah objek/komponen, dan metrik kualitas sederhana jika memungkinkan.
3. Jupyter notebook untuk analisis ilmiah dari dataset sampai hasil kuantitatif, visualisasi, interpretasi, dan kesimpulan.
4. Streamlit mini dashboard untuk demo interaktif yang memungkinkan pengguna memilih atau mengunggah citra, melihat hasil preprocessing, mask/overlay/bounding region, dan metrik intensitas.
5. README, requirements, dan struktur folder yang mudah dijalankan dosen/asisten.
6. Sample data kecil atau sample images agar demo bisa langsung berjalan tanpa mengunduh ulang dataset besar, bila memungkinkan.

Kerjakan secara iteratif dan diuji sampai benar-benar beres. Setelah setiap bagian penting diimplementasikan, jalankan pengujian yang relevan, periksa output, perbaiki bug, lalu test ulang sebelum lanjut. Minimal verifikasi mencakup functional test untuk loader dataset dan fungsi pemrosesan citra, smoke test pipeline analisis, validasi bahwa output metrik tidak kosong atau NaN untuk sample image, pengecekan visual mask/overlay, serta pengujian Streamlit app secara visual/interaktif memakai in-app browser Codex. Jika in-app browser tidak tersedia atau tidak memadai, gunakan Playwright sebagai fallback. Saat menguji app, pastikan halaman terbuka, citra dapat dipilih atau diunggah, hasil segmentasi/overlay muncul, metrik intensitas tampil, tidak ada error di terminal/browser, layout terbaca, dan interpretasi ilmiah tidak overclaim. Jika ditemukan bug, hasil segmentasi buruk, atau UI bermasalah, perbaiki lalu jalankan ulang pengujian sampai masalah hilang.

Akhiri dengan hasil yang siap dipakai untuk tugas:

1. Ringkasan ide final yang sudah divalidasi.
2. Dataset dan sumbernya.
3. Alasan pendekatan komputasi yang dipilih.
4. File yang dibuat atau diubah.
5. Cara menjalankan notebook dan Streamlit app.
6. Hasil pengujian yang sudah dilakukan.
7. Catatan keterbatasan biologis dan komputasional.

Pastikan seluruh framing tetap comply dengan spesifikasi tugas IF3211: solusi Python berbasis komputasi biologi, dataset nyata, metode jelas, analisis kuantitatif dan kualitatif, visualisasi hasil, dan interpretasi yang terkait dengan respirasi sel serta produksi energi tanpa mengklaim pengukuran ATP absolut jika data tidak mendukung.
