"""
Static plotting module for Dashboard Leap.
Creates various static plots for data visualization.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List
import os

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_histogram(df: pd.DataFrame, 
                    column: str, 
                    bins: int = 30,
                    title: Optional[str] = None,
                    save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a histogram for a numerical column.
    
    Args:
        df: Input DataFrame
        column: Column name to plot
        bins: Number of bins
        title: Plot title
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(df[column].dropna(), bins=bins, edgecolor='black', alpha=0.7)
    ax.set_xlabel(column.replace('_', ' ').title())
    ax.set_ylabel('Frequency')
    ax.set_title(title or f'Distribution of {column.replace("_", " ").title()}')
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def create_scatter_plot(df: pd.DataFrame, 
                      x_col: str, 
                      y_col: str,
                      hue_col: Optional[str] = None,
                      title: Optional[str] = None,
                      save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a scatter plot.
    
    Args:
        df: Input DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        hue_col: Column for color coding
        title: Plot title
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if hue_col:
        scatter = ax.scatter(df[x_col], df[y_col], c=df[hue_col], cmap='viridis', alpha=0.7)
        plt.colorbar(scatter, ax=ax, label=hue_col.replace('_', ' ').title())
    else:
        ax.scatter(df[x_col], df[y_col], alpha=0.7)
    
    ax.set_xlabel(x_col.replace('_', ' ').title())
    ax.set_ylabel(y_col.replace('_', ' ').title())
    ax.set_title(title or f'{x_col.replace("_", " ").title()} vs {y_col.replace("_", " ").title()}')
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def create_box_plot(df: pd.DataFrame, 
                   columns: List[str],
                   title: Optional[str] = None,
                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a box plot for multiple columns.
    
    Args:
        df: Input DataFrame
        columns: List of columns to plot
        title: Plot title
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    data_to_plot = [df[col].dropna() for col in columns]
    
    ax.boxplot(data_to_plot, labels=[col.replace('_', ' ').title() for col in columns])
    ax.set_ylabel('Value')
    ax.set_title(title or 'Box Plot Comparison')
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def create_correlation_heatmap(df: pd.DataFrame,
                              title: Optional[str] = None,
                              save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a correlation heatmap.
    
    Args:
        df: Input DataFrame
        title: Plot title
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        raise ValueError("No numeric columns found for correlation analysis")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    correlation_matrix = numeric_df.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', 
                center=0, ax=ax, square=True, cbar_kws={'shrink': 0.8})
    
    ax.set_title(title or 'Correlation Heatmap')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def create_bar_chart(df: pd.DataFrame,
                    x_col: str,
                    y_col: str,
                    title: Optional[str] = None,
                    save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a bar chart.
    
    Args:
        df: Input DataFrame
        x_col: X-axis column (categorical)
        y_col: Y-axis column (numerical)
        title: Plot title
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.bar(df[x_col], df[y_col], alpha=0.7, edgecolor='black')
    ax.set_xlabel(x_col.replace('_', ' ').title())
    ax.set_ylabel(y_col.replace('_', ' ').title())
    ax.set_title(title or f'{y_col.replace("_", " ").title()} by {x_col.replace("_", " ").title()}')
    
    # Rotate x-axis labels if too many categories
    if len(df[x_col].unique()) > 10:
        plt.xticks(rotation=45, ha='right')
    
    ax.grid(True, alpha=0.3, axis='y')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def save_all_plots(df: pd.DataFrame, output_dir: str = "reports/figures"):
    """
    Generate and save all applicable plots for the dataset.
    
    Args:
        df: Input DataFrame
        output_dir: Directory to save plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    # Histograms for numeric columns
    for col in numeric_cols:
        fig = create_histogram(df, col, save_path=os.path.join(output_dir, f'{col}_histogram.png'))
        plt.close(fig)
    
    # Correlation heatmap
    if len(numeric_cols) > 1:
        fig = create_correlation_heatmap(df, save_path=os.path.join(output_dir, 'correlation_heatmap.png'))
        plt.close(fig)
    
    # Box plot for numeric columns
    if len(numeric_cols) > 1:
        fig = create_box_plot(df, numeric_cols.tolist(), save_path=os.path.join(output_dir, 'box_plot.png'))
        plt.close(fig)
    
    # Bar charts for categorical columns with numeric aggregations
    for cat_col in categorical_cols:
        for num_col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            grouped = df.groupby(cat_col)[num_col].mean().reset_index()
            if len(grouped) <= 20:  # Only plot if not too many categories
                fig = create_bar_chart(grouped, cat_col, num_col, 
                                     save_path=os.path.join(output_dir, f'{cat_col}_{num_col}_bar.png'))
                plt.close(fig)