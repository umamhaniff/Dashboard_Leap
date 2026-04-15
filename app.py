"""
EduDecision AI - Streamlit Application.
Optimized for Single-Page Layout & On-Demand AI Analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import google.generativeai as genai

from core.data_pipeline import load_all_data, clean_all_data, get_data_quality_report
from core.llm_analyzer import analyze_security, generate_security_recommendations
from core.charts import create_attendance_chart
from config.settings import DASHBOARD_CONFIG, SPREADSHEET_URL

# --- PAGE CONFIG ---
st.set_page_config(
    page_title=DASHBOARD_CONFIG['title'],
    page_icon="🛡️",
    layout="wide"
)

# --- INITIALIZE SESSION STATE ---
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# --- DATA PIPELINE (OPTIMIZED) ---
@st.cache_data(ttl=300, show_spinner=False) # Hilangkan spinner default cache
def load_pipeline_data():
    try:
        raw_data = load_all_data()
        cleaned_data = clean_all_data(raw_data)
        quality_report = get_data_quality_report(cleaned_data)
        return raw_data, cleaned_data, quality_report
    except Exception as e:
        return {}, {}, {}

# --- HEADER SECTION ---
st.markdown(f'<h1 class="main-header">🛡️ {DASHBOARD_CONFIG["title"]}</h1>', unsafe_allow_html=True)

# --- 3 NEW BUTTONS BELOW HEADER ---
col_btn1, col_btn2, col_btn3, col_spacer = st.columns([1, 1, 1, 3])

with col_btn1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.analysis_result = None
        st.session_state.run_analysis = False
        st.rerun()

with col_btn2:
    if st.button("🤖 Run AI Analysis", use_container_width=True, type="primary"):
        st.session_state.run_analysis = True

with col_btn3:
    st.link_button("📊 Open Spreadsheet", SPREADSHEET_URL, use_container_width=True)

st.markdown("---")

# --- LOADING DATA (SINGLE SPINNER) ---
# Menggabungkan loading agar tidak tumpang tindih
with st.spinner("Sinkronisasi data EduDecision AI..."):
    raw_data, cleaned_data, quality_report = load_pipeline_data()

if not cleaned_data:
    st.error("Gagal menarik data. Cek koneksi atau konfigurasi SPS.")
    st.stop()

# --- SIDEBAR DEBUG (AS REQUESTED) ---
def display_sidebar_debug(cleaned_data):
    st.sidebar.subheader("🛠️ Debug Center")
    with st.sidebar.expander("🔍 Gemini Models", expanded=False):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.json({"status": "Connected", "models": models})
        except Exception as e:
            st.json({"status": "Error", "message": str(e)})

    with st.sidebar.expander("📊 Data Inventory", expanded=False):
        inventory = {sheet: {"rows": len(df), "cols": len(df.columns)} for sheet, df in cleaned_data.items()}
        st.json(inventory)

display_sidebar_debug(cleaned_data)

def display_overview_page(cleaned_data, quality_report):
    st.header("📊 Data Overview")

# --- SECTION 1: OVERVIEW METRICS ---
c1, c2, c3 = st.columns(3)
total_rec = sum(len(df) for df in cleaned_data.values())
c1.metric("Total Records", f"{total_rec:,}")
c2.metric("Data Quality", f"{100 - quality_report.get('overall_quality', {}).get('overall_missing_percentage', 0):.1f}%")
c3.metric("Sheets Active", len(cleaned_data))

st.subheader("🔍 Data Preview (Direct Access)")
if cleaned_data:
    # Mapping nama sheet: DATA_MASTER -> Master
    display_map = {k: k.replace('DATA_', '').title() for k in cleaned_data.keys()}
    reverse_map = {v: k for k, v in display_map.items()}
    
    # Cari index "Master" untuk jadi default
    options = list(display_map.values())
    default_idx = options.index("Master") if "Master" in options else 0
    
    selected_display = st.selectbox("Pilih Tabel:", options, index=default_idx)
    selected_real_key = reverse_map[selected_display]
    
    st.dataframe(cleaned_data[selected_real_key], use_container_width=True, height=400)

# --- SECTION 3: LLM SECURITY INTELLIGENCE (ON DEMAND) ---
st.markdown("---")
st.subheader("🤖 Gen AI Security Intelligence")

if st.session_state.run_analysis:
    if st.session_state.analysis_result is None:
        with st.spinner("Gemini sedang menganalisis pola data (Holistic Audit)..."):
            # Panggil fungsi analisis dari core/llm_analyzer.py
            st.session_state.analysis_result = analyze_security(cleaned_data)
    
    col_analysis, col_rec = st.columns([2, 1])
    with col_analysis:
        st.markdown(st.session_state.analysis_result)
    
    with col_rec:
        st.subheader("💡 Rekomendasi")
        recs = generate_security_recommendations(st.session_state.analysis_result)
        for i, r in enumerate(recs, 1):
            st.markdown(f'**{i}.** {r}')
else:
    st.info("Klik tombol 'Run AI Analysis' di atas untuk memulai audit keamanan berbasis AI. Ini membantu menghemat penggunaan token API.")

# --- FOOTER ---
st.caption(f"EduDecision AI v1.0 | Last Sync: {datetime.now().strftime('%H:%M:%S')}")
