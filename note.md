> [!NOTE] tekan _Ctrl+Shift+V_ untuk preview

# 📋 LEAP Security Dashboard - Setup & Usage Guide

> [!NOTE] tekan _Ctrl+Shift+V_ untuk preview

## 🎯 Project Overview

**LEAP Security Dashboard** adalah aplikasi Streamlit untuk analisis keamanan data LKP LEAP yang terintegrasi dengan Google Sheets dan Google Gemini AI. Dashboard ini fokus pada monitoring keamanan data siswa, analisis absensi, dan deteksi anomali menggunakan AI.

## 🔧 Prerequisites Check

Sebelum memulai, pastikan Python dan PIP sudah terinstal dengan benar:

```bash
where python
where pip
```

**Output yang benar:**

```
C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe
C:\Users\HP\AppData\Local\Programs\Python\Python313\Scripts\pip.exe
```

## 📦 Installation Steps

### 1. Install Dependencies

```bash
# Instalasi standar
pip install -r requirements.txt

# Atau instalasi quiet (lebih bersih)
pip install -r requirements.txt -q
```

### 2. Google Cloud Setup

**Wajib untuk functionality penuh:**

1. **Buat Google Cloud Project**
   - Pergi ke [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project atau pilih existing

2. **Enable Google Sheets API**
   - Cari "Google Sheets API" di API Library
   - Enable API tersebut

3. **Create Service Account**
   - Pergi ke "IAM & Admin" > "Service Accounts"
   - Create service account dengan role "Editor"
   - Download credentials JSON file

4. **Share Google Sheets**
   - Share spreadsheet dengan service account email
   - Berikan akses "Editor"

### 3. Gemini AI Setup

1. **Get API Key**
   - Pergi ke [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create API key baru

2. **Configure Secrets**
   - Edit `.streamlit/secrets.toml`
   - Masukkan API key dan credentials

## 🚀 Running the Application

### Perintah Utama

```bash
streamlit run app.py
```

### Perintah Alternatif

```bash
python -m streamlit run app.py
```

> [!TIP] Pastikan terminal dijalankan dari folder project yang berisi `app.py`

## 🎮 Dashboard Features

### 📊 Overview Page

- **Total Sheets**: Jumlah sheet data yang berhasil dimuat
- **Total Records**: Total baris data
- **Data Quality**: Persentase data yang valid
- **Data Preview**: Preview tabel data

### 📅 Absensi Page

- **Tingkat Kehadiran**: Persentase kehadiran keseluruhan
- **Grafik Kehadiran**: Visualisasi interaktif
- **Detail per Siswa**: Tabel kehadiran individual

### 🛡️ Security Analysis Page

- **AI Analysis**: Analisis keamanan oleh Google Gemini
- **Security Recommendations**: Saran perbaikan keamanan
- **Anomaly Detection**: Deteksi pola mencurigakan

## ⚙️ Configuration Files

### `.streamlit/secrets.toml`

```toml
# Gemini API Key (wajib)
GEMINI_API_KEY = "AIzaSy..."

# Google Sheets URL (wajib)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/.../edit"

# Sheet names (opsional, default sudah ada)
sheet_names = ["DATA_MASTER", "DATA_ABSENSI", "DATA_NILAI", "DATA_PERTEMUAN"]

# GCP Service Account JSON (wajib untuk full functionality)
[gcp_service_account_json]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "..."
client_email = "..."
# ... fields lainnya
```

### `config/settings.py`

File ini berisi konfigurasi default. Bisa dioverride oleh secrets.toml.

## 🔧 Troubleshooting

### ❌ "Cannot import name 'clean_all_data'"

**Solusi:** Pastikan file `core/data_pipeline.py` memiliki function `clean_all_data`

### ❌ "Failed to load data: ..."

**Solusi:**

- Check Google Sheets URL di secrets.toml
- Pastikan service account credentials benar
- Verifikasi spreadsheet sharing permissions

### ❌ "GEMINI_API_KEY not found"

**Solusi:** Tambahkan API key di `.streamlit/secrets.toml`

### ❌ "st.columns must be positive integer"

**Solusi:** Data tidak berhasil dimuat, check konfigurasi Google Sheets

## 📊 Data Structure Expected

Dashboard mengharapkan Google Sheets dengan struktur:

| Sheet Name       | Columns                     | Purpose           |
| ---------------- | --------------------------- | ----------------- |
| `DATA_MASTER`    | nama, rombel, dll           | Data master siswa |
| `DATA_ABSENSI`   | nama, tanggal, hadir        | Data kehadiran    |
| `DATA_NILAI`     | nama, mata_pelajaran, nilai | Data performa     |
| `DATA_PERTEMUAN` | tanggal, materi, dll        | Data pertemuan    |

## 🎯 Development Notes

### Menambah Feature Baru

1. Tambah function di folder `core/`
2. Import di `app.py`
3. Update UI di halaman yang relevan
4. Test dengan data sample

### Code Structure

- `app.py`: Main Streamlit application
- `core/data_pipeline.py`: Data loading & cleaning
- `core/llm_analyzer.py`: AI security analysis
- `core/charts.py`: Visualization functions
- `config/settings.py`: Configuration management

## 📈 Performance Tips

- **Caching**: Data dicache selama 5-10 menit untuk performa
- **Large Datasets**: Untuk data besar, consider pagination
- **API Limits**: Monitor Google Sheets API quota
- **Memory Usage**: Restart app jika memory penuh

## 🔐 Security Best Practices

- Jangan commit `secrets.toml` ke git
- Gunakan environment variables untuk production
- Rotate API keys secara berkala
- Monitor API usage di Google Cloud Console

---

## 🆘 Emergency Commands

**Stop Application**: `Ctrl + C`

**Clear Cache**: Hapus folder `__pycache__` dan restart

**Reset Environment**:

```bash
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

**🎉 Happy Coding! Dashboard LEAP Security siap digunakan.**

### 📋 Git Cheat Sheet (Lengkap)

| Command             | Fungsi                                                   | Contoh Penggunaan                                      |
| :------------------ | :------------------------------------------------------- | :----------------------------------------------------- |
| **Combo Upload** ⚡ | 🚀 **Cara Cepat** (3-in-1) Add + Commit + Push sekaligus | `git add . && git commit -m "update code" && git push` |
| `git status`        | 🔍 Cek file yang berubah                                 | `git status`                                           |
| `git add`           | 📦 Masukkan file ke Staging                              | `git add .` (semua)<br>`git add file.py` (satu)        |
| `git commit`        | 💾 Simpan perubahan                                      | `git commit -m "pesan"`                                |
| `git push`          | ☁️ Upload ke GitHub                                      | `git push origin main`                                 |
| `git pull`          | ⬇️ Ambil update dari GitHub                              | `git pull`                                             |
| `git log`           | 📜 Lihat riwayat                                         | `git log --oneline`                                    |

---
