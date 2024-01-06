# Author: Erik Alejandro Garcia Duarte (@erik172)
# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector

# Splash
from scrapy_splash import SplashRequest
from fake_useragent import UserAgent
from datetime import datetime
import json

# Scrapy
from bogota_apartments.items import ApartmentsItem
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
import scrapy

class MetrocuadradoSpider(scrapy.Spider):
    """
    Spider to scrape apartment data from metrocuadrado.com
    """
    name = 'metrocuadrado'
    allowed_domains = ['metrocuadrado.com']
    base_url = 'https://www.metrocuadrado.com/rest-search/search'

    def start_requests(self):
        """
        Generates the initial requests to scrape apartment data
        """
        headers = {
            'X-Api-Key': 'P1MfFHfQMOtL16Zpg36NcntJYCLFm8FqFfudnavl',
            'User-Agent': UserAgent().random
        }

        for type in ['venta', 'arriendo']:
            for offset in range(0, 9950, 50):
                url = f'{self.base_url}?realEstateTypeList=apartamento&realEstateBusinessList={type}&city=bogot%C3%A1&from={offset}&size=50'

                yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        """
        Parses the response from the initial requests and generates requests to scrape apartment details
        """
        result = json.loads(response.body)['results']
        self.logger.info(f'Found {len(result)} apartments')

        for item in result:
            yield SplashRequest(
                url=f'https://metrocuadrado.com{item["link"]}',
                callback=self.details_parse,
                args={'wait': 0.1},
                headers={
                    'User-Agent': UserAgent().random
                }
            )

    def details_parse(self, response):
        """
        Parses the response from the requests to scrape apartment details and yields the scraped data
        """
        script_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        script_data = json.loads(script_data)['props']['initialProps']['pageProps']['realEstate']

        for item in script_data:
            loader = ItemLoader(item=ApartmentsItem(), selector=item)

            #codigo
            loader.add_value('codigo', script_data['propertyId'])
            #tipo_propiedad
            loader.add_value('tipo_propiedad', script_data['propertyType']['nombre'])
            #tipo_operacion
            loader.add_value('tipo_operacion', script_data['businessType'])
            #precio_venta
            loader.add_value('precio_venta', script_data['salePrice'])
            #precio_arriendo
            loader.add_value('precio_arriendo', script_data['rentPrice'])
            #area
            loader.add_value('area', script_data['area'])
            #habitaciones
            loader.add_value('habitaciones', script_data['rooms'])
            #banos
            loader.add_value('banos', script_data['bathrooms'])
            #administracion
            loader.add_value('administracion', script_data['detail']['adminPrice'])
            #parqueaderos
            loader.add_value('parqueaderos', script_data['garages'])
            #sector
            loader.add_value('sector', self.try_get(script_data, ['sector', 'nombre']))
            #estrato
            loader.add_value('estrato', script_data['stratum'] if 'stratum' in script_data else None)
            #antiguedad
            loader.add_value('antiguedad', script_data['builtTime'])
            #estado
            loader.add_value('estado', script_data['propertyState'])
            #longitud
            loader.add_value('longitud', script_data['coordinates']['lon'])
            #latitud
            loader.add_value('latitud', script_data['coordinates']['lat'])
            #featured_interior
            loader.add_value('featured_interior', self.try_get(script_data, ['featured', 0, 'items']))
            #featured_exterior
            loader.add_value('featured_exterior', self.try_get(script_data, ['featured', 1, 'items']))
            #featured_zona_comun
            loader.add_value('featured_zona_comun', self.try_get(script_data, ['featured', 2, 'items']))
            #featured_sector
            loader.add_value('featured_sector', self.try_get(script_data, ['featured', 3, 'items']))
            #Imagenes
            try:
                imagenes = []
                for img in script_data['images']:
                    imagenes.append(img['image'])

                loader.add_value('imagenes', imagenes)
            except:
                pass
            #compania
            loader.add_value('compañia', script_data['companyName'] if 'companyName' in script_data else None)
            #descripcion            
            loader.add_value('descripcion', script_data['comment'])
            #website
            loader.add_value('website', 'metrocuadrado.com')
            # last_view
            loader.add_value('last_view', datetime.now())
            #datetime
            loader.add_value('datetime', datetime.now())
            #url 
            loader.add_value('url', response.url)

            yield loader.load_item()

    def try_get(self, dictionary, keys: list):
        """
        Tries to get a value from a nested data structure and returns None if the key is not found or if an index is out of range.
        """
        try:
            value = dictionary
            for key in keys:
                if isinstance(value, list) and isinstance(key, int) and 0 <= key < len(value):
                    value = value[key]
                elif isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None  # Key or index is not valid
            return value
        except (KeyError, TypeError, IndexError):
            return None  # Key or index is not valid

class MetrocuadradoSearchSpider(scrapy.Spider):
    name = 'metrocuadrado_search'
    allowed_domains = ['metrocuadrado.com']
    base_url = 'https://www.metrocuadrado.com/apartamento/venta'

    def __init__(self, *args, **kwargs):
        self.search_term = kwargs.get('search')
        self.search_term = self.search_term.replace(' ', '-').lower()

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument(f'user-agent={UserAgent().random}')
        chrome_options.add_argument('--no-sandbox')

        self.driver = webdriver.Chrome(
            options=chrome_options,
        )

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}/{self.search_term}', callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        response = Selector(text=self.driver.page_source)

        for item in response.xpath('//ul[@class="Ul-sctud2-0 jyGHXP realestate-results-list browse-results-list"]/li'):
            yield SplashRequest(
                url=f'https://metrocuadrado.com{item.xpath("./a/@href")[0]}',
                callback=self.details_parse,
                args={'wait': 2},
                headers={
                    'User-Agent': UserAgent().random
                }
            )

    def details_parse(self, response):
        """
        Parses the response from the requests to scrape apartment details and yields the scraped data
        """
        script_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if len(script_data) == 0:
            return

        script_data = script_data.get()
        script_data = json.loads(script_data)['props']['initialProps']['pageProps']['realEstate']

        for item in script_data:
            loader = ItemLoader(item=ApartmentsItem(), selector=item)

            #codigo
            loader.add_value('codigo', script_data['propertyId'])
            #tipo_propiedad
            loader.add_value('tipo_propiedad', script_data['propertyType']['nombre'])
            #tipo_operacion
            loader.add_value('tipo_operacion', script_data['businessType'])
            #precio_venta
            loader.add_value('precio_venta', script_data['salePrice'])
            #precio_arriendo
            loader.add_value('precio_arriendo', script_data['rentPrice'])
            #area
            loader.add_value('area', script_data['area'])
            #habitaciones
            loader.add_value('habitaciones', script_data['rooms'])
            #banos
            loader.add_value('banos', script_data['bathrooms'])
            #administracion
            loader.add_value('administracion', script_data['detail']['adminPrice'])
            #parqueaderos
            loader.add_value('parqueaderos', script_data['garages'])
            #sector
            loader.add_value('sector', self.try_get(script_data, ['sector', 'nombre']))
            #estrato
            loader.add_value('estrato', script_data['stratum'] if 'stratum' in script_data else None)
            #antiguedad
            loader.add_value('antiguedad', script_data['builtTime'])
            #estado
            loader.add_value('estado', script_data['propertyState'])
            #longitud
            loader.add_value('longitud', script_data['coordinates']['lon'])
            #latitud
            loader.add_value('latitud', script_data['coordinates']['lat'])
            #featured_interior
            loader.add_value('featured_interior', self.try_get(script_data, ['featured', 0, 'items']))
            #featured_exterior
            loader.add_value('featured_exterior', self.try_get(script_data, ['featured', 1, 'items']))
            #featured_zona_comun
            loader.add_value('featured_zona_comun', self.try_get(script_data, ['featured', 2, 'items']))
            #featured_sector
            loader.add_value('featured_sector', self.try_get(script_data, ['featured', 3, 'items']))
            #Imagenes
            try:
                imagenes = []
                for img in script_data['images']:
                    imagenes.append(img['image'])

                loader.add_value('imagenes', imagenes)
            except:
                pass
            #compania
            loader.add_value('compañia', script_data['companyName'] if 'companyName' in script_data else None)
            #descripcion            
            loader.add_value('descripcion', script_data['comment'])
            #website
            loader.add_value('website', 'metrocuadrado.com')
            #datetime
            loader.add_value('datetime', datetime.now())
            #url 
            loader.add_value('url', response.url)

            yield loader.load_item()