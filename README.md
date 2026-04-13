# 🛡️ LEAP Security Dashboard

## Overview

LEAP Security Dashboard adalah sistem analisis keamanan data interaktif untuk LKP LEAP yang mengintegrasikan Google Sheets sebagai sumber data utama dengan AI-powered insights menggunakan Google Gemini. Dashboard ini dirancang khusus untuk memantau keamanan data siswa, analisis absensi, dan deteksi anomali menggunakan kecerdasan buatan.

## ✨ Features

### 🔒 Security Analysis

- **AI-Powered Analysis**: Analisis keamanan menggunakan Google Gemini AI
- **Anomaly Detection**: Deteksi pola mencurigakan dalam data absensi dan performa
- **Automated Recommendations**: Saran keamanan berbasis AI

### 📊 Data Pipeline

- **Google Sheets Integration**: Langsung terhubung ke spreadsheet LKP LEAP
- **Automated Data Cleaning**: Penanganan missing values, error patterns, dan outliers
- **Real-time Data Loading**: Cache dengan TTL untuk performa optimal

### 📈 Interactive Visualizations

- **Attendance Analytics**: Analisis kehadiran siswa dengan grafik interaktif
- **Security Metrics**: Metrik keamanan real-time
- **Data Quality Reports**: Laporan kualitas data otomatis

### 🎯 Specialized for LKP LEAP

- **Student Data Monitoring**: Pemantauan data master siswa
- **Attendance Tracking**: Sistem tracking absensi canggih
- **Score Analysis**: Analisis performa akademik dengan deteksi anomali

## 🏗️ Project Structure

```
dashboard_leap/
├── app.py                    # 🎯 Entry point Streamlit dashboard
├── config/
│   └── settings.py           # ⚙️ Konfigurasi Google Sheets & GCP
├── core/
│   ├── data_pipeline.py      # 🔄 Pipeline data loading & cleaning
│   ├── llm_analyzer.py       # 🤖 Google Gemini AI security analysis
│   └── charts.py             # 📊 Plotly visualization helpers
├── styles/
│   └── style.css             # 🎨 Custom CSS untuk dashboard
├── .streamlit/
│   └── secrets.toml          # 🔐 Streamlit secrets (API keys, credentials)
├── requirements.txt          # 📦 Python dependencies
├── README.md                 # 📖 Dokumentasi proyek
├── flow.md                   # 🔄 Dokumentasi arsitektur & flow
└── note.md                   # 📝 Catatan setup & penggunaan
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Google Cloud Project dengan Google Sheets API enabled
- Service Account credentials untuk Google Sheets access

### Setup Steps

1. **Clone Repository**

```bash
git clone <repository-url>
cd dashboard_leap
```

2. **Create Virtual Environment**

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Secrets**
   Edit `.streamlit/secrets.toml`:

```toml
# Gemini API Key
GEMINI_API_KEY = "your-api-key-here"

# Google Sheets Configuration
spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"

# GCP Service Account (JSON format)
[gcp_service_account_json]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "..."
client_email = "..."
# ... other service account fields
```

## 🎮 Usage

### Running the Dashboard

```bash
streamlit run app.py
```

Dashboard akan terbuka di browser dengan 3 halaman utama:

1. **📊 Overview**: Ringkasan data dan metrik utama
2. **📅 Absensi**: Analisis kehadiran siswa mendalam
3. **🛡️ Security Analysis**: Analisis keamanan berbasis AI

### Data Sources

Dashboard mengambil data dari Google Sheets dengan sheet berikut:

- `DATA_MASTER`: Data master siswa
- `DATA_ABSENSI`: Data absensi siswa
- `DATA_NILAI`: Data nilai/performa
- `DATA_PERTEMUAN`: Data pertemuan kelas

## ⚙️ Configuration

### Settings Configuration (`config/settings.py`)

```python
# Google Sheets Configuration
SPREADSHEET_URL = "your-spreadsheet-url"
SERVICE_ACCOUNT_PATH = "path/to/service-account.json"

# Sheet Names
SHEET_NAMES = ['DATA_MASTER', 'DATA_ABSENSI', 'DATA_NILAI', 'DATA_PERTEMUAN']

# AI Configuration
SECURITY_ANALYSIS_CONFIG = {
    'system_instruction': "Kamu adalah Security Analyst untuk LKP LEAP...",
    'max_analysis_length': 2000,
    'temperature': 0.3
}
```

### Environment Variables

```bash
# Alternative to secrets.toml
export GEMINI_API_KEY="your-api-key"
```

## 🔄 Data Flow

1. **Data Ingestion**: Load data dari Google Sheets menggunakan gspread
2. **Data Cleaning**: Handle missing values, Google Sheets errors, data type conversion
3. **Security Analysis**: AI analysis menggunakan Google Gemini untuk deteksi anomali
4. **Visualization**: Interactive charts menggunakan Plotly
5. **Reporting**: Automated security recommendations

## 🤖 AI Features

### Security Analysis Capabilities

- Deteksi siswa dengan pola absensi mencurigakan
- Analisis konsistensi data antar sheet
- Identifikasi anomali performa akademik
- Deteksi potensi masalah integritas data
- Rekomendasi keamanan actionable

### Gemini Integration

- Context-aware analysis dengan system instructions khusus LKP LEAP
- Multi-sheet data correlation
- Natural language security insights
- Automated recommendation generation

## 📊 Data Quality Features

- **Error Pattern Detection**: Otomatis detect dan clean Google Sheets errors (#ERROR!, #REF!, etc.)
- **Missing Value Handling**: Smart imputation berdasarkan data type
- **Duplicate Detection**: Identifikasi data duplikat
- **Type Conversion**: Otomatis convert data types (date, numeric, boolean)
- **Quality Reporting**: Comprehensive data quality metrics

## 🔧 Development

### Adding New Features

1. Tambah function di `core/` modules
2. Update `config/settings.py` jika perlu
3. Test dengan data sample
4. Update documentation

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Handle exceptions properly

## 🐛 Troubleshooting

### Common Issues

**Import Error**: Pastikan semua dependencies terinstall

```bash
pip install -r requirements.txt
```

**Google Sheets Access**: Verifikasi service account credentials dan permissions

**API Quota**: Check Google Cloud Console untuk Gemini API quota

**Data Loading**: Pastikan spreadsheet URL dan sheet names benar

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

Untuk pertanyaan atau issues:

1. Check existing issues di repository
2. Buat issue baru dengan detail error
3. Sertakan logs dan konfigurasi (tanpa credentials)

---

**⚡ Quick Start:**

```bash
git clone <repo>
cd dashboard_leap
pip install -r requirements.txt
streamlit run app.py
```

- Google Sheets URL/ID
- Service account path
- Sheet names
- Project ID and app settings

For secret overrides, use `.streamlit/secrets.toml`.

## Data Flow

1. **Data Ingestion**: Load data from various sources
2. **Data Cleaning**: Handle missing values, outliers, and inconsistencies
3. **Feature Engineering**: Create new features and transform existing ones
4. **Model Training**: Train ML models on prepared data
5. **Model Evaluation**: Assess model performance and select best models
6. **Visualization**: Create interactive dashboards and reports
7. **AI Analysis**: Generate insights using LLM integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open an issue on the GitHub repository.

```

```
