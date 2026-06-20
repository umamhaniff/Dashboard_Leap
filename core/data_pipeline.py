"""
Data Pipeline for LEAP Security Dashboard.
Combines data fetching, loading, cleaning, and transformation.
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import pandas as pd
import numpy as np
import re
import streamlit as st
import logging
import pymysql
from sklearn.cluster import KMeans
from typing import Dict, List, Any, Optional
from config.settings import (
    SPREADSHEET_ID, SPREADSHEET_URL, SERVICE_ACCOUNT_PATH, SHEET_NAMES,
    ERROR_PATTERNS, DATA_TYPE_MAPPINGS, MARIADB_CONFIG
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_google_sheets() -> gspread.client.Client:
    """Authenticate with Google Sheets API using service account."""
    try:
        import socket
        socket.setdefaulttimeout(15.0)
        creds = None

        if hasattr(st, 'secrets'):
            if 'gcp_service_account_json' in st.secrets and st.secrets['gcp_service_account_json']:
                creds_dict = st.secrets['gcp_service_account_json']
                if isinstance(creds_dict, str):
                    creds_dict = json.loads(creds_dict)
                creds = Credentials.from_service_account_info(creds_dict)
            elif 'gcp_service_account_path' in st.secrets and st.secrets['gcp_service_account_path']:
                creds = Credentials.from_service_account_file(st.secrets['gcp_service_account_path'])

        if creds is None:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)

        scope = scope = [
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                        ]
        creds = creds.with_scopes(scope)

        client = gspread.authorize(creds)
        return client

    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Sheets: {str(e)}")


def _open_spreadsheet(client: gspread.client.Client):
    """Open the spreadsheet using URL or key configuration."""
    if hasattr(st, 'secrets'):
        if 'spreadsheet_url' in st.secrets and st.secrets['spreadsheet_url']:
            return client.open_by_url(st.secrets['spreadsheet_url'])
        if 'spreadsheet_id' in st.secrets and st.secrets['spreadsheet_id']:
            return client.open_by_key(st.secrets['spreadsheet_id'])

    if SPREADSHEET_URL:
        return client.open_by_url(SPREADSHEET_URL)
    if SPREADSHEET_ID:
        return client.open_by_key(SPREADSHEET_ID)

    raise Exception('Spreadsheet URL atau ID tidak ditemukan. Isi config/settings.py atau .streamlit/secrets.toml dengan spreadsheet_url atau spreadsheet_id.')


def get_sheet_data(sheet_name: str) -> List[Dict[str, Any]]:
    """Fetch data from a specific Google Sheets worksheet."""
    try:
        client = authenticate_google_sheets()
        spreadsheet = _open_spreadsheet(client)
        worksheet = spreadsheet.worksheet(sheet_name)

        # Get all values
        values = worksheet.get_all_values()

        if not values:
            return []

        # Convert to list of dicts (first row as headers)
        headers = values[0]
        data = []

        for row in values[1:]:
            # Ensure row has same length as headers
            while len(row) < len(headers):
                row.append('')

            row_dict = {}
            for i, header in enumerate(headers):
                # Clean header name
                clean_header = header.strip().replace(' ', '_').replace('-', '_').lower()
                row_dict[clean_header] = row[i] if i < len(row) else ''

            data.append(row_dict)

        return data

    except Exception as e:
        raise Exception(f"Failed to fetch data from sheet '{sheet_name}': {str(e)}")

def load_sheet_to_dataframe(sheet_name: str) -> pd.DataFrame:
    """Load a specific sheet and convert to DataFrame with proper data types."""
    try:
        logger.info(f"Loading data from sheet: {sheet_name}")

        # Fetch raw data from Google Sheets
        raw_data = get_sheet_data(sheet_name)

        if not raw_data:
            logger.warning(f"No data found in sheet: {sheet_name}")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(raw_data)

        # Apply data type conversions
        df = _apply_data_types(df, sheet_name)

        logger.info(f"Successfully loaded {len(df)} rows from {sheet_name}")
        return df

    except Exception as e:
        logger.error(f"Failed to load sheet {sheet_name}: {str(e)}")
        raise

def _apply_data_types(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """Konversi cerdas: Teks tetap teks, Angka tetap angka, Persen tetap tampil."""
    if df.empty: return df
    
    num_cols = ['tepat_waktu', 'terlambat', 'tidak_hadir', 'total', 'score']
    
    for col in df.columns:
        col_lower = col.lower()
        # 1. Jika kolom Persentase, biarkan string agar % tidak hilang
        if 'persentase' in col_lower or '%' in col:
            df[col] = df[col].astype(str).str.strip()
        # 2. Jika kolom Angka Murni
        elif any(n in col_lower for n in num_cols):
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        # 3. Sisanya String (Teks biasa)
        else:
            df[col] = df[col].astype(str).str.strip().replace('nan', '')
    return df

def load_all_data() -> Dict[str, pd.DataFrame]:
    """Load all configured sheets from Google Sheets."""
    try:
        logger.info("Starting to load all data from Google Sheets")

        # Load each sheet
        dataframes = {}
        for sheet_name in SHEET_NAMES:
            try:
                df = load_sheet_to_dataframe(sheet_name)
                if not df.empty:
                    dataframes[sheet_name] = df
                    logger.info(f"Loaded sheet: {sheet_name} with {len(df)} rows")
                else:
                    logger.warning(f"Sheet {sheet_name} is empty, skipping")
            except Exception as e:
                logger.error(f"Failed to load sheet {sheet_name}: {str(e)}")
                # Continue with other sheets
                continue

        logger.info(f"Successfully loaded {len(dataframes)} sheets")
        return dataframes

    except Exception as e:
        logger.error(f"Failed to load all data: {str(e)}")
        raise

def clean_google_sheets_errors(df: pd.DataFrame) -> pd.DataFrame:
    """Clean common Google Sheets errors and invalid values."""
    df_clean = df.copy()

    for col in df_clean.columns:
        df_clean[col] = df_clean[col].astype(str)

        # Replace error patterns with NaN
        for error_pattern in ERROR_PATTERNS:
            df_clean[col] = df_clean[col].str.replace(re.escape(error_pattern), '', regex=True)

        # Clean up empty strings and whitespace
        df_clean[col] = df_clean[col].str.strip()
        df_clean[col] = df_clean[col].replace('', np.nan)
        df_clean[col] = df_clean[col].replace('nan', np.nan)
        df_clean[col] = df_clean[col].replace('NaN', np.nan)

    logger.info("Cleaned Google Sheets errors")
    return df_clean

def clean_attendance_data(df: pd.DataFrame) -> pd.DataFrame:
    """Hanya merapikan teks, tanpa mengubah jadi boolean/checklist."""
    df_clean = df.copy()
    attendance_cols = [col for col in df_clean.columns if 'status' in col.lower() or 'hadir' in col.lower()]
    for col in attendance_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    return df_clean

def clean_master_data(df: pd.DataFrame) -> pd.DataFrame:
    """Specialized cleaning for master/student data."""
    df_clean = df.copy()

    # Clean name columns
    name_cols = [col for col in df_clean.columns if 'nama' in col.lower() or 'name' in col.lower()]

    for col in name_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.title()

    # Clean class/rombel columns
    class_cols = [col for col in df_clean.columns if 'rombel' in col.lower() or 'kelas' in col.lower() or 'class' in col.lower()]

    for col in class_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()

    # Clean numeric fields (age, etc.)
    numeric_cols = [col for col in df_clean.columns if 'umur' in col.lower() or 'age' in col.lower()]

    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    logger.info("Cleaned master data")
    return df_clean

def clean_score_data(df: pd.DataFrame) -> pd.DataFrame:
    """Specialized cleaning for score/nilai data."""
    df_clean = df.copy()

    # Identify score columns
    score_cols = [col for col in df_clean.columns if 'nilai' in col.lower() or 'score' in col.lower() or 'skor' in col.lower()]

    for col in score_cols:
        # Clean numeric values
        df_clean[col] = df_clean[col].astype(str).str.replace(',', '.').str.replace(' ', '')
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        # Validate score ranges (assuming 0-100 scale)
        df_clean[col] = df_clean[col].clip(0, 100)

    logger.info(f"Cleaned score data for {len(score_cols)} columns")
    return df_clean

def handle_missing_values(df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
    """Mencegah kolom penting seperti 'Catatan' dihapus otomatis."""
    df_clean = df.copy()
    # List kolom yang HARUS tetap ada meski banyak kosong
    protected_cols = ['catatan', 'keterangan', 'asal_sekolah', 'nama_siswa']
    
    for col in df_clean.columns:
        if any(p in col.lower() for p in protected_cols):
            df_clean[col] = df_clean[col].fillna('') # Isi kosong dengan string kosong saja
            continue
            
        missing_count = df_clean[col].isnull().sum()
        if missing_count / len(df_clean) > 0.8: # Longgarkan threshold jadi 80%
            df_clean = df_clean.drop(columns=[col])
    return df_clean

def clean_all_data(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Apply comprehensive cleaning to all DataFrames."""
    cleaned_data = {}

    for sheet_name, df in dataframes.items():
        logger.info(f"Cleaning data for sheet: {sheet_name}")

        # Start with Google Sheets error cleaning
        df_clean = clean_google_sheets_errors(df)

        # Apply sheet-specific cleaning
        sheet_lower = sheet_name.lower()
        if 'absensi' in sheet_lower or 'attendance' in sheet_lower:
            df_clean = clean_attendance_data(df_clean)
        elif 'master' in sheet_lower:
            df_clean = clean_master_data(df_clean)
        elif 'nilai' in sheet_lower or 'score' in sheet_lower:
            df_clean = clean_score_data(df_clean)

        # Handle missing values
        df_clean = handle_missing_values(df_clean)

        # Remove completely empty rows
        df_clean = df_clean.dropna(how='all')

        cleaned_data[sheet_name] = df_clean
        logger.info(f"Cleaned {sheet_name}: {len(df)} -> {len(df_clean)} rows")

    try:
        sheets_saw = calculate_sheets_saw_kmeans(cleaned_data)
        cleaned_data["DATA_SAW_RANKING"] = sheets_saw
    except Exception as e:
        logger.error(f"Failed to calculate Sheets SAW ranking: {str(e)}")

    return cleaned_data

def get_data_quality_report(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generate data quality report."""
    report = {
        'overall_quality': {},
        'sheet_reports': {}
    }

    total_rows = 0
    total_missing = 0

    for sheet_name, df in dataframes.items():
        sheet_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 0,
            'duplicate_rows': df.duplicated().sum()
        }

        report['sheet_reports'][sheet_name] = sheet_report
        total_rows += len(df)
        total_missing += df.isnull().sum().sum()

    report['overall_quality'] = {
        'total_sheets': len(dataframes),
        'total_rows': total_rows,
        'total_missing_values': total_missing,
        'overall_missing_percentage': (total_missing / (total_rows * sum(len(df.columns) for df in dataframes.values()))) * 100 if total_rows > 0 else 0
    }

    return report

def get_data_summary(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generate summary statistics for loaded data."""
    summary = {
        'total_sheets': len(dataframes),
        'sheet_summaries': {}
    }

    for sheet_name, df in dataframes.items():
        summary['sheet_summaries'][sheet_name] = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'data_types': df.dtypes.astype(str).to_dict()
        }

    return summary

def test_connection() -> bool:
    """Test connection to Google Sheets API."""
    try:
        client = authenticate_google_sheets()
        _open_spreadsheet(client)
        return True
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

def generate_mock_mariadb_data() -> Dict[str, pd.DataFrame]:
    """Menghasilkan mock data realistis untuk Siswa, Akademik, Absensi, dan Hubungannya."""
    siswa_df = pd.DataFrame([
        {"id_siswa": 1, "nis": "2601001", "nomor_induk": "2601001", "nama_lengkap": "Medina Novi Mareta", "status_siswa": "Aktif", "status_pendaftaran": "Siswa Lama"},
        {"id_siswa": 2, "nis": "2601002", "nomor_induk": "2601002", "nama_lengkap": "Nuzula Naura Dhuha", "status_siswa": "Aktif", "status_pendaftaran": "Siswa Baru"},
        {"id_siswa": 3, "nis": "2601003", "nomor_induk": "2601003", "nama_lengkap": "Yasuke Natalio", "status_siswa": "Aktif", "status_pendaftaran": "Siswa Lama"},
        {"id_siswa": 4, "nis": "2601004", "nomor_induk": "2601004", "nama_lengkap": "Dava Valecio Santoso", "status_siswa": "Keluar", "status_pendaftaran": ""}
    ])
    
    kursus_siswa_df = pd.DataFrame([
        {"id_siswa": 1, "nama_kursus": "Bahasa Inggris", "status_keaktifan": "Aktif", "status_kelulusan": "Belum Lulus", "status_aktif": 1, "status_lulus": 0},
        {"id_siswa": 2, "nama_kursus": "Bahasa Inggris", "status_keaktifan": "Aktif", "status_kelulusan": "Belum Lulus", "status_aktif": 1, "status_lulus": 0},
        {"id_siswa": 3, "nama_kursus": "Digital/Komputer", "status_keaktifan": "Aktif", "status_kelulusan": "Lulus", "status_aktif": 1, "status_lulus": 1},
        {"id_siswa": 4, "nama_kursus": "Komputer", "status_keaktifan": "Non-Aktif", "status_kelulusan": "Belum Lulus", "status_aktif": 0, "status_lulus": 0}
    ])

    jadwal_siswa_df = pd.DataFrame([
        {"id_siswa": 1, "rombel": "01 GOGO 1 SK1", "id_jadwal": 1, "status_keluar": 0, "is_acc_rapor": 1, "status_ketuntasan": "Tuntas"},
        {"id_siswa": 2, "rombel": "01 GOGO 1 SK1", "id_jadwal": 1, "status_keluar": 0, "is_acc_rapor": 0, "status_ketuntasan": "Belum Tuntas"},
        {"id_siswa": 3, "rombel": "02 GOGO 1 SK2", "id_jadwal": 2, "status_keluar": 0, "is_acc_rapor": 1, "status_ketuntasan": "Tuntas"},
        {"id_siswa": 4, "rombel": "Ing-02 GOGO 1 SK2", "id_jadwal": 2, "status_keluar": 1, "is_acc_rapor": 0, "status_ketuntasan": "Belum Tuntas"}
    ])

    catatan_siswa_df = pd.DataFrame([
        {"id_siswa": 2, "catatan": "Siswa kesulitan memahami materi listening.", "catatan_cs": "Siswa kesulitan memahami materi listening.", "status_followup": "NEED FURTHER OBSERVATION"},
        {"id_siswa": 4, "catatan": "Siswa sering bolos karena tabrakan jadwal les bola.", "catatan_cs": "Siswa sering bolos karena tabrakan jadwal les bola.", "status_followup": "CASE CLOSED"}
    ])

    catatan_remidi_siswa_df = pd.DataFrame([
        {"id_siswa": 2, "nilai_sebelum": 55, "nilai_sesudah": 70, "persetujuan_guru": "Approved"}
    ])

    web_statistik_df = pd.DataFrame([
        {"id_web_statistik": 1, "ip_address": "192.168.1.10", "page_views": 4, "visitor_session": "sess_01", "created_at": "2026-06-14 08:00:00"},
        {"id_web_statistik": 2, "ip_address": "192.168.1.15", "page_views": 10, "visitor_session": "sess_02", "created_at": "2026-06-14 08:15:00"}
    ])

    users_df = pd.DataFrame([
        {"id_user": 1, "username": "admin1", "nama_karyawan": "Admin One", "email": "admin1@leap.com"},
        {"id_user": 2, "username": "guru1", "nama_karyawan": "Guru One", "email": "guru1@leap.com"}
    ])

    divisions_df = pd.DataFrame([
        {"id_divisi": 1, "nama_divisi": "Akademik"},
        {"id_divisi": 2, "nama_divisi": "FO"}
    ])

    division_user_df = pd.DataFrame([
        {"id_division_user": 1, "id_user": 1, "id_divisi": 1, "id_role": 1},
        {"id_division_user": 2, "id_user": 2, "id_divisi": 2, "id_role": 2}
    ])

    kursus_df = pd.DataFrame([
        {"id_kursus": 1, "nama_kursus": "Coding Class"},
        {"id_kursus": 2, "nama_kursus": "English Program"}
    ])

    kursus_level_df = pd.DataFrame([
        {"id_kursus_level": 1, "id_kursus": 1, "nama_level": "Basic"},
        {"id_kursus_level": 2, "id_kursus": 2, "nama_level": "Gogo 1"}
    ])

    rapor_level_config_df = pd.DataFrame([
        {"id_rapor_level_config": 1, "id_kursus_level": 1, "format_penilaian": "Format A"},
        {"id_rapor_level_config": 2, "id_kursus_level": 2, "format_penilaian": "Format B"}
    ])

    jadwal_df = pd.DataFrame([
        {"id_jadwal": 1, "id_kursus": 1, "id_level": 1, "nama_kelas": "Coding Level 1", "periode": "Batch 1"},
        {"id_jadwal": 2, "id_kursus": 2, "id_level": 2, "nama_kelas": "English Gogo 1", "periode": "Batch 1"}
    ])

    jadwal_hari_df = pd.DataFrame([
        {"id_jadwal_hari": 1, "id_jadwal": 1, "hari": "Senin"},
        {"id_jadwal_hari": 2, "id_jadwal": 2, "hari": "Rabu"}
    ])

    jadwal_detail_df = pd.DataFrame([
        {"id_jadwal_detail": 1, "id_jadwal": 1, "tanggal": "2026-06-15", "zoom_link": "https://zoom.us/j/123", "status_pengerjaan": "Selesai"},
        {"id_jadwal_detail": 2, "id_jadwal": 2, "tanggal": "2026-06-17", "zoom_link": "https://zoom.us/j/456", "status_pengerjaan": "Selesai"}
    ])

    calon_siswa_df = pd.DataFrame([
        {"id_calon": 1, "kode_unik": "CS001", "nama_lengkap": "Budi Santoso", "id_provinsi": 1, "id_kabupaten": 1, "id_kecamatan": 1, "id_kelurahan": 1, "asal_sekolah": "SDN 1 Surabaya", "fo_status": "Lengkap", "created_at": "2026-06-01 10:00:00"},
        {"id_calon": 2, "kode_unik": "CS002", "nama_lengkap": "Siti Aminah", "id_provinsi": 1, "id_kabupaten": 2, "id_kecamatan": 2, "id_kelurahan": 2, "asal_sekolah": "SMPN 1 Sidoarjo", "fo_status": "Belum Lengkap", "created_at": "2026-06-02 11:00:00"}
    ])

    calon_siswa_akademik_df = pd.DataFrame([
        {"id_calon_akademik": 1, "id_calon": 1, "nama_sekolah": "SDN 1 Surabaya", "id_kursus": 1, "id_level": 1, "submission_state": "submitted", "sumber_info": "Instagram", "referensi": "Teman"},
        {"id_calon_akademik": 2, "id_calon": 2, "nama_sekolah": "SMPN 1 Sidoarjo", "id_kursus": 2, "id_level": 2, "submission_state": "submitted", "sumber_info": "Website", "referensi": "Instagram"}
    ])

    calon_siswa_bayar_df = pd.DataFrame([
        {"id_calon_bayar": 1, "id_calon_akademik": 1, "nomor_invoice": "INV/001", "bank_pembayaran": "BCA", "tanggal_konfirmasi_bayar": "2026-06-05 09:00:00", "jumlah_bayar": 500000.0},
        {"id_calon_bayar": 2, "id_calon_akademik": 2, "nomor_invoice": "INV/002", "bank_pembayaran": "Mandiri", "tanggal_konfirmasi_bayar": "2026-06-06 10:00:00", "jumlah_bayar": 250000.0}
    ])

    calon_siswa_ortu_df = pd.DataFrame([
        {"id_calon_ortu": 1, "id_calon": 1, "nama_ayah": "Bambang", "pekerjaan_ayah": "Swasta", "penghasilan_ayah": "3jt_5jt", "nama_ibu": "Siti", "pekerjaan_ibu": "IRT", "penghasilan_ibu": "kurang_1jt"},
        {"id_calon_ortu": 2, "id_calon": 2, "nama_ayah": "Joko", "pekerjaan_ayah": "PNS", "penghasilan_ayah": "lebih_5jt", "nama_ibu": "Ani", "pekerjaan_ibu": "Swasta", "penghasilan_ibu": "1jt_3jt"}
    ])

    calon_siswa_fo_detail_df = pd.DataFrame([
        {"id": 1, "id_calon": 1, "nama_lengkap": "Budi Santoso", "pilihan_program_snapshot": "[]", "catatan_awal_fo": "Tertarik dengan Coding Class"},
        {"id": 2, "id_calon": 2, "nama_lengkap": "Siti Aminah", "pilihan_program_snapshot": "[]", "catatan_awal_fo": "Masih mempertimbangkan jadwal"}
    ])

    catatan_kelas_df = pd.DataFrame([
        {"id_ck": 1, "id_jadwal": 1, "id_jadwal_detail": 1, "id_karyawan": 2, "catatan_kelas": "Introduction to Python", "topik_diskusi": "Variables and Types"}
    ])

    absensi_df = pd.DataFrame([
        {"id_absensi": 1, "id_karyawan": 2, "tanggal": "2026-06-15", "jam_masuk": "08:00:00", "jam_keluar": "17:00:00", "status_absensi": "Tepat Waktu", "tipe_absensi": "Fingerprint", "id_izin": None},
        {"id_absensi": 2, "id_karyawan": 3, "tanggal": "2026-06-15", "jam_masuk": "08:15:00", "jam_keluar": "17:00:00", "status_absensi": "Terlambat", "tipe_absensi": "Fingerprint", "id_izin": None}
    ])

    izin_karyawan_df = pd.DataFrame([
        {"id_izin": 1, "id_karyawan": 2, "jenis_izin": "Sakit", "tanggal_mulai": "2026-06-10", "tanggal_selesai": "2026-06-11", "keterangan_izin": "Sakit demam"}
    ])

    verifikasi_izin_df = pd.DataFrame([
        {"id_verifikasi_izin": 1, "id_izin": 1, "status_verifikasi_izin": "Approved", "catatan_verifikator": "Verified"}
    ])

    mock_data = {
        "siswa": siswa_df,
        "kursus_siswa": kursus_siswa_df,
        "jadwal_siswa": jadwal_siswa_df,
        "catatan_siswa": catatan_siswa_df,
        "catatan_remidi_siswa": catatan_remidi_siswa_df,
        "web_statistik": web_statistik_df,
        "users": users_df,
        "divisions": divisions_df,
        "division_user": division_user_df,
        "kursus": kursus_df,
        "kursus_level": kursus_level_df,
        "rapor_level_config": rapor_level_config_df,
        "jadwal": jadwal_df,
        "jadwal_hari": jadwal_hari_df,
        "jadwal_detail": jadwal_detail_df,
        "calon_siswa": calon_siswa_df,
        "calon_siswa_akademik": calon_siswa_akademik_df,
        "calon_siswa_bayar": calon_siswa_bayar_df,
        "calon_siswa_ortu": calon_siswa_ortu_df,
        "calon_siswa_fo_detail": calon_siswa_fo_detail_df,
        "catatan_kelas": catatan_kelas_df,
        "absensi": absensi_df,
        "izin_karyawan": izin_karyawan_df,
        "verifikasi_izin": verifikasi_izin_df
    }

    try:
        mock_data["DB_SAW_LEADS"] = calculate_db_saw_kmeans(mock_data)
        mock_data["UNIFIED_SAW"] = calculate_unified_saw_kmeans(mock_data, mock_data)
    except Exception as e:
        logger.error(f"Failed to calculate Mock DB SAW: {str(e)}")

    return mock_data

def load_mariadb_data() -> Dict[str, pd.DataFrame]:
    """Membaca data dari MariaDB atau fallback ke Mock jika gagal."""
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
                tables = [
                    "siswa", "kursus_siswa", "jadwal_siswa", "catatan_siswa", "catatan_remidi_siswa", "web_statistik",
                    "users", "divisions", "division_user", "kursus", "kursus_level", "rapor_level_config", "jadwal",
                    "jadwal_hari", "jadwal_detail", "calon_siswa", "calon_siswa_akademik", "calon_siswa_bayar",
                    "calon_siswa_ortu", "calon_siswa_fo_detail", "catatan_kelas", "absensi", "izin_karyawan", "verifikasi_izin"
                ]
                
                result = {}
                for table in tables:
                    cursor.execute(f"SELECT * FROM `{table}`")
                    result[table] = pd.DataFrame(cursor.fetchall())

                if result["siswa"].empty:
                    logger.warning("Database connected but 'siswa' table is empty. Falling back to mock data engine.")
                    return generate_mock_mariadb_data()

                try:
                    result["DB_SAW_LEADS"] = calculate_db_saw_kmeans(result)
                    result["UNIFIED_SAW"] = calculate_unified_saw_kmeans(generate_mock_mariadb_data(), result)
                except Exception as e:
                    logger.error(f"Failed to calculate DB SAW: {str(e)}")

                return result
        finally:
            connection.close()
    except Exception as e:
        logger.warning(f"Database connection failed ({str(e)}). Falling back to mock data engine.")
        return generate_mock_mariadb_data()


def calculate_saw(df: pd.DataFrame, criteria: List[str], weights: Dict[str, float], types: Dict[str, str]) -> pd.DataFrame:
    # Validate criteria configuration
    for c in criteria:
        if c not in types:
            raise ValueError(f"Criterion '{c}' must be specified in the 'types' configuration.")
        if c not in weights:
            raise ValueError(f"Criterion '{c}' must be specified in the 'weights' configuration.")

    if df.empty:
        df_copy = df.copy()
        df_copy["saw_score"] = 0.0
        df_copy["saw_rank"] = 0
        return df_copy
        
    df_copy = df.copy()
    norm_matrix = pd.DataFrame(index=df.index)
    
    for c in criteria:
        if c not in df_copy.columns:
            df_copy[c] = 0.0
            
        series = pd.to_numeric(df_copy[c], errors="coerce").fillna(0.0)
        max_val = series.max()
        min_val = series.min()
        
        c_type = types.get(c, "benefit")
        if c_type == "benefit":
            if max_val > 0:
                norm_matrix[c] = series / max_val
            else:
                norm_matrix[c] = 0.0
        elif c_type == "cost":
            norm_matrix[c] = (min_val + 1.0) / (series + 1.0)
        else:
            raise ValueError(f"Unknown criterion type '{c_type}' for '{c}'. Must be 'benefit' or 'cost'.")
            
    saw_score = np.zeros(len(df_copy))
    for c in criteria:
        saw_score += norm_matrix[c].values * weights.get(c, 0.0)
        
    df_copy["saw_score"] = saw_score
    df_copy["saw_rank"] = df_copy["saw_score"].rank(ascending=False, method="min").astype(int)
    return df_copy

def apply_kmeans_risk(df: pd.DataFrame, features: List[str], n_clusters: int = 3) -> pd.DataFrame:
    """
    Applies K-Means clustering to rank risks.
    
    This function depends on the 'saw_score' column for sorting cluster risk levels
    (where cluster 0 is High Risk / lowest mean SAW score, and cluster n_clusters-1 is Low Risk / highest mean SAW).
    If 'saw_score' is not present in the input DataFrame, the first feature in the features list
    will be used as a proxy for sorting risk, and the temporary 'saw_score' column will be dropped before returning.
    """
    if df.empty:
        df_copy = df.copy()
        df_copy["risk_cluster"] = 0
        return df_copy
        
    df_copy = df.copy()
    n_samples = len(df_copy)
    
    # Graceful fallback/safety check for 'saw_score' dependency
    has_saw_score = "saw_score" in df_copy.columns
    if not has_saw_score:
        if features:
            df_copy["saw_score"] = pd.to_numeric(df_copy[features[0]], errors="coerce").fillna(0.0)
        else:
            df_copy["saw_score"] = 0.0
            
    if n_samples < n_clusters:
        sorted_indices = df_copy["saw_score"].argsort()
        clusters = np.zeros(n_samples, dtype=int)
        for rank, idx in enumerate(sorted_indices):
            if n_samples == 1:
                clusters[idx] = (n_clusters - 1) // 2
            else:
                clusters[idx] = int(rank * (n_clusters - 1) / (n_samples - 1))
        df_copy["risk_cluster"] = clusters
        
        if not has_saw_score:
            df_copy = df_copy.drop(columns=["saw_score"])
        return df_copy
        
    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        X = df_copy[features].fillna(0.0)
        cluster_labels = kmeans.fit_predict(X)
        df_copy["risk_cluster"] = cluster_labels
        
        cluster_means = df_copy.groupby("risk_cluster")["saw_score"].mean().sort_values()
        mapping = {old: new for new, old in enumerate(cluster_means.index)}
        df_copy["risk_cluster"] = df_copy["risk_cluster"].map(mapping)
    except Exception as e:
        logger.warning(f"K-Means clustering failed ({str(e)}). Falling back to ranks.")
        sorted_ranks = df_copy["saw_score"].rank(ascending=True, method="first")
        percentiles = sorted_ranks / len(df_copy)
        df_copy["risk_cluster"] = np.where(percentiles <= 0.33, 0, np.where(percentiles <= 0.66, 1, 2))
        
    if not has_saw_score:
        df_copy = df_copy.drop(columns=["saw_score"])
        
    return df_copy


def calculate_sheets_saw_kmeans(cleaned_sheets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculates SAW and clusters active students from Sheets data."""
    siswa_df = cleaned_sheets.get("DATA_SISWA", pd.DataFrame())
    if siswa_df.empty and "siswa" in cleaned_sheets:
        db_siswa = cleaned_sheets["siswa"].copy()
        if "nama_lengkap" in db_siswa.columns:
            db_siswa.rename(columns={"nama_lengkap": "nama_siswa"}, inplace=True)
        siswa_df = db_siswa
        
    nilai_df = cleaned_sheets.get("DATA_NILAI", pd.DataFrame())
    if nilai_df.empty and "catatan_remidi_siswa" in cleaned_sheets:
        db_remidi = cleaned_sheets["catatan_remidi_siswa"].copy()
        if "nilai_sesudah" in db_remidi.columns:
            db_remidi["score"] = db_remidi["nilai_sesudah"]
        if "siswa" in cleaned_sheets and "nama_siswa" not in db_remidi.columns:
            db_siswa = cleaned_sheets["siswa"].copy()
            if "nama_lengkap" in db_siswa.columns:
                db_siswa.rename(columns={"nama_lengkap": "nama_siswa"}, inplace=True)
            db_remidi = db_remidi.merge(db_siswa[["id_siswa", "nama_siswa"]], on="id_siswa", how="left")
        nilai_df = db_remidi
        
    absensi_df = cleaned_sheets.get("DATA_ABSENSI", pd.DataFrame())
    if absensi_df.empty and "absensi" in cleaned_sheets:
        db_abs = cleaned_sheets["absensi"].copy()
        if "status_absensi" in db_abs.columns:
            db_abs.rename(columns={"status_absensi": "status"}, inplace=True)
        if "users" in cleaned_sheets and "nama_siswa" not in db_abs.columns:
            db_users = cleaned_sheets["users"].copy()
            if "nama_karyawan" in db_users.columns:
                db_users.rename(columns={"nama_karyawan": "nama_siswa"}, inplace=True)
            db_abs = db_abs.merge(db_users[["id_user", "nama_siswa"]], left_on="id_karyawan", right_on="id_user", how="left")
        absensi_df = db_abs
        
    if siswa_df.empty:
        return pd.DataFrame(columns=["nama_siswa", "saw_score", "saw_rank", "risk_cluster"])
        
    # Standardize names
    df = pd.DataFrame({"nama_siswa": siswa_df["nama_siswa"].unique()})
    
    # Feature 1: Average Score
    if not nilai_df.empty and "nama_siswa" in nilai_df.columns and "score" in nilai_df.columns:
        avg_scores = nilai_df.groupby("nama_siswa")["score"].mean().reset_index()
        df = df.merge(avg_scores, on="nama_siswa", how="left")
    else:
        df["score"] = 70.0
    df["score"] = df["score"].fillna(70.0)
    
    # Feature 2 & 4: Attendance Rate & Tardiness
    if not absensi_df.empty and "nama_siswa" in absensi_df.columns:
        absensi_df_copy = absensi_df.copy()
        absensi_df_copy["status_lower"] = absensi_df_copy["status"].astype(str).str.lower().str.strip()
        absensi_df_copy["hadir_num"] = absensi_df_copy["status_lower"].isin(["tepat waktu", "terlambat", "hadir"]).astype(int)
        absensi_df_copy["late_num"] = absensi_df_copy["status_lower"].str.contains("lambat").astype(int)
        
        att_rate = absensi_df_copy.groupby("nama_siswa")["hadir_num"].mean().reset_index()
        att_rate["hadir_num"] = att_rate["hadir_num"] * 100
        att_rate.rename(columns={"hadir_num": "attendance_rate"}, inplace=True)
        
        late_count = absensi_df_copy.groupby("nama_siswa")["late_num"].sum().reset_index()
        late_count.rename(columns={"late_num": "late_count"}, inplace=True)
        
        df = df.merge(att_rate, on="nama_siswa", how="left")
        df = df.merge(late_count, on="nama_siswa", how="left")
    else:
        df["attendance_rate"] = 90.0
        df["late_count"] = 0.0
    df["attendance_rate"] = df["attendance_rate"].fillna(90.0)
    df["late_count"] = df["late_count"].fillna(0.0)
    
    # Feature 3: Passing Rate (Exams > 70)
    if not nilai_df.empty and "nama_siswa" in nilai_df.columns and "score" in nilai_df.columns:
        nilai_df_copy = nilai_df.copy()
        nilai_df_copy["is_tuntas"] = (nilai_df_copy["score"] > 70).astype(int)
        tuntas_rate = nilai_df_copy.groupby("nama_siswa")["is_tuntas"].mean().reset_index()
        tuntas_rate.rename(columns={"is_tuntas": "passing_rate"}, inplace=True)
        df = df.merge(tuntas_rate, on="nama_siswa", how="left")
    else:
        df["passing_rate"] = 1.0
    df["passing_rate"] = df["passing_rate"].fillna(1.0)
    
    # Execute SAW (Academic settings)
    criteria = ["score", "attendance_rate", "passing_rate", "late_count"]
    weights = {"score": 0.40, "attendance_rate": 0.30, "passing_rate": 0.20, "late_count": 0.10}
    types = {"score": "benefit", "attendance_rate": "benefit", "passing_rate": "benefit", "late_count": "cost"}
    
    saw_df = calculate_saw(df, criteria, weights, types)
    return apply_kmeans_risk(saw_df, ["saw_score", "score", "attendance_rate"])

def calculate_db_saw_kmeans(db_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculates SAW and clusters prospective student leads from MariaDB."""
    calon_df = db_data.get("calon_siswa", pd.DataFrame())
    bayar_df = db_data.get("calon_siswa_bayar", pd.DataFrame())
    akad_df = db_data.get("calon_siswa_akademik", pd.DataFrame())
    
    if calon_df.empty:
        return pd.DataFrame(columns=["nama_lengkap", "saw_score", "saw_rank", "risk_cluster"])
        
    df = calon_df[["id_calon", "nama_lengkap", "fo_status"]].copy()
    df["is_fo_lengkap"] = (df["fo_status"] == "Lengkap").astype(int)
    
    # Amount Paid
    if not bayar_df.empty and not akad_df.empty:
        leads_payment = akad_df.merge(bayar_df, on="id_calon_akademik", how="inner")
        payment_sum = leads_payment.groupby("id_calon")["jumlah_bayar"].sum().reset_index()
        df = df.merge(payment_sum, on="id_calon", how="left")
    else:
        df["jumlah_bayar"] = 0.0
    df["jumlah_bayar"] = df["jumlah_bayar"].fillna(0.0)
    
    # FO comment length (Interest intensity proxy)
    fo_detail = db_data.get("calon_siswa_fo_detail", pd.DataFrame())
    if not fo_detail.empty and "catatan_awal_fo" in fo_detail.columns:
        fo_detail_copy = fo_detail.copy()
        fo_detail_copy["notes_len"] = fo_detail_copy["catatan_awal_fo"].astype(str).str.len()
        comment_len = fo_detail_copy.groupby("id_calon")["notes_len"].max().reset_index()
        df = df.merge(comment_len, on="id_calon", how="left")
    else:
        df["notes_len"] = 0.0
    df["notes_len"] = df["notes_len"].fillna(0.0)
    
    # Speed to confirm payment (days)
    df["days_to_pay"] = 30.0  # Default slow conversion penalty
    if not bayar_df.empty and not akad_df.empty:
        leads_payment = akad_df.merge(bayar_df, on="id_calon_akademik", how="inner")
        leads_payment = leads_payment.merge(calon_df, on="id_calon", how="inner")
        
        if "created_at" in leads_payment.columns and "tanggal_konfirmasi_bayar" in leads_payment.columns:
            leads_payment["created_dt"] = pd.to_datetime(leads_payment["created_at"], errors="coerce")
            leads_payment["pay_dt"] = pd.to_datetime(leads_payment["tanggal_konfirmasi_bayar"], errors="coerce")
            
            leads_payment["speed"] = (leads_payment["pay_dt"] - leads_payment["created_dt"]).dt.total_seconds() / (24 * 3600)
            leads_payment["speed"] = leads_payment["speed"].clip(0, 90).fillna(30.0)
            
            speed_df = leads_payment.groupby("id_calon")["speed"].min().reset_index()
            speed_df.rename(columns={"speed": "days_to_pay"}, inplace=True)
            
            # Drop temporary default
            df.drop(columns=["days_to_pay"], inplace=True)
            df = df.merge(speed_df, on="id_calon", how="left")
        
    df["days_to_pay"] = df["days_to_pay"].fillna(30.0)
    
    # Run SAW
    criteria = ["jumlah_bayar", "is_fo_lengkap", "notes_len", "days_to_pay"]
    weights = {"jumlah_bayar": 0.40, "is_fo_lengkap": 0.30, "notes_len": 0.10, "days_to_pay": 0.20}
    types = {"jumlah_bayar": "benefit", "is_fo_lengkap": "benefit", "notes_len": "benefit", "days_to_pay": "cost"}
    
    saw_df = calculate_saw(df, criteria, weights, types)
    return apply_kmeans_risk(saw_df, ["saw_score", "jumlah_bayar", "is_fo_lengkap"])

def calculate_unified_saw_kmeans(cleaned_sheets: Dict[str, pd.DataFrame], db_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculates Unified SAW and clusters students combining Sheets Academics & SQL CS records."""
    sheets_siswa = calculate_sheets_saw_kmeans(cleaned_sheets)
    db_siswa = db_data.get("siswa", pd.DataFrame())
    catatan_cs = db_data.get("catatan_siswa", pd.DataFrame())
    
    if sheets_siswa.empty:
        return pd.DataFrame(columns=["nama_siswa", "saw_score", "saw_rank", "risk_cluster"])
        
    df = sheets_siswa[["nama_siswa", "score", "attendance_rate"]].copy()
    df.rename(columns={"score": "academic_score"}, inplace=True)
    
    # Map Names to Database IDs
    if not db_siswa.empty and "nama_lengkap" in db_siswa.columns:
        # Simple name normalization mapping
        db_siswa_copy = db_siswa.copy()
        db_siswa_copy["clean_name"] = db_siswa_copy["nama_lengkap"].astype(str).str.lower().str.strip()
        df["clean_name"] = df["nama_siswa"].astype(str).str.lower().str.strip()
        
        df = df.merge(db_siswa_copy[["id_siswa", "clean_name"]], on="clean_name", how="left")
        df.drop(columns=["clean_name"], inplace=True)
    else:
        df["id_siswa"] = np.nan
        
    if not catatan_cs.empty and "id_siswa" in catatan_cs.columns:
        catatan_cs_copy = catatan_cs.copy()
        catatan_cs_copy["is_critical"] = (catatan_cs_copy["status_followup"] == "NEED FURTHER OBSERVATION").astype(int)
        
        crit = catatan_cs_copy.groupby("id_siswa")["is_critical"].max().reset_index()
        crit.rename(columns={"is_critical": "has_critical_notes"}, inplace=True)
        
        total = catatan_cs_copy.groupby("id_siswa")["is_critical"].count().reset_index()
        total.rename(columns={"is_critical": "total_notes"}, inplace=True)
        
        df = df.merge(crit, on="id_siswa", how="left")
        df = df.merge(total, on="id_siswa", how="left")
        
        df["has_critical_notes"] = df["has_critical_notes"].fillna(0.0)
        df["total_notes"] = df["total_notes"].fillna(0.0)
    else:
        df["has_critical_notes"] = 0.0
        df["total_notes"] = 0.0
        
    # Run SAW
    criteria = ["academic_score", "attendance_rate", "has_critical_notes", "total_notes"]
    weights = {"academic_score": 0.40, "attendance_rate": 0.30, "has_critical_notes": 0.20, "total_notes": 0.10}
    types = {"academic_score": "benefit", "attendance_rate": "benefit", "has_critical_notes": "cost", "total_notes": "cost"}
    
    saw_df = calculate_saw(df, criteria, weights, types)
    return apply_kmeans_risk(saw_df, ["saw_score", "academic_score", "attendance_rate"])