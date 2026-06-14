"""
LLM Security Analyzer for LEAP Dashboard.
Optimized with Explicit Failover List for Gemini & Gemma models.
"""

import google.generativeai as genai
import os
import pandas as pd
import streamlit as st
import logging
from config.settings import SECURITY_ANALYSIS_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_api_key() -> str:
    """Ambil API Key dari Streamlit secrets atau environment."""
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        return st.secrets['GEMINI_API_KEY']
    return os.getenv('GEMINI_API_KEY', "")

def get_academic_prompt(dataframes: dict) -> str:
    """Generate prompt template for Google Sheets (Academic focus)."""
    combined = "=== AUDIT AKADEMIK & NILAI SISWA (GOOGLE SHEETS - ACADEMIC) ===\n"
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
    """Generate prompt template for MariaDB (Operations focus)."""
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

def analyze_security(dataframes: dict, source_type: str = "google_sheets") -> str:
    """
    Melakukan audit keamanan dengan mencoba list model satu per satu.
    Berhenti saat berhasil mendapatkan respon, atau loncat jika terkena 429 (Rate Limit).
    """
    api_key = get_api_key()
    if not api_key:
        return "ERROR: API Key tidak ditemukan."
    
    genai.configure(api_key=api_key)

    # --- LIST MODEL SESUAI CONTOH HANS ---
    # Aku tambahkan prefix 'models/' supaya API-nya bisa mengenali dengan tepat
    models_to_try = [
        'models/gemini-3.1-flash-lite-preview', # Prioritas 1: Versi 3.1 Lite
        'models/gemini-3-flash-preview',      # Prioritas 2: Versi 3.0 Flash
        'models/gemini-2.5-flash-lite',       # Prioritas 3: Versi 2.5 Lite
        'models/gemini-2.5-flash',            # Prioritas 4: Versi 2.5 Standar
        'models/gemini-2.0-flash-lite',       # Prioritas 5: Versi 2.0 Lite
        'models/gemini-2.0-flash',            # Prioritas 6: Versi 2.0 Standar
        'models/gemini-3.1-pro-preview',      # Prioritas 7: Versi 3.1 Pro
        'models/gemma-3-27b-it',              # Prioritas 8: Gemma Generasi 3
        'models/gemini-flash-latest'          # Fallback: Paling stabil (1.5 Flash)
    ]

    # Ambil prompt dan system instruction sesuai source_type
    if source_type == "google_sheets":
        prompt = get_academic_prompt(dataframes)
        sys_instruction = "Kamu adalah Asisten Analisis Akademik LKP LEAP."
    else:
        prompt = get_operations_prompt(dataframes)
        sys_instruction = "Kamu adalah Auditor Integritas Database Siswa LKP LEAP."

    # --- FAILOVER LOOP ---
    last_error = ""
    for model_name in models_to_try:
        try:
            logger.info(f"Mencoba audit {source_type} dengan: {model_name}")
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=sys_instruction
            )
            
            response = model.generate_content(prompt)
            # Sukses! Langsung kembalikan hasilnya
            return f"**System Intelligence: {model_name}**\n\n{response.text.strip()}"
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                logger.warning(f"Model {model_name} limit (429). Mencoba model berikutnya...")
                last_error = "Semua model di list sedang sibuk. Silakan tunggu 1 menit."
                continue 
            else:
                logger.error(f"Gagal pada {model_name}: {error_msg}")
                # Jika errornya bukan soal limit, tetap coba model lain
                continue

    return f"ERROR: {last_error}"

def generate_security_recommendations(analysis_result: str) -> list:
    """Generate rekomendasi mitigasi menggunakan model fallback tercepat."""
    try:
        # Gunakan flash-lite untuk kecepatan generate rekomendasi
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")
        prompt = f"Berdasarkan analisis ini: {analysis_result}\nBerikan 5 poin rekomendasi mitigasi keamanan (bullet points)."
        response = model.generate_content(prompt)
        return [line.strip("- *• ") for line in response.text.strip().split('\n') if len(line) > 10][:5]
    except:
        return ["Rekomendasi tidak dapat dimuat karena limitasi API."]