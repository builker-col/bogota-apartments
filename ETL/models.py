"""
ETL Data Models Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides Pydantic models for data validation and structure.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


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
    direccion: Optional[str] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    datetime: Optional[datetime] = None
    last_view: Optional[datetime] = None
    
    # Geospatial enrichment fields
    localidad: Optional[str] = None
    barrio: Optional[str] = None
    
    # Feature extraction fields
    jacuzzi: Optional[int] = None
    piscina: Optional[int] = None
    salon_comunal: Optional[int] = None
    terraza: Optional[int] = None
    vigilancia: Optional[int] = None
    chimenea: Optional[int] = None
    permite_mascotas: Optional[int] = None
    gimnasio: Optional[int] = None
    ascensor: Optional[int] = None
    conjunto_cerrado: Optional[int] = None
    piso: Optional[int] = None
    closets: Optional[int] = None
    
    # Location enrichment fields
    estacion_tm_cercana: Optional[str] = None
    distancia_estacion_tm_m: Optional[float] = None
    is_cerca_estacion_tm: Optional[int] = None
    parque_cercano: Optional[str] = None
    distancia_parque_m: Optional[float] = None
    is_cerca_parque: Optional[int] = None
    centro_comercial_cercano: Optional[str] = None
    distancia_centro_comercial_m: Optional[float] = None
    is_cerca_centro_comercial: Optional[int] = None
    
    @field_validator('codigo')
    @classmethod
    def validate_codigo(cls, v):
        """Validate apartment code"""
        if v is not None:
            # Convert numbers to string for consistency
            return str(v)
        return v
    
    @field_validator('estrato')
    @classmethod
    def validate_estrato(cls, v):
        """Validate socioeconomic stratum (1-6)"""
        if v is not None and not (1 <= v <= 6):
            logger.warning(f"Invalid estrato value: {v}")
            return None
        return v
    
    @field_validator('latitud')
    @classmethod
    def validate_latitud(cls, v):
        """Validate latitude coordinates"""
        if v is not None and not pd.isna(v) and not (-90 <= v <= 90):
            logger.debug(f"Invalid latitude value: {v}")
            return None
        if pd.isna(v):
            return None
        return v
    
    @field_validator('longitud')
    @classmethod
    def validate_longitud(cls, v):
        """Validate longitude coordinates"""
        if v is not None and not pd.isna(v) and not (-180 <= v <= 180):
            logger.debug(f"Invalid longitude value: {v}")
            return None
        if pd.isna(v):
            return None
        return v

    @field_validator('timeline')
    @classmethod
    def validate_timeline(cls, v):
        """Validate timeline structure"""
        if v is None or pd.isna(v):
            return None
        
        if not isinstance(v, list):
            logger.warning(f"Timeline should be a list, got {type(v)}")
            return None
            
        # Validate each timeline entry
        valid_entries = []
        for entry in v:
            if isinstance(entry, dict) and 'fecha' in entry:
                valid_entries.append(entry)
            else:
                logger.debug(f"Invalid timeline entry: {entry}")
        
        return valid_entries if valid_entries else None

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, v):
        """Validate datetime field"""
        if v is None or pd.isna(v):
            return None
        
        # Handle pandas Timestamp
        if hasattr(v, 'to_pydatetime'):
            return v.to_pydatetime()
        
        # Handle string datetime
        if isinstance(v, str):
            try:
                from dateutil import parser
                return parser.parse(v)
            except Exception:
                logger.debug(f"Could not parse datetime string: {v}")
                return None
        
        # Already a datetime object
        if isinstance(v, datetime):
            return v
            
        logger.debug(f"Invalid datetime type: {type(v)}")
        return None

    @field_validator('last_view')
    @classmethod
    def validate_last_view(cls, v):
        """Validate last_view field"""
        if v is None or pd.isna(v):
            return None
        
        # Handle pandas Timestamp
        if hasattr(v, 'to_pydatetime'):
            return v.to_pydatetime()
        
        # Handle string datetime
        if isinstance(v, str):
            try:
                from dateutil import parser
                return parser.parse(v)
            except Exception:
                logger.debug(f"Could not parse last_view string: {v}")
                return None
        
        # Already a datetime object
        if isinstance(v, datetime):
            return v
            
        logger.debug(f"Invalid last_view type: {type(v)}")
        return None


class ValidationResult(BaseModel):
    """Result of data validation process"""
    
    valid_records: int
    invalid_records: int
    total_records: int
    timeline_records: int
    datetime_records: int
    last_view_records: int
    validation_errors: List[str]
    
    @property
    def success_rate(self) -> float:
        """Calculate validation success rate"""
        if self.total_records == 0:
            return 0.0
        return (self.valid_records / self.total_records) * 100 