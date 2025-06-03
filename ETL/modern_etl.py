"""
ETL Pipeline for Bogota Apartments
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides the main ETL pipeline for processing apartment data 
from Bogota real estate websites. Features include:
- Data validation with Pydantic
- Parallel processing with concurrent.futures
- Vectorized operations for performance
- Robust error handling and logging
- Memory-efficient processing
- Geospatial enrichment
- Configuration management
"""

import asyncio
import logging
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import pymongo
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator
from tqdm import tqdm
from unidecode import unidecode

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ETLConfig:
    """Configuration for ETL pipeline"""
    mongo_uri: str
    mongo_database: str
    mongo_collection_raw: str
    mongo_collection_processed: str
    data_dir: Path = Path("data")
    external_data_dir: Path = Path("data/external")
    interim_data_dir: Path = Path("data/interim")
    processed_data_dir: Path = Path("data/processed")
    chunk_size: int = 1000
    max_workers: int = os.cpu_count() or 4


class ApartmentModel(BaseModel):
    """Pydantic model for apartment data validation"""
    codigo: Optional[Union[str, int]] = None
    tipo_propiedad: Optional[str] = None
    tipo_operacion: Optional[str] = None
    precio_venta: Optional[float] = None
    precio_arriendo: Optional[float] = None
    area: Optional[float] = None
    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    administracion: Optional[float] = None
    parqueaderos: Optional[int] = None
    sector: Optional[str] = None
    estrato: Optional[int] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    descripcion: Optional[str] = None
    
    @field_validator('codigo')
    @classmethod
    def validate_codigo(cls, v):
        if v is not None:
            # Convertir números a string para consistencia
            return str(v)
        return v
    
    @field_validator('estrato')
    @classmethod
    def validate_estrato(cls, v):
        if v is not None and not (1 <= v <= 6):
            logger.warning(f"Invalid estrato value: {v}")
            return None
        return v
    
    @field_validator('latitud')
    @classmethod
    def validate_latitud(cls, v):
        if v is not None and not pd.isna(v) and not (-90 <= v <= 90):
            logger.debug(f"Invalid latitude value: {v}")
            return None
        if pd.isna(v):
            return None
        return v
    
    @field_validator('longitud')
    @classmethod
    def validate_longitud(cls, v):
        if v is not None and not pd.isna(v) and not (-180 <= v <= 180):
            logger.debug(f"Invalid longitude value: {v}")
            return None
        if pd.isna(v):
            return None
        return v


class BogotaETLPipeline:
    """ETL Pipeline for Bogota Apartments data processing"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.setup_directories()
        self.mongo_client = None
        self.db = None
        self.external_data = {}
        
    def setup_directories(self):
        """Create necessary directories"""
        for directory in [self.config.interim_data_dir, self.config.processed_data_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def connect_to_mongodb(self) -> bool:
        """Connect to MongoDB with error handling"""
        try:
            self.mongo_client = pymongo.MongoClient(self.config.mongo_uri)
            self.db = self.mongo_client[self.config.mongo_database]
            # Test connection
            self.mongo_client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def load_external_data(self):
        """Load external datasets (geofiles, etc.) with caching"""
        logger.info("Loading external datasets...")
        
        try:
            # Load localities
            localidades_path = self.config.external_data_dir / "localidades_bogota" / "loca.shp"
            if localidades_path.exists():
                self.external_data['localidades'] = gpd.read_file(localidades_path)
                logger.info(f"Loaded {len(self.external_data['localidades'])} localities")
            
            # Load neighborhoods
            barrios_path = self.config.external_data_dir / "barrios_bogota" / "barrios.geojson"
            if barrios_path.exists():
                self.external_data['barrios'] = gpd.read_file(barrios_path)
                self.external_data['barrios']['barriocomu'] = self.external_data['barrios']['barriocomu'].apply(self.normalize_text)
                self.external_data['barrios']['localidad'] = self.external_data['barrios']['localidad'].apply(self.normalize_text)
                # Fix known issues
                self.external_data['barrios'].loc[
                    self.external_data['barrios']['localidad'] == 'RAFAEL URIBE', 'localidad'
                ] = 'RAFAEL URIBE URIBE'
                self.external_data['barrios'].loc[
                    self.external_data['barrios']['localidad'].isna(), 'localidad'
                ] = 'SUBA'
                logger.info(f"Loaded {len(self.external_data['barrios'])} neighborhoods")
            
            # Load parks data
            parks_path = self.config.external_data_dir / "espacios_para_deporte_bogota" / "directorio-parques-y-escenarios-2023-datos-abiertos-v1.0.csv"
            if parks_path.exists():
                self.external_data['parques'] = pd.read_csv(parks_path)
                logger.info(f"Loaded {len(self.external_data['parques'])} parks")
            
            # Get TransMilenio stations (API call with caching)
            self.load_transmilenio_stations()
            
        except Exception as e:
            logger.error(f"Error loading external data: {e}")
            raise
    
    def load_transmilenio_stations(self):
        """Load TransMilenio stations data from API with caching"""
        cache_file = self.config.interim_data_dir / "transmilenio_stations.csv"
        
        if cache_file.exists() and (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days < 30:
            # Use cached data if less than 30 days old
            self.external_data['transmilenio'] = pd.read_csv(cache_file)
            logger.info(f"Loaded {len(self.external_data['transmilenio'])} TransMilenio stations from cache")
        else:
            try:
                url = 'https://gis.transmilenio.gov.co/arcgis/rest/services/Troncal/consulta_estaciones_troncales/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                stations_df = pd.DataFrame(data['features'])
                stations_df = pd.json_normalize(stations_df['attributes'])
                
                # Cache the data
                stations_df.to_csv(cache_file, index=False)
                self.external_data['transmilenio'] = stations_df
                logger.info(f"Loaded {len(self.external_data['transmilenio'])} TransMilenio stations from API")
                
            except Exception as e:
                logger.error(f"Failed to load TransMilenio stations: {e}")
                # Use empty DataFrame as fallback
                self.external_data['transmilenio'] = pd.DataFrame()
    
    @staticmethod
    def normalize_text(text) -> str:
        """Normalize text by removing accents and converting to uppercase"""
        try:
            return unidecode(str(text)).upper()
        except:
            return str(text)
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula (vectorized)"""
        R = 6371000  # Earth radius in meters
        
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def extract_features_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from characteristics column using vectorized operations"""
        logger.info("Extracting features from characteristics...")
        
        if 'caracteristicas' not in df.columns:
            logger.warning("No 'caracteristicas' column found, skipping feature extraction")
            return df
        
        # Fill NaN values with empty string for string operations
        caracteristicas = df['caracteristicas'].fillna('').astype(str).str.upper()
        
        # Vectorized feature extraction
        features = {
            'jacuzzi': caracteristicas.str.contains('JACUZZI|SPA', na=False),
            'piscina': caracteristicas.str.contains('PISCINA', na=False),
            'salon_comunal': caracteristicas.str.contains('SALON COMUNAL|SALÓN COMUNAL', na=False),
            'terraza': caracteristicas.str.contains('TERRAZA', na=False),
            'vigilancia': caracteristicas.str.contains('VIGILANCIA|PORTERIA', na=False),
            'chimenea': caracteristicas.str.contains('CHIMENEA', na=False),
            'permite_mascotas': caracteristicas.str.contains('MASCOTA|PET', na=False),
            'gimnasio': caracteristicas.str.contains('GIMNASIO|GYM', na=False),
            'ascensor': caracteristicas.str.contains('ASCENSOR|ELEVADOR', na=False),
            'conjunto_cerrado': caracteristicas.str.contains('CONJUNTO CERRADO|UNIDAD CERRADA', na=False),
        }
        
        # Extract numeric features
        piso_pattern = caracteristicas.str.extract(r'PISO (\d+)', expand=False)
        df['piso'] = pd.to_numeric(piso_pattern, errors='coerce')
        
        closets_pattern = caracteristicas.str.extract(r'(\d+) CLOSET', expand=False)
        df['closets'] = pd.to_numeric(closets_pattern, errors='coerce')
        
        # Add boolean features
        for feature_name, feature_values in features.items():
            df[feature_name] = feature_values.astype(int)
        
        # Drop original caracteristicas column
        df = df.drop(columns=['caracteristicas'], errors='ignore')
        
        logger.info(f"Extracted {len(features) + 2} features")
        return df
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate data using Pydantic models"""
        logger.info("Validating apartment data...")
        
        valid_records = []
        invalid_count = 0
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Validating records"):
            try:
                # Convert row to dict and validate
                row_dict = row.to_dict()
                apartment = ApartmentModel(**row_dict)
                valid_records.append(apartment.model_dump())
            except ValidationError as e:
                invalid_count += 1
                if invalid_count <= 5:  # Solo mostrar primeros 5 errores
                    logger.warning(f"Invalid record {row.get('codigo', f'index_{idx}')}: {e}")
                # En lugar de descartar completamente, mantener el registro original
                valid_records.append(row_dict)
        
        valid_df = pd.DataFrame(valid_records)
        logger.info(f"Processed {len(valid_df)} records, {invalid_count} had validation warnings")
        
        return valid_df
    
    def enrich_with_geospatial_data_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add geospatial enrichment using vectorized operations"""
        logger.info("Enriching data with geospatial information...")
        
        df['coords_modified'] = False
        
        # Add localidad and barrio from coordinates first
        df = self.add_locality_and_neighborhood(df)
        
        # Add TransMilenio station information (vectorized)
        if not self.external_data['transmilenio'].empty and 'latitud' in df.columns and 'longitud' in df.columns:
            df = self.add_transmilenio_info_vectorized(df)
        
        # Add parks information (vectorized)
        if 'parques' in self.external_data and not self.external_data['parques'].empty:
            df = self.add_parks_info_vectorized(df)
        
        return df
    
    def add_locality_and_neighborhood(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add localidad and barrio columns from coordinates and existing sector info"""
        logger.info("Adding locality and neighborhood information...")
        
        # Initialize columns if they don't exist
        if 'localidad' not in df.columns:
            df['localidad'] = None
        if 'barrio' not in df.columns:
            df['barrio'] = None
        
        # First, try to extract localidad from existing 'sector' field
        if 'sector' in df.columns:
            # Map common sector names to localities
            sector_to_localidad = {
                'USME': 'USME',
                'CIUDAD USME': 'USME',
                'KENNEDY': 'KENNEDY',
                'BOSA': 'BOSA',
                'SUBA': 'SUBA',
                'ENGATIVA': 'ENGATIVA',
                'FONTIBON': 'FONTIBON',
                'CHAPINERO': 'CHAPINERO',
                'ZONA ROSA': 'CHAPINERO',
                'EL PORVENIR': 'BOSA',
                'SAN CRISTOBAL': 'SAN CRISTOBAL',
                'RAFAEL URIBE': 'RAFAEL URIBE URIBE',
                'CIUDAD BOLIVAR': 'CIUDAD BOLIVAR',
                'SANTA FE': 'SANTA FE',
                'LA CANDELARIA': 'CANDELARIA',
                'TEUSAQUILLO': 'TEUSAQUILLO',
                'BARRIOS UNIDOS': 'BARRIOS UNIDOS',
                'PUENTE ARANDA': 'PUENTE ARANDA',
                'TUNJUELITO': 'TUNJUELITO',
                'ANTONIO NARIÑO': 'ANTONIO NARIÑO',
                'LOS MARTIRES': 'LOS MARTIRES'
            }
            
            for sector_name, localidad_name in sector_to_localidad.items():
                mask = df['sector'].str.contains(sector_name, case=False, na=False)
                df.loc[mask, 'localidad'] = localidad_name
                df.loc[mask, 'barrio'] = df.loc[mask, 'sector']  # Use sector as barrio for now
        
        # Try spatial join only for records without localidad and with valid coordinates
        missing_localidad = df['localidad'].isna()
        has_coords = df[['latitud', 'longitud']].notna().all(axis=1)
        needs_spatial = missing_localidad & has_coords
        
        if needs_spatial.sum() > 0 and 'localidades' in self.external_data:
            logger.info(f"Trying spatial join for {needs_spatial.sum()} records")
            try:
                from shapely.geometry import Point
                import geopandas as gpd
                
                subset_df = df.loc[needs_spatial, ['latitud', 'longitud']].copy()
                geometry = [Point(lon, lat) for lat, lon in zip(subset_df['latitud'], subset_df['longitud'])]
                apt_gdf = gpd.GeoDataFrame(subset_df, geometry=geometry, crs='EPSG:4326')
                
                localidades = self.external_data['localidades']
                apt_with_loc = gpd.sjoin(apt_gdf, localidades, how='left', predicate='within')
                
                # Find the locality name column
                loc_col = None
                for col in ['NOMBRE_LOC', 'localidad', 'LOCALIDAD', 'nombre', 'LocNombre']:
                    if col in apt_with_loc.columns:
                        loc_col = col
                        break
                
                if loc_col and not apt_with_loc[loc_col].isna().all():
                    # Only update the specific indices that need spatial join
                    df.loc[needs_spatial, 'localidad'] = apt_with_loc[loc_col].values
                    
            except Exception as e:
                logger.warning(f"Spatial join failed: {e}")
        
        localidad_count = df['localidad'].notna().sum()
        barrio_count = df['barrio'].notna().sum()
        logger.info(f"Added geographic info: {localidad_count} localities, {barrio_count} neighborhoods")
        
        return df
    
    def add_transmilenio_info_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add TransMilenio station information using vectorized operations"""
        logger.info("Adding TransMilenio station information...")
        
        stations = self.external_data['transmilenio']
        if stations.empty:
            logger.warning("No TransMilenio stations data available")
            return df
        
        # Prepare arrays for vectorized computation
        apt_coords = df[['latitud', 'longitud']].dropna()
        if apt_coords.empty:
            return df
        
        station_coords = stations[['latitud_estacion', 'longitud_estacion']].values
        station_names = stations['nombre_estacion'].values
        
        closest_stations = []
        min_distances = []
        
        # Process in chunks to manage memory
        chunk_size = 100
        for i in tqdm(range(0, len(apt_coords), chunk_size), desc="Processing TM stations"):
            chunk = apt_coords.iloc[i:i+chunk_size]
            
            chunk_closest = []
            chunk_distances = []
            
            for _, apt in chunk.iterrows():
                # Calculate distances to all stations
                distances = self.haversine_distance(
                    apt['latitud'], apt['longitud'],
                    station_coords[:, 0], station_coords[:, 1]
                )
                
                min_idx = np.argmin(distances)
                chunk_closest.append(station_names[min_idx])
                chunk_distances.append(distances[min_idx])
            
            closest_stations.extend(chunk_closest)
            min_distances.extend(chunk_distances)
        
        # Create result DataFrame
        result_df = apt_coords.copy()
        result_df['estacion_tm_cercana'] = closest_stations
        result_df['distancia_estacion_tm_m'] = np.round(min_distances, 2)
        result_df['is_cerca_estacion_tm'] = (result_df['distancia_estacion_tm_m'] <= 500).astype(int)
        
        # Merge back to original DataFrame
        df = df.merge(
            result_df[['estacion_tm_cercana', 'distancia_estacion_tm_m', 'is_cerca_estacion_tm']],
            left_index=True, right_index=True, how='left'
        )
        
        logger.info("TransMilenio station information added")
        return df
    
    def add_parks_info_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add parks information using vectorized operations"""
        logger.info("Adding parks information...")
        
        parks = self.external_data['parques']
        apt_coords = df[['latitud', 'longitud']].dropna()
        
        if apt_coords.empty or parks.empty:
            return df
        
        park_coords = parks[['LATITUD', 'LONGITUD']].values
        park_names = (parks['TIPO DE PARQUE'] + ' ' + parks['NOMBRE DEL PARQUE O ESCENARIO']).values
        
        closest_parks = []
        min_distances = []
        
        # Process in chunks
        chunk_size = 100
        for i in tqdm(range(0, len(apt_coords), chunk_size), desc="Processing parks"):
            chunk = apt_coords.iloc[i:i+chunk_size]
            
            chunk_closest = []
            chunk_distances = []
            
            for _, apt in chunk.iterrows():
                distances = self.haversine_distance(
                    apt['latitud'], apt['longitud'],
                    park_coords[:, 0], park_coords[:, 1]
                )
                
                min_idx = np.argmin(distances)
                chunk_closest.append(f"PARQUE {park_names[min_idx]}")
                chunk_distances.append(distances[min_idx])
            
            closest_parks.extend(chunk_closest)
            min_distances.extend(chunk_distances)
        
        # Create result DataFrame
        result_df = apt_coords.copy()
        result_df['parque_cercano'] = closest_parks
        result_df['distancia_parque_m'] = np.round(min_distances, 2)
        result_df['is_cerca_parque'] = (result_df['distancia_parque_m'] <= 500).astype(int)
        
        # Merge back
        df = df.merge(
            result_df[['parque_cercano', 'distancia_parque_m', 'is_cerca_parque']],
            left_index=True, right_index=True, how='left'
        )
        
        logger.info("Parks information added")
        return df
    
    def clean_and_filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and filter data based on business rules"""
        logger.info("Cleaning and filtering data...")
        
        initial_count = len(df)
        
        # Remove records with completely invalid data
        df = df.dropna(subset=['codigo'], how='any')  # At least need a codigo
        
        # Clean up estratos - only remove if explicitly invalid (not just missing)
        if 'estrato' in df.columns:
            # Remove only records with invalid estratos (not just NaN)
            invalid_estratos = df['estrato'].notna() & (~df['estrato'].between(1, 6))
            df = df[~invalid_estratos]
        
        # Remove invalid location combinations only if we have both localidad and estrato
        if 'localidad' in df.columns and 'estrato' in df.columns:
            invalid_combinations = {
                'KENNEDY': [6, 5],
                'RAFAEL URIBE URIBE': [6, 5],
                'BOSA': [6, 5, 4],
                'USME': [6, 5, 4, 3],
                'SAN CRISTOBAL': [6, 5, 4],
                'CIUDAD BOLIVAR': [6, 5, 4],
                'FONTIBON': [6],
                'LOS MARTIRES': [6, 5, 1],
                'SANTA FE': [6, 5],
                'TUNJUELITO': [6, 5, 4],
                'BARRIOS UNIDOS': [1, 2, 6],
                'TEUSAQUILLO': [1, 2, 6],
                'ANTONIO NARIÑO': [1, 5, 6],
                'CANDELARIA': [6, 5, 4],
            }
            
            for localidad, estratos in invalid_combinations.items():
                for estrato in estratos:
                    mask = (df['localidad'] == localidad) & (df['estrato'] == estrato)
                    if mask.sum() > 0:
                        logger.info(f"Removing {mask.sum()} records with invalid combination: {localidad} + Estrato {estrato}")
                        df = df[~mask]
        
        # Remove duplicates based on codigo
        if 'codigo' in df.columns:
            duplicates = df.duplicated(subset=['codigo'], keep='first')
            if duplicates.sum() > 0:
                logger.info(f"Removing {duplicates.sum()} duplicate records")
                df = df[~duplicates]
        
        # Only remove records that have NO location information at all
        location_cols = [col for col in ['localidad', 'barrio', 'sector'] if col in df.columns]
        if location_cols:
            # Remove only if ALL location fields are missing
            no_location = df[location_cols].isna().all(axis=1)
            if no_location.sum() > 0:
                logger.info(f"Removing {no_location.sum()} records with no location information")
                df = df[~no_location]
        
        # Remove records with invalid coordinates (if they exist)
        if 'latitud' in df.columns and 'longitud' in df.columns:
            # Only remove if coordinates are present but invalid
            has_coords = df[['latitud', 'longitud']].notna().all(axis=1)
            invalid_coords = has_coords & (
                (df['latitud'] < -90) | (df['latitud'] > 90) |
                (df['longitud'] < -180) | (df['longitud'] > 180)
            )
            if invalid_coords.sum() > 0:
                logger.info(f"Removing {invalid_coords.sum()} records with invalid coordinates")
                df = df[~invalid_coords]
        
        final_count = len(df)
        removed_count = initial_count - final_count
        logger.info(f"Data cleaned: {initial_count} -> {final_count} records ({removed_count} removed)")
        
        return df
    
    def save_to_mongodb(self, df: pd.DataFrame) -> bool:
        """Save processed data to MongoDB with upsert logic"""
        logger.info("Saving data to MongoDB...")
        
        if not self.connect_to_mongodb():
            return False
        
        try:
            collection = self.db[self.config.mongo_collection_processed]
            
            # Batch upsert for better performance
            operations = []
            batch_size = 1000
            
            for i in tqdm(range(0, len(df), batch_size), desc="Preparing MongoDB operations"):
                batch = df.iloc[i:i+batch_size]
                
                for _, row in batch.iterrows():
                    doc = row.to_dict()
                    # Convert numpy types to native Python types
                    for key, value in doc.items():
                        if pd.isna(value):
                            doc[key] = None
                        elif isinstance(value, np.integer):
                            doc[key] = int(value)
                        elif isinstance(value, np.floating):
                            doc[key] = float(value)
                    
                    operations.append(
                        pymongo.UpdateOne(
                            {'codigo': doc['codigo']},
                            {'$set': doc},
                            upsert=True
                        )
                    )
            
            # Execute batch operations
            if operations:
                result = collection.bulk_write(operations)
                logger.info(f"MongoDB bulk write completed: {result.upserted_count} inserted, {result.modified_count} updated")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {e}")
            return False
        finally:
            if self.mongo_client:
                self.mongo_client.close()
    
    def save_to_csv(self, df: pd.DataFrame):
        """Save processed data to CSV files"""
        logger.info("Saving data to CSV files...")
        
        # Save main apartments data
        apartments_file = self.config.processed_data_dir / "apartments.csv"
        df.to_csv(apartments_file, index=False)
        logger.info(f"Saved apartments data to {apartments_file}")
        
        # Extract and save images data if available
        if 'imagenes' in df.columns:
            images_df = df[['codigo', 'imagenes']].explode('imagenes').dropna(subset=['imagenes'])
            images_df = images_df.rename(columns={'imagenes': 'url_imagen'})
            
            images_file = self.config.processed_data_dir / "images.csv"
            images_df.to_csv(images_file, index=False)
            logger.info(f"Saved images data to {images_file}")
    
    def run_pipeline(self) -> bool:
        """Run the complete ETL pipeline"""
        start_time = time.time()
        logger.info("Starting ETL Pipeline")
        
        try:
            # 1. Connect to MongoDB and load raw data
            if not self.connect_to_mongodb():
                return False
            
            collection = self.db[self.config.mongo_collection_raw]
            raw_data = list(collection.find())
            
            if not raw_data:
                logger.error("No raw data found in MongoDB")
                return False
            
            df = pd.DataFrame(raw_data)
            df = df.drop(columns=['_id'], errors='ignore')
            logger.info(f"Loaded {len(df)} raw records from MongoDB")
            
            # 2. Load external data
            self.load_external_data()
            
            # 3. Initial transformations
            logger.info("Starting data transformations...")
            
            # Extract features from characteristics
            df = self.extract_features_vectorized(df)
            
            # Handle images column
            if 'imagenes' in df.columns:
                # Save images separately
                images_df = df[['codigo', 'imagenes']].explode('imagenes').dropna(subset=['imagenes'])
                images_df = images_df.rename(columns={'imagenes': 'url_imagen'})
                images_file = self.config.processed_data_dir / "images.csv"
                images_df.to_csv(images_file, index=False)
                logger.info(f"Saved {len(images_df)} image records")
                
                # Remove images column from main DataFrame
                df = df.drop(columns=['imagenes'])
            
            # 4. Data validation
            df = self.validate_data(df)
            
            # 5. Geospatial enrichment
            df = self.enrich_with_geospatial_data_vectorized(df)
            
            # 6. Data cleaning and filtering
            df = self.clean_and_filter_data(df)
            
            # 7. Save processed data
            self.save_to_csv(df)
            
            # 8. Save to MongoDB
            if not self.save_to_mongodb(df):
                logger.warning("Failed to save to MongoDB, but CSV files were created")
            
            execution_time = time.time() - start_time
            logger.info(f"ETL Pipeline completed successfully in {execution_time:.2f} seconds")
            logger.info(f"Processed {len(df)} final records")
            
            return True
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            return False
        finally:
            if self.mongo_client:
                self.mongo_client.close()


def main():
    """Main function to run the ETL pipeline"""
    # Load environment variables
    load_dotenv()
    
    # Create configuration
    config = ETLConfig(
        mongo_uri=os.getenv('MONGO_URI', ''),
        mongo_database=os.getenv('MONGO_DATABASE', ''),
        mongo_collection_raw=os.getenv('MONGO_COLLECTION_RAW', 'scrapy_bogota_apartments'),
        mongo_collection_processed=os.getenv('MONGO_COLLECTION_PROCESSED', 'scrapy_bogota_apartments_processed')
    )
    
    # Create and run pipeline
    pipeline = BogotaETLPipeline(config)
    success = pipeline.run_pipeline()
    
    if success:
        logger.info("ETL Pipeline completed successfully!")
        return 0
    else:
        logger.error("ETL Pipeline failed!")
        return 1


if __name__ == "__main__":
    exit(main()) 