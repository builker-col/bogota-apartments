from scrapers.metrocuadrado_scraper import MetrocuadradoScraper

if __name__ == '__main__':
    scraper = MetrocuadradoScraper('bogota')
    scraper.run()
    scraper.df.head()