"""
ETL Spatial Operations Module
Author: Erik Garcia (@erik172)
Version: 3.0.0

This module provides specialized geospatial operations for the ETL pipeline.
"""

import logging
from typing import Dict, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from .config import ETLConfig
from .utils import haversine_distance, is_valid_bogota_coordinates

logger = logging.getLogger(__name__)


class SpatialEnricher:
    """Handle all spatial enrichment operations"""
    
    def __init__(self, config: ETLConfig, external_data: Dict):
        self.config = config
        self.external_data = external_data
    
    def enrich_with_geospatial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add geospatial enrichment to apartment data"""
        logger.info("Enriching data with geospatial information...")
        
        df['coords_modified'] = False
        
        # Add localidad and barrio from coordinates
        df = self.add_locality_and_neighborhood(df)
        
        # Add TransMilenio station information
        if not self.external_data.get('transmilenio', pd.DataFrame()).empty:
            df = self.add_transmilenio_info(df)
        
        # Add parks information
        if 'parques' in self.external_data and not self.external_data['parques'].empty:
            df = self.add_parks_info(df)
        
        # Add shopping malls information
        if 'centros_comerciales' in self.external_data and not self.external_data['centros_comerciales'].empty:
            df = self.add_shopping_malls_info(df)
        
        return df
    
    def add_locality_and_neighborhood(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add localidad and barrio columns using spatial join with geojson data"""
        logger.info("Adding locality and neighborhood information using spatial data...")
        
        # Initialize columns if they don't exist
        if 'localidad' not in df.columns:
            df['localidad'] = None
        if 'barrio' not in df.columns:
            df['barrio'] = None
        
        # Filter for valid Bogotá coordinates
        valid_coords_mask = self._get_valid_coordinates_mask(df)
        
        if valid_coords_mask.sum() == 0:
            logger.warning("No records with valid Bogotá coordinates found for spatial assignment")
            return df
        
        # Step 1: Assign neighborhoods using barrios.geojson
        if 'barrios' in self.external_data and not self.external_data['barrios'].empty:
            self._assign_neighborhoods_from_geojson(df, valid_coords_mask)
        else:
            logger.warning("No barrios geojson data available")
        
        # Step 2: Assign localities using localidades shapefile
        if 'localidades' in self.external_data and not self.external_data['localidades'].empty:
            self._assign_localities_from_shapefile(df, valid_coords_mask)
        else:
            logger.warning("No localidades shapefile data available")
        
        localidad_count = df['localidad'].notna().sum()
        barrio_count = df['barrio'].notna().sum()
        logger.info(f"Spatial assignment completed: {localidad_count} localities, {barrio_count} neighborhoods")
        
        return df
    
    def _get_valid_coordinates_mask(self, df: pd.DataFrame) -> pd.Series:
        """Get mask for records with valid Bogotá coordinates"""
        has_coords = df[['latitud', 'longitud']].notna().all(axis=1)
        
        # Filter for coordinates within Bogotá bounds
        bogota_bounds_mask = has_coords & df.apply(
            lambda row: is_valid_bogota_coordinates(
                row['latitud'], row['longitud'], self.config.bogota_bounds
            ), axis=1
        )
        
        total_coords = has_coords.sum()
        valid_coords = bogota_bounds_mask.sum()
        invalid_coords = total_coords - valid_coords
        
        logger.info(f"Coordinate filtering for Bogotá:")
        logger.info(f"  📍 Total records with coordinates: {total_coords}")
        logger.info(f"  ✅ Valid Bogotá coordinates: {valid_coords}")
        logger.info(f"  ❌ Invalid/foreign coordinates: {invalid_coords}")
        
        return bogota_bounds_mask
    
    def _assign_neighborhoods_from_geojson(self, df: pd.DataFrame, has_coords: pd.Series):
        """Assign neighborhoods using spatial join with barrios.geojson"""
        try:
            logger.info(f"Assigning neighborhoods via spatial join with barrios.geojson for {has_coords.sum()} records")
            
            # Get coordinate data and ranges
            coords_df = df.loc[has_coords, ['latitud', 'longitud']].copy()
            lat_range = (coords_df['latitud'].min(), coords_df['latitud'].max())
            lon_range = (coords_df['longitud'].min(), coords_df['longitud'].max())
            logger.info(f"📍 Coordinate ranges - Lat: {lat_range}, Lon: {lon_range}")
            
            # Get and validate barrios geojson
            barrios = self.external_data['barrios']
            logger.info(f"📊 Barrios geojson info:")
            logger.info(f"   - Records: {len(barrios)}")
            logger.info(f"   - Columns: {list(barrios.columns)}")
            logger.info(f"   - CRS: {barrios.crs}")
            
            # Validate required fields
            if 'barriocomu' not in barrios.columns:
                logger.error("Column 'barriocomu' not found in barrios geojson!")
                return
            
            non_null_barrios = barrios['barriocomu'].notna().sum()
            logger.info(f"   - Non-null barriocomu: {non_null_barrios}")
            
            if non_null_barrios == 0:
                logger.error("All barriocomu values are null!")
                return
            
            # Create GeoDataFrame for apartments with coordinates
            geometry = [Point(lon, lat) for lat, lon in coords_df[['latitud', 'longitud']].values]
            apt_gdf = gpd.GeoDataFrame(coords_df, geometry=geometry, crs='EPSG:4326')
            
            logger.info(f"📍 Created apartment GeoDataFrame:")
            logger.info(f"   - Records: {len(apt_gdf)}")
            logger.info(f"   - CRS: {apt_gdf.crs}")
            
            # Ensure CRS compatibility
            if barrios.crs != apt_gdf.crs:
                logger.info(f"🔄 Converting barrios CRS from {barrios.crs} to {apt_gdf.crs}")
                barrios = barrios.to_crs(apt_gdf.crs)
            
            # Perform spatial join for neighborhoods
            logger.info("🔗 Performing spatial join for neighborhoods...")
            apt_with_barrio = gpd.sjoin(apt_gdf, barrios, how='left', predicate='within')
            
            logger.info(f"📊 Spatial join results for neighborhoods:")
            logger.info(f"   - Total records after join: {len(apt_with_barrio)}")
            
            # Process barrio results only
            self._process_spatial_join_results(df, apt_with_barrio, 'barriocomu', 'barrio')
            
        except Exception as e:
            logger.error(f"Failed to assign neighborhoods from barrios.geojson: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
    
    def _assign_localities_from_shapefile(self, df: pd.DataFrame, has_coords: pd.Series):
        """Assign localities using spatial join with localidades shapefile"""
        try:
            logger.info(f"Assigning localities via spatial join with localidades shapefile for {has_coords.sum()} records")
            
            # Get coordinate data
            coords_df = df.loc[has_coords, ['latitud', 'longitud']].copy()
            
            # Get and validate localidades shapefile
            localidades = self.external_data['localidades']
            logger.info(f"📊 Localidades shapefile info:")
            logger.info(f"   - Records: {len(localidades)}")
            logger.info(f"   - Columns: {list(localidades.columns)}")
            logger.info(f"   - CRS: {localidades.crs}")
            
            # Create GeoDataFrame for apartments with coordinates
            geometry = [Point(lon, lat) for lat, lon in coords_df[['latitud', 'longitud']].values]
            apt_gdf = gpd.GeoDataFrame(coords_df, geometry=geometry, crs='EPSG:4326')
            
            # Ensure CRS compatibility
            if localidades.crs != apt_gdf.crs:
                logger.info(f"🔄 Converting localidades CRS from {localidades.crs} to {apt_gdf.crs}")
                localidades = localidades.to_crs(apt_gdf.crs)
            
            # Perform spatial join for localities
            logger.info("🔗 Performing spatial join for localities...")
            apt_with_localidad = gpd.sjoin(apt_gdf, localidades, how='left', predicate='within')
            
            logger.info(f"📊 Spatial join results for localities:")
            logger.info(f"   - Total records after join: {len(apt_with_localidad)}")
            
            # Find the correct locality name column
            locality_columns = ['NOMBRE_LOC', 'localidad', 'LOCALIDAD', 'nombre', 'LocNombre', 'NOMBRE', 'Localidad']
            found_column = None
            
            for col in locality_columns:
                if col in apt_with_localidad.columns:
                    non_null_count = apt_with_localidad[col].notna().sum()
                    if non_null_count > 0:
                        found_column = col
                        logger.info(f"✅ Found locality column: '{col}' with {non_null_count} non-null values")
                        break
            
            if found_column:
                # Process locality results
                self._process_spatial_join_results(df, apt_with_localidad, found_column, 'localidad')
            else:
                logger.warning(f"❌ No valid locality column found in shapefile. Available columns: {list(apt_with_localidad.columns)}")
            
        except Exception as e:
            logger.error(f"Failed to assign localities from shapefile: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
    
    def _process_spatial_join_results(self, df: pd.DataFrame, spatial_result: gpd.GeoDataFrame, 
                                    source_col: str, target_col: str):
        """Process spatial join results and handle duplicates"""
        try:
            if source_col not in spatial_result.columns:
                logger.warning(f"Column '{source_col}' not found in spatial join result")
                return
            
            # Get valid matches
            valid_mask = spatial_result[source_col].notna()
            matched_count = valid_mask.sum()
            
            logger.info(f"📍 Spatial join matches for {source_col}: {matched_count} out of {len(spatial_result)}")
            
            if matched_count > 0:
                # Handle duplicate indices from spatial join
                result_clean = spatial_result.loc[valid_mask].copy()
                
                if result_clean.index.duplicated().any():
                    dup_count = result_clean.index.duplicated().sum()
                    logger.info(f"🔧 Handling {dup_count} duplicate spatial matches for {source_col}")
                    result_clean = result_clean[~result_clean.index.duplicated(keep='first')]
                
                # Assign values to the original DataFrame
                df.loc[result_clean.index, target_col] = result_clean[source_col].values
                logger.info(f"📍 Assigned {len(result_clean)} {target_col} values from coordinates")
                
                # Log sample assignments
                if len(result_clean) > 0:
                    sample_values = df.loc[result_clean.index, target_col].value_counts().head(5)
                    logger.info(f"📊 Sample assigned {target_col}: {dict(sample_values)}")
            
        except Exception as e:
            logger.error(f"Error processing spatial join results for {source_col}: {e}")
    
    def add_transmilenio_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add TransMilenio station information using vectorized operations"""
        logger.info("Adding TransMilenio station information...")
        
        stations = self.external_data['transmilenio']
        if stations.empty:
            logger.warning("No TransMilenio stations data available")
            return df
        
        apt_coords = df[['latitud', 'longitud']].dropna()
        if apt_coords.empty:
            return df
        
        # Prepare station data
        station_coords = stations[['latitud_estacion', 'longitud_estacion']].values
        station_names = stations['nombre_estacion'].values
        
        # Process in chunks for memory efficiency
        results = self._process_proximity_in_chunks(
            apt_coords, station_coords, station_names, 
            "TransMilenio stations", chunk_size=100
        )
        
        # Merge results back to original DataFrame
        if results:
            result_df = pd.DataFrame(results, index=apt_coords.index)
            result_df.columns = ['estacion_tm_cercana', 'distancia_estacion_tm_m']
            result_df['is_cerca_estacion_tm'] = (result_df['distancia_estacion_tm_m'] <= 500).astype(int)
            
            df = df.merge(result_df, left_index=True, right_index=True, how='left')
        
        logger.info("TransMilenio station information added")
        return df
    
    def add_parks_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add parks information using vectorized operations"""
        logger.info("Adding parks information...")
        
        parks = self.external_data['parques']
        apt_coords = df[['latitud', 'longitud']].dropna()
        
        if apt_coords.empty or parks.empty:
            return df
        
        # Prepare parks data
        park_coords = parks[['LATITUD', 'LONGITUD']].values
        park_names = (parks['TIPO DE PARQUE'] + ' ' + parks['NOMBRE DEL PARQUE O ESCENARIO']).values
        
        # Process in chunks
        results = self._process_proximity_in_chunks(
            apt_coords, park_coords, park_names, 
            "parks", chunk_size=100
        )
        
        # Merge results back to original DataFrame
        if results:
            result_df = pd.DataFrame(results, index=apt_coords.index)
            result_df.columns = ['parque_cercano', 'distancia_parque_m']
            result_df['parque_cercano'] = 'PARQUE ' + result_df['parque_cercano']
            result_df['is_cerca_parque'] = (result_df['distancia_parque_m'] <= 500).astype(int)
            
            df = df.merge(result_df, left_index=True, right_index=True, how='left')
        
        logger.info("Parks information added")
        return df
    
    def add_shopping_malls_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add shopping malls information using vectorized operations"""
        logger.info("Adding shopping malls information...")
        
        malls = self.external_data['centros_comerciales']
        apt_coords = df[['latitud', 'longitud']].dropna()
        
        if apt_coords.empty or malls.empty:
            return df
        
        # Prepare malls data
        mall_coords = malls[['LATITUD', 'LONGITUD']].values
        mall_names = malls['NAME'].values
        
        # Process in chunks
        results = self._process_proximity_in_chunks(
            apt_coords, mall_coords, mall_names, 
            "shopping malls", chunk_size=100
        )
        
        # Merge results back to original DataFrame
        if results:
            result_df = pd.DataFrame(results, index=apt_coords.index)
            result_df.columns = ['centro_comercial_cercano', 'distancia_centro_comercial_m']
            # Use 800 meters as threshold (8-10 minutes walking)
            result_df['is_cerca_centro_comercial'] = (result_df['distancia_centro_comercial_m'] <= 800).astype(int)
            
            df = df.merge(result_df, left_index=True, right_index=True, how='left')
        
        logger.info("Shopping malls information added")
        return df
    
    def _process_proximity_in_chunks(self, apt_coords: pd.DataFrame, poi_coords: np.ndarray, 
                                   poi_names: np.ndarray, poi_type: str, chunk_size: int = 100) -> list:
        """Process proximity calculations in chunks for memory efficiency"""
        from tqdm import tqdm
        
        closest_pois = []
        min_distances = []
        
        for i in tqdm(range(0, len(apt_coords), chunk_size), desc=f"Processing {poi_type}"):
            chunk = apt_coords.iloc[i:i+chunk_size]
            
            chunk_closest = []
            chunk_distances = []
            
            for _, apt in chunk.iterrows():
                # Calculate distances to all POIs
                distances = haversine_distance(
                    apt['latitud'], apt['longitud'],
                    poi_coords[:, 0], poi_coords[:, 1]
                )
                
                min_idx = np.argmin(distances)
                chunk_closest.append(poi_names[min_idx])
                chunk_distances.append(np.round(distances[min_idx], 2))
            
            closest_pois.extend(chunk_closest)
            min_distances.extend(chunk_distances)
        
        return list(zip(closest_pois, min_distances)) 