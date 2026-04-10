"""
Main entry point for the Dashboard Leap project.
This script orchestrates the data pipeline and launches the Streamlit dashboard.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.app import run_dashboard

if __name__ == "__main__":
    print("Starting Dashboard Leap...")
    run_dashboard()