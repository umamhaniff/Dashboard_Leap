"""
Charts and Visualization for LEAP Security Dashboard.
Creates interactive plots using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

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

    # Create horizontal bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=attendance_summary['attendance_rate'],
        y=attendance_summary['nama'],
        orientation='h',
        name='Tingkat Kehadiran (%)',
        marker_color='lightblue',
        hovertemplate='<b>%{y}</b><br>Tingkat Kehadiran: %{x:.1f}%<br>Total Pertemuan: %{customdata}<extra></extra>',
        customdata=attendance_summary['total_pertemuan']
    ))

    fig.update_layout(
        title='Tingkat Kehadiran Siswa',
        xaxis_title='Tingkat Kehadiran (%)',
        yaxis_title='Nama Siswa',
        height=max(400, len(attendance_summary) * 20),  # Dynamic height
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

    for col in score_cols:
        fig.add_trace(go.Histogram(
            x=df[col].dropna(),
            name=col.replace('_', ' ').title(),
            opacity=0.7
        ))

    fig.update_layout(
        title='Distribusi Nilai Siswa',
        xaxis_title='Nilai',
        yaxis_title='Frekuensi',
        barmode='overlay'
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
        name='Total Records',
        marker_color='lightblue'
    ))

    # Missing values line
    fig.add_trace(go.Scatter(
        x=metrics_df['Sheet'],
        y=metrics_df['Missing Values'],
        name='Missing Values',
        mode='lines+markers',
        line=dict(color='red'),
        yaxis='y2'
    ))

    fig.update_layout(
        title='Data Overview Metrics',
        xaxis_title='Sheet',
        yaxis_title='Records',
        yaxis2=dict(
            title='Missing Values',
            overlaying='y',
            side='right'
        ),
        showlegend=True
    )

    return fig

def create_security_alerts_chart(analysis_result: str) -> go.Figure:
    """Create security alerts visualization from analysis text."""
    # Simple placeholder - in real implementation, parse analysis for specific metrics
    alerts = ['Data Consistency', 'Attendance Patterns', 'Score Anomalies', 'Access Patterns']

    # Mock severity levels (in real implementation, extract from analysis)
    severity = np.random.choice(['Low', 'Medium', 'High'], len(alerts))

    severity_colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
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