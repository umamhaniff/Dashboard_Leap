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
|  Dashboard Akademik   |                               | Dashboard Relasi Siswa|
|  - Rata-rata Nilai    |                               |  - Profil Siswa 360   |
|  - Distribusi Grade   |                               |  - Rombel & Jadwal    |
|  - Siswa Remidi       |                               |  - Catatan & FollowUp |
+-----------+-----------+                               +-----------+-----------+
            |                                                       |
            v                                                       v
+-----------------------+                               +-----------------------+
| AI: Academic Engine   |                               | AI: Operations Engine |
| - Gemini Failover     |                               | - Gemini Failover     |
| - Rekomendasi Remidi  |                               | - Audit Catatan & Log |
+-----------------------+                               +-----------------------+
```

### A. Modul 1: Google Sheets (Academic Performance & Grades Focus)
*   **Input Data**: Sheet `DATA_SISWA`, `DATA_ABSENSI`, `DATA_NILAI`, `DATA_KELUAR`, dan `DATA_OVERVIEW`.
*   **KPI Utama & Penekanan Akademik** (Berdasarkan `docs/dashboard_context.md`):
    *   **Performa Rata-Rata Nilai**: Perbandingan performa program (Komputer vs Bahasa Inggris: Mid-Test 54.93, Final-Test 71.60).
    *   **Distribusi Grade Nilai**: Analisis persentase gabungan (Grade E: 26.7%, Grade F: 23.3%, B: 16.0%, C: 13.5%, A: 10.2%, D: 10.0%) serta segmentasi per jenjang (SD vs SMP) dan jenis program (Single vs Double Program).
    *   **Metrik Remidi**: Total 305 siswa remidi dengan batas atas nilai remedi (Score <= 70) dan pelacakan detail status ketuntasan siswa.
    *   **Metrik Penunjang**: Ringkasan operasional rombel dan tren kehadiran harian sebagai context pendukung untuk performa akademik.
*   **Output Dashboard**: Histogram interaktif untuk distribusi nilai, diagram batang sebaran grade siswa per kelompok kelas, tabel ringkasan daftar siswa remidi, dan panel metrik rata-rata nilai.
*   **AI Engine (Prescriptive Academic Engine)**: Pemicuan manual Gemini untuk menganalisis penurunan nilai siswa, mendeteksi korelasi antara ketidakhadiran dan nilai jelek, serta menyusun rekomendasi mitigasi ketuntasan belajar.

### B. Modul 2: MariaDB Database (Student Profiles & Relations Focus)
*   **Input Data**: Query SQL langsung dari database lokal `dataleap_v5_migration` (Port `3077`) dengan fokus utama pada tabel **`siswa`** dan tabel anak relasionalnya:
    *   `siswa` (Master Data Siswa Aktif hasil migrasi)
    *   `kursus_siswa` (Mapping program yang diambil, status keaktifan, dan status kelulusan siswa)
    *   `jadwal_siswa` (Peta rombel siswa, persetujuan rapor `is_acc_rapor`, status keluar, dan ketuntasan kelas)
    *   `catatan_siswa` & `followup_cs` (Catatan perkembangan, kendala kelas siswa, dan tracking kasus)
    *   `catatan_remidi_siswa` (Log perbaikan nilai yang disetujui guru)
    *   `calon_siswa` (Sebagai data hulu pipeline CRM sebelum resmi menjadi siswa)
*   **KPI & Fokus Relasi Siswa** (Berdasarkan `docs/database_context.md`):
    *   **Student Profile & Enrollment**: Distribusi siswa aktif berdasarkan level program dan rombel kelas.
    *   **Class & Schedule Tracking**: Status ketuntasan siswa di rombel harian, status persetujuan rapor oleh management, dan pelacakan siswa keluar (`status_keluar`).
    *   **Behavioral & Case Follow-up**: Analisis status kasus siswa (`NEED FURTHER OBSERVATION` vs `CASE CLOSED`) untuk penanganan dini kendala belajar.
    *   **Remedial Database Audit**: Verifikasi log perbaikan nilai siswa di database, membandingkan nilai sebelum dan sesudah remidi.
*   **Output Dashboard**: Tampilan profil holistik siswa (Student 360 View), status peminjaman kursus, panel tracking kasus follow-up, list data persetujuan rapor rombel, dan log audit remedial.
*   **AI Engine (System Integrity & Student Operations Audit)**: Pemicuan manual Gemini untuk menganalisis data kualitatif catatan siswa, mendeteksi siswa bermasalah (terjebak status observasi lama), dan mengaudit integritas relasi foreign key dari riwayat remidi siswa.

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
