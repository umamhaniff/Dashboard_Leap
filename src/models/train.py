"""
Model training module for Dashboard Leap.
Handles training machine learning models.
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from typing import Dict, Any, Optional

class ModelTrainer:
    def __init__(self, model_type: str = "classification"):
        """
        Initialize model trainer.
        
        Args:
            model_type: Type of model ('classification' or 'regression')
        """
        self.model_type = model_type
        self.model = None
        self.feature_names = None
    
    def prepare_data(self, df: pd.DataFrame, 
                    target_col: str, 
                    test_size: float = 0.2,
                    random_state: int = 42) -> tuple:
        """
        Prepare data for training.
        
        Args:
            df: Input DataFrame
            target_col: Target column name
            test_size: Test set size
            random_state: Random state for reproducibility
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")
        
        X = df.drop(target_col, axis=1)
        y = df[target_col]
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        return train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series, 
                   model_name: str = "random_forest") -> Any:
        """
        Train the model.
        
        Args:
            X_train: Training features
            y_train: Training target
            model_name: Name of the model to train
            
        Returns:
            Trained model
        """
        if self.model_type == "classification":
            if model_name == "random_forest":
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_name == "logistic_regression":
                self.model = LogisticRegression(random_state=42)
            else:
                raise ValueError(f"Unsupported classification model: {model_name}")
        elif self.model_type == "regression":
            if model_name == "random_forest":
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_name == "linear_regression":
                self.model = LinearRegression()
            else:
                raise ValueError(f"Unsupported regression model: {model_name}")
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        self.model.fit(X_train, y_train)
        return self.model
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """
        Evaluate the trained model.
        
        Args:
            X_test: Test features
            y_test: Test target
            
        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        y_pred = self.model.predict(X_test)
        
        metrics = {}
        
        if self.model_type == "classification":
            metrics['accuracy'] = accuracy_score(y_test, y_pred)
            metrics['classification_report'] = classification_report(y_test, y_pred, output_dict=True)
        elif self.model_type == "regression":
            metrics['mse'] = mean_squared_error(y_test, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])
        
        return metrics
    
    def save_model(self, filepath: str):
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str) -> Any:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            Loaded model
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.model_type = model_data['model_type']
        self.feature_names = model_data['feature_names']
        
        return self.model

def train_model_pipeline(df: pd.DataFrame, 
                        target_col: str, 
                        model_type: str = "classification",
                        model_name: str = "random_forest") -> Dict[str, Any]:
    """
    Complete model training pipeline.
    
    Args:
        df: Input DataFrame
        target_col: Target column name
        model_type: Type of model
        model_name: Name of the model
        
    Returns:
        Dictionary with trained model and evaluation metrics
    """
    trainer = ModelTrainer(model_type)
    
    # Prepare data
    X_train, X_test, y_train, y_test = trainer.prepare_data(df, target_col)
    
    # Train model
    model = trainer.train_model(X_train, y_train, model_name)
    
    # Evaluate model
    metrics = trainer.evaluate_model(X_test, y_test)
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_model.pkl')
    trainer.save_model(model_path)
    
    return {
        'model': model,
        'metrics': metrics,
        'trainer': trainer
    }