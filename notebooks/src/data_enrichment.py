from shapely.geometry import Point
from unidecode import unidecode
import geopandas as gpd
import numpy as np

def get_localidad(row, localidades: gpd.GeoDataFrame) -> str:
    """
    Given a row with longitude and latitude coordinates, and a GeoDataFrame with localidades polygons,
    returns the name of the localidad that contains the point defined by the coordinates.
    If the point is not contained in any localidad, returns np.nan.
    """
    try:
        point = Point(row['longitud'], row['latitud'])
        for i, localidad in localidades.iterrows():
            if point.within(localidad['geometry']):
                return unidecode(localidad['LocNombre']).upper()
        return np.nan
    except:
        return np.nan
    
def get_barrio(row, barrios: gpd.GeoDataFrame) -> str:
    """
    Given a row of data and a GeoDataFrame of neighborhoods, returns the name of the neighborhood
    that contains the point defined by the row's longitude and latitude columns.
    
    Args:
    - row: a pandas Series representing a single row of data
    - barrios: a GeoDataFrame containing neighborhood polygons
    
    Returns:
    - A string representing the name of the neighborhood that contains the point defined by the row's
      longitude and latitude columns. If the point is not contained within any neighborhood, returns np.nan.
    """
    try:
        point = Point(row['longitud'], row['latitud'])
        loca = row['localidad']
        barrios_localidad = barrios.loc[barrios['localidad'] == loca]
        for i, barrio in barrios_localidad.iterrows():
            if point.within(barrio['geometry']):
                return barrio['barriocomu']
            
        return np.nan
    except:
        return np.nan