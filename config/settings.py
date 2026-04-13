"""
Settings and configuration for LEAP Security Dashboard.
Centralized configuration management.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent


def _extract_spreadsheet_key(value: str) -> str:
    if not value:
        return ''

    value = value.strip()
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', value)
    if match:
        return match.group(1)

    match = re.search(r'spreadsheetId=([a-zA-Z0-9-_]+)', value)
    if match:
        return match.group(1)

    return value


def _get_streamlit_secrets() -> Dict[str, Any]:
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            return dict(st.secrets)
    except Exception:
        pass
    return {}

# Google Sheets Configuration
SPREADSHEET_URL = ""
SPREADSHEET_ID = ""
SERVICE_ACCOUNT_PATH = "service_account.json"
SERVICE_ACCOUNT_JSON = None

# Override with Streamlit secrets if available
_streamlit_secrets = _get_streamlit_secrets()
if _streamlit_secrets.get('spreadsheet_url'):
    SPREADSHEET_URL = _streamlit_secrets['spreadsheet_url']
    SPREADSHEET_ID = _extract_spreadsheet_key(SPREADSHEET_URL)
elif _streamlit_secrets.get('spreadsheet_id'):
    SPREADSHEET_ID = _streamlit_secrets['spreadsheet_id']

if _streamlit_secrets.get('gcp_service_account_path'):
    SERVICE_ACCOUNT_PATH = _streamlit_secrets['gcp_service_account_path']

if _streamlit_secrets.get('gcp_service_account_json'):
    SERVICE_ACCOUNT_JSON = _streamlit_secrets['gcp_service_account_json']

# Sheet names yang akan diakses
SHEET_NAMES = _streamlit_secrets.get('sheet_names', [
    'DATA_MASTER',
    'DATA_ABSENSI',
    'DATA_NILAI',
    'DATA_OVERVIEW',
    # Tambahkan sheet lainnya sesuai kebutuhan
])

# GCP Project ID (optional)
PROJECT_ID = _streamlit_secrets.get('project_id', 'your-gcp-project-id')

# Error patterns commonly found in Google Sheets
ERROR_PATTERNS = [
    '#ERROR!', '#REF!', '#VALUE!', '#NAME?', '#DIV/0!', '#NUM!',
    '#N/A', '#NULL!', 'ERROR', 'REF', 'N/A', 'NULL'
]

# Data type mappings for automatic conversion
DATA_TYPE_MAPPINGS = {
    'date_columns': ['tanggal', 'date', 'waktu', 'time', 'created_at', 'updated_at'],
    'numeric_columns': ['nilai', 'score', 'skor', 'umur', 'age', 'jumlah', 'count', 'total'],
    'boolean_columns': ['hadir', 'present', 'aktif', 'active', 'status'],
}

# Security analysis configuration
SECURITY_ANALYSIS_CONFIG = {
    'system_instruction': """
Kamu adalah Security Analyst untuk LKP LEAP. Tugasmu menganalisis data siswa, absensi, dan performa untuk mendeteksi anomali keamanan dan pola mencurigakan.

Fokus analisis:
1. Akses Tidak Wajar: Pola login/logout yang tidak normal, akses di luar jam operasional
2. Tren Ketidakhadiran Sistemik: Pola absensi yang mencurigakan, siswa yang sering tidak hadir
3. Anomali Input Data: Data yang tidak konsisten, nilai yang tidak masuk akal, duplikasi mencurigakan
4. Pola Performa: Fluktuasi nilai yang tidak wajar, indikasi kecurangan akademik
5. Konsistensi Data: Inkonsistensi antara tabel master, absensi, dan nilai

Berikan analisis yang objektif dan berbasis data, spesifik dengan contoh, dan mengusulkan rekomendasi keamanan.
""",
    'max_analysis_length': 2000,
    'temperature': 0.3
}

# Dashboard configuration
DASHBOARD_CONFIG = {
    'title': '🛡️ LEAP Security Dashboard',
    'subtitle': 'Sistem Analisis Keamanan Data LKP LEAP',
    'pages': ['Overview', 'Absensi', 'Security Analysis'],
    'theme': {
        'primary_color': '#1f77b4',
        'background_color': '#f0f2f6',
        'secondary_background_color': '#ffffff'
    }
}

def get_config() -> Dict[str, Any]:
    """Get all configuration as dictionary."""
    return {
        'spreadsheet_id': SPREADSHEET_ID,
        'spreadsheet_url': SPREADSHEET_URL,
        'service_account_path': SERVICE_ACCOUNT_PATH,
        'service_account_json': SERVICE_ACCOUNT_JSON,
        'sheet_names': SHEET_NAMES,
        'project_id': PROJECT_ID,
        'error_patterns': ERROR_PATTERNS,
        'data_type_mappings': DATA_TYPE_MAPPINGS,
        'security_analysis': SECURITY_ANALYSIS_CONFIG,
        'dashboard': DASHBOARD_CONFIG
    }

def validate_config() -> List[str]:
    """Validate configuration and return list of issues."""
    issues = []

    if not SPREADSHEET_ID:
        issues.append("Spreadsheet URL atau ID belum diisi di config/settings.py atau .streamlit/secrets.toml")

    if not SERVICE_ACCOUNT_JSON:
        if not SERVICE_ACCOUNT_PATH or not os.path.exists(SERVICE_ACCOUNT_PATH):
            issues.append(f"Service account file tidak ditemukan: {SERVICE_ACCOUNT_PATH}")

    return issues