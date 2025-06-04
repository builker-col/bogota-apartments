"""
ETL Data Loaders Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides classes for loading processed data to different destinations.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import pymongo
from tqdm import tqdm

from .config import ETLConfig
from .utils import convert_numpy_type, safe_process_timeline

logger = logging.getLogger(__name__)


class MongoDBLoader:
    """Load processed data to MongoDB"""
    
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
    
    def save_to_mongodb(self, df: pd.DataFrame) -> bool:
        """Save processed data to MongoDB with upsert logic"""
        logger.info("Saving data to MongoDB...")
        
        if not self.connect():
            return False
        
        try:
            # Clean DataFrame types first
            df_clean = self._clean_dataframe_types(df)
            
            collection = self.db[self.config.mongo_collection_processed]
            
            # Batch upsert for better performance
            operations = []
            batch_size = 1000
            
            for i in tqdm(range(0, len(df_clean), batch_size), desc="Preparing MongoDB operations"):
                batch = df_clean.iloc[i:i+batch_size]
                
                for idx, row in batch.iterrows():
                    try:
                        # Convert row to dict with better type handling
                        doc = self._convert_row_to_document(row)
                        
                        # Only add operation if we have a valid codigo
                        if doc.get('codigo') is not None:
                            operations.append(
                                pymongo.UpdateOne(
                                    {'codigo': doc['codigo']},
                                    {'$set': doc},
                                    upsert=True
                                )
                            )
                    except Exception as row_error:
                        logger.error(f"Error processing row {idx}: {row_error}")
                        continue
            
            # Execute batch operations
            if len(operations) > 0:
                result = collection.bulk_write(operations)
                logger.info(f"MongoDB bulk write completed: {result.upserted_count} inserted, {result.modified_count} updated")
            else:
                logger.warning("No valid operations to execute in MongoDB")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
        finally:
            if self.client:
                self.client.close()
    
    def _clean_dataframe_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame to remove problematic numpy types before MongoDB save"""
        logger.info("Cleaning DataFrame types for MongoDB compatibility...")
        
        cleaned_df = df.copy()
        
        for column in cleaned_df.columns:
            try:
                series = cleaned_df[column]
                
                # Handle different data types
                if series.dtype == 'object':
                    # Special handling for timeline column
                    if column == 'timeline':
                        logger.debug(f"Special cleaning for timeline column")
                        cleaned_df[column] = series.apply(safe_process_timeline)
                    else:
                        # Check if any values in this column are numpy arrays
                        has_arrays = series.apply(lambda x: isinstance(x, np.ndarray)).any()
                        if has_arrays:
                            logger.debug(f"Cleaning numpy arrays in column: {column}")
                            cleaned_df[column] = series.apply(
                                lambda x: x.tolist() if isinstance(x, np.ndarray) and x.size > 0 
                                else None if isinstance(x, np.ndarray) and x.size == 0
                                else x
                            )
                
                # Convert numpy dtypes to pandas native dtypes
                elif str(series.dtype).startswith('int'):
                    cleaned_df[column] = series.astype('Int64')
                elif str(series.dtype).startswith('float'):
                    cleaned_df[column] = series.astype('Float64')
                elif str(series.dtype).startswith('bool'):
                    cleaned_df[column] = series.astype('boolean')
                    
            except Exception as e:
                logger.warning(f"Could not clean column {column}: {e}")
                continue
        
        logger.info("DataFrame type cleaning completed")
        return cleaned_df
    
    def _convert_row_to_document(self, row: pd.Series) -> Dict[str, Any]:
        """Convert a pandas row to a MongoDB document"""
        doc = {}
        
        for key, value in row.items():
            try:
                # Special handling for timeline field
                if key == 'timeline':
                    doc[key] = safe_process_timeline(value)
                    continue
                
                # Handle different types
                doc[key] = self._convert_value_for_mongodb(value)
                
            except Exception as key_error:
                logger.warning(f"Error processing key {key}: {key_error}")
                doc[key] = None
        
        return doc
    
    def _convert_value_for_mongodb(self, value: Any) -> Any:
        """Convert a value to MongoDB-compatible format"""
        if value is None or pd.isna(value):
            return None
        elif isinstance(value, (np.integer, int)):
            return int(value)
        elif isinstance(value, (np.floating, float)):
            if np.isnan(float(value)):
                return None
            else:
                return float(value)
        elif isinstance(value, np.ndarray):
            # Handle numpy arrays - convert to list if not empty
            if hasattr(value, 'size') and value.size > 0:
                return value.tolist()
            else:
                return None
        elif isinstance(value, (np.bool_, bool)):
            return bool(value)
        elif hasattr(value, 'to_pydatetime'):
            # Handle pandas Timestamps
            return value.to_pydatetime()
        elif isinstance(value, str):
            return str(value)
        elif isinstance(value, list):
            # Handle lists that might contain numpy types
            try:
                if len(value) == 0:
                    return []
                else:
                    return [convert_numpy_type(item) for item in value]
            except Exception:
                return value
        else:
            # For any other type, try to convert or use as-is
            try:
                # Check if it's a numpy scalar
                if hasattr(value, 'item'):
                    return value.item()
                else:
                    # Convert to string if value exists
                    if value is not None:
                        return str(value)
                    else:
                        return None
            except Exception:
                return str(value) if value is not None else None


class CSVLoader:
    """Load processed data to CSV files"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
    
    def save_to_csv(self, df: pd.DataFrame) -> bool:
        """Save processed data to CSV files"""
        logger.info("Saving data to CSV files...")
        
        try:
            # Save main apartments data
            apartments_file = self.config.processed_data_dir / "apartments.csv"
            df.to_csv(apartments_file, index=False, encoding='utf-8')
            logger.info(f"Saved apartments data to {apartments_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return False


class DataLoader:
    """Main data loader orchestrator"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.mongodb_loader = MongoDBLoader(config)
        self.csv_loader = CSVLoader(config)
    
    def load_data(self, df: pd.DataFrame) -> bool:
        """Load processed data to all configured destinations"""
        logger.info("Starting data loading phase...")
        
        success = True
        
        try:
            # Save to CSV (always attempt this first as it's more reliable)
            csv_success = self.csv_loader.save_to_csv(df)
            if not csv_success:
                logger.warning("CSV save failed")
                success = False
            
            # Save to MongoDB
            mongodb_success = self.mongodb_loader.save_to_mongodb(df)
            if not mongodb_success:
                logger.warning("MongoDB save failed, but CSV files were created")
                # Don't mark as complete failure if CSV succeeded
                if csv_success:
                    logger.info("Data loading completed with partial success (CSV only)")
                else:
                    success = False
            
            if success:
                logger.info("Data loading phase completed successfully")
            else:
                logger.error("Data loading phase failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            return False 