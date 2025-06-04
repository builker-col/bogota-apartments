"""
ETL Data Extractors Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides classes for extracting data from various sources.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import geopandas as gpd
import pandas as pd
import pymongo
import requests

from .config import ETLConfig
from .utils import normalize_text

logger = logging.getLogger(__name__)


class MongoDBExtractor:
    """Extract data from MongoDB collections"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.client: Optional[pymongo.MongoClient] = None
        self.db = None
    
    def connect(self) -> bool:
        """Connect to MongoDB with error handling"""
        try:
            self.client = pymongo.MongoClient(self.config.mongo_uri)
            self.db = self.client[self.config.mongo_database]
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def extract_raw_data(self) -> pd.DataFrame:
        """Extract raw apartment data from MongoDB"""
        if not self.connect():
            raise ConnectionError("Failed to connect to MongoDB")
        
        try:
            collection = self.db[self.config.mongo_collection_raw]
            raw_data = list(collection.find())
            
            if not raw_data:
                logger.error("No raw data found in MongoDB")
                return pd.DataFrame()
            
            df = pd.DataFrame(raw_data)
            df = df.drop(columns=['_id'], errors='ignore')
            logger.info(f"Extracted {len(df)} raw records from MongoDB")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting data from MongoDB: {e}")
            raise
        finally:
            if self.client:
                self.client.close()


class GeospatialDataExtractor:
    """Extract geospatial data from various file formats"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.external_data: Dict[str, gpd.GeoDataFrame] = {}
    
    def load_all_external_data(self) -> Dict[str, gpd.GeoDataFrame]:
        """Load all external geospatial datasets"""
        logger.info("Loading external datasets...")
        
        try:
            # Load localities
            self._load_localities()
            
            # Load neighborhoods
            self._load_neighborhoods()
            
            # Load parks
            self._load_parks()
            
            # Load shopping malls
            self._load_shopping_malls()
            
            return self.external_data
            
        except Exception as e:
            logger.error(f"Error loading external data: {e}")
            raise
    
    def _load_localities(self):
        """Load Bogotá localities from shapefile"""
        localidades_path = self.config.external_data_dir / "localidades_bogota" / "loca.shp"
        
        if localidades_path.exists():
            try:
                self.external_data['localidades'] = gpd.read_file(localidades_path)
                logger.info(f"Loaded {len(self.external_data['localidades'])} localities")
            except Exception as e:
                logger.warning(f"Failed to load localities: {e}")
        else:
            logger.warning(f"Localities file not found: {localidades_path}")
    
    def _load_neighborhoods(self):
        """Load Bogotá neighborhoods from geojson"""
        barrios_path = self.config.external_data_dir / "barrios_bogota" / "barrios.geojson"
        
        if barrios_path.exists():
            try:
                barrios_gdf = gpd.read_file(barrios_path)
                
                # Normalize text fields
                if 'barriocomu' in barrios_gdf.columns:
                    barrios_gdf['barriocomu'] = barrios_gdf['barriocomu'].apply(normalize_text)
                
                if 'localidad' in barrios_gdf.columns:
                    barrios_gdf['localidad'] = barrios_gdf['localidad'].apply(normalize_text)
                    
                    # Fix known issues
                    barrios_gdf.loc[
                        barrios_gdf['localidad'] == 'RAFAEL URIBE', 'localidad'
                    ] = 'RAFAEL URIBE URIBE'
                    
                    barrios_gdf.loc[
                        barrios_gdf['localidad'].isna(), 'localidad'
                    ] = 'SUBA'
                
                self.external_data['barrios'] = barrios_gdf
                logger.info(f"Loaded {len(self.external_data['barrios'])} neighborhoods")
                
            except Exception as e:
                logger.warning(f"Failed to load neighborhoods: {e}")
        else:
            logger.warning(f"Neighborhoods file not found: {barrios_path}")
    
    def _load_parks(self):
        """Load parks data from CSV"""
        parks_path = self.config.external_data_dir / "espacios_para_deporte_bogota" / "directorio-parques-y-escenarios-2023-datos-abiertos-v1.0.csv"
        
        if parks_path.exists():
            try:
                parks_df = pd.read_csv(parks_path)
                self.external_data['parques'] = parks_df
                logger.info(f"Loaded {len(self.external_data['parques'])} parks")
            except Exception as e:
                logger.warning(f"Failed to load parks: {e}")
        else:
            logger.warning(f"Parks file not found: {parks_path}")
    
    def _load_shopping_malls(self):
        """Load shopping malls data from CSV"""
        malls_path = self.config.external_data_dir / "centros_comerciales_bogota" / "centros_comerciales_bogota.csv"
        
        if malls_path.exists():
            try:
                malls_df = pd.read_csv(malls_path)
                
                # Validate required columns
                required_cols = ['NAME', 'LATITUD', 'LONGITUD', 'LOCALIDAD']
                if all(col in malls_df.columns for col in required_cols):
                    # Remove any rows with missing coordinates
                    malls_df = malls_df.dropna(subset=['LATITUD', 'LONGITUD'])
                    
                    self.external_data['centros_comerciales'] = malls_df
                    logger.info(f"Loaded {len(self.external_data['centros_comerciales'])} shopping malls")
                else:
                    logger.warning(f"Shopping malls file missing required columns: {required_cols}")
                    
            except Exception as e:
                logger.warning(f"Failed to load shopping malls: {e}")
        else:
            logger.warning(f"Shopping malls file not found: {malls_path}")


class TransMilenioExtractor:
    """Extract TransMilenio stations data from API"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
    
    def extract_stations(self) -> pd.DataFrame:
        """Extract TransMilenio stations data with caching"""
        cache_file = self.config.interim_data_dir / "transmilenio_stations.csv"
        
        # Check if cached data exists and is recent (less than 30 days)
        if cache_file.exists():
            cache_age = (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days
            if cache_age < 30:
                try:
                    stations_df = pd.read_csv(cache_file)
                    logger.info(f"Loaded {len(stations_df)} TransMilenio stations from cache")
                    return stations_df
                except Exception as e:
                    logger.warning(f"Failed to load cached TransMilenio data: {e}")
        
        # Fetch fresh data from API
        try:
            url = 'https://gis.transmilenio.gov.co/arcgis/rest/services/Troncal/consulta_estaciones_troncales/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
            
            logger.info("Fetching TransMilenio stations from API...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'features' not in data:
                logger.error("Invalid API response format")
                return pd.DataFrame()
            
            stations_df = pd.DataFrame(data['features'])
            stations_df = pd.json_normalize(stations_df['attributes'])
            
            # Cache the data
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            stations_df.to_csv(cache_file, index=False)
            
            logger.info(f"Loaded {len(stations_df)} TransMilenio stations from API")
            return stations_df
            
        except Exception as e:
            logger.error(f"Failed to load TransMilenio stations: {e}")
            # Return empty DataFrame as fallback
            return pd.DataFrame()


class ImageExtractor:
    """Extract and process image data from apartment records"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
    
    def extract_images(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract images data from apartment DataFrame"""
        if 'imagenes' not in df.columns:
            logger.info("No images column found")
            return pd.DataFrame()
        
        try:
            # Extract and normalize images
            images_df = df[['codigo', 'imagenes']].explode('imagenes').dropna(subset=['imagenes'])
            images_df = images_df.rename(columns={'imagenes': 'url_imagen'})
            
            images_file = self.config.processed_data_dir / "images.csv"
            images_df.to_csv(images_file, index=False)
            
            logger.info(f"Extracted and saved {len(images_df)} image records")
            return images_df
            
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return pd.DataFrame()


class DataExtractor:
    """Main data extractor orchestrator"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.mongodb_extractor = MongoDBExtractor(config)
        self.geospatial_extractor = GeospatialDataExtractor(config)
        self.transmilenio_extractor = TransMilenioExtractor(config)
        self.image_extractor = ImageExtractor(config)
    
    def extract_all_data(self) -> tuple[pd.DataFrame, Dict]:
        """Extract all required data for the ETL pipeline"""
        logger.info("Starting data extraction phase...")
        
        try:
            # Extract main apartment data
            apartments_df = self.mongodb_extractor.extract_raw_data()
            
            # Extract external geospatial data
            external_data = self.geospatial_extractor.load_all_external_data()
            
            # Extract TransMilenio data
            transmilenio_df = self.transmilenio_extractor.extract_stations()
            external_data['transmilenio'] = transmilenio_df
            
            # Extract images (this also processes them)
            self.image_extractor.extract_images(apartments_df)
            
            # Remove images column from main DataFrame to avoid processing issues
            apartments_df = apartments_df.drop(columns=['imagenes'], errors='ignore')
            
            logger.info("Data extraction phase completed successfully")
            return apartments_df, external_data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            raise 