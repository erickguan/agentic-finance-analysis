"""
Financial Analysis AI - Main Application Entry Point

Launch the Streamlit dashboard for comprehensive stock analysis.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main dashboard
from dashboard.main_app import safe_main

if __name__ == "__main__":
    safe_main()