# 📑 DESIGN SPECIFICATION: EDUDECISION AI V2 - DUAL-INPUT DSS
**Date:** 2026-06-14  
**Status:** Approved by User  
**Target Branch:** `feature/dss-hybrid-mariadb-gsheets`  

---

## 1. Executive Summary & Core Concept

EduDecision AI V2 adalah sistem pendukung keputusan hibrida (*Hybrid Decision Support System*) yang diimplementasikan menggunakan **Streamlit** dan dirancang dengan estetika **Apple Web Design**. 

Berdasarkan analisis kebutuhan terbaru, sistem ini mengisolasi **2 Input berbeda dan menghasilkan 2 Output terpisah** (tidak dapat digabungkan) untuk memenuhi dua tujuan yang sangat berbeda:
1.  **Modul Google Sheets (Akademik & Retensi Siswa)**: Menganalisis data harian siswa untuk mengidentifikasi tren ketidakhadiran, tingkat kelulusan, remedi, dan mitigasi siswa keluar (*dropout*).
2.  **Modul MariaDB Database (ERP & Keamanan Operasional)**: Mengaudit aktivitas sistem ERP, melacak alur prospek (*leads CRM*), memantau kepatuhan kehadiran karyawan, dan mendeteksi anomali akses.

---

## 2. Dual Input & Dual Output Blueprint

```
                     +---------------------------------------+
                     |         EduDecision AI v2             |
                     +-------------------+-------------------+
                                         |
                                         v
                      [ Autentikasi: Password Gate ]
                                         |
             +---------------------------+---------------------------+
             | (Pilihan Sumber Data)                                 |
             v                                                       v
+-----------------------+                               +-----------------------+
|  Input: Google Sheets |                               |  Input: MariaDB       |
|  (Cloud SPS Connector)|                               |  (Database Port 3077) |
+-----------+-----------+                               +-----------+-----------+
            |                                                       |
            v                                                       v
+-----------------------+                               +-----------------------+
|  Dashboard Akademik   |                               |  Dashboard ERP Audit  |
|  - Rombel & Siswa     |                               |  - Pipeline Leads FO  |
|  - Kehadiran & Absen  |                               |  - Kehadiran Karyawan |
|  - Nilai & Remidi     |                               |  - Audit Activity Log |
+-----------+-----------+                               +-----------+-----------+
            |                                                       |
            v                                                       v
+-----------------------+                               +-----------------------+
| AI: Retention Engine  |                               | AI: Security Engine   |
| - Gemini Failover     |                               | - Gemini Failover     |
| - Rekomendasi Retensi |                               | - Deteksi Anomali     |
+-----------------------+                               +-----------------------+
```

### A. Modul 1: Google Sheets (Akademik)
*   **Input Data**: Sheet `DATA_SISWA`, `DATA_ABSENSI`, `DATA_NILAI`, `DATA_KELUAR`, dan `DATA_OVERVIEW`.
*   **KPI & Metrik Operasional** (Berdasarkan `docs/dashboard_context.md`):
    *   **High-Level Summary**: Jumlah Rombel (16), Siswa Aktif (236), Siswa Keluar (4), Kelas Tambahan (42), Siswa Pengganti (34).
    *   **Kehadiran**: Tren kehadiran harian siswa, Top/Bottom 3 Rombel terbaik/terendah, persentase alasan ketidakhadiran (Tanpa Keterangan: 50.6%, Izin: 21.8%, Sakit: 8.9%).
    *   **Nilai & Remidi**: Performa rata-rata kelas (Mid-Test: 54.93, Final-Test: 71.60), distribusi grade (A, B, C, D, E, F), total siswa remedi (305 siswa) dengan batas nilai kelulusan 70.
    *   **Siswa Keluar**: Segmentasi alasan keluar (tidak tertarik: 20%, instruktur tidak cocok: 17.1%) dan daftar siswa pengganti (*Replaced*).
*   **Output Dashboard**: Visualisasi Plotly berupa tren kehadiran harian, bar chart rombel performa, histogram distribusi grade nilai, dan dataframe interaktif daftar siswa remedi/keluar.
*   **AI Engine (Prescriptive Retention)**: Pemicuan manual Gemini untuk menganalisis anomali kehadiran siswa dan memberikan 5 rekomendasi mitigasi retensi akademik.

### B. Modul 2: MariaDB Database (ERP & Security Audit)
*   **Input Data**: Query SQL langsung dari database lokal `dataleap_v5_migration` (Port `3077`) untuk tabel `calon_siswa`, `calon_siswa_akademik`, `calon_siswa_bayar`, `web_statistik`, `karyawan`, `absensi` (karyawan), dan `activity_log`.
*   **KPI & Metrik Operasional** (Berdasarkan `docs/database_context.md`):
    *   **Pipeline CRM (Calon Siswa)**: Tingkat konversi leads (`kontak_prospek`) dari status 'baru' -> `calon_siswa` -> pengisian form (`calon_siswa_akademik`) -> kelulusan pipeline -> transaksi pembayaran (`calon_siswa_bayar`).
    *   **HR Karyawan**: Absensi harian karyawan (Tepat Waktu, Izin, Terlambat, Hadir) dan jenis pengajuan izin (Sakit, Cuti, Lembur, Ijin Darurat).
    *   **Kemitraan (BusDev)**: Progres deal kemitraan B2B dan pembagian link folder drive.
    *   **Audit Activity Log**: Log mutasi database (Create, Update, Delete) yang direkam dalam format payload JSON.
*   **Output Dashboard**: Statistik konversi pipeline leads CRM, kepatuhan kehadiran staf karyawan, dan visualisasi aktivitas write/delete database untuk keperluan compliance.
*   **AI Engine (Security & Integrity Audit)**: Pemicuan manual Gemini untuk mendeteksi akses mencurigakan di luar jam kerja, anomali input, dan inkonsistensi foreign key, serta menyusun rekomendasi mitigasi keamanan.

---

## 3. Tech Stack & Integration Specs

*   **Framework**: Streamlit (Single-Page App dengan modul navigasi dinamis berbasis Session State).
*   **Database Connector**: `pymysql` atau `mysql-connector-python` untuk MariaDB Port `3077`.
*   **Google Sheets Connector**: `gspread` + Google Service Account Credentials.
*   **Gen AI Engine**: `google-generativeai` dengan implementasi **Multi-Model Failover Registry**:
    1.  `models/gemini-3.1-flash-lite-preview` (Utama)
    2.  `models/gemini-3-flash-preview`
    3.  `models/gemini-2.5-flash-lite`
    4.  `models/gemini-2.5-flash`
    5.  `models/gemini-flash-latest` (Fallback)
*   **Visual Engine**: Plotly Express & Go untuk visualisasi chart interaktif.

---

## 4. Apple Aesthetics Styling System

Dashboard akan dihias menggunakan kustom CSS ([styles/style.css](file:///D:/_CampusLife/ProjectCampus/6Magang/Dashboard_Leap/styles/style.css)) berdasarkan panduan Apple Design Guidelines:
*   **Global Navigation**: Bar hitam pekat (`#000000`) setinggi 44px di bagian paling atas.
*   **Sub-Navigation**: Frosted glass transparan dengan backdrop blur di bawah global nav untuk memuat filter pencarian, tombol "Change Source", dan tombol "Run AI Analysis".
*   **Rhythms Layout**: Alternating Canvas (Overview menggunakan background putih bersih `#ffffff` atau parchment `#f5f5f7` dengan card `18px` membulat; Panel AI menggunakan background gelap `#1d1d1f` dengan tulisan putih).
*   **Accent Color**: Satu-satunya warna interaksi utama adalah **Action Blue** (`#0066cc`).
*   **Shadows**: Satu drop-shadow lembut (`rgba(0, 0, 0, 0.22) 3px 5px 30px`) hanya diberikan pada card AI yang melayang di atas permukaan canvas.

---

## 5. Development Strategy & Mock Fallback

*   **Google Sheets API**: Apabila koneksi gagal, sistem akan menampilkan error log secara eksplisit dan menghentikan pemuatan (tidak menggunakan fallback lokal).
*   **MariaDB Port 3077**: Jika database lokal kosong atau tidak aktif, sistem akan beralih secara otomatis ke **Mock Mode** untuk menyimulasikan data `calon_siswa`, `web_statistik`, dan `activity_log` yang realistis berdasarkan kamus data ERP v5.

---

## 6. Pre-Submission Checklist

*   [ ] Mengubah pengaturan loading di [.streamlit/secrets.toml](file:///D:/_CampusLife/ProjectCampus/6Magang/Dashboard_Leap/.streamlit/secrets.toml) agar memuat sheet `DATA_SISWA` sebagai pengganti `DATA_MASTER`, serta menambahkan `DATA_KELUAR`.
*   [ ] Membuat modul otentikasi (Password Gate) yang divalidasi dari parameter di secrets.
*   [ ] Memastikan credentials privat tidak masuk ke repositori git dengan menambahkan `.streamlit/secrets.toml` ke `.gitignore`.
