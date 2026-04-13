"""
LLM Security Analyzer for LEAP Dashboard.
Uses Google Generative AI (Gemini) to analyze data anomalies and security patterns.
"""

import google.generativeai as genai
import os
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import streamlit as st
import logging
from config.settings import SECURITY_ANALYSIS_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_api_key() -> str:
    """Get Gemini API key from Streamlit secrets or environment."""
    # Try Streamlit secrets first
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        return st.secrets['GEMINI_API_KEY']

    # Fallback to environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        return api_key

    raise ValueError("GEMINI_API_KEY not found in Streamlit secrets or environment variables")

def initialize_security_analyst() -> genai.GenerativeModel:
    """Initialize Gemini model with Security Analyst configuration."""
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)

        # Initialize with system instruction
        model = genai.GenerativeModel(
            'gemini-pro',
            system_instruction=SECURITY_ANALYSIS_CONFIG['system_instruction']
        )

        logger.info("Security Analyst LLM initialized successfully")
        return model

    except Exception as e:
        logger.error(f"Failed to initialize Security Analyst: {str(e)}")
        raise

def prepare_data_summary(dataframes: Dict[str, pd.DataFrame]) -> str:
    """Prepare a comprehensive data summary for LLM analysis."""
    summary_parts = []

    for sheet_name, df in dataframes.items():
        summary_parts.append(f"=== SHEET: {sheet_name} ===")
        summary_parts.append(f"Jumlah baris: {len(df)}")
        summary_parts.append(f"Kolom: {', '.join(df.columns.tolist())}")

        # Basic statistics
        if not df.empty:
            # Numeric columns stats
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary_parts.append("Statistik numerik:")
                for col in numeric_cols:
                    stats = df[col].describe()
                    summary_parts.append(f"  {col}: mean={stats.get('mean', 'N/A'):.2f}, "
                                       f"min={stats.get('min', 'N/A')}, max={stats.get('max', 'N/A')}")

            # Categorical insights
            if 'hadir' in df.columns:
                attendance_rate = df['hadir'].mean() * 100 if df['hadir'].dtype == bool else 0
                summary_parts.append(f"Tingkat kehadiran: {attendance_rate:.1f}%")

            if 'nilai' in df.columns:
                try:
                    if df['nilai'].dtype in ['int64', 'float64']:
                        avg_score = df['nilai'].mean()
                        summary_parts.append(f"Rata-rata nilai: {avg_score:.2f}")
                    else:
                        # Try to convert to numeric
                        numeric_nilai = pd.to_numeric(df['nilai'], errors='coerce')
                        if numeric_nilai.notna().any():
                            avg_score = numeric_nilai.mean()
                            summary_parts.append(f"Rata-rata nilai: {avg_score:.2f}")
                except:
                    pass  # Skip if calculation fails

        summary_parts.append("")  # Empty line between sheets

    return "\n".join(summary_parts)

def analyze_security(dataframes: Dict[str, pd.DataFrame]) -> str:
    """Main security analysis function using Gemini."""
    try:
        logger.info("Starting security analysis with Gemini")

        # Initialize model
        model = initialize_security_analyst()

        # Prepare data summary
        data_summary = prepare_data_summary(dataframes)

        # Create analysis prompt
        analysis_prompt = f"""
Berikut adalah ringkasan data dari sistem LKP LEAP:

{data_summary}

TUGAS ANALISIS KEAMANAN:
1. Analisis pola kehadiran siswa - identifikasi siswa dengan tren ketidakhadiran mencurigakan
2. Periksa konsistensi data antar sheet (master, absensi, nilai)
3. Deteksi anomali dalam performa akademik
4. Identifikasi potensi masalah integritas data
5. Berikan rekomendasi keamanan berdasarkan temuan

Fokus pada indikator keamanan seperti:
- Siswa yang tidak pernah hadir atau selalu hadir (mencurigakan)
- Nilai yang terlalu seragam atau berfluktuasi ekstrem
- Inkonsistensi nama/identitas siswa antar tabel
- Pola absensi yang tidak wajar per rombel/kelas
"""

        # Generate analysis
        response = model.generate_content(analysis_prompt)

        analysis_result = response.text.strip()
        logger.info("Security analysis completed successfully")

        return analysis_result

    except Exception as e:
        error_msg = f"Security analysis failed: {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"

def analyze_single_sheet(df: pd.DataFrame, sheet_name: str, focus_area: str = "general") -> str:
    """Analyze a single sheet for specific security concerns."""
    try:
        model = initialize_security_analyst()

        # Prepare sheet data preview (first 20 rows)
        data_preview = df.head(20).to_string()

        focus_prompts = {
            'attendance': "Fokus pada pola absensi mencurigakan, tingkat kehadiran ekstrem, dan tren ketidakhadiran.",
            'scores': "Fokus pada anomali nilai, fluktuasi performa yang tidak wajar, dan indikasi kecurangan.",
            'master': "Fokus pada konsistensi data master siswa, duplikasi, dan inkonsistensi identitas.",
            'general': "Berikan analisis keamanan umum untuk sheet ini."
        }

        prompt = f"""
Sheet: {sheet_name}
Fokus: {focus_prompts.get(focus_area, focus_prompts['general'])}

Data Preview (20 baris pertama):
{data_preview}

Analisis keamanan untuk sheet ini:
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"Analysis failed for {sheet_name}: {str(e)}"

def generate_security_recommendations(analysis_result: str) -> List[str]:
    """Extract actionable security recommendations from analysis."""
    try:
        model = initialize_security_analyst()

        prompt = f"""
Berdasarkan analisis keamanan berikut:

{analysis_result}

Ekstrak 5-7 rekomendasi keamanan yang paling penting dan actionable.
Format: Berikan dalam bentuk bullet points yang spesifik dan dapat diimplementasikan.
"""

        response = model.generate_content(prompt)
        recommendations_text = response.text.strip()

        # Split into list
        recommendations = [line.strip('- •').strip() for line in recommendations_text.split('\n') if line.strip() and not line.lower().startswith(('rekomendasi', 'saran'))]

        return recommendations[:7]  # Limit to 7 recommendations

    except Exception as e:
        return [f"Could not generate recommendations: {str(e)}"]

def validate_data_consistency(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Validate data consistency across sheets."""
    report = {
        'consistency_checks': [],
        'issues_found': 0,
        'recommendations': []
    }

    # Check if master data exists
    if 'DATA_MASTER' in dataframes:
        master_df = dataframes['DATA_MASTER']

        # Check attendance consistency
        if 'DATA_ABSENSI' in dataframes:
            attendance_df = dataframes['DATA_ABSENSI']

            # Find students in attendance but not in master
            if 'nama' in master_df.columns and 'nama' in attendance_df.columns:
                master_names = set(master_df['nama'].dropna().str.lower().str.strip())
                attendance_names = set(attendance_df['nama'].dropna().str.lower().str.strip())

                missing_in_master = attendance_names - master_names
                if missing_in_master:
                    report['consistency_checks'].append({
                        'type': 'missing_students',
                        'description': f"{len(missing_in_master)} siswa di absensi tidak ada di data master",
                        'details': list(missing_in_master)[:5]  # Show first 5
                    })
                    report['issues_found'] += 1

        # Check score consistency
        if 'DATA_NILAI' in dataframes:
            score_df = dataframes['DATA_NILAI']

            if 'nama' in master_df.columns and 'nama' in score_df.columns:
                master_names = set(master_df['nama'].dropna().str.lower().str.strip())
                score_names = set(score_df['nama'].dropna().str.lower().str.strip())

                missing_in_master = score_names - master_names
                if missing_in_master:
                    report['consistency_checks'].append({
                        'type': 'missing_students_scores',
                        'description': f"{len(missing_in_master)} siswa di nilai tidak ada di data master",
                        'details': list(missing_in_master)[:5]
                    })
                    report['issues_found'] += 1

    return report