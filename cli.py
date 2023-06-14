import argparse
from scrapers.metrocuadrado_scraper import MetrocuadradoScraper, MetrocuadradoArriendoScraper

parser = argparse.ArgumentParser(description='CLI BogotaHaus')
parser.version = '0.2.0'

parser.add_argument('-s', '--scrape', type=str, help='Selecione el scraper a ejecutar', required=False, choices=['metrocuadrado'], default='metrocuadrado')
parser.add_argument('-c', '--ciudad', type=str, help='Ciudad a scrapear', required=False, choices=['bogota', 'medellin'], default='bogota')
parser.add_argument('-b', '--barrio', type=str, help='Barrio a scrapear *(Opcional)', required=False, default=None)
parser.add_argument('-t', '--tipo', type=str, help='Tipo de apartamento a scrapear *(Opcional)', required=False, choices=['venta', 'arriendo'], default='venta')
parser.add_argument('-o', '--output', type=str, help='Nombre del archivo de salida *(Opcional)', required=False, default='apartamentos')
parser.add_argument('-v', '--version', action='version', help='Muestra la version del CLI', version='%(prog)s 0.2.0')

args = parser.parse_args()

if __name__ == '__main__':
    if args.ciudad == 'bogota':
        if args.tipo == 'venta':
            if args.barrio:
                scraper = MetrocuadradoScraper(args.barrio, args.output)
            else:
                scraper = MetrocuadradoScraper('bogota', args.output)
        elif args.tipo == 'arriendo':
            if args.barrio:
                scraper = MetrocuadradoArriendoScraper(args.barrio)
            else:
                scraper = MetrocuadradoArriendoScraper('bogota')

    else:
        print('No se ha implementado el scraper para otras ciudades')
        exit(1)

    scraper.run()