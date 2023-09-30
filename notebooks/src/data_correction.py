import numpy as np
import pandas as pd
from shapely.geometry import Point

def generate_random_coords_in_polygon(polygon):
    """
    Generates random coordinates within a given polygon.

    Args:
    - polygon: a Shapely Polygon object

    Returns:
    - x, y: a tuple of random coordinates within the polygon
    """
    while True:
        x = np.random.uniform(polygon.bounds['minx'], polygon.bounds['maxx'])[0]
        y = np.random.uniform(polygon.bounds['miny'], polygon.bounds['maxy'])[0]
        point = Point(x, y)
        if polygon.contains(point).any():
            return x, y

def correction_ubication(df, barrios, localidades):
    corrections = {
        'CHICO': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'S.C. CHICO NORTE', 'geometry'],
            'localidad': 'CHAPINERO',
            'barrio': 'S.C. CHICO NORTE'
        },
        'CEDRITOS': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'CEDRITOS', 'geometry'],
            'localidad': 'USAQUEN',
            'barrio': 'CEDRITOS'
        },
        'CHAPINERO ALTO': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'S.C. CHAPINERO NORTE', 'geometry'],
            'localidad': 'CHAPINERO',
            'barrio': 'S.C. CHAPINERO NORTE'
        },
        'LOS ROSALES': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'LOS ROSALES', 'geometry'],
            'localidad': 'CHAPINERO',
            'barrio': 'LOS ROSALES'
        },
        'PUENTE ARANDA': {
            'polygon': localidades.loc[localidades['LocNombre'] == 'PUENTE ARANDA', 'geometry'],
            'localidad': 'PUENTE ARANDA',
            'barrio': 'PUENTE ARANDA'
        },
        'SANTA BARBARA': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'SANTA BARBARA OCCIDENTAL', 'geometry'],
            'localidad': 'USAQUEN',
            'barrio': 'SANTA BARBARA OCCIDENTAL'
        },
        'COUNTRY': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'NUEVO COUNTRY', 'geometry'],
            'localidad': 'USAQUEN',
            'barrio': 'NUEVO COUNTRY'
        },
        'CENTRO INTERNACIONAL': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'SAMPER', 'geometry'],
            'localidad': 'SANTA FE',
            'barrio': 'SAMPER'
        },
        'CERROS DE SUBA': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'S.C. NIZA SUBA', 'geometry'],
            'localidad': 'SUBA',
            'barrio': 'S.C. NIZA SUBA'
        },
        'NIZA ALHAMBRA': {
            'polygon': barrios.loc[barrios['barriocomu'] == 'NIZA SUR', 'geometry'],
            'localidad': 'SUBA',
            'barrio': 'NIZA SUR'
        }
    }

    corrected_rows = []
    for _, row in df.iterrows():
        sector = row['sector']
        if sector in corrections:
            correction = corrections[sector]
            if row['localidad'] != correction['localidad']:
                x, y = generate_random_coords_in_polygon(correction['polygon'])
                corrected_row = {
                    'latitud': float(y),
                    'longitud': float(x),
                    'coords_modified': True,
                    'localidad': correction['localidad'],
                    'barrio': correction['barrio']
                }
                corrected_rows.append(corrected_row)
            else:
                corrected_rows.append(row)
        else:
            corrected_rows.append(row)

    corrected_df = pd.DataFrame(corrected_rows)
    return corrected_df
