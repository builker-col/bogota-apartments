"""
ETL Main Orchestrator Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides the main ETL pipeline orchestrator that coordinates
all phases of the data processing pipeline.
"""

import logging
import time
from typing import Dict, Tuple

import pandas as pd

from .config import ETLConfig
from .extractors import DataExtractor
from .loaders import DataLoader
from .models import ValidationResult
from .spatial import SpatialEnricher
from .transformers import DataTransformer
from .utils import log_statistics, setup_logging

logger = logging.getLogger(__name__)


class BogotaETLPipeline:
    """Main ETL Pipeline orchestrator for Bogota Apartments data processing"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.config.setup_directories()
        
        # Initialize pipeline components
        self.extractor = DataExtractor(config)
        self.transformer = DataTransformer()
        self.loader = DataLoader(config)
        
        # External data will be loaded during extraction
        self.external_data: Dict = {}
        self.spatial_enricher = None
    
    def run_pipeline(self) -> bool:
        """Run the complete ETL pipeline"""
        start_time = time.time()
        logger.info("🚀 Starting ETL Pipeline")
        
        try:
            # Phase 1: Extraction
            apartments_df, external_data = self._extract_data()
            self.external_data = external_data
            
            # Initialize spatial enricher with external data
            self.spatial_enricher = SpatialEnricher(self.config, external_data)
            
            # Phase 2: Transformation
            apartments_df, validation_result = self._transform_data(apartments_df)
            
            # Phase 3: Spatial Enrichment
            apartments_df = self._enrich_data(apartments_df)
            
            # Phase 4: Loading
            success = self._load_data(apartments_df)
            
            # Pipeline completion
            execution_time = time.time() - start_time
            
            if success:
                logger.info(f"✅ ETL Pipeline completed successfully in {execution_time:.2f} seconds")
                logger.info(f"📊 Processed {len(apartments_df)} final records")
                self._log_final_statistics(apartments_df, validation_result)
                return True
            else:
                logger.error(f"❌ ETL Pipeline failed after {execution_time:.2f} seconds")
                return False
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"💥 ETL Pipeline failed with error after {execution_time:.2f} seconds: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def _extract_data(self) -> Tuple[pd.DataFrame, Dict]:
        """Phase 1: Extract data from all sources"""
        logger.info("📥 Phase 1: Data Extraction")
        
        try:
            apartments_df, external_data = self.extractor.extract_all_data()
            
            log_statistics(apartments_df, "Extracted Data")
            
            return apartments_df, external_data
            
        except Exception as e:
            logger.error(f"Data extraction phase failed: {e}")
            raise
    
    def _transform_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationResult]:
        """Phase 2: Transform and validate data"""
        logger.info("🔄 Phase 2: Data Transformation")
        
        try:
            transformed_df, validation_result = self.transformer.transform_data(df)
            
            return transformed_df, validation_result
            
        except Exception as e:
            logger.error(f"Data transformation phase failed: {e}")
            raise
    
    def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Phase 3: Enrich data with geospatial information"""
        logger.info("🗺️ Phase 3: Geospatial Enrichment")
        
        try:
            if self.spatial_enricher is None:
                logger.warning("Spatial enricher not initialized, skipping enrichment")
                return df
            
            enriched_df = self.spatial_enricher.enrich_with_geospatial_data(df)
            
            log_statistics(enriched_df, "Enriched Data")
            
            return enriched_df
            
        except Exception as e:
            logger.error(f"Data enrichment phase failed: {e}")
            raise
    
    def _load_data(self, df: pd.DataFrame) -> bool:
        """Phase 4: Load processed data to destinations"""
        logger.info("💾 Phase 4: Data Loading")
        
        try:
            success = self.loader.load_data(df)
            return success
            
        except Exception as e:
            logger.error(f"Data loading phase failed: {e}")
            return False
    
    def _log_final_statistics(self, df: pd.DataFrame, validation_result: ValidationResult):
        """Log final pipeline statistics"""
        logger.info("📊 Final Pipeline Statistics:")
        logger.info(f"   - Total processed records: {len(df):,}")
        logger.info(f"   - Validation success rate: {validation_result.success_rate:.1f}%")
        
        # Location coverage
        if 'localidad' in df.columns:
            localidad_coverage = (df['localidad'].notna().sum() / len(df)) * 100
            logger.info(f"   - Localidad coverage: {localidad_coverage:.1f}%")
        
        if 'barrio' in df.columns:
            barrio_coverage = (df['barrio'].notna().sum() / len(df)) * 100
            logger.info(f"   - Barrio coverage: {barrio_coverage:.1f}%")
        
        # Coordinate coverage
        if 'latitud' in df.columns and 'longitud' in df.columns:
            coords_coverage = (df[['latitud', 'longitud']].notna().all(axis=1).sum() / len(df)) * 100
            logger.info(f"   - Coordinates coverage: {coords_coverage:.1f}%")
        
        # Feature enrichment
        feature_cols = [col for col in df.columns if col in [
            'jacuzzi', 'piscina', 'salon_comunal', 'terraza', 'vigilancia',
            'chimenea', 'permite_mascotas', 'gimnasio', 'ascensor', 'conjunto_cerrado'
        ]]
        
        if feature_cols:
            features_with_data = sum(df[col].sum() for col in feature_cols if col in df.columns)
            logger.info(f"   - Total feature flags set: {features_with_data:,}")
        
        # Transportation enrichment
        if 'estacion_tm_cercana' in df.columns:
            tm_coverage = (df['estacion_tm_cercana'].notna().sum() / len(df)) * 100
            logger.info(f"   - TransMilenio enrichment: {tm_coverage:.1f}%")
        
        # Parks enrichment
        if 'parque_cercano' in df.columns:
            parks_coverage = (df['parque_cercano'].notna().sum() / len(df)) * 100
            logger.info(f"   - Parks enrichment: {parks_coverage:.1f}%")
        
        # Shopping malls enrichment
        if 'centro_comercial_cercano' in df.columns:
            malls_coverage = (df['centro_comercial_cercano'].notna().sum() / len(df)) * 100
            logger.info(f"   - Shopping malls enrichment: {malls_coverage:.1f}%")
            
            # Additional stats for nearby shopping malls
            if 'is_cerca_centro_comercial' in df.columns:
                nearby_malls = (df['is_cerca_centro_comercial'] == 1).sum()
                logger.info(f"   - Apartments near shopping malls (<800m): {nearby_malls:,}")


def run_etl_pipeline(config: ETLConfig = None) -> bool:
    """
    Run the complete ETL pipeline with given configuration
    
    Args:
        config: ETL configuration. If None, will load from environment.
    
    Returns:
        bool: True if pipeline completed successfully, False otherwise
    """
    # Setup logging
    setup_logging()
    
    # Use provided config or load from environment
    if config is None:
        config = ETLConfig.from_env()
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        return False
    
    # Create and run pipeline
    pipeline = BogotaETLPipeline(config)
    return pipeline.run_pipeline() 