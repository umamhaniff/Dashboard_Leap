# 📑 PRODUCT REQUIREMENT DOCUMENT (PRD)

**Project Name:** EduDecision AI V2 - Hybrid Decision Support System (DSS)

**Author:** Chotibul Umam Hanif (Data Analyst Intern / IS Student)

**Status:** Draft (Branch Development - Pending Team Review)

**Target Release:** June 2026

---

## 1. Executive Summary & Problem Statement

### 1.1 Background

LKP LEAP saat ini mengelola dua jalur data operasional utama: data transaksional/aplikan baru yang bermigrasi ke database lokal **MariaDB (Port 3077)**, serta data akademik/kehadiran harian siswa yang berjalan aktif di **Google Sheets (SPS Connector)** Dashboard LEAP - README.csv, umamhaniff/dashboard_leap/Dashboard_Leap-b2b5d43ee593fa9921717b1750bb3f40cb34684d/config/settings.py].

Proses pengambilan keputusan strategis terkait performa siswa, anomali kehadiran, dan rekomendasi mitigasi akademik masih terfragmentasi. Diperlukan sebuah sistem hibrida berbasis **Streamlit** yang menggabungkan kemampuan **Machine Learning (Predictive Analytics)** dan **Generative AI (Prescriptive Intelligence via Gemini/Gemma)** untuk mengotomatisasi evaluasi ini dalam satu *dashboard* terpadu.

### 1.2 Objectives

* Membangun pipeline *dual-input* terisolasi: Mengambil data transaksional dari MariaDB (Port 3077) dan data evaluasi akademik dari Google Sheets API via GCP.
* Mengintegrasikan *Intelligence Layer* berbasis AI yang adaptif (memiliki fitur *Failover Model* otomatis untuk mencegah kendala *Rate Limit* API).
* Menyediakan rekomendasi keputusan berbasis aksi langsung yang dapat diverifikasi oleh tim internal sebelum diproduksi penuh.

---

## 2. User Personas & Scope

| Persona | Role | User Goal | Tech Literacy |
| --- | --- | --- | --- |
| **Academic Admin / Mentor** | Data Entry & Supervisor | Memantau absensi siswa harian dan melihat peringatan dini jika ada siswa terindikasi akan keluar (*dropout*). | Medium (Terbiasa dengan Google Sheets/SPS) |
| **Management / Stakeholder** | Decision Maker | Mendapatkan *insight* holistik keamanan data, kualitas input, serta rekomendasi kebijakan strategis. | Medium |
| **Data Team (Hans & Team)** | Developer / Analyst | Memastikan data tersinkronisasi dengan aman tanpa merusak performa *hardware* lokal (8GB RAM Baseline). | High |

### 2.1 Scope of Work (In-Scope)

1. **Dual-Input Data Pipeline**: Konektor MariaDB (`port=3077`) + Konektor GSheets via `gspread` menggunakan Google Cloud Service Account Credentials.
2. **Data Preprocessing & Quality Engineering**: Pembersihan otomatis pola error spreadsheet (`#REF!`, `#VALUE!`, dsb) dan standardisasi tipe data.
3. **On-Demand Security & Decision Intelligence**: Modul audit data berbasis Gen AI yang hanya berjalan saat dieksekusi manual (*button click*) demi efisiensi token biaya.
4. **Multi-Model Failover Mechanism**: Logika pemanggilan beruntun model LLM (Gemini 3.1, Gemini 3.0, Gemini 2.5, hingga Gemma) apabila terjadi error status 429.

### 2.2 Out-of-Scope (Future Phases)

* Penulisan data balik langsung dari Streamlit ke MariaDB (untuk fase ini, akses database bersifat *Read-Only* demi menjaga integritas data awal).
* Sistem otentikasi multi-user dengan Role-Based Access Control (RBAC) tingkat lanjut (sementara menggunakan *environment level security* via `secrets.toml`).

---

## 3. User Personas & Hybrid DSS Scope

### 3.1 Deep-Dive User Personas

#### Persona 1: Academic Admin & Mentor (The Frontliner)
* **Profil & Karakateristik:** Staf administrasi akademis LKP LEAP yang bertanggung jawab penuh atas pencatatan harian, pengelolaan kelas (rombel), dan interaksi langsung dengan siswa Dashboard LEAP - README.csv, umamhaniff/dashboard_leap/Dashboard_Leap-b2b5d43ee593fa9921717b1750bb3f40cb34684d/note.md]. Tingkat literasi teknologi berada di level *Medium* (sangat mahir Spreadsheet, namun awam dengan kueri database/Python) Dashboard LEAP - README.csv].
* **User Story:** *"Sebagai Academic Admin, aku ingin memantau absensi harian dan rekam jejak siswa keluar-masuk dengan mudah, tanpa perlu mengotak-atik rumus yang rumit, sehingga aku bisa memberikan peringatan dini kepada mentor jika ada siswa yang terindikasi akan dropout."* Dashboard LEAP - DATA_KELUAR.csv, [CONNECTOR] Dashboard LEAP - README.csv]
* **Pain Points (Masalah Utama):**
    * Sering terjadi error rumit seperti `#REF!` atau `#DIV/0!` akibat ketidaksengajaan modifikasi kolom oleh tim admin lain Dashboard LEAP - README.csv].
    * Kesulitan mencocokkan data absensi manual di Google Sheets dengan data transaksional aplikan yang ada di database inti Dashboard LEAP - README.csv].
* **Sistem Touchpoints (Fitur Terkait):** Area *Data Overview Metrics* dan *Direct Access Data Preview Dataframe*.

#### Persona 2: LKP LEAP Management & Stakeholders (The Decision Maker)
* **Profil & Karakateristik:** Kepala cabang atau jajaran manajemen LKP LEAP yang membutuhkan visualisasi cepat dan kesimpulan tingkat tinggi untuk menentukan arah kebijakan operasional.
* **User Story:** *"Sebagai pengambil kebijakan, aku ingin melihat laporan kualitas data operasional serta analisis tren anomali akademik berbasis AI secara periodik, sehingga aku bisa mengambil tindakan preventif (seperti penyesuaian jadwal kelas tambahan atau mitigasi kecurangan) secara objektif."*
* **Pain Points (Masalah Utama):**
    * Data akademik yang masif membuat proses evaluasi manual memakan waktu berhari-hari.
    * Sulit mendeteksi kecurangan atau pola ketidakhadiran sistemik hanya dengan melihat baris data mentah Spreadsheet.
* **Sistem Touchpoints (Fitur Terkait):** Tombol *Run AI Analysis* dan panel *Gen AI Security/Decision Intelligence Output* beserta 5 Poin Rekomendasi Mitigasi.

#### Persona 3: Data & IS Developer Team (Hans, Resti, Fajar)
* **Profil & Karakateristik:** Pengembang sistem dan analisis data yang bertanggung jawab atas stabilitas aplikasi, efisiensi memori, dan keandalan API. Memiliki literasi teknologi yang sangat tinggi (*High*).
* **User Story:** *"Sebagai pengembang, aku ingin mengintegrasikan dual-source pipeline data (MariaDB + Google Sheets) ke dalam aplikasi Streamlit yang ringan, lengkap dengan penanganan limitasi API LLM (Failover), agar sistem tetap andal berjalan pada infrastruktur lokal 8GB RAM."*
* **Pain Points (Masalah Utama):**
    * Keterbatasan kuota token API dan ancaman error HTTP 429 (*Rate Limit*) sewaktu jam sibuk.
    * Risiko kebocoran memori (*memory leak*) akibat pembacaan dataset yang tidak di-cache dengan benar.
* **Sistem Touchpoints (Fitur Terkait):** *Debug Center* (Gemini Models Validator & Data Inventory JSON) pada *Sidebar Layout*.

---

### 3.2 Functional Scope (MoSCoW Matrix)

Untuk memastikan target pengerjaan di *isolated branch* selesai tepat waktu sebelum batas pengumpulan tugas ke dosen, batasan ruang lingkup diklasifikasikan sebagai berikut:

#### 1. Must Have (Wajib Ada di Phase Ini)
* **M.1:** Inisiasi konektor data hibrida hulu: Membaca tabel transaksional dasar dari server lokal MariaDB via `port 3077` sekaligus menarik data akademik berkala dari Google Sheets API (GCP Service Account).
* **M.2:** Mekanisme *Multi-Model Failover Registry* (logika beruntun dari Gemini 3.1 Flash Lite down to Gemini 1.5 Flash Latest) untuk menjamin audit AI bebas dari interupsi kendala teknis *Rate Limit*.
* **M.3:** Fitur pembersihan otomatis (*Sanitization Engine*) terhadap baris string kosong (`nan`) dan anomali formula hancur bawaan Google Sheets.
* **M.4:** Tombol eksekusi manual *On-Demand Run AI Analysis* guna memotong konsumsi kuota token yang sia-sia pada saat *refresh* halaman Streamlit dijalankan.

#### 2. Should Have (Sangat Penting, Tapi Ada Workaround)
* **S.1:** Visualisasi grafik interaktif performa tren kehadiran siswa per rombel menggunakan kombinasi matplotlib/plotly/altair.
* **S.2:** Panel proteksi parsial berupa enkripsi *environment variables* lokal memanfaatkan `.streamlit/secrets.toml` untuk mencegah kebocoran *private key* GCP dan API Key Gemini.

#### 3. Could Have (Bagus Kalau Ada, Tapi Tidak Kritikal)
* **C.1:** Pembuatan fitur ekspor otomatis lembar kerja yang telah dibersihkan oleh pipeline ke dalam format berkas lokal `.csv` atau `.xlsx` langsung dari *dataframe viewer* Streamlit.
* **C.2:** Panel visualisasi *Dark Mode / Light Mode* kustom tambahan di luar tema bawaan kerangka kerja Streamlit.

#### 4. Won't Have (Ditunda untuk Pengembangan Fase Selanjutnya)
* **W.1:** Sinkronisasi penulisan balik (*Write-Back data stream*) dua arah dari antarmuka dashboard Streamlit ke dalam tabel fisik MariaDB (Akses dikunci total secara *Read-Only* pada fase pengerjaan kampus saat ini demi menjaga keamanan database).
* **W.2:** Manajemen akun pengguna berlapis (*Multi-user Role-Based Access Control*) di tingkat kode aplikasi.

---

## 4. System Architecture & Technical Specifications

```
                     +---------------------------------------+
                     |         Dual-Input Pipelines          |
                     +-------------------+-------------------+
                                         |
            +----------------------------+----------------------------+
            |                                                         |
            v                                                         v
+-----------------------+                                 +-----------------------+
|  MariaDB Database     |                                 |     Google Sheets     |
|  (Port: 3077)         |                                 |  (GCP Cloud Connector)|
+-----------+-----------+                                 +-----------+-----------+
            |                                                         |
            +----------------------------+----------------------------+
                                         | (Pandas / SQL Engine Data Stream)
                                         v
                        +----------------------------------+
                        |     Streamlit Core Pipeline      |
                        |     (8GB RAM Cache Management)   |
                        +----------------+-----------------+
                                         |
                                         v
                        +----------------------------------+
                        |    Gen AI Orchestration Layer    |
                        |  (Adaptive Multi-Model Failover) |
                        +----------------------------------+

```

### 4.1 Tech Stack

* **Logic & Processing:** Python (Pandas, Scikit-learn, `mysql-connector-python` / `SQLAlchemy`)
* **User Interface:** Streamlit (Single-page, Clean layout)
* **Database Input 1:** MariaDB (Host: localhost/cloud, Port: 3077)
* **Database Input 2:** Google Sheets via GCP API (`gspread`)
* **AI Engine:** Google Generative AI Python Library (`google-generativeai`)

### 4.2 Memory Constrained Hardware Strategy (8GB RAM Optimization)

* **Data Chunking & Head Slicing:** Pipeline LLM hanya mengekstrak `$N` baris teratas (`df.head(40)`) sebagai representasi kontekstual untuk audit.
* **Data Downcasting & Cache Optimization:** Pemanfaatan `@st.cache_data(ttl=300)` tanpa mengaktifkan penumpukan spinner bawaan agar memori tidak bocor sewaktu pemicuan fungsi ulang.

---

## 5. Functional Requirements & Core Flows

### 5.1 Input Flow 1: MariaDB Connection (Port 3077)

* **FR-1.1:** Sistem harus menginisiasi koneksi aman ke server MariaDB pada port 3077 menggunakan *credentials* terenkripsi dari `secrets.toml`.
* **FR-1.2:** Sistem harus mengekstrak skema tabel transaksional dasar (seperti `absensi`, `web_statistik`, atau data aplikan) tanpa membebani performa server.

### 5.2 Input Flow 2: Google Sheets Connection (GCP)

* **FR-2.1:** Sistem wajib terhubung ke Google Sheets menggunakan file Service Account JSON yang divalidasi oleh GCP.
* **FR-2.2:** Sistem harus memetakan lembar kerja target otomatis berdasar daftar `SHEET_NAMES` (`DATA_MASTER`, `DATA_ABSENSI`, `DATA_NILAI`).
* **FR-2.3:** Pembersihan otomatis wajib dilakukan terhadap nilai-nilai tidak valid akibat kesalahan ketik atau rumus spreadsheet hancur (`#REF!`, `#DIV/0!`).

### 5.3 Intelligence & Failover Flow (Gen AI Integration)

* **FR-3.1:** Sistem menyediakan tombol pemicu manual **"Run AI Analysis"** untuk mengaktifkan audit keputusan.
* **FR-3.2 (Failover Core):** Sistem harus mengeksekusi pemeriksaan keamanan menggunakan daftar prioritas model secara sekuensial jika model utama sibuk atau terkena batas limit (Rate Limit 429):
1. `models/gemini-3.1-flash-lite-preview` (Prioritas Utama)
2. `models/gemini-3-flash-preview`
3. `models/gemini-2.5-flash-lite`
4. ... hingga Fallback akhir pada `models/gemini-flash-latest`.


* **FR-3.3:** Sistem harus menyajikan 5 poin rekomendasi mitigasi taktis secara cepat berbasis keluaran dari model analisis.

---

## 6. UI/UX & Interface Design Wireframe

Aplikasi dirancang menggunakan tata letak ringkas komponen atas (*Header Menu Layout*) agar mempermudah monitoring cepat:

```
+------------------------------------------------------------------------------------+
| 🛡️ EduDecision AI - Dashboard                                                     |
+------------------------------------------------------------------------------------+
| [🔄 Refresh Data]   [🤖 Run AI Analysis (Primary)]   [📊 Open Spreadsheet (Link)]  |
+------------------------------------------------------------------------------------+
| ---------------------------------------------------------------------------------- |
| 📊 Data Overview                                                                   |
| Total Records: 236,102       Data Quality: 98.4%       Sheets Active: 4            |
+------------------------------------------------------------------------------------+
| 🔍 Data Preview (Direct Access)                                                    |
| [Selectbox: Master / Absensi / Nilai]                                             |
| +--------------------------------------------------------------------------------+ |
| | Dataframe Viewer (Pandas output with clean type casting)                       | |
| +--------------------------------------------------------------------------------+ |
+------------------------------------------------------------------------------------+
| 🤖 Gen AI Security Intelligence                                                     |
| (Menampilkan hasil temuan komparasi anomali multi-model & 5 poin rekomendasi)       |
+------------------------------------------------------------------------------------+

```

---

## 7. Git Branching Strategy & Collaboration Protocol

### 7.1 Branching Workflow

1. **Isolated Branch Creation:** ```bash
git checkout -b feature/dss-hybrid-mariadb-gsheets
```

```


2. **Combo Upload Execution:** (Gunakan metode cepat yang biasa kamu pakai untuk melacak progres pengerjaan di branch lokal tanpa mengganggu *production branch*):
```bash
git add . && git commit -m "feat: integrate dual-input pipeline mariadb 3077 & gsheets failover" && git push origin feature/dss-hybrid-mariadb-gsheets

```


3. **Peer Review Mechanism:** Bagikan *pull request* (PR) hasil *push* tersebut kepada rekan tim (seperti Resti atau Fajar) untuk validasi fungsionalitas query database sebelum digabungkan ke `main` branch.

### 7.2 Pre-submission Checklist for Campus Project

* [ ] Pastikan konfigurasi port MariaDB terkunci statis pada `3077` di setup environment.
* [ ] Uji coba tombol `Refresh Data` untuk memastikan fungsi `st.cache_data.clear()` bekerja optimal membersihkan sisa memori.
* [ ] Pastikan file rahasia kredensial GCP (`service_account.json` & `secrets.toml`) masuk daftar `.gitignore` agar tidak bocor ke publik.
