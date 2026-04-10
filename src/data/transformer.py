"""
Data transformation module for Dashboard Leap.
Handles data transformation: feature engineering, scaling, encoding, etc.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_regression
from typing import List, Optional

class DataTransformer:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
    
    def scale_features(self, df: pd.DataFrame, 
                      columns: List[str], 
                      method: str = "standard") -> pd.DataFrame:
        """
        Scale numerical features.
        
        Args:
            df: Input DataFrame
            columns: Columns to scale
            method: Scaling method ('standard', 'minmax')
            
        Returns:
            DataFrame with scaled features
        """
        df_scaled = df.copy()
        
        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unsupported scaling method: {method}")
        
        df_scaled[columns] = scaler.fit_transform(df_scaled[columns])
        self.scalers[method] = scaler
        
        return df_scaled
    
    def encode_categorical(self, df: pd.DataFrame, 
                          columns: List[str], 
                          method: str = "label") -> pd.DataFrame:
        """
        Encode categorical features.
        
        Args:
            df: Input DataFrame
            columns: Columns to encode
            method: Encoding method ('label', 'onehot')
            
        Returns:
            DataFrame with encoded features
        """
        df_encoded = df.copy()
        
        if method == "label":
            for col in columns:
                encoder = LabelEncoder()
                df_encoded[col] = encoder.fit_transform(df_encoded[col])
                self.encoders[col] = encoder
        elif method == "onehot":
            for col in columns:
                encoder = OneHotEncoder(sparse=False, drop='first')
                encoded = encoder.fit_transform(df_encoded[[col]])
                encoded_df = pd.DataFrame(encoded, columns=[f"{col}_{i}" for i in range(encoded.shape[1])])
                df_encoded = pd.concat([df_encoded.drop(col, axis=1), encoded_df], axis=1)
                self.encoders[col] = encoder
        
        return df_encoded
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features from existing data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with additional features
        """
        df_featured = df.copy()
        
        # Example feature engineering
        numeric_cols = df_featured.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            # Create interaction features
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    df_featured[f"{col1}_{col2}_interaction"] = df_featured[col1] * df_featured[col2]
        
        # Create polynomial features (degree 2)
        for col in numeric_cols:
            df_featured[f"{col}_squared"] = df_featured[col] ** 2
        
        return df_featured
    
    def select_features(self, df: pd.DataFrame, 
                       target_col: str, 
                       k: int = 10) -> pd.DataFrame:
        """
        Select top k features using statistical tests.
        
        Args:
            df: Input DataFrame
            target_col: Target column name
            k: Number of features to select
            
        Returns:
            DataFrame with selected features
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")
        
        X = df.drop(target_col, axis=1)
        y = df[target_col]
        
        # Use only numeric columns for feature selection
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X_numeric = X[numeric_cols]
        
        if len(numeric_cols) <= k:
            return df
        
        selector = SelectKBest(score_func=f_regression, k=k)
        X_selected = selector.fit_transform(X_numeric, y)
        
        selected_features = X_numeric.columns[selector.get_support()].tolist()
        selected_features.append(target_col)
        
        return df[selected_features]

def transform_data(df: pd.DataFrame, 
                  scale_columns: List[str] = None,
                  encode_columns: List[str] = None,
                  create_features: bool = False,
                  select_features: bool = False,
                  target_col: str = None) -> pd.DataFrame:
    """
    Main transformation function.
    
    Args:
        df: Input DataFrame
        scale_columns: Columns to scale
        encode_columns: Columns to encode
        create_features: Whether to create new features
        select_features: Whether to perform feature selection
        target_col: Target column for feature selection
        
    Returns:
        Transformed DataFrame
    """
    transformer = DataTransformer()
    df_transformed = df.copy()
    
    # Scale features
    if scale_columns:
        df_transformed = transformer.scale_features(df_transformed, scale_columns)
    
    # Encode categorical features
    if encode_columns:
        df_transformed = transformer.encode_categorical(df_transformed, encode_columns)
    
    # Create new features
    if create_features:
        df_transformed = transformer.create_features(df_transformed)
    
    # Select features
    if select_features and target_col:
        df_transformed = transformer.select_features(df_transformed, target_col)
    
    return df_transformed