"""
Streamlit Dashboard for Financial Analysis

Interactive web interface for the three-agent financial analysis system.
"""

from .main_app import main
from .components.query_interface import QueryInterface
from .components.analysis_display import AnalysisDisplay
from .components.visualization import VisualizationComponent

__all__ = ["main", "QueryInterface", "AnalysisDisplay", "VisualizationComponent"]