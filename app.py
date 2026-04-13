"""
LEAP Security Dashboard - Streamlit Application.
Optimized for AI-First Security Insights & Separate Debug Expanders.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
import google.generativeai as genai

# Import core modules dari folder project kamu
from core.data_pipeline import load_all_data, clean_all_data, get_data_quality_report
from core.llm_analyzer import analyze_security, generate_security_recommendations
from core.charts import create_attendance_chart
from config.settings import DASHBOARD_CONFIG

# --- PAGE CONFIG ---
st.set_page_config(
    page_title=DASHBOARD_CONFIG['title'],
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS LOADER ---
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'styles', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

load_css()

# --- DATA & AI PIPELINE (CACHED) ---
@st.cache_data(ttl=300)
def load_pipeline_data():
    try:
        raw_data = load_all_data()
        cleaned_data = clean_all_data(raw_data)
        quality_report = get_data_quality_report(cleaned_data)
        return raw_data, cleaned_data, quality_report
    except Exception as e:
        st.error(f"Gagal narik data dari SPS: {str(e)}")
        return {}, {}, {}

@st.cache_data(ttl=600)
def get_security_analysis(_cleaned_data):
    if not _cleaned_data:
        return "Data tidak tersedia untuk dianalisis."
    try:
        # Gunakan model gemini-1.5-flash untuk performa terbaik
        analysis = analyze_security(_cleaned_data)
        return analysis
    except Exception as e:
        return f"ERROR: Security analysis failed: {str(e)}"

# --- SIDEBAR DEBUG (EXPANDER MASING-MASING) ---
# Di dalam file app.py, ganti fungsi display_sidebar_debug

def display_sidebar_debug(cleaned_data):
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Debug Center")
    
    # 1. Expander Daftar Model Gemini
    with st.sidebar.expander("🔍 Debug: Daftar Model Gemini", expanded=False):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                # Output JSON
                st.json({
                    "status": "Connected",
                    "total_models": len(models),
                    "available_models": models,
                    "recommended_model": "gemini-2.5-flash" if "models/gemini-2.5-flash" in models else "gemini-1.5-flash"
                })
        except Exception as e:
            st.json({"status": "Error", "message": str(e)})

    # 2. Expander Inventori Data (SPS Connector)
    with st.sidebar.expander("📊 Debug: Data Inventory", expanded=False):
        if cleaned_data:
            inventory = {}
            for sheet, df in cleaned_data.items():
                inventory[sheet] = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns)
                }
            st.json(inventory)
        else:
            st.json({"status": "Waiting", "message": "No data loaded from SPS"})

# --- PAGE: SECURITY ANALYSIS (DEFAULT) ---
def display_security_page(cleaned_data, analysis):
    st.markdown(f'<h1 class="main-header">🛡️ Gen AI Security Intelligence</h1>', unsafe_allow_html=True)
    st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    if not cleaned_data:
        st.warning("Data kosong. Pastikan koneksi GCP ke SPS sudah 'Allow Access'.")
        return

    col_analysis, col_rec = st.columns([2, 1])
    
    with col_analysis:
        st.subheader("📋 Laporan Anomali Gemini")
        if "ERROR" in analysis:
            st.error(analysis)
        else:
            st.markdown(analysis)

    with col_rec:
        st.subheader("💡 Rekomendasi Mitigasi")
        try:
            recs = generate_security_recommendations(analysis)
            for i, r in enumerate(recs, 1):
                st.markdown(f'<div class="recommendation-box">**{i}.** {r}</div>', unsafe_allow_html=True)
        except:
            st.info("Generating recommendations...")

# --- PAGE: OVERVIEW & RAW DATA ---
def display_overview_page(cleaned_data, quality_report):
    st.header("📊 Data Overview")
    c1, c2, c3 = st.columns(3)
    total_rec = sum(len(df) for df in cleaned_data.values())
    c1.metric("Total Records", f"{total_rec:,}")
    c2.metric("Data Quality", f"{100 - quality_report.get('overall_quality', {}).get('overall_missing_percentage', 0):.1f}%")
    c3.metric("Sheets Active", len(cleaned_data))

    st.subheader("🔍 Data Preview (Direct Access)")
    if cleaned_data:
        selected = st.selectbox("Pilih Sheet:", list(cleaned_data.keys()))
        st.dataframe(cleaned_data[selected], use_container_width=True, height=400)

# --- MAIN APP ---
def main():
    with st.spinner("Sinkronisasi data SPS..."):
        raw_data, cleaned_data, quality_report = load_pipeline_data()

    st.sidebar.title("🧭 Control Hub")
    pages = ["Security Analysis", "Overview", "Absensi"]
    choice = st.sidebar.radio("Navigasi Utama:", pages)

    display_sidebar_debug(cleaned_data)

    if choice == "Security Analysis":
        with st.spinner("Gemini sedang menganalisis pola keamanan..."):
            analysis = get_security_analysis(cleaned_data)
        display_security_page(cleaned_data, analysis)
    
    elif choice == "Overview":
        display_overview_page(cleaned_data, quality_report)
    
    elif choice == "Absensi":
        st.header("📅 Analisis Absensi")
        if 'DATA_ABSENSI' in cleaned_data:
            fig = create_attendance_chart(cleaned_data['DATA_ABSENSI'])
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(cleaned_data['DATA_ABSENSI'], use_container_width=True)

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()