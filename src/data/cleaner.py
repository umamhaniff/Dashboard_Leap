"""
Data cleaning module for Dashboard Leap.
Handles data preprocessing: missing values, duplicates, outliers, etc.
"""

import pandas as pd
import numpy as np
from typing import List, Optional

def clean_data(df: pd.DataFrame, 
               handle_missing: str = "drop", 
               remove_duplicates: bool = True,
               outlier_method: Optional[str] = None) -> pd.DataFrame:
    """
    Clean the input DataFrame.
    
    Args:
        df: Input DataFrame
        handle_missing: How to handle missing values ('drop', 'fill_mean', 'fill_median', 'fill_mode')
        remove_duplicates: Whether to remove duplicate rows
        outlier_method: Method to handle outliers ('iqr', 'zscore', None)
        
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Handle missing values
    if handle_missing == "drop":
        df_clean = df_clean.dropna()
    elif handle_missing == "fill_mean":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
    elif handle_missing == "fill_median":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
    elif handle_missing == "fill_mode":
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(df_clean[col].mode().iloc[0] if not df_clean[col].mode().empty else df_clean[col])
    
    # Remove duplicates
    if remove_duplicates:
        df_clean = df_clean.drop_duplicates()
    
    # Handle outliers
    if outlier_method == "iqr":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
    elif outlier_method == "zscore":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
            df_clean = df_clean[z_scores < 3]
    
    return df_clean

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names: lowercase, replace spaces with underscores.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with standardized column names
    """
    df_standardized = df.copy()
    df_standardized.columns = df_standardized.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    return df_standardized

def convert_data_types(df: pd.DataFrame, type_conversions: dict = None) -> pd.DataFrame:
    """
    Convert data types of columns.
    
    Args:
        df: Input DataFrame
        type_conversions: Dict mapping column names to target data types
        
    Returns:
        DataFrame with converted data types
    """
    if type_conversions is None:
        type_conversions = {}
    
    df_converted = df.copy()
    
    for col, dtype in type_conversions.items():
        if col in df_converted.columns:
            df_converted[col] = df_converted[col].astype(dtype)
    
    return df_converted