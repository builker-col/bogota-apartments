from fake_useragent import UserAgent
from datetime import datetime
import json

# Scrapy
from bogota_apartments.items import ApartmentsItem
from scrapy.loader import ItemLoader
import scrapy


class HabiSpider(scrapy.Spider):
    """
    This spider is used to scrape apartment data from habi.co website.
    """
    name = 'habi'
    allowed_domains = ['habi.co', 'apiv2.habi.co']
    base_url = 'https://apiv2.habi.co/listing-global-api/get_properties'

    def start_requests(self):
        '''
        This function is used to obtain the metrosquare API data by iterating on the operation types and API offsets.
        
        :return: scrapy.Request
        '''
        headers = {
            'X-Api-Key': 'VnXl0bdH2gaVltgd7hJuHPOrMZAlvLa5KGHJsrr6',
            'Referer': 'https://habi.co/',
            'Origin': 'https://habi.co',
            'User-Agent': UserAgent().random
        }

        # hay en total 817 resultados
        for offset in range(0, 832, 32):
            url = f'{self.base_url}?offset={offset}&limit=32&filters=%7B%22cities%22:[%22bogota%22]%7D&country=CO'

            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        """
        This function is used to parse the response from the start_requests function and extract the apartment data.
        
        :param response: scrapy.Response
        :return: scrapy.Request
        """
        result = json.loads(response.body)['messagge']['data']
        self.logger.info(f'Found {len(result)} apartments')

        for item in result:
            property_nid = item['property_nid']
            slug = item['slug']

            headers = {
                'Referer': f'https://habi.co/venta-apartamentos/{property_nid}/{slug}',
                'User-Agent': UserAgent().random
            }

            yield scrapy.Request(
                url=f'https://habi.co/page-data/venta-apartamentos/{property_nid}/{slug}/page-data.json',
                headers=headers,
                callback=self.parse_details
            )

    def parse_details(self, response):
        """
        This function is used to parse the response from the parse function and extract the apartment details.
        
        :param response: scrapy.Response
        :return: scrapy.Item
        """
        details = json.loads(response.body)['result']['pageContext']

        loader = ItemLoader(item=ApartmentsItem(), selector=details)
        #codigo
        loader.add_value('codigo', details['propertyId'])

        details = details['propertyDetail']['property']
        #tipo propiedad
        loader.add_value('tipo_propiedad', details['detalles_propiedad']['tipo_inmueble'])
        #tipo operacion
        loader.add_value('tipo_operacion', 'venta')
        #precio ventas
        loader.add_value('precio_venta', details['detalles_propiedad']['precio_venta'])
        #area
        loader.add_value('area', details['detalles_propiedad']['area'])
        #habitaciones
        loader.add_value('habitaciones', details['detalles_propiedad']['num_habitaciones'])
        #baños
        loader.add_value('banos', details['detalles_propiedad']['baños'])
        #administracion
        loader.add_value('administracion', details['detalles_propiedad']['last_admin_price'])
        #parqueaderos
        loader.add_value('parqueaderos', details['detalles_propiedad']['garajes'])
        #sector
        loader.add_value('sector', details['detalles_propiedad']['zona_mediana'])
        #estrato 
        loader.add_value('estrato', details['detalles_propiedad']['estrato'])
        #estado
        #antiguedad
        loader.add_value('antiguedad', details['detalles_propiedad']['anos_antiguedad'])
        #latitud
        loader.add_value('latitud', details['detalles_propiedad']['latitud'])
        #langitud
        loader.add_value('longitud', details['detalles_propiedad']['longitud'])
        #direccion
        loader.add_value('direccion', details['detalles_propiedad']['direccion'])
        #featured_interior
        loader.add_value('featured_interior', details['caracteristicas_propiedad'])
        #featured_exterior
        #featured_zona_comun
        #featured_sector
        #descripcion
        loader.add_value('descripcion', details['descripcion'])
        #compañia
        #imagenes
        images = []
        for image in details['images']:
            url = f'https://d3hzflklh28tts.cloudfront.net/{image["url"]}?d=400x400'
            images.append(url)
        loader.add_value('imagenes', images)
        #website
        loader.add_value('website', 'habi.co')
        #datetime
        loader.add_value('datetime', datetime.now())

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
            return None  #
        
