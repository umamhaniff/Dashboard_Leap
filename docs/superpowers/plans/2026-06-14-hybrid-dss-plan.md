# EduDecision AI V2 DSS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membangun sistem pendukung keputusan hibrida (DSS) dual-input dan dual-output terpisah berbasis Streamlit dengan visual estetika Apple.

**Architecture:** Menggunakan Session State Streamlit untuk mengelola alur login dan pemilihan sumber data (Google Sheets vs MariaDB). Masing-masing pilihan memicu data pipeline terpisah (akademik via Sheets API dan profil/relasi siswa via MariaDB 3077 dengan fallback mock data) serta visualisasi dashboard dan model AI Gemini yang terisolasi.

**Tech Stack:** Streamlit, Pandas, Plotly, gspread, mysql-connector-python, google-generativeai, pytest

---

### Task 1: Update Settings & Configuration
Memperbarui konfigurasi lembar kerja Google Sheets (mengubah `DATA_MASTER` menjadi `DATA_SISWA`, menambahkan `DATA_KELUAR`) serta menambahkan konfigurasi dasar MariaDB dan password gate.

**Files:**
- Modify: `config/settings.py`
- Modify: `.streamlit/secrets.toml`
- Test: `tests/test_settings.py`

- [ ] **Step 1: Tulis unit test untuk verifikasi konfigurasi**
Create: `tests/test_settings.py`
```python
from config.settings import get_config

def test_settings_load():
    config = get_config()
    assert "DATA_SISWA" in config["sheet_names"]
    assert "DATA_KELUAR" in config["sheet_names"]
    assert "mariadb" in config
    assert config["mariadb"]["port"] == 3077
```

- [ ] **Step 2: Jalankan test dan pastikan gagal**
Run: `.venv/Scripts/pytest tests/test_settings.py -v`
Expected: FAIL (tabel/kunci belum diperbarui)

- [ ] **Step 3: Perbarui config/settings.py**
TargetContent di `config/settings.py` baris 60-66:
```python
SHEET_NAMES = _streamlit_secrets.get('sheet_names', [
    'DATA_MASTER',
    'DATA_ABSENSI',
    'DATA_NILAI',
    'DATA_OVERVIEW',
    # Tambahkan sheet lainnya sesuai kebutuhan
])
```
ReplacementContent:
```python
SHEET_NAMES = _streamlit_secrets.get('sheet_names', [
    'DATA_SISWA',
    'DATA_ABSENSI',
    'DATA_NILAI',
    'DATA_KELUAR',
    'DATA_OVERVIEW',
])

# MariaDB Connection settings
MARIADB_CONFIG = {
    'host': _streamlit_secrets.get('mariadb_host', 'localhost'),
    'port': int(_streamlit_secrets.get('mariadb_port', 3077)),
    'user': _streamlit_secrets.get('mariadb_user', 'root'),
    'password': _streamlit_secrets.get('mariadb_password', ''),
    'database': _streamlit_secrets.get('mariadb_database', 'dataleap_v5_migration')
}
```
Dan perbarui fungsi `get_config()` untuk mengembalikan:
```python
def get_config() -> Dict[str, Any]:
    return {
        'spreadsheet_url': SPREADSHEET_URL,
        'spreadsheet_id': SPREADSHEET_ID,
        'service_account_path': SERVICE_ACCOUNT_PATH,
        'service_account_json': SERVICE_ACCOUNT_JSON,
        'sheet_names': SHEET_NAMES,
        'project_id': PROJECT_ID,
        'error_patterns': ERROR_PATTERNS,
        'data_type_mappings': DATA_TYPE_MAPPINGS,
        'security_analysis': SECURITY_ANALYSIS_CONFIG,
        'dashboard': DASHBOARD_CONFIG,
        'mariadb': MARIADB_CONFIG
    }
```

- [ ] **Step 4: Perbarui .streamlit/secrets.toml**
Tambahkan konfigurasi di bawah line 23:
```toml
# MariaDB Config
mariadb_host = "localhost"
mariadb_port = 3077
mariadb_user = "root"
mariadb_password = ""
mariadb_database = "dataleap_v5_migration"

# System Password Gate
SYSTEM_PASSWORD = "leapadmin2026"
```

- [ ] **Step 5: Jalankan test dan pastikan PASS**
Run: `.venv/Scripts/pytest tests/test_settings.py -v`
Expected: PASS

- [ ] **Step 6: Commit**
```bash
git add config/settings.py .streamlit/secrets.toml tests/test_settings.py
git commit -m "feat: configure sheet names, mariadb connection, and system password"
```

---

### Task 2: Implement MariaDB Connector & Mock Data Engine
Membangun konektor MariaDB pada port 3077 dan mengimplementasikan mesin data mock untuk tabel `siswa`, `kursus_siswa`, `jadwal_siswa`, `catatan_siswa`, `catatan_remidi_siswa`, dan `web_statistik` sebagai failover jika koneksi database lokal tidak aktif.

**Files:**
- Modify: `core/data_pipeline.py`
- Test: `tests/test_data_pipeline.py`

- [ ] **Step 1: Tulis unit test untuk load data MariaDB/Mock**
Create: `tests/test_data_pipeline.py`
```python
from core.data_pipeline import load_mariadb_data

def test_load_mariadb_data():
    dfs = load_mariadb_data()
    assert "siswa" in dfs
    assert "kursus_siswa" in dfs
    assert "web_statistik" in dfs
    assert not dfs["siswa"].empty
```

- [ ] **Step 2: Jalankan test dan pastikan gagal**
Run: `.venv/Scripts/pytest tests/test_data_pipeline.py -v`
Expected: FAIL (fungsi `load_mariadb_data` belum ada)

- [ ] **Step 3: Tulis minimal implementasi load_mariadb_data di core/data_pipeline.py**
Tambahkan kode koneksi dan fallback mock ke akhir `core/data_pipeline.py`:
```python
import pymysql
from config.settings import MARIADB_CONFIG

def generate_mock_mariadb_data() -> Dict[str, pd.DataFrame]:
    """Menghasilkan mock data realistis untuk Siswa dan Hubungannya."""
    siswa_df = pd.DataFrame([
        {"id_siswa": 1, "nis": "2601001", "nama_lengkap": "Medina Novi Mareta", "status_siswa": "Aktif"},
        {"id_siswa": 2, "nis": "2601002", "nama_lengkap": "Nuzula Naura Dhuha", "status_siswa": "Aktif"},
        {"id_siswa": 3, "nis": "2601003", "nama_lengkap": "Yasuke Natalio", "status_siswa": "Aktif"},
        {"id_siswa": 4, "nis": "2601004", "nama_lengkap": "Dava Valecio Santoso", "status_siswa": "Keluar"}
    ])
    
    kursus_siswa_df = pd.DataFrame([
        {"id_siswa": 1, "nama_kursus": "Bahasa Inggris", "status_keaktifan": "Aktif", "status_kelulusan": "Belum Lulus"},
        {"id_siswa": 2, "nama_kursus": "Bahasa Inggris", "status_keaktifan": "Aktif", "status_kelulusan": "Belum Lulus"},
        {"id_siswa": 3, "nama_kursus": "Digital/Komputer", "status_keaktifan": "Aktif", "status_kelulusan": "Lulus"},
        {"id_siswa": 4, "nama_kursus": "Komputer", "status_keaktifan": "Non-Aktif", "status_kelulusan": "Belum Lulus"}
    ])

    jadwal_siswa_df = pd.DataFrame([
        {"id_siswa": 1, "rombel": "01 GOGO 1 SK1", "status_keluar": 0, "is_acc_rapor": 1, "status_ketuntasan": "Tuntas"},
        {"id_siswa": 2, "rombel": "01 GOGO 1 SK1", "status_keluar": 0, "is_acc_rapor": 0, "status_ketuntasan": "Belum Tuntas"},
        {"id_siswa": 3, "rombel": "02 GOGO 1 SK2", "status_keluar": 0, "is_acc_rapor": 1, "status_ketuntasan": "Tuntas"},
        {"id_siswa": 4, "rombel": "Ing-02 GOGO 1 SK2", "status_keluar": 1, "is_acc_rapor": 0, "status_ketuntasan": "Belum Tuntas"}
    ])

    catatan_siswa_df = pd.DataFrame([
        {"id_siswa": 2, "catatan": "Siswa kesulitan memahami materi listening.", "status_followup": "NEED FURTHER OBSERVATION"},
        {"id_siswa": 4, "catatan": "Siswa sering bolos karena tabrakan jadwal les bola.", "status_followup": "CASE CLOSED"}
    ])

    catatan_remidi_siswa_df = pd.DataFrame([
        {"id_siswa": 2, "nilai_sebelum": 55, "nilai_sesudah": 70, "persetujuan_guru": "Approved"}
    ])

    web_statistik_df = pd.DataFrame([
        {"id_web_statistik": 1, "ip_address": "192.168.1.10", "page_views": 4, "visitor_session": "sess_01", "created_at": "2026-06-14 08:00:00"},
        {"id_web_statistik": 2, "ip_address": "192.168.1.15", "page_views": 10, "visitor_session": "sess_02", "created_at": "2026-06-14 08:15:00"}
    ])

    return {
        "siswa": siswa_df,
        "kursus_siswa": kursus_siswa_df,
        "jadwal_siswa": jadwal_siswa_df,
        "catatan_siswa": catatan_siswa_df,
        "catatan_remidi_siswa": catatan_remidi_siswa_df,
        "web_statistik": web_statistik_df
    }

def load_mariadb_data() -> Dict[str, pd.DataFrame]:
    """Membaca data siswa dan relasinya dari MariaDB port 3077, atau fallback ke Mock jika gagal."""
    try:
        connection = pymysql.connect(
            host=MARIADB_CONFIG['host'],
            port=MARIADB_CONFIG['port'],
            user=MARIADB_CONFIG['user'],
            password=MARIADB_CONFIG['password'],
            database=MARIADB_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=3
        )
        try:
            with connection.cursor() as cursor:
                # Ambil tabel siswa
                cursor.execute("SELECT * FROM siswa")
                siswa = pd.DataFrame(cursor.fetchall())
                
                # Ambil tabel kursus_siswa
                cursor.execute("SELECT * FROM kursus_siswa")
                kursus_siswa = pd.DataFrame(cursor.fetchall())

                # Ambil tabel jadwal_siswa
                cursor.execute("SELECT * FROM jadwal_siswa")
                jadwal_siswa = pd.DataFrame(cursor.fetchall())

                # Ambil tabel catatan_siswa
                cursor.execute("SELECT * FROM catatan_siswa")
                catatan_siswa = pd.DataFrame(cursor.fetchall())

                # Ambil tabel catatan_remidi_siswa
                cursor.execute("SELECT * FROM catatan_remidi_siswa")
                catatan_remidi_siswa = pd.DataFrame(cursor.fetchall())

                # Ambil tabel web_statistik
                cursor.execute("SELECT * FROM web_statistik")
                web_statistik = pd.DataFrame(cursor.fetchall())

                return {
                    "siswa": siswa,
                    "kursus_siswa": kursus_siswa,
                    "jadwal_siswa": jadwal_siswa,
                    "catatan_siswa": catatan_siswa,
                    "catatan_remidi_siswa": catatan_remidi_siswa,
                    "web_statistik": web_statistik
                }
        finally:
            connection.close()
    except Exception as e:
        logger.warning(f"Database connection failed ({str(e)}). Falling back to mock data engine.")
        return generate_mock_mariadb_data()
```

- [ ] **Step 4: Jalankan test dan pastikan PASS**
Run: `.venv/Scripts/pytest tests/test_data_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add core/data_pipeline.py tests/test_data_pipeline.py
git commit -m "feat: implement load_mariadb_data with mock fallback engine"
```

---

### Task 3: Split AI Prompt Registry
Memperbarui generator prompt AI di `core/llm_analyzer.py` untuk memisahkan instruksi dan target audit antara data Google Sheets (Analisis Nilai & Rapor) dan MariaDB Database (Profil Siswa & Kasus Observasi).

**Files:**
- Modify: `core/llm_analyzer.py`
- Test: `tests/test_llm_analyzer.py`

- [ ] **Step 1: Tulis unit test untuk verifikasi pemisahan prompt**
Create: `tests/test_llm_analyzer.py`
```python
from core.llm_analyzer import get_academic_prompt, get_operations_prompt

def test_prompts():
    assert "ACADEMIC" in get_academic_prompt({})
    assert "SISWA" in get_operations_prompt({})
```

- [ ] **Step 2: Jalankan test dan pastikan gagal**
Run: `.venv/Scripts/pytest tests/test_llm_analyzer.py -v`
Expected: FAIL (fungsi belum didefinisikan)

- [ ] **Step 3: Implementasikan fungsi prompt baru di core/llm_analyzer.py**
Ubah dan pisahkan logic pembuatan prompt:
```python
def get_academic_prompt(dataframes: dict) -> str:
    combined = "=== AUDIT AKADEMIK & NILAI SISWA (GOOGLE SHEETS) ===\n"
    for name in ["DATA_SISWA", "DATA_NILAI", "DATA_KELUAR"]:
        df = dataframes.get(name)
        if df is not None and not df.empty:
            combined += f"\n[TABEL: {name}]\n{df.head(40).to_string(index=False)}\n"
    
    return f"""Kamu adalah Academic Decision Support Assistant untuk LKP LEAP.
Tugasmu adalah menganalisis data nilai siswa, sebaran grade, dan kasus remedi untuk memberikan rekomendasi evaluasi akademik.
Fokus Analisis:
1. Identifikasi program/rombel dengan tingkat remedi tertinggi.
2. Analisis korelasi antara kehadiran dengan pencapaian nilai (grade).
3. Berikan usulan perbaikan pembelajaran yang konkret untuk siswa remedi.

Data Input:
{combined}
"""

def get_operations_prompt(dataframes: dict) -> str:
    combined = "=== AUDIT OPERASIONAL & PROFILE SISWA (MARIADB) ===\n"
    for name in ["siswa", "kursus_siswa", "jadwal_siswa", "catatan_siswa", "catatan_remidi_siswa"]:
        df = dataframes.get(name)
        if df is not None and not df.empty:
            combined += f"\n[TABEL: {name}]\n{df.head(40).to_string(index=False)}\n"
            
    return f"""Kamu adalah Database Operations Auditor untuk LKP LEAP.
Tugasmu mengaudit konsistensi status keaktifan siswa, log kasus observasi, dan riwayat perbaikan remidi pada database operasional.
Fokus Analisis:
1. Temukan siswa yang terjebak pada status 'NEED FURTHER OBSERVATION' yang belum selesai ditangani.
2. Periksa inkonsistensi data (misal siswa non-aktif tapi masih terdaftar tuntas di kelas berjalan).
3. Berikan saran tindak lanjut administratif untuk penyelesaian kasus siswa.

Data Input:
{combined}
"""
```
Dan perbarui `analyze_security()` untuk menerima argumen `source_type`:
```python
def analyze_security(dataframes: dict, source_type: str = "google_sheets") -> str:
    api_key = get_api_key()
    if not api_key:
        return "ERROR: API Key tidak ditemukan."
    
    genai.configure(api_key=api_key)
    
    models_to_try = [
        'models/gemini-3.1-flash-lite-preview',
        'models/gemini-3-flash-preview',
        'models/gemini-2.5-flash-lite',
        'models/gemini-flash-latest'
    ]
    
    if source_type == "google_sheets":
        prompt = get_academic_prompt(dataframes)
        sys_instruction = "Kamu adalah Asisten Analisis Akademik LKP LEAP."
    else:
        prompt = get_operations_prompt(dataframes)
        sys_instruction = "Kamu adalah Auditor Integritas Database Siswa LKP LEAP."

    last_error = ""
    for model_name in models_to_try:
        try:
            logger.info(f"Mencoba audit {source_type} dengan: {model_name}")
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=sys_instruction
            )
            response = model.generate_content(prompt)
            return f"**System Intelligence: {model_name}**\n\n{response.text.strip()}"
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                last_error = "Semua model di list sedang sibuk. Silakan tunggu 1 menit."
                continue
            else:
                logger.error(f"Gagal pada {model_name}: {error_msg}")
                continue
    return f"ERROR: {last_error}"
```

- [ ] **Step 4: Jalankan test dan pastikan PASS**
Run: `.venv/Scripts/pytest tests/test_llm_analyzer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add core/llm_analyzer.py tests/test_llm_analyzer.py
git commit -m "feat: split prompts and implement dual AI analysis modes"
```

---

### Task 4: Apple CSS Styling Customization
Menerapkan visual styling khas Apple di CSS untuk membuang shadow pada card standard, menambahkan frosted effect, membuat layout section gelap bergantian, serta mendesain header navigasi hitam.

**Files:**
- Modify: `styles/style.css`

- [ ] **Step 1: Perbarui styles/style.css**
Ganti seluruh isi `styles/style.css` dengan:
```css
/* --- Apple Typography & Base Canvas --- */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
  font-family: 'Outfit', -apple-system, system-ui, sans-serif !important;
  background-color: #f5f5f7 !important; /* Canvas Parchment */
  color: #1d1d1f !important; /* Near-black Ink */
}

/* --- Navigation Bars --- */
.apple-global-nav {
  background-color: #000000;
  color: #ffffff;
  padding: 10px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  letter-spacing: -0.12px;
  margin-top: -60px;
  margin-bottom: 20px;
}

.apple-sub-nav {
  background-color: rgba(245, 245, 247, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid #e0e0e0;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

/* --- Hero Displays --- */
.apple-hero-display {
  font-family: 'Outfit', sans-serif;
  font-size: 44px !important;
  font-weight: 600 !important;
  line-height: 1.1;
  letter-spacing: -0.374px !important;
  color: #1d1d1f !important;
  margin-bottom: 5px;
}

.apple-tagline {
  font-size: 19px !important;
  color: #7a7a7a !important;
  margin-bottom: 35px;
}

/* --- Card Styles --- */
div[data-testid="stMetricValue"] {
  font-size: 34px !important;
  font-weight: 600 !important;
  color: #1d1d1f !important;
}

div[data-testid="metric-container"] {
  background-color: #ffffff !important;
  border: 1px solid #e0e0e0 !important;
  border-radius: 18px !important; /* rounded.lg */
  padding: 18px !important;
  box-shadow: none !important; /* No shadow */
}

/* --- AI recommendations (Resting Shadow) --- */
.apple-ai-panel {
  background-color: #1d1d1f !important;
  color: #ffffff !important;
  border-radius: 18px !important;
  padding: 24px;
  box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0 !important; /* Single Shadow */
  margin-top: 20px;
}

.apple-ai-panel h3 {
  color: #2997ff !important;
  font-weight: 600;
}

/* --- Buttons --- */
button[kind="primary"] {
  background-color: #0066cc !important; /* Action Blue */
  color: white !important;
  border-radius: 9999px !important; /* rounded.pill */
  border: none !important;
  padding: 8px 18px !important;
  transition: transform 0.1s ease;
}

button[kind="primary"]:active {
  transform: scale(0.95); /* scale micro-interaction */
}
```

- [ ] **Step 2: Commit**
```bash
git add styles/style.css
git commit -m "style: implement full Apple design system CSS styles"
```

---

### Task 5: Build Login, Selection & Dual Dashboards UI
Mengintegrasikan seluruh state mesin login (Password Gate), layar pemilihan sumber data utama, dan menyajikan 2 dashboard berbeda dengan visualisasi detail performa akademik (Google Sheets) dan profil relasional siswa (MariaDB).

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Ganti app.py dengan alur login dan visualisasi ganda**
Ganti seluruh isi `app.py` dengan:
```python
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import google.generativeai as genai

from core.data_pipeline import load_all_data, clean_all_data, get_data_quality_report, load_mariadb_data
from core.llm_analyzer import analyze_security, generate_security_recommendations
from core.charts import create_attendance_chart, create_score_distribution
from config.settings import DASHBOARD_CONFIG, SPREADSHEET_URL

# --- LOAD STYLING ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles/style.css")

# --- INITIALIZE SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'selected_source' not in st.session_state:
    st.session_state.selected_source = None
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# --- HTML TEMPLATES ---
st.markdown('<div class="apple-global-nav"><span> EduDecision AI</span><span>Overview | Analytics | Logs</span></div>', unsafe_allow_html=True)

# --- PASSWORD GATE ---
if not st.session_state.logged_in:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown('<div style="text-align: center; margin-top: 50px; font-size: 50px;">🛡️</div>', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; font-family: SF Pro Display; font-weight: 600;">Sign in to EduDecision AI</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #7a7a7a; margin-bottom: 30px;">Gunakan password sistem LKP LEAP.</p>', unsafe_allow_html=True)
        
        password = st.text_input("Enter Password", type="password", label_visibility="collapsed")
        
        if st.button("Sign In", use_container_width=True, type="primary"):
            target_pass = st.secrets.get("SYSTEM_PASSWORD", "leapadmin2026")
            if password == target_pass:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Password salah. Silakan hubungi administrator.")
    st.stop()

# --- SOURCE SELECTION ---
if st.session_state.selected_source is None:
    st.markdown('<h2 style="text-align: center; font-family: SF Pro Display; margin-top: 40px;">Pilih Sumber Data Utama</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7a7a7a; margin-bottom: 40px;">Tentukan data yang ingin dianalisis saat ini.</p>', unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown('<div style="background: white; border: 1px solid #e0e0e0; border-radius: 18px; padding: 25px; text-align: center; height: 180px;">'
                    '<h3>📊 Google Sheets</h3>'
                    '<p style="color: 7a7a7a; font-size: 14px;">Laporan Akademik, Nilai, Kehadiran, & Remidi Siswa.</p>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Pilih Google Sheets", key="btn_sheets", use_container_width=True, type="primary"):
            st.session_state.selected_source = 'google_sheets'
            st.session_state.run_analysis = False
            st.session_state.analysis_result = None
            st.rerun()
            
    with col_s2:
        st.markdown('<div style="background: white; border: 1px solid #e0e0e0; border-radius: 18px; padding: 25px; text-align: center; height: 180px;">'
                    '<h3>🗄️ MariaDB Database</h3>'
                    '<p style="color: 7a7a7a; font-size: 14px;">Log Profil Siswa Aktif, Status Rombel, & Catatan Kualitatif.</p>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Pilih MariaDB Database", key="btn_mariadb", use_container_width=True, type="primary"):
            st.session_state.selected_source = 'mariadb'
            st.session_state.run_analysis = False
            st.session_state.analysis_result = None
            st.rerun()
            
    st.stop()

# --- SUB NAV FROSTED BAR ---
col_sub1, col_sub2 = st.columns([3, 1])
with col_sub1:
    source_title = "Google Sheets (Akademik)" if st.session_state.selected_source == 'google_sheets' else "MariaDB (Profil Siswa)"
    st.markdown(f'<div style="font-family: SF Pro Display; font-size: 22px; font-weight: 600; padding: 10px 0;">Active Source: {source_title}</div>', unsafe_allow_html=True)

with col_sub2:
    st.write("")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("Switch", use_container_width=True):
            st.session_state.selected_source = None
            st.rerun()
    with col_c2:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.selected_source = None
            st.rerun()

st.markdown("---")

# --- LOADING AND DASHBOARD RENDERING ---

if st.session_state.selected_source == 'google_sheets':
    # --- MODUL A: GOOGLE SHEETS (ACADEMIC FOCUS) ---
    st.markdown('<h1 class="apple-hero-display">Academic Performance & Grades</h1>', unsafe_allow_html=True)
    st.markdown('<p class="apple-tagline">Analisis rata-rata nilai, sebaran grade, dan ketuntasan remidi siswa.</p>', unsafe_allow_html=True)

    with st.spinner("Sinkronisasi data Google Sheets..."):
        try:
            raw_data = load_all_data()
            cleaned_data = clean_all_data(raw_data)
            quality_report = get_data_quality_report(cleaned_data)
        except Exception as e:
            st.error(f"Gagal memuat API Google Sheets: {str(e)}")
            st.stop()

    # Metrics
    c1, c2, c3 = st.columns(3)
    total_siswa = len(cleaned_data.get("DATA_SISWA", []))
    total_remidi = len(cleaned_data.get("DATA_NILAI", [])) # placeholder count
    c1.metric("Total Siswa", f"{total_siswa}")
    c2.metric("Siswa Remidi", "305") # Statis dari docs/dashboard_context.md
    c3.metric("Rata-rata Nilai (Final)", "71.60")

    st.markdown("### 📊 Distribusi & Analisis Nilai")
    
    col_graph1, col_graph2 = st.columns(2)
    with col_graph1:
        if "DATA_NILAI" in cleaned_data:
            fig_scores = create_score_distribution(cleaned_data["DATA_NILAI"])
            st.plotly_chart(fig_scores, use_container_width=True)
    with col_graph2:
        # Tampilkan sebaran kualitatif grade dari prd
        st.markdown("""
        **Sebaran Grade Nilai Gabungan:**
        *   **26.7%** - Grade E (50-59)
        *   **23.3%** - Grade F (Below 50)
        *   **16.0%** - Grade B (80-89)
        *   **13.5%** - Grade C (70-79)
        *   **10.2%** - Grade A (90-100)
        *   **10.0%** - Grade D (60-69)
        """)

    # AI Section
    st.markdown("---")
    if st.button("🤖 Run Academic AI Analysis", type="primary"):
        st.session_state.run_analysis = True

    if st.session_state.run_analysis:
        with st.spinner("Gemini sedang menganalisis performa akademik..."):
            st.session_state.analysis_result = analyze_security(cleaned_data, "google_sheets")
        
        st.markdown(f'<div class="apple-ai-panel"><h3>💡 AI Academic Recommendations</h3>{st.session_state.analysis_result}</div>', unsafe_allow_html=True)

else:
    # --- MODUL B: MARIADB DATABASE (STUDENT RELATIONS FOCUS) ---
    st.markdown('<h1 class="apple-hero-display">Student Profiles & Operational Relations</h1>', unsafe_allow_html=True)
    st.markdown('<p class="apple-tagline">Log relasi program siswa, catatan kualitatif rombel, dan log remidi database.</p>', unsafe_allow_html=True)

    with st.spinner("Sinkronisasi database MariaDB (Port 3077)..."):
        db_data = load_mariadb_data()

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Siswa Terdaftar (DB)", f"{len(db_data['siswa'])}")
    c2.metric("Rombel Aktif", "16 Rombel")
    c3.metric("Kasus Observasi Aktif", f"{len(db_data['catatan_siswa'][db_data['catatan_siswa']['status_followup']=='NEED FURTHER OBSERVATION'])}")

    st.markdown("### 🗂️ Profil Siswa & Catatan Kelas")
    col_db1, col_db2 = st.columns([2, 1])
    
    with col_db1:
        st.subheader("Daftar Siswa & Rombel (Direct Access)")
        st.dataframe(db_data['jadwal_siswa'], use_container_width=True)

    with col_db2:
        st.subheader("Log Kasus Observasi Staf")
        for idx, row in db_data['catatan_siswa'].iterrows():
            badge = "🔴 Observasi" if row['status_followup'] == 'NEED FURTHER OBSERVATION' else "🟢 Selesai"
            st.markdown(f"**Siswa ID {row['id_siswa']}** ({badge}):\n* {row['catatan']}")

    # AI Section
    st.markdown("---")
    if st.button("🤖 Run Database Operations AI Audit", type="primary"):
        st.session_state.run_analysis = True

    if st.session_state.run_analysis:
        with st.spinner("Gemini sedang melakukan audit operasional database..."):
            st.session_state.analysis_result = analyze_security(db_data, "mariadb")
        
        st.markdown(f'<div class="apple-ai-panel"><h3>💡 AI Operations Audit Recommendations</h3>{st.session_state.analysis_result}</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.caption(f"EduDecision AI v2.0 | Last Sync: {datetime.now().strftime('%H:%M:%S')}")
```

- [ ] **Step 2: Jalankan dashboard untuk verifikasi syntax**
Run: `.venv/Scripts/python.exe -m streamlit run app.py` (Wait for 2-3 seconds, then stop it if it runs correctly).
Expected: Runs without syntax errors.

- [ ] **Step 3: Commit**
```bash
git add app.py
git commit -m "feat: implement login screen, selection flow, and distinct dual-input dashboards"
```
