from scraper import metrocudrado_scraper

interes = ['bosque-izquierdo', 'centro-internacional', 'cabrera']

localidades = ['usaquen', 'chapinero', 'santa-fe', 'san-cristobal', 'usme',
               'tunjuelito', 'bosa', 'kennedy', 'fontibon', 'engativa',                       
               'suba', 'barrios-unidos', 'teusaquillo', 'los-martires',                       
               'antonio-nariño', 'puente-aranda', 'la-candelaria', 'rafael-uribe-uribe',                       
               'ciudad-bolivar', 'sumapaz']

localidades.append(interes)


def main():
    for i in localidades:
        print(f'Running in {i}')
        metrocudrado_scraper.run(i, path='data/raw/')

if __name__ == '__main__':
    main()