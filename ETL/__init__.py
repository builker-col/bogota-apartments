"""
ETL Package for Bogota Apartments
Author: Erik Garcia (@erik172)
Version: 3.0.0

This package provides a modular ETL pipeline for processing apartment data 
from Bogota real estate websites.
"""

from .config import ETLConfig, config
from .main_etl import BogotaETLPipeline, run_etl_pipeline
from .models import ApartmentModel, ValidationResult

__version__ = "3.0.0"
__author__ = "Erik Garcia (@erik172)"

__all__ = [
    "ETLConfig",
    "config", 
    "BogotaETLPipeline",
    "run_etl_pipeline",
    "ApartmentModel", 
    "ValidationResult"
]
