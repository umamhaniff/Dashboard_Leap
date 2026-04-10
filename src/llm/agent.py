"""
LLM integration module for Dashboard Leap.
Provides AI-powered analysis and insights using Google Generative AI.
"""

import google.generativeai as genai
import os
import yaml
from typing import Optional, Dict, Any
import pandas as pd

def load_config() -> Dict[str, Any]:
    """Load configuration from db.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'db.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def initialize_llm(api_key: Optional[str] = None) -> genai.GenerativeModel:
    """
    Initialize the Google Generative AI model.
    
    Args:
        api_key: API key for Google AI (optional, will use config if not provided)
        
    Returns:
        Initialized GenerativeModel
    """
    if api_key is None:
        config = load_config()
        api_key = config.get('api', {}).get('key')
    
    if not api_key:
        raise ValueError("API key not found. Please provide API key or set it in config/db.yaml")
    
    genai.configure(api_key=api_key)
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-pro')
    
    return model

def analyze_data_with_llm(df: pd.DataFrame, 
                         query: str, 
                         model: Optional[genai.GenerativeModel] = None) -> str:
    """
    Analyze data using LLM based on user query.
    
    Args:
        df: Input DataFrame
        query: User's analysis query
        model: Pre-initialized model (optional)
        
    Returns:
        LLM analysis response
    """
    if model is None:
        model = initialize_llm()
    
    # Create data summary for context
    data_summary = create_data_summary(df)
    
    # Construct prompt
    prompt = f"""
You are a data analysis expert. Analyze the following dataset and answer the user's query.

Dataset Summary:
{data_summary}

User Query: {query}

Please provide a comprehensive analysis including:
1. Key insights from the data
2. Statistical observations
3. Recommendations based on the data
4. Any potential concerns or limitations

Be specific and reference actual data points where possible.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error in LLM analysis: {str(e)}"

def create_data_summary(df: pd.DataFrame) -> str:
    """
    Create a summary of the dataset for LLM context.
    
    Args:
        df: Input DataFrame
        
    Returns:
        String summary of the data
    """
    summary = f"""
Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns

Column Information:
"""
    
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].count()
        null_count = df[col].isnull().sum()
        
        summary += f"- {col}: {dtype}, {non_null} non-null values"
        if null_count > 0:
            summary += f", {null_count} null values"
        summary += "\n"
        
        # Add basic statistics for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            summary += f"  Stats: mean={df[col].mean():.2f}, std={df[col].std():.2f}, min={df[col].min():.2f}, max={df[col].max():.2f}\n"
        elif pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == 'object':
            unique_vals = df[col].nunique()
            summary += f"  Unique values: {unique_vals}"
            if unique_vals <= 10:
                top_vals = df[col].value_counts().head(3)
                summary += f", Top values: {', '.join([f'{val} ({count})' for val, count in top_vals.items()])}"
            summary += "\n"
    
    return summary

def generate_insights(df: pd.DataFrame, 
                     model: Optional[genai.GenerativeModel] = None) -> str:
    """
    Generate automatic insights from the dataset.
    
    Args:
        df: Input DataFrame
        model: Pre-initialized model (optional)
        
    Returns:
        Generated insights
    """
    if model is None:
        model = initialize_llm()
    
    data_summary = create_data_summary(df)
    
    prompt = f"""
Analyze this dataset and provide key insights and observations:

{data_summary}

Please provide:
1. Overall data quality assessment
2. Key patterns or trends
3. Potential areas for further analysis
4. Any data quality issues or concerns
5. Suggestions for modeling or visualization

Focus on actionable insights that would be valuable for business or research purposes.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def ask_llm_question(question: str, 
                    context: Optional[str] = None,
                    model: Optional[genai.GenerativeModel] = None) -> str:
    """
    Ask a general question to the LLM with optional context.
    
    Args:
        question: Question to ask
        context: Additional context
        model: Pre-initialized model (optional)
        
    Returns:
        LLM response
    """
    if model is None:
        model = initialize_llm()
    
    prompt = f"Question: {question}"
    if context:
        prompt = f"Context: {context}\n\n{prompt}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_with_llm(query: str, df: Optional[pd.DataFrame] = None) -> str:
    """
    Main function for LLM analysis.
    
    Args:
        query: User's query
        df: Optional DataFrame for data-specific analysis
        
    Returns:
        Analysis result
    """
    try:
        model = initialize_llm()
        
        if df is not None:
            return analyze_data_with_llm(df, query, model)
        else:
            return ask_llm_question(query, model=model)
    except Exception as e:
        return f"LLM analysis failed: {str(e)}. Please check your API key configuration."