"""
ETL Utilities Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides utility functions for the ETL pipeline.
"""

import logging
import sys
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
from unidecode import unidecode

logger = logging.getLogger(__name__)


def setup_logging(log_file: str = 'logs/etl.log') -> None:
    """Setup logging with UTF-8 support for emojis"""
    
    # Create handlers with proper encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    stream_handler = logging.StreamHandler()

    # Configure stream handler for Windows
    if sys.platform.startswith('win'):
        try:
            import io
            stream_handler.stream = io.TextIOWrapper(
                sys.stdout.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
        except Exception:
            # Fallback: keep default stream
            pass

    # Set formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, stream_handler],
        force=True
    )


def normalize_text(text: str) -> str:
    """Normalize text by removing accents and converting to uppercase"""
    try:
        return unidecode(str(text)).upper()
    except:
        return str(text)


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


def clean_timeline_value(value: Any) -> Any:
    """Clean timeline values safely, handling all possible states"""
    if value is None or pd.isna(value):
        return None
    elif isinstance(value, np.ndarray):
        # Convert numpy array to list if not empty, otherwise None
        if value.size > 0:
            try:
                return value.tolist()
            except:
                return None
        else:
            return None
    elif isinstance(value, list):
        # Return list as-is if it has content, otherwise None for empty lists
        return value if len(value) > 0 else None
    elif value == "" or value == []:
        return None
    else:
        # For any other type, try to preserve it if it seems valid
        return value


def safe_process_timeline(value: Any) -> Any:
    """Safely process timeline field to avoid numpy array ambiguity errors"""
    try:
        # Handle None and NaN values
        if value is None or pd.isna(value):
            return None
        
        # Handle numpy arrays specifically
        if isinstance(value, np.ndarray):
            # Check array size safely
            try:
                if hasattr(value, 'size'):
                    if value.size == 0:
                        return None
                    elif value.size > 0:
                        # Convert to list safely
                        return value.tolist()
                return None
            except:
                return None
        
        # Handle regular lists
        elif isinstance(value, list):
            if len(value) == 0:
                return None
            # Clean each item in the list
            try:
                cleaned_list = []
                for item in value:
                    if isinstance(item, dict):
                        cleaned_list.append(item)
                    elif isinstance(item, np.ndarray):
                        if item.size > 0:
                            cleaned_list.append(item.tolist())
                    else:
                        cleaned_list.append(item)
                return cleaned_list if len(cleaned_list) > 0 else None
            except:
                return None
        
        # Handle empty string or empty list representations
        elif value == "" or value == [] or str(value).strip() == "":
            return None
        
        # For any other type, try to preserve if valid
        else:
            return value
            
    except Exception as e:
        logger.debug(f"Error processing timeline value {type(value)}: {e}")
        return None


def convert_numpy_type(value: Any) -> Any:
    """Helper method to convert numpy types to Python native types"""
    if pd.isna(value):
        return None
    elif isinstance(value, (np.integer, int)):
        return int(value)
    elif isinstance(value, (np.floating, float)):
        return float(value) if not np.isnan(float(value)) else None
    elif isinstance(value, (np.bool_, bool)):
        return bool(value)
    elif hasattr(value, 'item'):
        return value.item()
    else:
        return value


def is_valid_bogota_coordinates(lat: float, lon: float, bounds: Dict[str, float]) -> bool:
    """Check if coordinates are within Bogotá bounds"""
    if pd.isna(lat) or pd.isna(lon):
        return False
    
    return (
        bounds['lat_min'] <= lat <= bounds['lat_max'] and
        bounds['lon_min'] <= lon <= bounds['lon_max']
    )


def extract_features_from_text(text: str) -> Dict[str, Union[int, float]]:
    """Extract features from characteristics text"""
    if pd.isna(text) or not isinstance(text, str):
        text = ""
    
    text_upper = text.upper()
    
    # Boolean features
    features = {
        'jacuzzi': int('JACUZZI' in text_upper or 'SPA' in text_upper),
        'piscina': int('PISCINA' in text_upper),
        'salon_comunal': int('SALON COMUNAL' in text_upper or 'SALÓN COMUNAL' in text_upper),
        'terraza': int('TERRAZA' in text_upper),
        'vigilancia': int('VIGILANCIA' in text_upper or 'PORTERIA' in text_upper),
        'chimenea': int('CHIMENEA' in text_upper),
        'permite_mascotas': int('MASCOTA' in text_upper or 'PET' in text_upper),
        'gimnasio': int('GIMNASIO' in text_upper or 'GYM' in text_upper),
        'ascensor': int('ASCENSOR' in text_upper or 'ELEVADOR' in text_upper),
        'conjunto_cerrado': int('CONJUNTO CERRADO' in text_upper or 'UNIDAD CERRADA' in text_upper),
    }
    
    # Numeric features
    import re
    
    # Extract floor number
    piso_match = re.search(r'PISO (\d+)', text_upper)
    features['piso'] = int(piso_match.group(1)) if piso_match else None
    
    # Extract number of closets
    closets_match = re.search(r'(\d+) CLOSET', text_upper)
    features['closets'] = int(closets_match.group(1)) if closets_match else None
    
    return features


def get_invalid_location_combinations() -> Dict[str, List[int]]:
    """Get dictionary of invalid localidad-estrato combinations"""
    return {
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
        'CHAPINERO': [1],
    }


def log_statistics(df: pd.DataFrame, stage: str) -> None:
    """Log DataFrame statistics for a given processing stage"""
    logger.info(f"📊 {stage} Statistics:")
    logger.info(f"   - Total records: {len(df):,}")
    
    if 'localidad' in df.columns:
        localidad_count = df['localidad'].notna().sum()
        logger.info(f"   - Records with localidad: {localidad_count:,}")
    
    if 'barrio' in df.columns:
        barrio_count = df['barrio'].notna().sum()
        logger.info(f"   - Records with barrio: {barrio_count:,}")
    
    if 'latitud' in df.columns and 'longitud' in df.columns:
        coords_count = df[['latitud', 'longitud']].notna().all(axis=1).sum()
        logger.info(f"   - Records with coordinates: {coords_count:,}")


def safe_log(logger_func, message: str) -> None:
    """Safely log messages with emojis, handling encoding issues on Windows"""
    try:
        logger_func(message)
    except UnicodeEncodeError:
        # Remove emojis if encoding fails
        import re
        clean_message = re.sub(r'[^\x00-\x7F]+', '', message)
        logger_func(clean_message) 