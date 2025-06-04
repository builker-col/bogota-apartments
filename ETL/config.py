"""
ETL Configuration Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides centralized configuration management for the ETL pipeline.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ETLConfig:
    """Configuration class for ETL pipeline"""
    
    # MongoDB Configuration
    mongo_uri: str
    mongo_database: str
    mongo_collection_raw: str
    mongo_collection_processed: str
    
    # Directory Configuration
    data_dir: Path = Path("data")
    external_data_dir: Path = Path("data/external")
    interim_data_dir: Path = Path("data/interim")
    processed_data_dir: Path = Path("data/processed")
    logs_dir: Path = Path("logs")
    
    # Processing Configuration
    chunk_size: int = 1000
    max_workers: int = os.cpu_count() or 4
    
    # Geospatial Configuration
    bogota_bounds: dict = None
    
    def __post_init__(self):
        """Initialize derived configurations"""
        if self.bogota_bounds is None:
            # Bogotá coordinate bounds (slightly expanded for safety)
            self.bogota_bounds = {
                'lat_min': 3.8,
                'lat_max': 5.2,
                'lon_min': -74.8,
                'lon_max': -73.2
            }
    
    @classmethod
    def from_env(cls) -> 'ETLConfig':
        """Create configuration from environment variables"""
        return cls(
            mongo_uri=os.getenv('MONGO_URI', ''),
            mongo_database=os.getenv('MONGO_DATABASE', 'bogota_apartments'),
            mongo_collection_raw=os.getenv('MONGO_COLLECTION_RAW', 'scrapy_bogota_apartments'),
            mongo_collection_processed=os.getenv('MONGO_COLLECTION_PROCESSED', 'scrapy_bogota_apartments_processed')
        )
    
    def setup_directories(self):
        """Create necessary directories"""
        for directory in [
            self.interim_data_dir, 
            self.processed_data_dir,
            self.logs_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.mongo_uri:
            raise ValueError("MONGO_URI not configured. Check your .env file")
        
        return True


# Global configuration instance
config = ETLConfig.from_env() 