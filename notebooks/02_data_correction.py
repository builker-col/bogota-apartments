"""
This script imports data from CSV files, performs data correction and enrichment, and exports the cleaned data to a new CSV file.
The script first imports apartment data from a CSV file and shapefiles containing information about Bogota's localities and neighborhoods.
It then performs data correction and enrichment, including adding missing locality and neighborhood information to apartments, removing apartments with invalid locality or neighborhood information, and dropping duplicates.
Finally, the cleaned data is exported to a new CSV file.
"""
from src import data_enrichment, data_correction
from unidecode import unidecode
from dotenv import load_dotenv
import logging
import pandas as pd
import geopandas as gpd
import warnings
import os

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# verificar si etoy dentro de la carpeta notebooks o no
if os.getcwd().split('/')[-1] == 'notebooks':
    os.chdir('..')

load_dotenv()

def normalize_text(text):
    """
    This function takes a string as input and returns a normalized version of the string.
    The normalization process involves converting any accented characters to their unaccented
    equivalents and converting the resulting string to uppercase. If an error occurs during
    the normalization process, the original string is returned.
    
    Args:
    - text (str): The string to be normalized.
    
    Returns:
    - str: The normalized version of the input string, or the original string if an error occurs.
    """
    try:
        return unidecode(text).upper()
    except:
        return text

# Importar Datos
logging.info('Importando datos...')
apartments = pd.read_csv('data/interim/apartments.csv')
apartments['coords_modified'] = False # Para saber si se modificó la coordenada original


localidades = gpd.read_file('data/external/localidades_bogota/loca.shp')
barrios = gpd.read_file('data/external/barrios_bogota/barrios.geojson')

# Data Corection
logging.info('Corrigiendo datos... (esto puede tardar un rato)')
apartments['localidad'] = apartments.apply(data_enrichment.get_localidad, axis=1, localidades=localidades)
apartments = apartments.dropna(subset=['localidad', 'sector'], how='all')
apartments.drop(apartments.loc[apartments['estrato'] == 7].index, inplace=True)

# Agregando barrios, segun las coordenadas de los apartamentos

barrios['barriocomu'] = barrios['barriocomu'].apply(normalize_text)
barrios['localidad'] = barrios['localidad'].apply(normalize_text)
barrios.localidad.unique()

barrios.loc[barrios['localidad'] == 'RAFAEL URIBE', 'localidad'] = 'RAFAEL URIBE URIBE'
barrios.loc[barrios['localidad'].isna(), 'localidad'] = 'SUBA'

apartments['barrio'] = apartments.apply(data_enrichment.get_barrio, axis=1, barrios=barrios)

apartments = apartments.apply(data_correction.correction_ubication, axis=1, barrios=barrios, localidades=localidades)

conditions = {
    'KENNEDY': [6, 5],
    'RAFAEL URIBE URIBE': [6, 5],
    'LA PAZ CENTRAL': [6],
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

for loc, estratos in conditions.items():
    for estrato in estratos:
        out = apartments.loc[(apartments['localidad'] == loc) & (apartments['estrato'] == estrato)]
        apartments = apartments.drop(out.index)


apartments.dropna(subset=['localidad', 'barrio'], how='all', inplace=True)


# del apartments['direccion']
apartments = apartments.drop_duplicates(subset=['codigo'], keep='first')
apartments.to_csv('data/interim/apartments.csv', index=False)