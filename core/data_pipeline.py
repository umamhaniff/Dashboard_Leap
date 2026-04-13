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
from typing import Dict, List, Any, Optional
from config.settings import (
    SPREADSHEET_ID, SPREADSHEET_URL, SERVICE_ACCOUNT_PATH, SHEET_NAMES,
    ERROR_PATTERNS, DATA_TYPE_MAPPINGS
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_google_sheets() -> gspread.client.Client:
    """Authenticate with Google Sheets API using service account."""
    try:
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

        scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
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
    """Apply appropriate data types based on column patterns."""
    if df.empty:
        return df

    date_columns = DATA_TYPE_MAPPINGS['date_columns']
    numeric_columns = DATA_TYPE_MAPPINGS['numeric_columns']
    boolean_columns = DATA_TYPE_MAPPINGS['boolean_columns']

    for col in df.columns:
        col_lower = col.lower()

        # Convert date columns
        if any(date_pattern in col_lower for date_pattern in date_columns):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                logger.info(f"Converted column '{col}' to datetime")
            except Exception as e:
                logger.warning(f"Could not convert column '{col}' to datetime: {str(e)}")

        # Convert numeric columns
        elif any(num_pattern in col_lower for num_pattern in numeric_columns):
            try:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
                logger.info(f"Converted column '{col}' to numeric")
            except Exception as e:
                logger.warning(f"Could not convert column '{col}' to numeric: {str(e)}")

        # Convert boolean columns
        elif any(bool_pattern in col_lower for bool_pattern in boolean_columns):
            try:
                df[col] = df[col].astype(str).str.lower().str.strip()
                df[col] = df[col].replace({
                    'ya': True, 'yes': True, 'true': True, '1': True, 'hadir': True, 'present': True,
                    'tidak': False, 'no': False, 'false': False, '0': False, '': False, 'nan': False
                }).fillna(False)
                logger.info(f"Converted column '{col}' to boolean")
            except Exception as e:
                logger.warning(f"Could not convert column '{col}' to boolean: {str(e)}")

        # Default: keep as string but clean whitespace
        else:
            df[col] = df[col].astype(str).str.strip()

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
    """Specialized cleaning for attendance/absensi data."""
    df_clean = df.copy()

    # Standardize attendance status columns
    attendance_cols = [col for col in df_clean.columns if 'hadir' in col.lower() or 'absen' in col.lower() or 'status' in col.lower()]

    for col in attendance_cols:
        df_clean[col] = df_clean[col].astype(str).str.lower().str.strip()

        # Standardize attendance values
        df_clean[col] = df_clean[col].replace({
            'hadir': 'Hadir',
            'present': 'Hadir',
            'ya': 'Hadir',
            'y': 'Hadir',
            '1': 'Hadir',
            'true': 'Hadir',
            'absen': 'Tidak Hadir',
            'absent': 'Tidak Hadir',
            'tidak': 'Tidak Hadir',
            'no': 'Tidak Hadir',
            'n': 'Tidak Hadir',
            '0': 'Tidak Hadir',
            'false': 'Tidak Hadir',
            '': 'Tidak Hadir',
            'nan': 'Tidak Hadir'
        })

        # Convert to boolean for easier analysis
        df_clean[col] = df_clean[col].map({'Hadir': True, 'Tidak Hadir': False})

    logger.info(f"Cleaned attendance data for {len(attendance_cols)} columns")
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
    """Handle missing values based on column type and context."""
    df_clean = df.copy()

    for col in df_clean.columns:
        missing_count = df_clean[col].isnull().sum()
        if missing_count == 0:
            continue

        col_lower = col.lower()

        if strategy == 'drop':
            df_clean = df_clean.dropna(subset=[col])
        elif strategy == 'auto':
            # Auto strategy based on column type
            if any(keyword in col_lower for keyword in ['nama', 'name', 'rombel', 'kelas']):
                # For identifier columns, keep as is
                pass
            elif any(keyword in col_lower for keyword in ['nilai', 'score', 'skor']):
                # For scores, fill with mean
                if df_clean[col].dtype in ['int64', 'float64']:
                    df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
                else:
                    # Try to convert to numeric first
                    try:
                        numeric_series = pd.to_numeric(df_clean[col], errors='coerce')
                        if numeric_series.notna().any():
                            mean_val = numeric_series.mean()
                            df_clean[col] = numeric_series.fillna(mean_val)
                    except:
                        pass  # Keep original if conversion fails
            elif any(keyword in col_lower for keyword in ['hadir', 'absen', 'status']):
                # For attendance, assume not present
                df_clean[col] = df_clean[col].fillna(False)
            else:
                # For other columns, fill with mode or drop if too many missing
                if missing_count / len(df_clean) > 0.5:
                    df_clean = df_clean.drop(columns=[col])
                    logger.warning(f"Dropped column '{col}' due to >50% missing values")
                else:
                    # Fill with mode for categorical, mean for numeric
                    if df_clean[col].dtype == 'object':
                        mode_val = df_clean[col].mode()
                        if not mode_val.empty:
                            df_clean[col] = df_clean[col].fillna(mode_val.iloc[0])
                        elif df_clean[col].dtype in ['int64', 'float64']:
                            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
                        # Skip mean calculation for other dtypes to avoid errors

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