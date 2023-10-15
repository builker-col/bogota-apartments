import numpy as np
from shapely.geometry import Point

def random_coords_in_polygon(polygon):
    """
    Generates random coordinates within a given polygon.

    Args:
    - polygon: a Shapely Polygon object

    Returns:
    - x, y: a tuple of random coordinates within the polygon
    """
    while True:
        x = np.random.uniform(polygon.bounds[0], polygon.bounds[2])
        y = np.random.uniform(polygon.bounds[1], polygon.bounds[3])
        point = Point(x, y)
        if polygon.contains(point):
            return x, y

def correction_ubication(row, barrios, localidades):
    sector_dict = {
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

    sector = row['sector']
    if sector in sector_dict:
        if row['localidad'] != sector_dict[sector]['localidad']:
            polygon = sector_dict[sector]['polygon'].iloc[0] # extract the first element of the Series object
            x, y = random_coords_in_polygon(polygon)
            row['latitud'] = float(y)
            row['longitud'] = float(x)
            row['coords_modified'] = True
            row['localidad'] = sector_dict[sector]['localidad']
            row['barrio'] = sector_dict[sector]['barrio']

    return row