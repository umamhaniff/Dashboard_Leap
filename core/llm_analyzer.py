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

def get_academic_performance_prompt(dataframes: dict) -> str:
    """Generate prompt template for academic performance analysis."""
    nilai_df = dataframes.get("DATA_NILAI", pd.DataFrame())
    data_str = f"Data Nilai (Sample):\n{nilai_df.head(50).to_string(index=False)}" if not nilai_df.empty else "Data kosong."
    return f"""Kamu adalah Academic Performance Analyst LKP LEAP.
Analisis data performa nilai berikut:
{data_str}

Tugas:
1. Berikan analisis sebaran grade (A, B, C, D, E, F) dan statistik nilai rata-rata (Mid-Test & Final-Test).
2. Identifikasi masalah performa belajar dan rekomendasikan strategi peningkatan akademik.
"""

def get_attendance_prompt(dataframes: dict) -> str:
    """Generate prompt template for attendance analysis."""
    absensi_df = dataframes.get("DATA_ABSENSI", pd.DataFrame())
    data_str = f"Data Kehadiran (Sample):\n{absensi_df.head(50).to_string(index=False)}" if not absensi_df.empty else "Data kosong."
    return f"""Kamu adalah Student Attendance Analyst LKP LEAP.
Analisis data absensi berikut:
{data_str}

Tugas:
1. Evaluasi tingkat kehadiran siswa harian, tren tepat waktu, terlambat, sakit, izin, alfa.
2. Rekomendasikan tindakan pencegahan ketidakhadiran berulang.
"""

def get_student_predictor_prompt(dataframes: dict) -> str:
    """Generate prompt template for student predictor and overall student health analysis."""
    siswa_df = dataframes.get("DATA_SISWA", pd.DataFrame())
    nilai_df = dataframes.get("DATA_NILAI", pd.DataFrame())
    absensi_df = dataframes.get("DATA_ABSENSI", pd.DataFrame())
    keluar_df = dataframes.get("DATA_KELUAR", pd.DataFrame())
    
    siswa_str = f"Data Siswa (Sample 20):\n{siswa_df.head(20).to_string(index=False)}" if not siswa_df.empty else "Data kosong."
    nilai_str = f"Data Nilai (Sample 20):\n{nilai_df.head(20).to_string(index=False)}" if not nilai_df.empty else "Data kosong."
    absensi_str = f"Data Absensi (Sample 20):\n{absensi_df.head(20).to_string(index=False)}" if not absensi_df.empty else "Data kosong."
    keluar_str = f"Data Siswa Keluar (Sample 20):\n{keluar_df.head(20).to_string(index=False)}" if not keluar_df.empty else "Data kosong."
    
    return f"""Kamu adalah Senior Student Success Specialist & Predictor LKP LEAP Surabaya.
Tugasmu adalah menganalisis seluruh aspek terkait siswa (kehadiran, prestasi akademik/nilai, hambatan belajar, serta potensi siswa keluar/churn) secara menyeluruh.

Data Input (Sample):
--- DATA SISWA ---
{siswa_str}

--- DATA NILAI ---
{nilai_str}

--- DATA ABSENSI ---
{absensi_str}

--- DATA SISWA KELUAR ---
{keluar_str}

Tugas:
1. **Analisis Kondisi Akademik & Keaktifan**: Evaluasi sebaran nilai siswa dan hubungannya dengan pola kehadiran mereka.
2. **Prediksi Kendala Belajar & Risiko**: Identifikasi siswa yang berisiko mengalami hambatan belajar (nilai remedi) atau berisiko berhenti les (churn) berdasarkan data historis siswa keluar dan pola absensi/nilai.
3. **Rekomendasi Dukungan Siswa Terpadu**: Berikan usulan konkret untuk membantu siswa meningkatkan performa akademiknya, mencegah ketidakhadiran, meningkatkan motivasi, serta meminimalkan angka dropout secara preventif.
"""

def get_rombel_prompt(db_data: dict) -> str:
    """Generate prompt template for rombel analysis."""
    jadwal_df = db_data.get("jadwal_siswa", pd.DataFrame())
    data_str = f"Data Rombel & Rapor (Sample):\n{jadwal_df.head(50).to_string(index=False)}" if not jadwal_df.empty else "Data kosong."
    return f"""Kamu adalah Academic Operations Auditor LKP LEAP.
Analisis data rombel dan persetujuan rapor berikut:
{data_str}

Tugas:
1. Evaluasi efisiensi rombel (kelas) dan sebaran status persetujuan (ACC) rapor.
2. Identifikasi rombel yang masih pending persetujuannya dan rekomendasikan percepatan approval.
"""

def get_cs_cases_prompt(db_data: dict) -> str:
    """Generate prompt template for CS cases analysis."""
    catatan_df = db_data.get("catatan_siswa", pd.DataFrame())
    data_str = f"Data Kasus CS (Sample):\n{catatan_df.head(50).to_string(index=False)}" if not catatan_df.empty else "Data kosong."
    return f"""Kamu adalah Customer Relationship & Student Care Auditor LKP LEAP.
Analisis data catatan kasus perkembangan siswa berikut:
{data_str}

Tugas:
1. Identifikasi kasus-kasus kritis siswa yang memerlukan observasi lebih lanjut (CS follow-up).
2. Tentukan prioritas penanganan dan berikan usulan tindakan mitigasi untuk tim CS.
"""

def get_remedial_audit_prompt(db_data: dict) -> str:
    """Generate prompt template for remedial audit analysis."""
    remidi_df = db_data.get("catatan_remidi_siswa", pd.DataFrame())
    data_str = f"Data Log Remedial (Sample):\n{remidi_df.head(50).to_string(index=False)}" if not remidi_df.empty else "Data kosong."
    return f"""Kamu adalah Quality Assurance Academic Auditor LKP LEAP.
Analisis data audit remedial berikut:
{data_str}

Tugas:
1. Evaluasi kenaikan nilai pasca remedial (perbandingan nilai sebelum vs sesudah).
2. Audit persetujuan guru (ACC) untuk nilai remedial dan identifikasi penyimpangan jika ada.
"""

def get_unified_overview_prompt(combined_data: dict) -> str:
    """Generate prompt template for Unified LKP Overview analysis."""
    sheets_data = combined_data.get("sheets", {})
    db_data = combined_data.get("db", {})
    
    total_siswa = len(sheets_data.get("DATA_SISWA", []))
    nilai_df = sheets_data.get("DATA_NILAI", pd.DataFrame())
    avg_final = 71.60
    if not nilai_df.empty:
        final_df = nilai_df[nilai_df["periode"] == "Final"]
        if not final_df.empty:
            avg_final = final_df["score"].mean()
            
    siswa_df = db_data.get("siswa", pd.DataFrame())
    total_active = len(siswa_df[siswa_df["status_siswa"] == "Aktif"]) if not siswa_df.empty else 0
    catatan_df = db_data.get("catatan_siswa", pd.DataFrame())
    cases_count = len(catatan_df[catatan_df["status_followup"] == "NEED FURTHER OBSERVATION"]) if not catatan_df.empty else 0
    
    return f"""Kamu adalah Principal Educational Director & Executive Auditor LKP LEAP Surabaya.
Analisis data kinerja institusi LKP LEAP berikut secara menyeluruh (gabungan data akademik Sheets dan operasional Database):

[RINGKASAN EKSEKUTIF]
- Total Siswa Terdaftar (Sheets): {total_siswa}
- Siswa Aktif (Database): {total_active}
- Rata-rata Nilai Akhir Siswa: {avg_final:.2f}
- Jumlah Kasus Observasi CS Terbuka: {cases_count}

Tugas:
1. Berikan evaluasi kinerja makro LKP LEAP yang memadukan data akademik (keberhasilan nilai) dan data operasional (kondisi CS/staf pendukung).
2. Identifikasi apakah ada kendala koordinasi atau penurunan retensi siswa secara makro.
3. Berikan 3 rekomendasi taktis eksekutif untuk meningkatkan kualitas layanan pendidikan dan operasional LKP LEAP.
"""

def analyze_feature(dataframes: dict, feature_key: str) -> str:
    """Melakukan analisis AI spesifik untuk fitur tertentu."""
    api_key = get_api_key()
    if not api_key:
        return "ERROR: API Key tidak ditemukan."
    
    client = genai.Client(api_key=api_key)
    
    prompt_map = {
        "unified_overview": (get_unified_overview_prompt, "Kamu adalah Executive Auditor LKP LEAP. Sajikan analisis eksekutif secara objektif dan ringkas. Jangan pernah mengajukan pertanyaan di akhir tanggapan Anda."),
        "academic_perf": (get_academic_performance_prompt, "Kamu adalah Asisten Analisis Performa Akademik LKP LEAP. Sajikan data, temuan, dan rekomendasi secara objektif. Jangan pernah mengajukan pertanyaan di akhir tanggapan Anda."),
        "attendance": (get_attendance_prompt, "Kamu adalah Asisten Analisis Kehadiran Siswa LKP LEAP. Sajikan data, temuan, dan rekomendasi secara objektif. Jangan pernah mengajukan pertanyaan di akhir tanggapan Anda."),
        "student_predictor": (get_student_predictor_prompt, "Kamu adalah Senior Student Success Specialist & Predictor LKP LEAP. Sajikan analisis kesehatan siswa, prediksi risiko, dan rekomendasi dukungan secara objektif. Jangan pernah mengajukan pertanyaan di akhir tanggapan Anda."),
        "rombel": (get_rombel_prompt, "Kamu adalah Asisten Analisis Operasional Kelas LKP LEAP. Sajikan data, temuan, dan rekomendasi secara objektif. Jangan pernah mengajukan pertanyaan di akhir tanggapan Anda."),
        "cs_cases": (get_cs_cases_prompt, "Kamu adalah Asisten Analisis Layanan CS & Konseling LKP LEAP. Sajikan data, temuan, dan rekomendasi secara objektif. Jangan pernah mengajukan pertanyaan di akhir tanggapan Anda."),
        "remedial_audit": (get_remedial_audit_prompt, "Kamu adalah Asisten Auditor Remedial Akademik LKP LEAP. Sajikan data, temuan, dan rekomendasi secara objektif. Jangan pernah mengajukan pertanyaan di akhir tanggapan Anda.")
    }
    
    if feature_key not in prompt_map:
        return "ERROR: Fitur analisis tidak dikenal."
        
    prompt_func, sys_instruction = prompt_map[feature_key]
    prompt = prompt_func(dataframes)
    
    models_to_try = [
        'models/gemini-3.1-flash-lite-preview',
        'models/gemini-3-flash-preview',
        'models/gemini-2.5-flash-lite',
        'models/gemini-2.5-flash',
        'models/gemini-2.0-flash-lite',
        'models/gemini-2.0-flash',
        'models/gemini-3.1-pro-preview',
        'models/gemma-3-27b-it',
        'models/gemini-flash-latest'
    ]
    
    last_error = ""
    for model_name in models_to_try:
        try:
            logger.info(f"Mencoba analisis {feature_key} dengan: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction
                )
            )
            return f"**System Intelligence: {model_name}**\n\n{response.text.strip()}"
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                logger.warning(f"Model {model_name} limit (429). Mencoba model berikutnya...")
                last_error = "Semua model di list sedang sibuk. Silakan tunggu 1 menit."
                continue
            else:
                logger.error(f"Gagal pada {model_name}: {error_msg}")
                continue
                
    return f"ERROR: {last_error}"

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