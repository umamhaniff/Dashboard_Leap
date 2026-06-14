"""
LLM Security Analyzer for LEAP Dashboard.
Optimized with Explicit Failover List for Gemini & Gemma models.
"""

from google import genai
from google.genai import types
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
    """Generate prompt template for SQL Database (Website Statistics focus)."""
    combined = "=== AUDIT STATISTIK & TRAFIK WEBSITE (DATABASE SQL) ===\n"
    for name in ["web_statistik"]:
        df = dataframes.get(name)
        if df is not None and not df.empty:
            combined += f"\n[TABEL: {name}]\n{df.head(100).to_string(index=False)}\n"
            
    return f"""Kamu adalah SQL Database Website Traffic Auditor untuk LKP LEAP.
Tugasmu menganalisis log statistik pengunjung website untuk mendeteksi tren trafik, pola akses, dan potensi anomali/keamanan akses demi kenyamanan belajar online SISWA.
Fokus Analisis:
1. Analisis tren trafik: Hitung total views, unique IPs, dan rata-rata page views per sesi.
2. Deteksi Anomali Keamanan: Temukan apakah ada IP Address yang melakukan akses berlebihan (high page views) dalam satu sesi (potensi bot/scraping).
3. Berikan rekomendasi operasional dan keamanan website untuk meningkatkan performa server dan keamanan akses website LKP LEAP.

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
    
    client = genai.Client(api_key=api_key)

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
        sys_instruction = "Kamu adalah Asisten Analisis Akademik LKP LEAP. Sajikan data, temuan, dan rekomendasi secara objektif. Jangan pernah mengajukan pertanyaan atau kalimat tanya terbuka di akhir tanggapan Anda."
    else:
        prompt = get_operations_prompt(dataframes)
        sys_instruction = "Kamu adalah Auditor Integritas Database Siswa LKP LEAP. Sajikan data, audit, dan rekomendasi secara objektif. Jangan pernah mengajukan pertanyaan atau kalimat tanya terbuka di akhir tanggapan Anda."

    # --- FAILOVER LOOP ---
    last_error = ""
    for model_name in models_to_try:
        try:
            logger.info(f"Mencoba audit {source_type} dengan: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction
                )
            )
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
        api_key = get_api_key()
        client = genai.Client(api_key=api_key)
        # Gunakan flash-lite untuk kecepatan generate rekomendasi
        response = client.models.generate_content(
            model="models/gemini-2.5-flash-lite",
            contents=f"Berdasarkan analisis ini: {analysis_result}\nBerikan 5 poin rekomendasi mitigasi keamanan (bullet points)."
        )
        return [line.strip("- *• ") for line in response.text.strip().split('\n') if len(line) > 10][:5]
    except:
        return ["Rekomendasi tidak dapat dimuat karena limitasi API."]

def analyze_student_profile(student_name: str, student_info: dict) -> str:
    """Generate custom academic and behavioral advice for a specific student using Gemini AI."""
    api_key = get_api_key()
    if not api_key:
        return "ERROR: API Key tidak ditemukan."
    
    client = genai.Client(api_key=api_key)
    
    # Prioritas model untuk kecepatan dan kestabilan
    models_to_try = [
        'models/gemini-3.1-flash-lite-preview',
        'models/gemini-2.5-flash-lite',
        'models/gemini-2.0-flash-lite',
        'models/gemini-flash-latest'
    ]
    
    info_str = f"=== PROFIL SISWA: {student_name} ===\n"
    for key, val in student_info.items():
        if isinstance(val, pd.DataFrame):
            info_str += f"\n[{key}]\n{val.to_string(index=False)}\n"
        else:
            info_str += f"\n[{key}]: {val}\n"
            
    prompt = f"""Kamu adalah Educational Consultant & AI DSS Expert untuk LKP LEAP Surabaya.
Tugasmu adalah menganalisis data akademik (kehadiran, nilai) dan data operasional (observasi staf, program remedial) untuk siswa bernama '{student_name}'.

Berikan laporan evaluasi terpadu yang memuat:
1. **Analisis Akademik & Partisipasi**: Evaluasi tingkat kehadiran siswa dan performa nilainya. Apakah ada masalah ketidakhadiran yang berdampak pada pencapaian akademik?
2. **Kondisi Observasi & Sikap**: Tinjau catatan observasi guru (jika ada) dan hubungkan dengan performa belajarnya.
3. **Rencana Mitigasi Remedial Konkret**: Buat rencana pembelajaran adaptif dan mitigasi remedi spesifik agar siswa ini bisa lulus kelas dengan baik.
4. **Saran Retensi (Operasional)**: Jika ada risiko keluar (churn) atau masalah jadwal, berikan rekomendasi administratif untuk staf operasional LKP LEAP.

Data Siswa:
{info_str}
"""
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="Kamu adalah Konsultan Pendidikan AI LKP LEAP. Sajikan analisis, rekomendasi, dan mitigasi secara objektif. Jangan pernah mengajukan pertanyaan atau kalimat tanya terbuka di akhir tanggapan Anda."
                )
            )
            return f"**System Intelligence: {model_name}**\n\n{response.text.strip()}"
        except Exception as e:
            logger.warning(f"Gagal generate analisis siswa dengan model {model_name}: {str(e)}")
            continue
            
    return "ERROR: Gagal menghasilkan analisis siswa menggunakan Gemini API."