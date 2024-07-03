# Author: Erik Garcia (@erik172)
# Version: Unreleased
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

import logging

class MetrocuadradoSpider(scrapy.Spider):
    name = 'metrocuadrado'
    allowed_domains = ['metrocuadrado.com']
    base_url = 'https://www.metrocuadrado.com/rest-search/search'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(
            filename='metrocuadrado_spider.log',
            format='%(levelname)s: %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(self.name)

    def start_requests(self):
        user_agent = UserAgent().random
        headers = {
            'X-Api-Key': 'P1MfFHfQMOtL16Zpg36NcntJYCLFm8FqFfudnavl',
            'User-Agent': user_agent
        }

        for type in ['venta', 'arriendo']:
            for offset in range(0, 9950, 50):
                url = f'{self.base_url}?realEstateTypeList=apartamento&realEstateBusinessList={type}&city=bogot%C3%A1&from={offset}&size=50'
                self.logger.info(f'Sending request to URL: {url}')
                yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.body)['results']
        self.logger.info(f'Found {len(result)} apartments in response')

        user_agent = UserAgent().random

        for item in result:
            self.logger.info(f'Parsing details for apartment: {item["link"]}')
            yield SplashRequest(
                url=f'https://metrocuadrado.com{item["link"]}',
                callback=self.details_parse,
                args={'wait': 0.1},
                headers={'User-Agent': user_agent}
            )

    def details_parse(self, response):
        script_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        
        if not script_data:
            self.logger.warning(f'No script data found in response for URL: {response.url}')
            return

        script_data = json.loads(script_data)['props']['initialProps']['pageProps']['realEstate']
        self.logger.info(f'Parsing data for property ID: {script_data["propertyId"]}')

        loader = self.populate_loader(script_data)
        loader.add_value('last_view', datetime.now())
        loader.add_value('datetime', datetime.now())
        loader.add_value('url', response.url)

        yield loader.load_item()

    def populate_loader(self, script_data):
        loader = ItemLoader(item=ApartmentsItem())
        # Resto del código de populate_loader aquí
        loader.add_value('codigo', script_data['propertyId'])
        loader.add_value('tipo_propiedad', script_data['propertyType']['nombre'])
        loader.add_value('tipo_operacion', script_data['businessType'])
        loader.add_value('precio_venta', script_data['salePrice'])
        loader.add_value('precio_arriendo', script_data['rentPrice'])
        loader.add_value('area', script_data['area'])
        loader.add_value('habitaciones', script_data['rooms'])
        loader.add_value('banos', script_data['bathrooms'])
        loader.add_value('administracion', script_data['detail']['adminPrice'])
        loader.add_value('parqueaderos', script_data['garages'])
        loader.add_value('sector', self.try_get(script_data, ['sector', 'nombre']))
        loader.add_value('estrato', script_data.get('stratum'))
        loader.add_value('antiguedad', script_data['builtTime'])
        loader.add_value('estado', script_data['propertyState'])
        loader.add_value('longitud', script_data['coordinates']['lon'])
        loader.add_value('latitud', script_data['coordinates']['lat'])
        loader.add_value('featured_interior', self.try_get(script_data, ['featured', 0, 'items']))
        loader.add_value('featured_exterior', self.try_get(script_data, ['featured', 1, 'items']))
        loader.add_value('featured_zona_comun', self.try_get(script_data, ['featured', 2, 'items']))
        loader.add_value('featured_sector', self.try_get(script_data, ['featured', 3, 'items']))

        if 'images' in script_data:
            images = [img['image'] for img in script_data['images']]
            loader.add_value('imagenes', images)
        loader.add_value('compañia', script_data.get('companyName'))
        loader.add_value('descripcion', script_data['comment'])
        loader.add_value('website', 'metrocuadrado.com')

        return loader

    def try_get(self, dictionary, keys):
        try:
            value = dictionary
            for key in keys:
                if isinstance(value, list) and isinstance(key, int) and 0 <= key < len(value):
                    value = value[key]
                elif isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
        except (KeyError, TypeError, IndexError):
            return None
