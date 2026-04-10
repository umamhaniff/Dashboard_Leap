"""
Interactive visualization module for Dashboard Leap.
Creates interactive plots using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

def create_interactive_scatter(df: pd.DataFrame,
                              x_col: str,
                              y_col: str,
                              color_col: Optional[str] = None,
                              size_col: Optional[str] = None,
                              title: Optional[str] = None) -> go.Figure:
    """
    Create an interactive scatter plot.
    
    Args:
        df: Input DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        color_col: Column for color coding
        size_col: Column for point size
        title: Plot title
        
    Returns:
        Plotly figure
    """
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
    """
    Create an interactive histogram.
    
    Args:
        df: Input DataFrame
        column: Column to plot
        color_col: Column for color grouping
        title: Plot title
        
    Returns:
        Plotly figure
    """
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
    """
    Create an interactive box plot.
    
    Args:
        df: Input DataFrame
        y_col: Y-axis column
        x_col: X-axis column for grouping
        color_col: Column for color coding
        title: Plot title
        
    Returns:
        Plotly figure
    """
    title = title or f'Box Plot of {y_col.replace("_", " ").title()}'
    
    fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title,
                template="plotly_white", points="outliers")
    
    fig.update_layout(height=600)
    
    return fig

def create_interactive_heatmap(df: pd.DataFrame,
                              title: Optional[str] = None) -> go.Figure:
    """
    Create an interactive correlation heatmap.
    
    Args:
        df: Input DataFrame
        title: Plot title
        
    Returns:
        Plotly figure
    """
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
    """
    Create an interactive bar chart.
    
    Args:
        df: Input DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        color_col: Column for color coding
        title: Plot title
        
    Returns:
        Plotly figure
    """
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
    """
    Create an interactive line chart.
    
    Args:
        df: Input DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        color_col: Column for color grouping
        title: Plot title
        
    Returns:
        Plotly figure
    """
    title = title or f'{y_col.replace("_", " ").title()} over {x_col.replace("_", " ").title()}'
    
    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title,
                 template="plotly_white", markers=True)
    
    fig.update_layout(height=600)
    
    return fig

def create_dashboard_summary(df: pd.DataFrame) -> Dict[str, go.Figure]:
    """
    Create a set of interactive plots for dashboard summary.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary of plot figures
    """
    plots = {}
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    # Scatter plot for first two numeric columns
    if len(numeric_cols) >= 2:
        plots['scatter'] = create_interactive_scatter(
            df, numeric_cols[0], numeric_cols[1], 
            title="Data Scatter Plot"
        )
    
    # Histogram for first numeric column
    if len(numeric_cols) >= 1:
        plots['histogram'] = create_interactive_histogram(
            df, numeric_cols[0], 
            title="Data Distribution"
        )
    
    # Correlation heatmap
    if len(numeric_cols) > 1:
        plots['heatmap'] = create_interactive_heatmap(df, title="Correlation Analysis")
    
    # Bar chart for categorical data
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        # Group by categorical and aggregate numeric
        grouped = df.groupby(categorical_cols[0])[numeric_cols[0]].mean().reset_index()
        plots['bar'] = create_interactive_bar_chart(
            grouped, categorical_cols[0], numeric_cols[0],
            title="Category Analysis"
        )
    
    return plots

def create_interactive_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a default interactive plot based on data characteristics.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly figure
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) >= 2:
        return create_interactive_scatter(df, numeric_cols[0], numeric_cols[1])
    elif len(numeric_cols) == 1:
        return create_interactive_histogram(df, numeric_cols[0])
    else:
        # Fallback to bar chart with value counts
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) >= 1:
            value_counts = df[categorical_cols[0]].value_counts().reset_index()
            value_counts.columns = [categorical_cols[0], 'count']
            return create_interactive_bar_chart(value_counts, categorical_cols[0], 'count')
        else:
            raise ValueError("No suitable columns found for plotting")