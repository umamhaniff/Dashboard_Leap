"""
Data loading module for Dashboard Leap.
Handles loading data from various sources: CSV, Excel, databases, etc.
"""

import pandas as pd
import os
from typing import Optional
from .api.fetch import fetch_from_api, fetch_from_database

def load_data(source: str = "csv", file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load data from specified source.
    
    Args:
        source: Data source type ('csv', 'excel', 'api', 'database')
        file_path: Path to file if loading from file
        
    Returns:
        Loaded DataFrame
    """
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
    
    if source == "csv":
        if file_path is None:
            # Load default CSV file
            csv_files = [f for f in os.listdir(os.path.join(data_dir, 'csv')) if f.endswith('.csv')]
            if csv_files:
                file_path = os.path.join(data_dir, 'csv', csv_files[0])
            else:
                raise FileNotFoundError("No CSV files found in data/raw/csv/")
        
        return pd.read_csv(file_path)
    
    elif source == "excel":
        if file_path is None:
            excel_files = [f for f in os.listdir(os.path.join(data_dir, 'sheets')) if f.endswith(('.xlsx', '.xls'))]
            if excel_files:
                file_path = os.path.join(data_dir, 'sheets', excel_files[0])
            else:
                raise FileNotFoundError("No Excel files found in data/raw/sheets/")
        
        return pd.read_excel(file_path)
    
    elif source == "api":
        # Fetch from API
        data = fetch_from_api("data_endpoint")
        return pd.DataFrame(data)
    
    elif source == "database":
        # Fetch from database
        data = fetch_from_database("SELECT * FROM table_name")
        return pd.DataFrame(data)
    
    else:
        raise ValueError(f"Unsupported data source: {source}")

def load_multiple_sources() -> pd.DataFrame:
    """
    Load and combine data from multiple sources.
    
    Returns:
        Combined DataFrame
    """
    dfs = []
    
    # Try loading from CSV
    try:
        df_csv = load_data("csv")
        dfs.append(df_csv)
    except FileNotFoundError:
        pass
    
    # Try loading from Excel
    try:
        df_excel = load_data("excel")
        dfs.append(df_excel)
    except FileNotFoundError:
        pass
    
    if not dfs:
        raise FileNotFoundError("No data sources found")
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df