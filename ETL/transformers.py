"""
ETL Data Transformers Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides classes for transforming and cleaning data.
"""

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from pydantic import ValidationError
from tqdm import tqdm

from .models import ApartmentModel, ValidationResult
from .utils import extract_features_from_text, get_invalid_location_combinations, log_statistics

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features from raw apartment data"""
    
    def extract_features_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from characteristics column using vectorized operations"""
        logger.info("Extracting features from characteristics...")
        
        if 'caracteristicas' not in df.columns:
            logger.warning("No 'caracteristicas' column found, skipping feature extraction")
            return df
        
        # Fill NaN values with empty string for string operations
        caracteristicas = df['caracteristicas'].fillna('').astype(str)
        
        # Extract features for each row
        features_list = caracteristicas.apply(extract_features_from_text)
        
        # Convert list of dictionaries to DataFrame
        features_df = pd.DataFrame(features_list.tolist(), index=df.index)
        
        # Add features to original DataFrame
        for col in features_df.columns:
            df[col] = features_df[col]
        
        # Drop original caracteristicas column
        df = df.drop(columns=['caracteristicas'], errors='ignore')
        
        logger.info(f"Extracted {len(features_df.columns)} features")
        return df


class DataValidator:
    """Validate apartment data using Pydantic models"""
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationResult]:
        """Validate data using Pydantic models"""
        logger.info("Validating apartment data...")
        
        valid_records = []
        invalid_count = 0
        validation_errors = []
        timeline_count = 0
        total_timeline_entries = 0
        datetime_count = 0
        last_view_count = 0
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Validating records"):
            try:
                # Convert row to dict and validate
                row_dict = row.to_dict()
                apartment = ApartmentModel(**row_dict)
                valid_records.append(apartment.model_dump())
                
                # Count timeline statistics
                self._count_timeline_stats(row_dict, timeline_count, total_timeline_entries)
                
                # Count temporal field statistics
                if row_dict.get('datetime') is not None and not pd.isna(row_dict.get('datetime')):
                    datetime_count += 1
                    
                if row_dict.get('last_view') is not None and not pd.isna(row_dict.get('last_view')):
                    last_view_count += 1
                        
            except ValidationError as e:
                invalid_count += 1
                if invalid_count <= 5:  # Only show first 5 errors
                    error_msg = f"Invalid record {row.get('codigo', f'index_{idx}')}: {e}"
                    logger.warning(error_msg)
                    validation_errors.append(error_msg)
                
                # Keep original record even with validation warnings
                valid_records.append(row_dict)
        
        valid_df = pd.DataFrame(valid_records)
        
        # Create validation result
        result = ValidationResult(
            valid_records=len(valid_df) - invalid_count,
            invalid_records=invalid_count,
            total_records=len(valid_df),
            timeline_records=timeline_count,
            datetime_records=datetime_count,
            last_view_records=last_view_count,
            validation_errors=validation_errors
        )
        
        self._log_validation_statistics(result, total_timeline_entries, valid_df)
        
        return valid_df, result
    
    def _count_timeline_stats(self, row_dict: dict, timeline_count: int, total_timeline_entries: int):
        """Count timeline statistics safely"""
        timeline_val = row_dict.get('timeline')
        
        if timeline_val is not None:
            # Check if it's a numpy array first
            if isinstance(timeline_val, np.ndarray):
                if timeline_val.size > 0:
                    timeline_count += 1
                    try:
                        timeline_list = timeline_val.tolist()
                        if isinstance(timeline_list, list):
                            total_timeline_entries += len(timeline_list)
                        else:
                            total_timeline_entries += 1
                    except:
                        total_timeline_entries += 1
            # Check if it's a regular list
            elif isinstance(timeline_val, list):
                if len(timeline_val) > 0:
                    timeline_count += 1
                    total_timeline_entries += len(timeline_val)
            # Handle other truthy values
            elif timeline_val and timeline_val != "":
                timeline_count += 1
                total_timeline_entries += 1
    
    def _log_validation_statistics(self, result: ValidationResult, total_timeline_entries: int, df: pd.DataFrame):
        """Log validation statistics"""
        logger.info(f"Processed {result.total_records} records, {result.invalid_records} had validation warnings")
        
        # Timeline statistics
        if result.timeline_records > 0:
            avg_timeline_entries = total_timeline_entries / result.timeline_records
            logger.info(f"📈 Timeline data: {result.timeline_records:,} records with timeline, avg {avg_timeline_entries:.1f} entries per record")
        else:
            logger.warning("⚠️ No timeline data found in records")
        
        # Temporal field statistics
        logger.info(f"📅 Temporal data: {result.datetime_records:,} records with datetime, {result.last_view_records:,} records with last_view")
        
        # Calculate temporal ranges if data exists
        if result.datetime_records > 0:
            self._log_temporal_ranges(df, 'datetime', '📅 Scraping range')
        
        if result.last_view_records > 0:
            self._log_temporal_ranges(df, 'last_view', '👁️ Last view range')
    
    def _log_temporal_ranges(self, df: pd.DataFrame, column: str, label: str):
        """Log temporal ranges for a given column"""
        try:
            temporal_series = df[column].dropna()
            if len(temporal_series) > 0:
                oldest = temporal_series.min()
                newest = temporal_series.max()
                logger.info(f"{label}: {oldest} to {newest}")
        except Exception as e:
            logger.debug(f"Error calculating temporal range for {column}: {e}")


class DataCleaner:
    """Clean and filter apartment data"""
    
    def clean_and_filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and filter data based on business rules"""
        logger.info("Cleaning and filtering data...")
        
        initial_count = len(df)
        
        # Remove records with completely invalid data
        df = df.dropna(subset=['codigo'], how='any')
        
        # Clean up estratos - only remove if explicitly invalid
        df = self._clean_estratos(df)
        
        # Remove invalid location combinations
        df = self._remove_invalid_location_combinations(df)
        
        # Remove duplicates based on codigo
        df = self._remove_duplicates(df)
        
        # Remove records with no location information at all
        df = self._remove_no_location_records(df)
        
        # Remove records with invalid coordinates
        df = self._remove_invalid_coordinates(df)
        
        final_count = len(df)
        removed_count = initial_count - final_count
        logger.info(f"Data cleaned: {initial_count} -> {final_count} records ({removed_count} removed)")
        
        return df
    
    def _clean_estratos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean estrato values"""
        if 'estrato' in df.columns:
            # Remove only records with invalid estratos (not just NaN)
            invalid_estratos = df['estrato'].notna() & (~df['estrato'].between(1, 6))
            df = df[~invalid_estratos]
        return df
    
    def _remove_invalid_location_combinations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove invalid localidad-estrato combinations"""
        if 'localidad' not in df.columns or 'estrato' not in df.columns:
            return df
        
        invalid_combinations = get_invalid_location_combinations()
        
        for localidad, estratos in invalid_combinations.items():
            for estrato in estratos:
                mask = (df['localidad'] == localidad) & (df['estrato'] == estrato)
                if mask.sum() > 0:
                    logger.info(f"Removing {mask.sum()} records with invalid combination: {localidad} + Estrato {estrato}")
                    df = df[~mask]
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records based on codigo"""
        if 'codigo' in df.columns:
            duplicates = df.duplicated(subset=['codigo'], keep='first')
            if duplicates.sum() > 0:
                logger.info(f"Removing {duplicates.sum()} duplicate records")
                df = df[~duplicates]
        return df
    
    def _remove_no_location_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records with no location information"""
        location_cols = [col for col in ['localidad', 'barrio', 'sector'] if col in df.columns]
        if location_cols:
            # Remove only if ALL location fields are missing
            no_location = df[location_cols].isna().all(axis=1)
            if no_location.sum() > 0:
                logger.info(f"Removing {no_location.sum()} records with no location information")
                df = df[~no_location]
        return df
    
    def _remove_invalid_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records with invalid coordinates"""
        if 'latitud' not in df.columns or 'longitud' not in df.columns:
            return df
        
        # Only remove if coordinates are present but invalid
        has_coords = df[['latitud', 'longitud']].notna().all(axis=1)
        invalid_coords = has_coords & (
            (df['latitud'] < -90) | (df['latitud'] > 90) |
            (df['longitud'] < -180) | (df['longitud'] > 180)
        )
        
        if invalid_coords.sum() > 0:
            logger.info(f"Removing {invalid_coords.sum()} records with invalid coordinates")
            df = df[~invalid_coords]
        
        return df


class DataTransformer:
    """Main data transformer orchestrator"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
    
    def transform_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationResult]:
        """Transform raw apartment data through the complete pipeline"""
        logger.info("Starting data transformation phase...")
        
        # Log initial statistics
        log_statistics(df, "Initial Data")
        
        # Extract features from characteristics
        df = self.feature_extractor.extract_features_vectorized(df)
        log_statistics(df, "After Feature Extraction")
        
        # Validate data
        df, validation_result = self.validator.validate_data(df)
        log_statistics(df, "After Validation")
        
        # Clean and filter data
        df = self.cleaner.clean_and_filter_data(df)
        log_statistics(df, "After Cleaning")
        
        logger.info("Data transformation phase completed successfully")
        return df, validation_result 