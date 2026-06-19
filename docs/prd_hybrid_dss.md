# 📑 PRODUCT REQUIREMENT DOCUMENT (PRD) - VERSION 2.0

**Project Name:** EduDecision AI V2 - Hybrid Decision Support System (DSS)

**Author:** Chotibul Umam Hanif (Data Analyst Intern / IS Student)

**Status:** Updated (Branch Development - Pending Team Review)

**Target Release:** June 2026

---

## 1. Executive Summary & Problem Statement

### 1.1 Background

LKP LEAP saat ini mengelola dua jalur data operasional utama: data operasional/statistik situs web yang dimigrasikan ke database lokal **MariaDB (Port 3077)**, serta data akademik/kehadiran harian siswa yang berjalan aktif di **Google Sheets (SPS Connector)**.

Proses pengambilan keputusan strategis terkait performa siswa, anomali kehadiran, audit log akses, dan rekomendasi mitigasi akademik/operasi masih terfragmentasi. Diperlukan sebuah sistem pendukung keputusan hibrida (*Hybrid DSS*) berbasis **Streamlit** dengan estetika visual **Genesis Design** yang menggabungkan kemampuan **Generative AI** dengan dual-input dan dual-output terisolasi untuk mengotomatisasi evaluasi ini dalam satu *dashboard* terpadu.

### 1.2 Objectives

* Membangun pipeline *dual-input* terisolasi: Mengambil data transaksional statistik web dari MariaDB (Port 3077) dan data evaluasi akademik dari Google Sheets API via GCP.
* Mengintegrasikan dua mesin AI khusus (*Dual AI Engines*):
  1. **Gemini Academic Engine**: Mengolah data akademis dan kehadiran siswa dari Google Sheets untuk menghasilkan rekomendasi kehadiran & analisis nilai.
  2. **Gemini Operations Engine**: Mengolah data statistik dari MariaDB (`web_statistik`) untuk melakukan audit trafik website, deteksi anomali akses, dan analisis log performa.
* Menerapkan antarmuka premium **Genesis Design** dengan pendekatan *Mobile First Approach* (MFA) pada formulir login dan navigasi sidebar Streamlit.
* Menyediakan rekomendasi keputusan berbasis aksi langsung yang dapat diverifikasi oleh tim internal sebelum diproduksi penuh.

---

## 2. User Personas & Scope

| Persona | Role | User Goal | Tech Literacy |
| --- | --- | --- | --- |
| **Academic Admin / Mentor** | Data Entry & Supervisor | Memantau absensi siswa harian, nilai, dan melihat peringatan dini jika ada siswa terindikasi akan keluar (*dropout*). | Medium (Terbiasa dengan Google Sheets/SPS) |
| **Operations Manager** | IT & Web Administrator | Memantau trafik web, keamanan akses log server, dan mendeteksi anomali akses eksternal. | High |
| **Management / Stakeholder** | Decision Maker | Mendapatkan *insight* holistik keamanan data, kualitas input, statistik web, serta rekomendasi kebijakan strategis. | Medium |
| **Data Team (Hans & Team)** | Developer / Analyst | Memastikan data tersinkronisasi dengan aman tanpa merusak performa *hardware* lokal (8GB RAM Baseline). | High |

### 2.1 Scope of Work (In-Scope)

1. **Dual-Input Data Pipeline & Dual-Output Isolation**:
   * **Input Google Sheets (Akademik & Kehadiran)**: Data diambil dari `DATA_SISWA`, `DATA_ABSENSI`, `DATA_NILAI`, `DATA_KELUAR`, `DATA_OVERVIEW`.
   * **Input Database SQL MariaDB (Trafik & Operasional)**: Data diambil dari tabel `web_statistik` di MariaDB port `3077`.
2. **Dual AI Engines Integration**:
   * **Gemini Academic Engine**: Menganalisis tingkat absensi, tren nilai, prediksi retensi siswa, dan rekomendasi mitigasi dropout.
   * **Gemini Operations Engine**: Mengaudit lalu lintas situs web, deteksi anomali akses (percobaan peretasan, lonjakan trafik tak wajar), dan log performa.
3. **Estetika Visual Genesis Design**:
   * **Halaman Login (MFA)**: Form login berbasis CSS dengan lebar responsif. Melebar secara dinamis hingga `850px` pada layar desktop (`min-width: 1200px`) dan `680px` pada tablet (`min-width: 768px`), namun tetap `100%` di layar mobile (MFA).
   * **Navigasi Utama (Streamlit Sidebar)**: Menu navigasi terintegrasi menggunakan `st.sidebar.radio` untuk memilih modul aktif secara langsung, dilengkapi tombol **Sign Out** terintegrasi.
4. **Data Preprocessing & Quality Engineering**: Pembersihan otomatis pola error spreadsheet (`#REF!`, `#VALUE!`, dsb) dan standardisasi tipe data sebelum diproses oleh model.
5. **Multi-Model Failover Mechanism**: Logika pemanggilan beruntun model LLM (Gemini 3.1, Gemini 3.0, Gemini 2.5, hingga Gemma) apabila terjadi error status 429 pada salah satu engine.

### 2.2 Out-of-Scope (Future Phases)

* Penulisan data balik langsung dari Streamlit ke MariaDB (untuk fase ini, akses database bersifat *Read-Only* demi menjaga integritas data awal).
* Sistem otentikasi multi-user dengan Role-Based Access Control (RBAC) tingkat lanjut (sementara menggunakan *environment level security* via `secrets.toml`).

---

## 3. User Personas & Hybrid DSS Scope

### 3.1 Deep-Dive User Personas

#### Persona 1: Academic Admin & Mentor (The Academic Frontliner)
* **Profil & Karakateristik:** Staf administrasi akademis LKP LEAP yang bertanggung jawab penuh atas pencatatan harian, pengelolaan kelas, dan interaksi langsung dengan siswa. Tingkat literasi teknologi berada di level *Medium*.
* **User Story:** *"Sebagai Academic Admin, aku ingin memantau absensi harian dan rekam jejak siswa keluar-masuk dengan mudah, tanpa perlu mengotak-atik rumus yang rumit, sehingga aku bisa memberikan peringatan dini kepada mentor jika ada siswa yang terindikasi akan dropout."*
* **Pain Points (Masalah Utama):**
    * Sering terjadi error rumit seperti `#REF!` atau `#DIV/0!` akibat ketidaksengajaan modifikasi kolom oleh tim admin lain.
    * Kesulitan mencocokkan data absensi manual di Google Sheets dengan data transaksional aplikan yang ada di database inti.
* **Sistem Touchpoints:** Modul Akademik & Kehadiran (Google Sheets) yang didukung oleh **Gemini Academic Engine**.

#### Persona 2: IT / Operations Admin (The Infrastructure Keeper)
* **Profil & Karakateristik:** Pengelola infrastruktur web LKP LEAP yang memantau performa server dan keamanan sistem. Memiliki tingkat literasi teknologi yang *High*.
* **User Story:** *"Sebagai Operations Admin, saya ingin memantau kesehatan server, tren trafik pengunjung situs web, dan mendapatkan deteksi dini anomali akses atau serangan siber tanpa harus memilah log baris demi baris secara manual."*
* **Pain Points (Masalah Utama):**
    * Log trafik web yang berukuran besar dan sulit dibaca secara langsung.
    * Kurangnya waktu untuk mendeteksi pola anomali akses eksternal (brute force, scraping agresif, dsb.) secara real-time.
* **Sistem Touchpoints:** Modul Statistik Web (MariaDB `web_statistik`) yang didukung oleh **Gemini Operations Engine**.

#### Persona 3: LKP LEAP Management (The Decision Maker)
* **Profil & Karakateristik:** Pengambil kebijakan yang membutuhkan kesimpulan ringkas, visual, dan akurat untuk menentukan arah bisnis dan akademis.
* **User Story:** *"Sebagai pengambil kebijakan, saya ingin melihat ringkasan performa akademik lembaga serta audit operasional situs secara bersamaan agar dapat meluncurkan kampanye promosi dan program bimbingan belajar yang tepat sasaran."*
* **Sistem Touchpoints:** Halaman *Unified LKP Overview (Dashboard)* dan hasil analisis ringkas dari kedua AI Engine.

---

### 3.2 Functional Scope (MoSCoW Matrix)

#### 1. Must Have (Wajib Ada di Phase Ini)
* **M.1:** Inisiasi konektor data hibrida hulu: Membaca tabel `web_statistik` dari MariaDB via `port 3077` sekaligus menarik data akademik dari Google Sheets API.
* **M.2:** Integrasi **Gemini Academic Engine** (analisis nilai & kehadiran) dan **Gemini Operations Engine** (audit log trafik & deteksi anomali akses).
* **M.3:** Penerapan **Genesis Design System** pada visual UI Streamlit, terutama halaman login MFA responsif dengan pengaturan lebar dinamis (`850px` / `680px` / `100%`) dan navigasi sidebar.
* **M.4:** Mekanisme *Multi-Model Failover Registry* untuk menjamin proses analisis tetap berjalan saat terjadi *Rate Limit 429*.
* **M.5:** Tombol pemicu manual **"Run AI Analysis"** pada masing-masing modul terisolasi agar menghemat kuota token.

#### 2. Should Have (Sangat Penting, Tapi Ada Workaround)
* **S.1:** Visualisasi grafik interaktif sebaran nilai ujian dan tren trafik web bulanan/harian menggunakan Plotly.
* **S.2:** Panel proteksi parsial berupa enkripsi *environment variables* lokal memanfaatkan `.streamlit/secrets.toml`.

#### 3. Could Have (Bagus Kalau Ada, Tapi Tidak Kritikal)
* **C.1:** Pembuatan fitur ekspor otomatis lembar kerja yang telah dibersihkan oleh pipeline ke dalam format berkas lokal `.csv` atau `.xlsx`.
* **C.2:** Pilihan skema warna kontras tinggi untuk aksesibilitas admin yang memiliki keterbatasan visual.

#### 4. Won't Have (Ditunda untuk Pengembangan Fase Selanjutnya)
* **W.1:** Sinkronisasi penulisan balik (*Write-Back*) dari antarmuka dashboard Streamlit ke database MariaDB atau Google Sheets.
* **W.2:** Manajemen akun pengguna berlapis (*Multi-user Role-Based Access Control*) di tingkat kode aplikasi.

---

## 4. System Architecture & Technical Specifications

```
                     +-------------------------------------------------+
                     |              Dual-Input Pipelines               |
                     +-----------------------+-------------------------+
                                             |
             +-------------------------------+-------------------------------+
             |                                                               |
             v (Operations Stream)                                           v (Academic Stream)
+--------------------------+                                    +--------------------------+
|  MariaDB Database        |                                    |  Google Sheets           |
|  (Port: 3077)            |                                    |  (GCP Cloud Connector)   |
|  Tabel: web_statistik    |                                    |  DATA_SISWA, ABSENSI, etc|
+------------+-------------+                                    +------------+-------------+
             |                                                               |
             v                                                               v
+--------------------------+                                    +--------------------------+
| Gemini Operations Engine |                                    | Gemini Academic Engine   |
| (Audit Trafik & Anomali) |                                    | (Analisis Nilai & Absen) |
+------------+-------------+                                    +------------+-------------+
             |                                                               |
             +-------------------------------+-------------------------------+
                                             |
                                             v
                            +----------------------------------+
                            |     Streamlit Core Pipeline      |
                            |     (8GB RAM Cache Management)   |
                            +----------------+-----------------+
                                             |
                                             v
                            +----------------------------------+
                            |     Genesis Design UI Layout     |
                            | (MFA Login Form & Sidebar Nav)   |
                            +----------------------------------+
```

### 4.1 Tech Stack

* **Logic & Processing:** Python (Pandas, `mysql-connector-python` / `SQLAlchemy`)
* **User Interface:** Streamlit (Single-page, Clean layout, Custom CSS Genesis Design)
* **Database Input:** MariaDB (Port: 3077, Host: localhost/secrets)
* **Spreadsheet Input:** Google Sheets via GCP API (`gspread`)
* **AI Engine:** Google Generative AI Python Library (`google-generativeai`)

### 4.2 UI Design Specifications (Genesis Design System)

* **Form Login MFA**: CSS Form login dengan layout responsif:
  * Desktop (`min-width: 1200px`): Maksimal lebar `850px`.
  * Tablet (`min-width: 768px`): Maksimal lebar `680px`.
  * Mobile: Lebar `100%`.
* **Navigasi Utama**: Navigasi menggunakan `st.sidebar.radio` yang terbagi ke dalam menu:
  * 🏠 Unified LKP Overview
  * 📊 Modul Akademik (Google Sheets)
  * 🗄️ Modul Operasional (MariaDB web_statistik)
  * 🚪 Sign Out (di bagian bawah sidebar)

---

## 5. Functional Requirements & Core Flows

### 5.1 Input Flow 1: MariaDB Connection (Port 3077)

* **FR-1.1:** Sistem harus menginisiasi koneksi aman ke database MariaDB pada port 3077 menggunakan *credentials* terenkripsi dari `secrets.toml`.
* **FR-1.2:** Sistem harus memuat tabel `web_statistik` dan membatasi pembacaan memori agar tetap stabil di server lokal 8GB RAM menggunakan caching data `@st.cache_data(ttl=300)`.

### 5.2 Input Flow 2: Google Sheets Connection (GCP)

* **FR-2.1:** Sistem wajib terhubung ke Google Sheets menggunakan berkas kredensial Service Account GCP.
* **FR-2.2:** Sistem harus memetakan lembar kerja target otomatis berdasar daftar `SHEET_NAMES` (`DATA_SISWA`, `DATA_ABSENSI`, `DATA_NILAI`, `DATA_KELUAR`, `DATA_OVERVIEW`).
* **FR-2.3:** Pembersihan otomatis wajib dilakukan terhadap nilai-nilai tidak valid akibat kesalahan rumus spreadsheet hancur (`#REF!`, `#DIV/0!`).

### 5.3 Intelligence & Failover Flow (Gen AI Integration)

* **FR-3.1:** Sistem menyediakan tombol manual **"Run AI Analysis"** di masing-masing modul akademik dan operasional.
* **FR-3.2 (Academic):** Gemini Academic Engine harus menganalisis data siswa dan absensi untuk memberikan ringkasan status akademik dan 5 rekomendasi mitigasi belajar.
* **FR-3.3 (Operations):** Gemini Operations Engine harus mengaudit data trafik web, mendeteksi pola anomali akses (misal lonjakan aktivitas mencurigakan), dan memberikan laporan performa sistem.
* **FR-3.4 (Failover):** Sistem harus mengeksekusi pemeriksaan keamanan menggunakan daftar prioritas model secara sekuensial jika model utama sibuk atau terkena batas limit (Rate Limit 429):
  1. `models/gemini-3.1-flash-lite-preview`
  2. `models/gemini-3-flash-preview`
  3. `models/gemini-2.5-flash-lite`
  4. Fallback akhir pada `models/gemini-flash-latest`.

---

## 6. Git Branching Strategy & Collaboration Protocol

### 6.1 Branching Workflow

1. **Isolated Branch Active:** `feature/dss-hybrid-mariadb-gsheets`
2. **Combo Upload Execution:**
```bash
git add . && git commit -m "feat: integrate dual-input pipeline mariadb 3077 & gsheets failover with genesis design" && git push origin feature/dss-hybrid-mariadb-gsheets
```

### 6.2 Pre-submission Checklist for Campus Project

* [ ] Pastikan konfigurasi port MariaDB terkunci statis pada `3077` di setup environment.
* [ ] Uji coba tombol `Refresh Data` untuk memastikan fungsi `st.cache_data.clear()` bekerja optimal membersihkan sisa memori.
* [ ] Pastikan file rahasia kredensial GCP (`service_account.json` & `secrets.toml`) masuk daftar `.gitignore` agar tidak bocor ke publik.
* [ ] Lakukan verifikasi form login MFA responsif di berbagai resolusi layar.
