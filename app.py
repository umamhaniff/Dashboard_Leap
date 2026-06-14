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
st.markdown('<div class="apple-global-nav"><span> EduDecision AI</span><span>Overview | Analytics | Logs</span></div>', unsafe_allow_html=True)

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
    
    # Calculate cases count based on catatan_siswa
    obs_count = 0
    if not db_data['catatan_siswa'].empty:
        obs_count = len(db_data['catatan_siswa'][db_data['catatan_siswa']['status_followup']=='NEED FURTHER OBSERVATION'])
    c3.metric("Kasus Observasi Aktif", f"{obs_count}")

    st.markdown("### 🗂️ Profil Siswa & Catatan Kelas")
    col_db1, col_db2 = st.columns([2, 1])
    
    with col_db1:
        st.subheader("Daftar Siswa & Rombel (Direct Access)")
        st.dataframe(db_data['jadwal_siswa'], use_container_width=True)

    with col_db2:
        st.subheader("Log Kasus Observasi Staf")
        if db_data['catatan_siswa'].empty:
            st.write("Tidak ada log catatan siswa.")
        else:
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
