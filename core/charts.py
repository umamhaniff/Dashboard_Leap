"""
Charts and Visualization for LEAP Security Dashboard.
Creates interactive plots using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

def apply_genesis_theme(fig: go.Figure, title_text: str, xaxis_title: Optional[str] = None, yaxis_title: Optional[str] = None) -> go.Figure:
    """Applies a premium, colorful, and glassmorphic Genesis theme to any Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title_text}</b>",
            font=dict(
                family="General Sans, sans-serif",
                size=18,
                color="var(--text-color)"
            ),
            x=0.02,
            y=0.95
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, sans-serif",
            color="var(--text-color)"
        ),
        xaxis=dict(
            title=xaxis_title,
            gridcolor="var(--genesis-border, rgba(99, 102, 241, 0.08))",
            linecolor="var(--genesis-border, rgba(99, 102, 241, 0.12))",
            zerolinecolor="var(--genesis-border, rgba(99, 102, 241, 0.12))",
            title_font=dict(size=12, color="var(--text-color)", family="DM Sans"),
            tickfont=dict(size=10, color="var(--text-color)")
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor="var(--genesis-border, rgba(99, 102, 241, 0.08))",
            linecolor="var(--genesis-border, rgba(99, 102, 241, 0.12))",
            zerolinecolor="var(--genesis-border, rgba(99, 102, 241, 0.12))",
            title_font=dict(size=12, color="var(--text-color)", family="DM Sans"),
            tickfont=dict(size=10, color="var(--text-color)")
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="var(--genesis-border, rgba(99, 102, 241, 0.12))",
            borderwidth=1,
            font=dict(size=10, color="var(--text-color)")
        ),
        colorway=["#6366F1", "#06B6D4", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"]
    )
    return fig

def create_attendance_chart(df: pd.DataFrame) -> go.Figure:
    """Create an interactive attendance visualization."""
    if 'nama' not in df.columns or 'hadir' not in df.columns:
        # Fallback chart
        fig = go.Figure()
        fig.add_annotation(text="Data absensi tidak lengkap", showarrow=False)
        return fig

    # Calculate attendance summary
    attendance_summary = df.groupby('nama')['hadir'].agg(['count', 'sum', 'mean']).reset_index()
    attendance_summary.columns = ['nama', 'total_pertemuan', 'hadir_count', 'attendance_rate']
    attendance_summary['attendance_rate'] = attendance_summary['attendance_rate'] * 100

    # Sort by attendance rate
    attendance_summary = attendance_summary.sort_values('attendance_rate', ascending=True)

    # Dynamic colors: Red (<75), Orange (75-90), Green (90-99), Indigo (100)
    rates = attendance_summary['attendance_rate']
    bar_colors = []
    for r in rates:
        if r < 75:
            bar_colors.append('#EF4444')
        elif r < 90:
            bar_colors.append('#F59E0B')
        elif r < 100:
            bar_colors.append('#10B981')
        else:
            bar_colors.append('#6366F1')

    # Create horizontal bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=attendance_summary['attendance_rate'],
        y=attendance_summary['nama'],
        orientation='h',
        name='Tingkat Kehadiran (%)',
        marker=dict(
            color=bar_colors,
            line=dict(color='var(--secondary-background-color)', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>Tingkat Kehadiran: %{x:.1f}%<br>Total Pertemuan: %{customdata}<extra></extra>',
        customdata=attendance_summary['total_pertemuan']
    ))

    apply_genesis_theme(fig, "Tingkat Kehadiran Siswa", "Tingkat Kehadiran (%)", "Nama Siswa")
    fig.update_layout(
        height=max(400, len(attendance_summary) * 22),  # Dynamic height
        showlegend=False
    )

    return fig

def create_score_distribution(df: pd.DataFrame) -> go.Figure:
    """Create score distribution visualization."""
    # Find score columns
    score_cols = [col for col in df.columns if 'nilai' in col.lower() or 'score' in col.lower() or 'skor' in col.lower()]

    if not score_cols:
        fig = go.Figure()
        fig.add_annotation(text="Tidak ada kolom nilai ditemukan", showarrow=False)
        return fig

    # Create histogram for each score column
    fig = go.Figure()
    colors = ['#6366F1', '#06B6D4', '#10B981', '#F59E0B']

    for idx, col in enumerate(score_cols):
        color = colors[idx % len(colors)]
        fig.add_trace(go.Histogram(
            x=df[col].dropna(),
            name=col.replace('_', ' ').title(),
            opacity=0.75,
            marker_color=color,
            nbinsx=15,
            hovertemplate='<b>Rentang Nilai %{x}</b><br>Frekuensi: %{y} siswa<extra></extra>'
        ))

    apply_genesis_theme(fig, "Distribusi Nilai Siswa", "Nilai Rapor", "Jumlah Siswa")
    fig.update_layout(
        barmode='overlay',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def create_overview_metrics_chart(dataframes: dict) -> go.Figure:
    """Create overview metrics visualization."""
    # Calculate metrics
    metrics = []
    for sheet_name, df in dataframes.items():
        metrics.append({
            'Sheet': sheet_name,
            'Records': len(df),
            'Columns': len(df.columns),
            'Missing Values': df.isnull().sum().sum()
        })

    metrics_df = pd.DataFrame(metrics)

    # Create subplots
    fig = go.Figure()

    # Records bar chart
    fig.add_trace(go.Bar(
        x=metrics_df['Sheet'],
        y=metrics_df['Records'],
        name='Total Baris Data',
        marker_color='#6366F1',
        hovertemplate='<b>Sheet: %{x}</b><br>Total Baris: %{y}<extra></extra>'
    ))

    # Missing values line
    fig.add_trace(go.Scatter(
        x=metrics_df['Sheet'],
        y=metrics_df['Missing Values'],
        name='Missing Values (Ketiadaan Data)',
        mode='lines+markers',
        line=dict(color='#EF4444', width=3),
        marker=dict(size=8, symbol='circle', borderwidth=2, bordercolor='var(--secondary-background-color)'),
        yaxis='y2',
        hovertemplate='<b>Sheet: %{x}</b><br>Missing Values: %{y}<extra></extra>'
    ))

    apply_genesis_theme(fig, "Ikhtisar Kapasitas & Ketiadaan Data Pipeline", "Lembar Kerja (Sheets)", "Total Baris")
    fig.update_layout(
        yaxis2=dict(
            title='Ketiadaan Data (Missing)',
            overlaying='y',
            side='right',
            gridcolor="rgba(239, 68, 68, 0.05)",
            title_font=dict(size=12, color="#EF4444", family="DM Sans"),
            tickfont=dict(size=10, color="#EF4444")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def create_security_alerts_chart(analysis_result: str) -> go.Figure:
    """Create security alerts visualization from analysis text."""
    # Simple placeholder - in real implementation, parse analysis for specific metrics
    alerts = ['Data Consistency', 'Attendance Patterns', 'Score Anomalies', 'Access Patterns']

    # Mock severity levels (in real implementation, extract from analysis)
    severity = np.random.choice(['Low', 'Medium', 'High'], len(alerts))

    severity_colors = {'Low': '#10B981', 'Medium': '#F59E0B', 'High': '#EF4444'}
    colors = [severity_colors[s] for s in severity]

    fig = go.Figure(data=[go.Bar(
        x=alerts,
        y=np.random.randint(1, 10, len(alerts)),  # Mock counts
        marker_color=colors,
        text=severity,
        textposition='auto'
    )])

    fig.update_layout(
        title='Security Alert Summary',
        xaxis_title='Alert Type',
        yaxis_title='Count',
        showlegend=False
    )

    return fig

def create_interactive_scatter(df: pd.DataFrame,
                              x_col: str,
                              y_col: str,
                              color_col: Optional[str] = None,
                              size_col: Optional[str] = None,
                              title: Optional[str] = None) -> go.Figure:
    """Create an interactive scatter plot."""
    title = title or f'{x_col.replace("_", " ").title()} vs {y_col.replace("_", " ").title()}'

    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col,
                    title=title, template="plotly_white")

    fig.update_traces(marker=dict(opacity=0.7))
    fig.update_layout(height=600)

    return fig

def create_interactive_histogram(df: pd.DataFrame,
                                column: str,
                                color_col: Optional[str] = None,
                                title: Optional[str] = None) -> go.Figure:
    """Create an interactive histogram."""
    title = title or f'Distribution of {column.replace("_", " ").title()}'

    fig = px.histogram(df, x=column, color=color_col, title=title,
                      template="plotly_white", marginal="box")

    fig.update_layout(height=600)

    return fig

def create_interactive_box_plot(df: pd.DataFrame,
                               y_col: str,
                               x_col: Optional[str] = None,
                               color_col: Optional[str] = None,
                               title: Optional[str] = None) -> go.Figure:
    """Create an interactive box plot."""
    title = title or f'Box Plot of {y_col.replace("_", " ").title()}'

    fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title,
                template="plotly_white", points="outliers")

    fig.update_layout(height=600)

    return fig

def create_interactive_heatmap(df: pd.DataFrame,
                              title: Optional[str] = None) -> go.Figure:
    """Create an interactive correlation heatmap."""
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty:
        raise ValueError("No numeric columns found for correlation analysis")

    correlation_matrix = numeric_df.corr()

    title = title or 'Correlation Heatmap'

    fig = px.imshow(correlation_matrix,
                   text_auto=True,
                   aspect="auto",
                   title=title,
                   template="plotly_white")

    fig.update_layout(height=600)

    return fig

def create_interactive_bar_chart(df: pd.DataFrame,
                                x_col: str,
                                y_col: str,
                                color_col: Optional[str] = None,
                                title: Optional[str] = None) -> go.Figure:
    """Create an interactive bar chart."""
    title = title or f'{y_col.replace("_", " ").title()} by {x_col.replace("_", " ").title()}'

    fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title,
                template="plotly_white")

    fig.update_layout(height=600)

    return fig

def create_interactive_line_chart(df: pd.DataFrame,
                                 x_col: str,
                                 y_col: str,
                                 color_col: Optional[str] = None,
                                 title: Optional[str] = None) -> go.Figure:
    """Create an interactive line chart."""
    title = title or f'{y_col.replace("_", " ").title()} over {x_col.replace("_", " ").title()}'

    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title,
                 template="plotly_white", markers=True)

    fig.update_layout(height=600)

    return fig

def create_dashboard_summary(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, go.Figure]:
    """Create a set of interactive plots for dashboard summary."""
    plots = {}

    # Overview metrics
    if dataframes:
        plots['overview'] = create_overview_metrics_chart(dataframes)

    # Attendance analysis if available
    if 'DATA_ABSENSI' in dataframes:
        absensi_df = dataframes['DATA_ABSENSI']
        if 'nama' in absensi_df.columns and 'hadir' in absensi_df.columns:
            plots['attendance'] = create_attendance_chart(absensi_df)

    # Score analysis if available
    if 'DATA_NILAI' in dataframes:
        nilai_df = dataframes['DATA_NILAI']
        plots['scores'] = create_score_distribution(nilai_df)

    # Master data analysis
    if 'DATA_MASTER' in dataframes:
        master_df = dataframes['DATA_MASTER']

        # Age distribution if available
        if 'umur' in master_df.columns:
            plots['age_dist'] = create_interactive_histogram(
                master_df, 'umur', title="Distribusi Umur Siswa"
            )

        # Class distribution if available
        if 'rombel' in master_df.columns:
            class_counts = master_df['rombel'].value_counts().reset_index()
            class_counts.columns = ['rombel', 'count']
            plots['class_dist'] = create_interactive_bar_chart(
                class_counts, 'rombel', 'count', title="Distribusi Siswa per Rombel"
            )

    return plots

def create_web_page_views_chart(db: Dict[str, pd.DataFrame]) -> go.Figure:
    """Create a bar chart showing page views by visitor session."""
    web_df = db.get("web_statistik", pd.DataFrame())
    if web_df.empty or "visitor_session" not in web_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Data statistik web kosong", showarrow=False)
        return fig
        
    fig = go.Figure(data=[go.Bar(
        x=web_df["visitor_session"],
        y=web_df["page_views"],
        marker_color="#06B6D4",
        hovertemplate='<b>Sesi: %{x}</b><br>Halaman Dilihat: %{y}<extra></extra>'
    )])
    
    apply_genesis_theme(fig, "Distribusi Page Views per Sesi Pengunjung", "Sesi Pengunjung (Session)", "Page Views")
    fig.update_layout(height=300)
    return fig

def create_web_traffic_timeline(db: Dict[str, pd.DataFrame]) -> go.Figure:
    """Create a line/scatter chart showing web traffic timeline."""
    web_df = db.get("web_statistik", pd.DataFrame())
    if web_df.empty or "created_at" not in web_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Data timeline web kosong", showarrow=False)
        return fig
        
    # Sort by created_at
    web_df = web_df.sort_values("created_at")
    
    fig = go.Figure(data=[go.Scatter(
        x=web_df["created_at"],
        y=web_df["page_views"],
        mode="lines+markers",
        line=dict(color="#6366F1", width=3),
        marker=dict(size=8, color="#06B6D4"),
        hovertemplate='<b>Waktu: %{x}</b><br>Views: %{y}<extra></extra>'
    )])
    
    apply_genesis_theme(fig, "Tren Aktivitas Trafik Website", "Tanggal & Waktu", "Page Views")
    fig.update_layout(height=300)
    return fig

def create_absence_reasons_chart(df: pd.DataFrame) -> go.Figure:
    """Create a pie chart for absence reasons."""
    # Find absent rows
    absent_df = df[df["status"] == "Tidak Hadir"]
    if absent_df.empty or "catatan" not in absent_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Tidak ada data alasan ketidakhadiran", showarrow=False)
        return fig
        
    counts = absent_df["catatan"].value_counts().reset_index()
    counts.columns = ["reason", "count"]
    
    # Map empty/nan reason to 'Tanpa Keterangan'
    counts["reason"] = counts["reason"].replace(["", "nan", None], "Tanpa Keterangan")
    counts = counts.groupby("reason")["count"].sum().reset_index()
    counts = counts.sort_values("count", ascending=False)
    
    fig = go.Figure(data=[go.Pie(
        labels=counts["reason"],
        values=counts["count"],
        hole=0.4,
        hovertemplate='<b>%{label}</b><br>Frekuensi: %{value}<br>Persentase: %{percent}<extra></extra>'
    )])
    
    apply_genesis_theme(fig, "Analisis Alasan Ketidakhadiran Siswa")
    fig.update_layout(height=350)
    return fig

def create_grade_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing grade distribution."""
    if df.empty or "grade" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Data grade kosong", showarrow=False)
        return fig
        
    # Clean grade names
    df_clean = df.copy()
    df_clean["grade_clean"] = df_clean["grade"].apply(lambda x: str(x).split(" ")[0] if " " in str(x) else str(x))
    
    # Order of grades
    grade_order = ["A", "B", "C", "D", "E", "F"]
    
    counts = df_clean["grade_clean"].value_counts().reindex(grade_order, fill_value=0).reset_index()
    counts.columns = ["grade", "count"]
    
    # Beautiful color palette for grades: A (indigo), B (cyan), C (green), D (yellow), E (orange), F (red)
    colors = ["#6366F1", "#06B6D4", "#10B981", "#F59E0B", "#EC4899", "#EF4444"]
    
    fig = go.Figure(data=[go.Bar(
        x=counts["grade"],
        y=counts["count"],
        marker_color=colors,
        hovertemplate='<b>Grade %{x}</b><br>Jumlah: %{y} siswa<extra></extra>'
    )])
    
    apply_genesis_theme(fig, "Sebaran Grade Nilai Siswa", "Grade", "Jumlah Siswa")
    fig.update_layout(height=350)
    return fig

def create_dropout_reasons_chart(df: pd.DataFrame) -> go.Figure:
    """Create a donut chart for dropout reasons."""
    if df.empty or "alasan_keluar" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Tidak ada data alasan keluar", showarrow=False)
        return fig
        
    counts = df["alasan_keluar"].value_counts().reset_index()
    counts.columns = ["reason", "count"]
    
    fig = go.Figure(data=[go.Pie(
        labels=counts["reason"],
        values=counts["count"],
        hole=0.4,
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>'
    )])
    
    apply_genesis_theme(fig, "Distribusi Alasan Siswa Keluar")
    fig.update_layout(height=350)
    return fig

def create_rombel_distribution_chart(df_jadwal: pd.DataFrame) -> go.Figure:
    """Create a horizontal bar chart showing student counts per rombel."""
    if df_jadwal.empty or "rombel" not in df_jadwal.columns:
        fig = go.Figure()
        fig.add_annotation(text="Data rombel kosong", showarrow=False)
        return fig
        
    counts = df_jadwal["rombel"].value_counts().reset_index()
    counts.columns = ["rombel", "count"]
    counts = counts.sort_values("count", ascending=True)
    
    fig = go.Figure(data=[go.Bar(
        x=counts["count"],
        y=counts["rombel"],
        orientation="h",
        marker_color="#6366F1",
        hovertemplate='<b>Rombel: %{y}</b><br>Jumlah Siswa: %{x}<extra></extra>'
    )])
    
    apply_genesis_theme(fig, "Distribusi Siswa per Rombel", "Jumlah Siswa", "Rombel")
    fig.update_layout(height=max(300, len(counts) * 25))
    return fig

def create_marketing_funnel(df_calon: pd.DataFrame, df_bayar: pd.DataFrame) -> go.Figure:
    """Create marketing funnel from calon_siswa and calon_siswa_bayar."""
    total_leads = len(df_calon) if not df_calon.empty else 0
    total_paid = df_bayar["id_calon_akademik"].nunique() if not df_bayar.empty else 0
    
    stages = ["Total leads (Calon)", "Siswa Bayar (Konversi)"]
    values = [total_leads, total_paid]
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker=dict(color=["#6366F1", "#10B981"])
    ))
    
    apply_genesis_theme(fig, "Corong Konversi Pemasaran (Funnel)", "Jumlah", "")
    return fig

def create_parent_income_chart(df_ortu: pd.DataFrame) -> go.Figure:
    """Create bar chart of father/mother income distribution."""
    if df_ortu.empty or "penghasilan_ayah" not in df_ortu.columns:
        fig = go.Figure()
        fig.add_annotation(text="Data penghasilan orang tua kosong", showarrow=False)
        return fig
        
    counts = df_ortu["penghasilan_ayah"].value_counts().reset_index()
    counts.columns = ["income", "count"]
    
    fig = go.Figure(go.Bar(
        x=counts["income"],
        y=counts["count"],
        marker_color="#06B6D4",
        hovertemplate='<b>Penghasilan: %{x}</b><br>Jumlah: %{y} orang<extra></extra>'
    ))
    
    apply_genesis_theme(fig, "Segmentasi Sosio-Ekonomi (Penghasilan Ayah)", "Tingkat Penghasilan", "Jumlah")
    return fig

def create_teacher_compliance_chart(df_detail: pd.DataFrame, df_catatan: pd.DataFrame) -> go.Figure:
    """Create compliance chart: percentage of sessions with catatan_kelas."""
    if df_detail.empty:
        fig = go.Figure()
        fig.add_annotation(text="Data detail jadwal kosong", showarrow=False)
        return fig
        
    if df_catatan.empty:
        compliance_rate = 0.0
        recorded_sessions = 0
        total_sessions = len(df_detail)
    else:
        recorded_details = set(df_catatan["id_jadwal_detail"].dropna())
        total_sessions = len(df_detail)
        recorded_sessions = df_detail["id_jadwal_detail"].isin(recorded_details).sum()
        compliance_rate = (recorded_sessions / total_sessions) * 100 if total_sessions > 0 else 0.0
        
    fig = go.Figure(go.Pie(
        labels=["Sudah Isi Laporan", "Belum Isi Laporan"],
        values=[recorded_sessions, total_sessions - recorded_sessions],
        hole=0.4,
        marker=dict(colors=["#10B981", "#EF4444"])
    ))
    
    apply_genesis_theme(fig, "Rasio Kepatuhan Laporan Mengajar Guru")
    return fig

def create_late_attendance_chart(df_absensi: pd.DataFrame) -> go.Figure:
    """Create attendance status distribution (Tepat Waktu, Terlambat, Izin, Hadir)."""
    if df_absensi.empty or "status_absensi" not in df_absensi.columns:
        fig = go.Figure()
        fig.add_annotation(text="Data absensi kosong", showarrow=False)
        return fig
        
    counts = df_absensi["status_absensi"].value_counts().reset_index()
    counts.columns = ["status", "count"]
    
    color_map = {"Tepat Waktu": "#10B981", "Terlambat": "#EF4444", "Izin": "#F59E0B", "Hadir": "#6366F1"}
    colors = [color_map.get(s, "#8B5CF6") for s in counts["status"]]
    
    fig = go.Figure(go.Bar(
        x=counts["status"],
        y=counts["count"],
        marker_color=colors,
        hovertemplate='<b>Status: %{x}</b><br>Jumlah: %{y}<extra></extra>'
    ))
    
    apply_genesis_theme(fig, "Distribusi Status Kehadiran Karyawan", "Status Absensi", "Jumlah")
    return fig

def create_sales_velocity_chart(df_calon: pd.DataFrame, df_bayar: pd.DataFrame, df_calon_akademik: pd.DataFrame) -> go.Figure:
    """Analyze sales velocity: days from calon_siswa.created_at to payment."""
    if df_calon.empty or df_bayar.empty or df_calon_akademik.empty:
        fig = go.Figure()
        fig.add_annotation(text="Data pendaftaran kurang lengkap", showarrow=False)
        return fig
        
    c_df = df_calon[["id_calon", "created_at"]].copy()
    ca_df = df_calon_akademik[["id_calon_akademik", "id_calon"]].copy()
    merged = pd.merge(c_df, ca_df, on="id_calon")
    
    pay_df = df_bayar[["id_calon_akademik", "tanggal_konfirmasi_bayar"]].copy()
    final_df = pd.merge(merged, pay_df, on="id_calon_akademik")
    
    final_df["created_at"] = pd.to_datetime(final_df["created_at"])
    final_df["tanggal_konfirmasi_bayar"] = pd.to_datetime(final_df["tanggal_konfirmasi_bayar"])
    final_df["days_to_pay"] = (final_df["tanggal_konfirmasi_bayar"] - final_df["created_at"]).dt.days
    
    fig = go.Figure(go.Histogram(
        x=final_df["days_to_pay"],
        marker_color="#EC4899",
        nbinsx=10,
        hovertemplate='<b>Kecepatan Bayar %{x} Hari</b><br>Jumlah: %{y} pendaftar<extra></extra>'
    ))
    
    apply_genesis_theme(fig, "Distribusi Siklus Penjualan (Sales Velocity)", "Durasi Konversi (Hari)", "Jumlah Calon Siswa")
    return fig