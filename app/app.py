"""
Streamlit dashboard application for Dashboard Leap.
Provides interactive visualizations and data insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
from src.data.loader import load_data
from src.data.cleaner import clean_data
from src.data.transformer import transform_data
from src.models.predict import predict
from src.visualization.interactive import create_interactive_plot
from src.llm.agent import analyze_with_llm

def run_dashboard():
    st.title("Dashboard Leap - Data Analytics Platform")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Overview", "Data Exploration", "Model Prediction", "LLM Analysis"])
    
    if page == "Overview":
        st.header("Project Overview")
        st.write("Welcome to Dashboard Leap! This platform provides comprehensive data analytics and machine learning insights.")
        
        # Load and display sample data
        try:
            data = load_data()
            st.subheader("Sample Data Preview")
            st.dataframe(data.head())
        except Exception as e:
            st.error(f"Error loading data: {e}")
    
    elif page == "Data Exploration":
        st.header("Data Exploration")
        
        # Load data
        data = load_data()
        cleaned_data = clean_data(data)
        transformed_data = transform_data(cleaned_data)
        
        st.subheader("Data Processing Pipeline")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Raw Data Rows", len(data))
        with col2:
            st.metric("Cleaned Data Rows", len(cleaned_data))
        with col3:
            st.metric("Transformed Data Rows", len(transformed_data))
        
        # Interactive visualization
        st.subheader("Interactive Visualization")
        fig = create_interactive_plot(transformed_data)
        st.plotly_chart(fig)
    
    elif page == "Model Prediction":
        st.header("Model Predictions")
        
        # Load data and make predictions
        data = load_data()
        cleaned_data = clean_data(data)
        transformed_data = transform_data(cleaned_data)
        
        predictions = predict(transformed_data)
        
        st.subheader("Prediction Results")
        st.write(predictions.head())
        
        # Visualization of predictions
        st.subheader("Prediction Distribution")
        st.bar_chart(predictions.value_counts())
    
    elif page == "LLM Analysis":
        st.header("LLM-Powered Analysis")
        
        user_query = st.text_input("Enter your analysis query:")
        
        if st.button("Analyze"):
            if user_query:
                analysis = analyze_with_llm(user_query)
                st.write("LLM Analysis Result:")
                st.write(analysis)
            else:
                st.warning("Please enter a query.")

if __name__ == "__main__":
    run_dashboard()