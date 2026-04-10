"""
Model prediction module for Dashboard Leap.
Handles making predictions using trained models.
"""

import pandas as pd
import pickle
import os
from typing import Any, List, Optional
from .train import ModelTrainer

class ModelPredictor:
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize predictor.
        
        Args:
            model_path: Path to the saved model
        """
        self.model = None
        self.model_type = None
        self.feature_names = None
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.model_type = model_data['model_type']
        self.feature_names = model_data['feature_names']
    
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions using the loaded model.
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Ensure input has correct features
        if self.feature_names:
            missing_features = set(self.feature_names) - set(X.columns)
            if missing_features:
                raise ValueError(f"Missing features: {missing_features}")
            
            # Reorder columns to match training order
            X = X[self.feature_names]
        
        predictions = self.model.predict(X)
        return pd.Series(predictions, index=X.index, name='predictions')
    
    def predict_proba(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Make probability predictions for classification models.
        
        Args:
            X: Input features
            
        Returns:
            Prediction probabilities
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        if self.model_type != "classification":
            raise ValueError("predict_proba only available for classification models")
        
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("Model does not support probability predictions")
        
        # Ensure input has correct features
        if self.feature_names:
            missing_features = set(self.feature_names) - set(X.columns)
            if missing_features:
                raise ValueError(f"Missing features: {missing_features}")
            
            # Reorder columns to match training order
            X = X[self.feature_names]
        
        probabilities = self.model.predict_proba(X)
        
        # Create DataFrame with class probabilities
        if hasattr(self.model, 'classes_'):
            columns = [f"prob_class_{cls}" for cls in self.model.classes_]
        else:
            columns = [f"prob_class_{i}" for i in range(probabilities.shape[1])]
        
        return pd.DataFrame(probabilities, index=X.index, columns=columns)
    
    def get_feature_importance(self) -> Optional[pd.Series]:
        """
        Get feature importance if available.
        
        Returns:
            Series with feature importance scores
        """
        if self.model is None:
            return None
        
        if hasattr(self.model, 'feature_importances_'):
            return pd.Series(self.model.feature_importances_, 
                           index=self.feature_names, 
                           name='importance')
        elif hasattr(self.model, 'coef_'):
            # For linear models
            return pd.Series(np.abs(self.model.coef_.flatten()), 
                           index=self.feature_names, 
                           name='importance')
        else:
            return None

def predict(df: pd.DataFrame, 
           model_path: Optional[str] = None,
           target_col: Optional[str] = None) -> pd.DataFrame:
    """
    Main prediction function.
    
    Args:
        df: Input DataFrame
        model_path: Path to the saved model
        target_col: Target column to exclude from features (if present)
        
    Returns:
        DataFrame with predictions
    """
    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_model.pkl')
    
    predictor = ModelPredictor(model_path)
    
    # Prepare features
    if target_col and target_col in df.columns:
        X = df.drop(target_col, axis=1)
    else:
        X = df
    
    # Make predictions
    predictions = predictor.predict(X)
    
    # Combine with original data
    result = df.copy()
    result['predictions'] = predictions
    
    return result

def batch_predict(data_list: List[pd.DataFrame], 
                 model_path: Optional[str] = None) -> List[pd.DataFrame]:
    """
    Make predictions on multiple datasets.
    
    Args:
        data_list: List of DataFrames to predict on
        model_path: Path to the saved model
        
    Returns:
        List of DataFrames with predictions
    """
    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_model.pkl')
    
    predictor = ModelPredictor(model_path)
    
    results = []
    for df in data_list:
        predictions = predictor.predict(df)
        result = df.copy()
        result['predictions'] = predictions
        results.append(result)
    
    return results