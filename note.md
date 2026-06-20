> [!NOTE] tekan _Ctrl+Shift+V_ untuk menampilkan preview Markdown di VS Code

# 📋 EduDecision AI V2 - Setup & Usage Guide

## 🎯 Project Overview

**EduDecision AI V2** adalah sistem pendukung keputusan hibrida (*Hybrid Decision Support System - DSS*) LKP LEAP Surabaya. Aplikasi ini mengintegrasikan data akademik & absensi siswa dari Google Sheets (didukung oleh **Gemini Academic Engine**) dan data statistik lalu lintas situs web dari database MariaDB lokal port 3077 (didukung oleh **Gemini Operations Engine**). Antarmuka didesain menggunakan **Genesis Design System** dengan tata letak responsif (*Mobile First Approach*).

---

## 🔧 Prerequisites Check

Sebelum memulai, pastikan interpreter Python dan virtual environment (`.venv`) dikonfigurasi dengan benar:

```powershell
# Jalankan perintah ini di PowerShell proyek Anda untuk memverifikasi jalur virtual env
.venv/Scripts/python.exe --version
.venv/Scripts/pip.exe --version
```

**Output yang diharapkan:**
* Python versi 3.9 s.d. 3.13 (disarankan 3.11 atau 3.12)
* Path mengarah ke folder lokal `.venv/Scripts/`

---

## 📦 Installation Steps

### 1. Install Dependencies
Pastikan virtual environment telah aktif terlebih dahulu, kemudian pasang seluruh pustaka pustaka dependensi:

```powershell
# Menggunakan pip dari virtual env secara langsung
.venv/Scripts/pip.exe install -r requirements.txt -q
```

### 2. Google Cloud Setup (GSheets API)
Diperlukan akun layanan GCP agar aplikasi dapat terhubung ke Google Sheets:
1. **Buat Project**: Buat proyek baru di [Google Cloud Console](https://console.cloud.google.com/).
2. **Enable Sheets API**: Cari "Google Sheets API" di kolom pencarian konsol dan klik tombol **Enable**.
3. **Service Account Key**:
   - Buka menu **IAM & Admin** > **Service Accounts**.
   - Buat Service Account baru, unduh kunci kredensial dalam format JSON, lalu ubah namanya menjadi `service_account.json` (pastikan file ini masuk ke `.gitignore`!).
4. **Bagi Akses Spreadsheet**: Buka Google Sheets target Anda, bagikan akses edit kepada alamat email Service Account (`client_email`) yang tertera di berkas JSON.

### 3. Gemini AI Setup
1. Dapatkan API Key melalui [Google AI Studio](https://aistudio.google.com/).
2. Konfigurasikan kunci tersebut ke dalam file konfigurasi Streamlit rahasia.

---

## ⚙️ Configuration Files

### `.streamlit/secrets.toml`
Buat berkas ini di dalam direktori `.streamlit/` pada proyek root:

```toml
# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyYourGeminiApiKeyHere"

# Google Sheets Configuration
spreadsheet_url = "https://docs.google.com/spreadsheets/d/SpreadsheetID/edit"

# MariaDB Local Port 3077 Configuration
mariadb_host = "127.0.0.1"
mariadb_port = 3077
mariadb_user = "root"
mariadb_password = ""
mariadb_database = "dataleap"

# Kunci Masuk Dashboard
SYSTEM_PASSWORD = "PasswordMasukSini"

# GCP Service Account credentials JSON
[gcp_service_account_json]
type = "service_account"
project_id = "dashboard-leap"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
# ... lengkapi field lainnya sesuai berkas JSON GCP
```

---

## 🚀 Running the Application

### 1. Menjalankan Dashboard Streamlit
Gunakan interpreter python dari virtual environment untuk memicu modul Streamlit:

```powershell
.venv/Scripts/python.exe -m streamlit run app.py
```

### 2. Menjalankan Unit Test (Pytest)
Jalankan unit test untuk memastikan pipeline data, kredensial, dan prompt model AI terintegrasi dengan baik:

```powershell
# Jalankan seluruh tes
.venv/Scripts/pytest -v

# Jalankan tes spesifik
.venv/Scripts/pytest tests/test_data_pipeline.py -v
.venv/Scripts/pytest tests/test_llm_analyzer.py -v
```

---

## 📊 Expected Data Structures

### A. Google Sheets (Fokus Akademik)
Dashboard mengharapkan struktur sheet dengan nama-nama berikut:

| Nama Lembar (Sheet) | Kolom Penting | Deskripsi |
| :--- | :--- | :--- |
| `DATA_SISWA` | `nama`, `rombel`, `status` | Informasi data diri siswa aktif |
| `DATA_ABSENSI` | `nama`, `tanggal`, `hadir` (Boolean/String) | Riwayat kehadiran harian siswa |
| `DATA_NILAI` | `nama`, `mata_pelajaran`, `nilai_mid`, `nilai_final` | Riwayat akademik & ujian siswa |
| `DATA_KELUAR` | `nama`, `tanggal_keluar`, `alasan` | Data siswa yang mengundurkan diri |
| `DATA_OVERVIEW` | `kunci`, `nilai` | Ringkasan metrik statistik ringkas |

### B. MariaDB Database (Fokus Operasional)
Aplikasi terhubung ke database `dataleap` pada port `3077` untuk membaca:
* Tabel `web_statistik`: Menyimpan data audit log lalu lintas, waktu akses, alamat IP klien, browser yang digunakan, dan waktu respon server.

---

## 🎨 UI/UX Specifications (Genesis Design)

Aplikasi menerapkan aturan desain **Genesis Design**:
1. **Responsive MFA Login Form**: Form masuk memiliki lebar dinamis untuk memastikan pendekatan *Mobile First* (Maksimal `850px` pada layar desktop, `680px` pada tablet, dan `100%` pada layar mobile). Menampilkan status koneksi Google Sheets & MariaDB (menampilkan status `No Local DB Connection` jika database offline).
2. **Sidebar Navigation**: Menggunakan selectbox (`st.sidebar.selectbox`) yang terintegrasi secara dinamis. Jika database terdeteksi offline, opsi menu **Unified Overview** dan **Database SQL (Operations)** akan disembunyikan sepenuhnya dari pilihan navigasi dan halaman diarahkan secara otomatis ke **Google Sheets (Academic)** sebagai *default landing page*.

---

## 🔧 Troubleshooting

### ❌ Error: "Status check - DB failed: (2003, ... Connection refused)"
* **Solusi**: Pastikan database MariaDB lokal Anda aktif pada port yang sesuai (default `3307`). Jika dideploy di server seperti Streamlit Cloud dan database offline, aplikasi akan mendeteksi status offline secara dinamis, menampilkan label `No Local DB Connection` pada halaman masuk, serta menyembunyikan halaman **Unified Overview** dan **Database SQL (Operations)** secara otomatis pasca-login.

### ❌ Error: "API_KEY_INVALID" / Rate Limit 429
* **Solusi**: Periksa validitas `GEMINI_API_KEY` pada file `.streamlit/secrets.toml`. Jika terkena batasan kuota (*Rate Limit*), sistem secara otomatis memicu *Multi-Model Failover* untuk bergeser mencari model cadangan yang aktif.

---

## 🆘 Git Branching & Combo Upload

Aktivitas pengerjaan berada pada branch lokal `feature/dss-hybrid`. Selalu lakukan commit sesering mungkin untuk melacak perubahan Anda.

**Perintah Combo Upload (3-in-1)**:
```powershell
git add . && git commit -m "feat: implement dynamic navigation hiding and default landing page fallback when DB is offline" && git push origin feature/dss-hybrid
```
