"""
LEAP Security Dashboard - Streamlit Application.
Interactive dashboard with data visualization and AI-powered security insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Import our modules
from core.data_pipeline import load_all_data, clean_all_data, get_data_quality_report
from core.llm_analyzer import analyze_security, generate_security_recommendations
from core.charts import create_attendance_chart, create_score_distribution, create_overview_metrics_chart
from config.settings import DASHBOARD_CONFIG

# Page configuration
st.set_page_config(
    page_title=DASHBOARD_CONFIG['title'],
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'styles', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found. Please add styles/style.css")

load_css()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_pipeline_data():
    """Load and process all data for the dashboard."""
    try:
        # Load raw data
        raw_data = load_all_data()

        # Clean data
        cleaned_data = clean_all_data(raw_data)

        # Get quality report
        quality_report = get_data_quality_report(cleaned_data)

        return raw_data, cleaned_data, quality_report
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return {}, {}, {}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_security_analysis(_cleaned_data):
    """Get security analysis from Gemini (cached to avoid repeated API calls)."""
    if not _cleaned_data:
        return "No data available for analysis"

    try:
        analysis = analyze_security(_cleaned_data)
        return analysis
    except Exception as e:
        return f"Analysis failed: {str(e)}"

def display_overview_page(raw_data, cleaned_data, quality_report):
    """Display the overview dashboard page."""
    st.markdown(f'<h1 class="main-header">{DASHBOARD_CONFIG["title"]}</h1>', unsafe_allow_html=True)
    st.markdown(DASHBOARD_CONFIG["subtitle"])

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Sheets", len(cleaned_data))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        total_records = sum(len(df) for df in cleaned_data.values())
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Records", f"{total_records:,}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        missing_pct = quality_report.get('overall_quality', {}).get('overall_missing_percentage', 0)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Data Quality", f"{100-missing_pct:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Last Updated", datetime.now().strftime("%H:%M"))
        st.markdown('</div>', unsafe_allow_html=True)

    # Data Summary
    st.subheader("📊 Data Summary")
    if cleaned_data:
        summary_cols = st.columns(len(cleaned_data))

        for i, (sheet_name, df) in enumerate(cleaned_data.items()):
            with summary_cols[i]:
                st.markdown(f"**{sheet_name}**")
                st.info(f"{len(df)} records")
    else:
        st.info("No data sheets loaded yet. Please check your configuration.")

    # Quick Data Preview
    st.subheader("🔍 Data Preview")
    if cleaned_data:
        selected_sheet = st.selectbox("Select sheet to preview:", list(cleaned_data.keys()))
        if selected_sheet in cleaned_data:
            df = cleaned_data[selected_sheet]
            st.dataframe(df.head(10), use_container_width=True)
    else:
        st.info("No data available for preview.")

def display_absensi_page(cleaned_data):
    """Display attendance analysis page."""
    st.header("📅 Analisis Absensi")

    if 'DATA_ABSENSI' not in cleaned_data:
        st.warning("Data absensi tidak ditemukan")
        return

    absensi_df = cleaned_data['DATA_ABSENSI']

    # Attendance Statistics
    col1, col2, col3 = st.columns(3)

    if 'hadir' in absensi_df.columns:
        # Ensure hadir column is boolean for calculations
        hadir_series = absensi_df['hadir']
        if hadir_series.dtype != bool:
            # Convert to boolean if not already
            hadir_series = hadir_series.astype(str).str.lower().str.strip().isin(['ya', 'yes', 'true', '1', 'hadir', 'present'])
        
        attendance_rate = hadir_series.mean() * 100
        with col1:
            st.metric("Tingkat Kehadiran", f"{attendance_rate:.1f}%")

        total_students = len(absensi_df)
        present_count = hadir_series.sum()
        with col2:
            st.metric("Siswa Hadir", f"{int(present_count)}/{total_students}")

        with col3:
            st.metric("Siswa Tidak Hadir", total_students - int(present_count))

    # Attendance Chart
    st.subheader("Grafik Kehadiran")
    try:
        fig = create_attendance_chart(absensi_df)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to create attendance chart: {str(e)}")

    # Detailed Attendance Table
    st.subheader("Detail Absensi per Siswa")
    if 'nama' in absensi_df.columns and 'hadir' in absensi_df.columns:
        attendance_summary = absensi_df.groupby('nama')['hadir'].agg(['count', 'sum', 'mean']).reset_index()
        attendance_summary.columns = ['Nama', 'Total Pertemuan', 'Hadir', 'Tingkat Kehadiran']
        attendance_summary['Tingkat Kehadiran'] = (attendance_summary['Tingkat Kehadiran'] * 100).round(1)
        st.dataframe(attendance_summary.sort_values('Tingkat Kehadiran'), use_container_width=True)

def display_security_page(cleaned_data, security_analysis):
    """Display security analysis page."""
    st.header("🛡️ Analisis Keamanan")

    # Security Analysis Results
    st.subheader("Hasil Analisis Gemini AI")

    if security_analysis.startswith("ERROR"):
        st.error(security_analysis)
    else:
        # Display analysis in expandable sections
        with st.expander("📋 Laporan Lengkap Analisis Keamanan", expanded=True):
            st.markdown(security_analysis)

        # Generate and display recommendations
        st.subheader("💡 Rekomendasi Keamanan")
        try:
            recommendations = generate_security_recommendations(security_analysis)
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f'<div class="recommendation-box">**{i}.** {rec}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to generate recommendations: {str(e)}")

    # Security Metrics
    st.subheader("🔍 Metrik Keamanan")

    if cleaned_data:
        col1, col2, col3 = st.columns(3)

        # Data consistency check
        consistency_issues = 0
        if 'DATA_MASTER' in cleaned_data and 'DATA_ABSENSI' in cleaned_data:
            master_names = set(cleaned_data['DATA_MASTER'].get('nama', pd.Series()).dropna().str.lower().str.strip())
            attendance_names = set(cleaned_data['DATA_ABSENSI'].get('nama', pd.Series()).dropna().str.lower().str.strip())
            consistency_issues = len(attendance_names - master_names)

        with col1:
            st.metric("Inkonsistensi Data", consistency_issues)

        # Data quality
        total_missing = sum(df.isnull().sum().sum() for df in cleaned_data.values())
        with col2:
            st.metric("Nilai Kosong Total", total_missing)

        # Suspicious patterns (placeholder - could be enhanced)
        suspicious_count = 0
        if 'DATA_ABSENSI' in cleaned_data:
            absensi_df = cleaned_data['DATA_ABSENSI']
            if 'hadir' in absensi_df.columns and 'nama' in absensi_df.columns:
                # Ensure hadir column is boolean for calculations
                if absensi_df['hadir'].dtype != bool:
                    # Convert to boolean if not already
                    absensi_df = absensi_df.copy()
                    absensi_df['hadir'] = absensi_df['hadir'].astype(str).str.lower().str.strip().isin(['ya', 'yes', 'true', '1', 'hadir', 'present'])
                
                # Count students with perfect attendance (might be suspicious)
                perfect_attendance = absensi_df.groupby('nama')['hadir'].mean() == 1.0
                suspicious_count = perfect_attendance.sum()

        with col3:
            st.metric("Pola Mencurigakan", suspicious_count)

def main():
    """Main dashboard application."""
    # Load data
    with st.spinner("Loading data pipeline..."):
        raw_data, cleaned_data, quality_report = load_pipeline_data()

    # Sidebar navigation
    st.sidebar.title("🧭 Navigasi")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Pilih Halaman:",
        DASHBOARD_CONFIG['pages'],
        help="Pilih halaman yang ingin ditampilkan"
    )

    # Get security analysis (only when needed)
    security_analysis = ""
    if page == "Security Analysis" and cleaned_data:
        with st.spinner("Running AI security analysis..."):
            security_analysis = get_security_analysis(cleaned_data)

    # Display selected page
    if page == "Overview":
        display_overview_page(raw_data, cleaned_data, quality_report)
    elif page == "Absensi":
        display_absensi_page(cleaned_data)
    elif page == "Security Analysis":
        display_security_page(cleaned_data, security_analysis)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**LEAP Security Dashboard**")
    st.sidebar.markdown("*v1.0 - Powered by Gemini AI*")

    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

def run_dashboard():
    """Entry point for the dashboard."""
    try:
        main()
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")
        st.error("Please check your configuration and try again.")

if __name__ == "__main__":
    run_dashboard()