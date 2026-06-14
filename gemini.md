#  EduDecision AI V2 - Gemini Context

Dokumen ini memuat konteks persisten dan perintah CLI khusus untuk memandu agen AI (Gemini) dalam memelihara dan mengembangkan proyek **EduDecision AI V2** di lingkungan LKP LEAP Surabaya.

---

## 📋 Proyek & Arsitektur Utama
EduDecision AI V2 adalah sistem pendukung keputusan hibrida (*Hybrid DSS*) berbasis **Streamlit** dengan estetika visual **Genesis Design** (sesuai docs/genesis-DESIGN.md). Sistem ini memiliki dual-input dan dual-output terisolasi:

1.  **Google Sheets (Absensi & Nilai)**:
    *   **Fokus**: *Attendance & Grades*.
    *   **Data**: `DATA_SISWA`, `DATA_ABSENSI`, `DATA_NILAI`, `DATA_KELUAR`, `DATA_OVERVIEW`.
    *   **AI Engine**: Rekomendasi kehadiran & analisis nilai (Gemini Academic Engine).
2.  **Database SQL (Statistik Website)**:
    *   **Fokus**: *Website Analytics & Traffic Logs*.
    *   **Data**: `web_statistik`.
    *   **AI Engine**: Audit trafik website, deteksi anomali akses, dan log performa (Gemini Operations Engine).

---

## 🛠️ Panduan Pengembangan & Perintah Penting

### Lingkungan Virtual (Virtual Environment)
*   **Virtual Env**: Menggunakan Python venv di `.venv/`
*   **Interpreter**: `.venv/Scripts/python.exe`
*   **Pip**: `.venv/Scripts/pip.exe`

### Perintah CLI Khusus (Custom Commands)
Gunakan perintah-perintah berikut untuk pengujian dan pengembangan proyek ini:

```powershell
# 1. Menjalankan Dashboard Streamlit secara Lokal
.venv/Scripts/python.exe -m streamlit run app.py

# 2. Menjalankan Seluruh Unit Test (Pytest)
.venv/Scripts/pytest -v

# 3. Menjalankan Test Spesifik untuk Konfigurasi
.venv/Scripts/pytest tests/test_settings.py -v

# 4. Menjalankan Test Spesifik untuk Pipeline Data
.venv/Scripts/pytest tests/test_data_pipeline.py -v

# 5. Menjalankan Test Spesifik untuk AI Prompts
.venv/Scripts/pytest tests/test_llm_analyzer.py -v
```

---

## 🚦 Status Branch & Kolaborasi
*   **Branch Aktif**: `feature/dss-hybrid-mariadb-gsheets`
*   **Aturan Commit**: Commit sesering mungkin untuk setiap unit task yang berhasil diselesaikan dan lolos uji unit test.
