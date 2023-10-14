"""
This script reads data about apartments from a CSV file, enriches it with data about the nearest TransMilenio station, and saves the processed data to a new CSV file.

The script defines the following functions:
- normalize(text): Takes a string as input and returns a normalized version of the string. The normalization process involves converting any accented characters to their unaccented equivalents and converting the resulting string to uppercase.
- haversine_m(lat1, lon1, lat2, lon2): Calculates the distance between two points on Earth using the Haversine formula.
- estacion_tm_cercana(row): Returns the name of the TransMilenio station closest to the given latitude and longitude coordinates.
- get_distancia_estacion_m(row): Calculates the distance in meters between a given location (latitude and longitude) and the nearest TransMilenio station.
- is_cerca_estacion(row): Determines if a given row is close to a transportation station based on the distance to the nearest station.

The script reads data from the following file:
- ../data/interim/apartments.csv

The script saves processed data to the following file:
- ../data/processed/apartments.csv
"""
import math
import requests
from dotenv import load_dotenv
from unidecode import unidecode
from datetime import datetime
import logging
import numpy as np
import pandas as pd
import os

if os.getcwd().split('/')[-1] == 'notebooks':
    logging.info('Cambiando directorio de trabajo')
    os.chdir('..')

load_dotenv()

filename = f'logs/03_data_enrichment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=filename)

def normalize(text):
    """
    This function takes a string as input and returns a normalized version of the string.
    The normalization process involves converting any accented characters to their unaccented
    equivalents and converting the resulting string to uppercase.
    
    Args:
    - text (str): The string to be normalized.
    
    Returns:
    - str: The normalized version of the input string.
    """
    try:
        return unidecode(text).upper()
    except:
        return text

def haversine_m(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two points on Earth using the Haversine formula.

    Args:
        lat1 (float): Latitude of the first point in degrees.
        lon1 (float): Longitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
        lon2 (float): Longitude of the second point in degrees.

    Returns:
        float: Distance between the two points in meters.
    """
    r = 6371000 # radio de la tierra en metros

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Fórmula de haversine
    a = math.sin(delta_lat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distancia = r * c
    
    return distancia

# Read apartments data
logging.info('Reading apartments data...')
apartments = pd.read_csv('data/interim/apartments.csv')

# Get TransMilenio stations data
logging.info('Getting TransMilenio stations data...')
response = requests.get('https://gis.transmilenio.gov.co/arcgis/rest/services/Troncal/consulta_estaciones_troncales/FeatureServer/1/query?where=1%3D1&outFields=*&f=json').json()
troncal_transmilenio = pd.DataFrame(response['features'])
troncal_transmilenio = pd.json_normalize(troncal_transmilenio['attributes'])

# Add data about TransMilenio stations
def estacion_tm_cercana(row):
    """
    Returns the name of the TransMilenio station closest to the given latitude and longitude coordinates.

    Args:
        row (pandas.Series): A pandas Series containing the latitude and longitude coordinates.

    Returns:
        str: The name of the closest TransMilenio station.
    """
    try:
        distancias = []
        for i, estacion in troncal_transmilenio.iterrows():
            distancias.append(haversine_m(row['latitud'], row['longitud'], estacion['coordenada_y_estacion'], estacion['coordenada_x_estacion']))
        return troncal_transmilenio.loc[np.argmin(distancias), 'nombre_estacion']
    except Exception as e:
        print(e)
        return np.nan
    
def get_distancia_estacion_m(row):
    """
    Calculates the distance in meters between a given location (latitude and longitude) and the nearest TransMilenio station.
    
    Args:
    - row: a pandas Series containing the following fields:
        - latitud: float, the latitude of the location
        - longitud: float, the longitude of the location
        
    Returns:
    - float: the distance in meters between the location and the nearest TransMilenio station. If an error occurs during the calculation, returns np.nan.
    """
    try:
        distancias = []
        for i, estacion in troncal_transmilenio.iterrows():
            distancias.append(haversine_m(row['latitud'], row['longitud'], estacion['coordenada_y_estacion'], estacion['coordenada_x_estacion']))
        return min(distancias)
    except:
        return np.nan

logging.info('Adding TransMilenio stations data...')
apartments['estacion_tm_cercana'] = apartments.apply(estacion_tm_cercana, axis=1)
apartments['distancia_estacion_tm_m'] = apartments.apply(get_distancia_estacion_m, axis=1)
apartments['distancia_estacion_tm_m'] = apartments['distancia_estacion_tm_m'].apply(lambda x: round(x, 2))

def is_cerca_estacion(row):
    """
    Determines if a given row is close to a transportation station based on the distance to the nearest station.

    Args:
        row (pandas.Series): A row of a pandas DataFrame containing the distance to the nearest transportation station.

    Returns:
        int: 1 if the distance to the nearest station is less than or equal to 500 meters, 0 otherwise.
    """
    if row['distancia_estacion_tm_m'] <= 500:
        return 1
    else:
        return 0

logging.info('Adding is_cerca_estacion_tm column...')
apartments['is_cerca_estacion_tm'] = apartments.apply(is_cerca_estacion, axis=1)

# Save processed data
logging.info('Saving processed data...')
apartments.to_csv('data/processed/apartments.csv', index=False)