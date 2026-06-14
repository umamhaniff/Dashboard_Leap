# 🛡️ EduDecision AI V2 - LKP LEAP Surabaya

**EduDecision AI V2** adalah sistem pendukung keputusan hibrida (*Hybrid Decision Support System - DSS*) berbasis **Streamlit** yang dirancang untuk LKP LEAP Surabaya. Sistem ini memadukan data akademis dari Google Sheets dengan data operasional dari database SQL (MariaDB) untuk menghasilkan analisis taktis dan rekomendasi yang dipandu oleh kecerdasan buatan (**Google Gemini AI**).

Sistem ini didesain menggunakan **Genesis Design System** yang responsif dan mengedepankan pendekatan *Mobile First Approach (MFA)* tetapi tetap optimal saat dijalankan pada layar desktop.

---

## 🎨 Arsitektur & Sumber Data Utama

EduDecision AI V2 memiliki dual-input terisolasi untuk memetakan dua aspek utama operasional lembaga:

1. **Google Sheets (Fokus Akademik & Kehadiran)**:
   * **Sumber Data**: `DATA_SISWA`, `DATA_ABSENSI`, `DATA_NILAI`, `DATA_KELUAR`, `DATA_OVERVIEW`.
   * **Fokus**: Monitoring performa akademis (nilai ujian), tren kehadiran harian, dan prediksi retensi belajar siswa.
   
2. **Database SQL MariaDB (Fokus Operasional & Layanan Siswa)**:
   * **Sumber Data**: Tabel `siswa`, `kursus_siswa`, `jadwal_siswa`, `catatan_siswa`, `catatan_remidi_siswa`, `web_statistik`.
   * **Fokus**: Audit administrasi kelas (rombel), persetujuan rapor (*Rapor Approval*), penanganan kasus siswa oleh CS (*Customer Relationship*), dan audit log remedial.

---

## ✨ Fitur Utama Sistem

### 🏠 1. Unified LKP Overview (Default Landing Page)
* Halaman utama ringkasan eksekutif setelah login yang menyinkronkan data Google Sheets dan MariaDB secara bersamaan.
* Menyajikan KPI makro: Total siswa terdaftar, siswa aktif, rata-rata kehadiran harian, persentase kelulusan rapor, dan jumlah kasus observasi terbuka.
* Visualisasi grafik tren kehadiran dan pembagian rombel secara berdampingan.

### 📊 2. Modul Akademik (Google Sheets)
* **Performa Akademik & Grade**: Distribusi nilai ujian tengah semester (Mid) dan akhir (Final) beserta sebaran grade kelulusan.
* **Kehadiran & Ketidakhadiran**: Analisis detail tren absensi harian dan identifikasi alasan ketidakhadiran (Sakit, Izin, Alfa).
* **🔮 AI Student Predictor**: Analisis holistik kesehatan belajar siswa untuk mendeteksi siswa yang membutuhkan perhatian khusus (nilai rendah, kehadiran rendah, atau risiko putus les) beserta rencana mitigasi pembinaannya.

### 🗄️ 3. Modul Operasional (Database SQL)
* **👤 Student 360 View**: Pencarian profil siswa terpadu yang merangkum data diri, riwayat kursus aktif, rombel jadwal, log remedial, hingga catatan kasus bimbingan CS.
* **🏫 Rombel & Persetujuan Rapor**: Monitoring kemajuan persetujuan rapor per rombel kelas.
* **🔍 Kasus Observasi (CRM/CS)**: Pelacakan kasus bimbingan siswa yang sedang diobservasi lebih lanjut oleh tim CS.
* **📝 Audit Remedial**: Pelacakan riwayat kenaikan nilai siswa sebelum dan sesudah remedial serta status persetujuan guru pengampu.

### 📥 4. Ekspor Laporan Premium (PNG Local Download)
* Semua panel analisis AI dilengkapi dengan tombol unduh lokal (**Unduh Laporan sebagai PNG**).
* Proses konversi dilakukan secara aman pada sisi peramban klien (*browser-side*) menggunakan library `html2canvas` dan `marked` di dalam Streamlit iframe sandbox.
* **Tanpa Write-Back**: Sistem tidak menyimpan data rekomendasi AI ke database maupun Google Sheets demi menjaga integritas data asli.

---

## 🏗️ Struktur Proyek

```
Dashboard_Leap/
├── app.py                      # 🎯 Entry point Streamlit application
├── config/
│   └── settings.py             # ⚙️ Pengaturan & pemetaan variabel database/GSheets
├── core/
│   ├── data_pipeline.py        # 🔄 Pipeline penarikan, pembersihan, & mock data
│   ├── llm_analyzer.py         # 🤖 Engine integrasi Gemini AI (Failover & Prompts)
│   └── charts.py               # 📊 Visualisasi grafik interaktif (Plotly)
├── styles/
│   └── style.css               # 🎨 Lembar gaya Genesis Design System
├── tests/
│   ├── test_data_pipeline.py   # 🧪 Unit test untuk pipeline data
│   ├── test_llm_analyzer.py    # 🧪 Unit test untuk prompt AI
│   └── test_settings.py        # 🧪 Unit test untuk pemuatan konfigurasi
├── .streamlit/
│   └── secrets.toml            # 🔐 Kredensial rahasia (API Key, Service Account)
├── requirements.txt            # 📦 Daftar dependensi Python
├── README.md                   # 📖 Dokumentasi proyek utama
└── GEMINI.md                   #  Konteks persisten untuk AI Code Assistant
```

---

## 🚀 Pemasangan & Konfigurasi

### Prasyarat Sistem
* Python 3.9 s.d. 3.13
* MariaDB / MySQL Server (Default: Port `3307` sesuai konfigurasi sistem LKP)

### Langkah Setup

1. **Clone repositori proyek**:
   ```bash
   git clone <url-repository>
   cd Dashboard_Leap
   ```

2. **Buat & aktifkan virtual environment**:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instal dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Secrets**:
   Buat atau sesuaikan file `.streamlit/secrets.toml` dengan format berikut:
   ```toml
   # Gemini API Key
   GEMINI_API_KEY = "AIzaSy..."

   # Google Sheets URL
   spreadsheet_url = "https://docs.google.com/spreadsheets/d/ID_SPREADSHEET/edit"

   # MariaDB Config
   mariadb_host = "127.0.0.1"
   mariadb_port = 3307
   mariadb_user = "root"
   mariadb_password = ""
   mariadb_database = "dataleap_v5_migration"

   # Password Login
   SYSTEM_PASSWORD = "leapadmin2026"

   # GCP Service Account
   [gcp_service_account_json]
   type = "service_account"
   project_id = "dashboard-leap"
   private_key_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "..."
   # ... lengkapi field lainnya
   ```

---

## 🎮 Cara Menjalankan

### 1. Menjalankan Dashboard Streamlit
```powershell
.venv/Scripts/python.exe -m streamlit run app.py
```
Aplikasi secara default dapat diakses melalui peramban di alamat `http://localhost:8501`.

### 2. Menjalankan Unit Test (Pytest)
Untuk memverifikasi fungsionalitas pipeline data, prompt, dan settings, jalankan:
```powershell
.venv/Scripts/python.exe -m pytest -v
```

---

## 🤖 Failover Model Gemini AI
Modul analisis didesain tangguh terhadap kendala kuota API (*rate limiting*) menggunakan mekanisme *failover loop* dengan prioritas model sebagai berikut:
1. `gemini-3.1-flash-lite-preview`
2. `gemini-3-flash-preview`
3. `gemini-2.5-flash-lite`
4. `gemini-2.5-flash`
5. `gemini-2.0-flash-lite`
6. `gemini-2.0-flash`
7. `gemini-3.1-pro-preview`
8. `gemma-3-27b-it`
9. `gemini-flash-latest` (1.5 Flash - Stabil Fallback)

---

## 🔐 Keamanan & Kebijakan Data
* **Kredensial**: File `.streamlit/secrets.toml` dan berkas kunci JSON akun layanan tidak boleh di-commit ke Git.
* **Akses Read-Only**: Database dan Sheets diproses secara *Read-Only* di tingkat aplikasi untuk menghindari manipulasi data yang tidak sengaja.
* **Mock Failover Engine**: Jika koneksi MariaDB lokal gagal dijangkau, sistem akan otomatis beralih menggunakan simulasi mesin data (*Mock Engine*) sehingga dashboard tetap dapat diuji.
