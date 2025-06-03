from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
import json

# Scrapy
from bogota_apartments.items import ApartmentsItem
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
import scrapy
import logging
import os

# 🔧 NUEVO: Importar parser y utilidades separadas
from bogota_apartments.parsers import MetrocuadradoParser
from bogota_apartments.utils import try_get, setup_spider_logging, log_scraping_stats, log_error_with_context, ProgressLogger

class MetrocuadradoSpider(scrapy.Spider):
    """
    Spider to scrape apartment data from metrocuadrado.com
    """
    name = 'metrocuadrado'
    allowed_domains = ['metrocuadrado.com']
    base_url = 'https://www.metrocuadrado.com/rest-search/search'

    def __init__(self):
        """
        Initializes the spider with a headless Chrome browser instance
        """
        # 🔧 CORREGIDO: Usar nombre diferente para evitar conflicto con logger de Scrapy
        self.spider_logger = setup_spider_logging(self.name)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument(f'user-agent={UserAgent().random}')
        chrome_options.add_argument('--disk-cache=true')

        self.driver = webdriver.Chrome(options=chrome_options,)
        
        # 🔧 NUEVO: Inicializar parser especializado
        self.parser = MetrocuadradoParser(self.spider_logger)
        
        # 📊 Estadísticas de scraping
        self.stats = {
            'total_requests': 0,
            'successful_parses': 0,
            'failed_parses': 0,
            'total_apartments': 0,
            'venta_apartments': 0,
            'arriendo_apartments': 0
        }
        
        # 📈 Progress tracker
        self.progress_logger = None

    def start_requests(self):
        """
        Generación dinámica de requests basada en totales reales de API
        """
        self.spider_logger.info("🚀 Iniciando descubrimiento de apartamentos disponibles...")
        
        headers = {
            'X-Api-Key': 'P1MfFHfQMOtL16Zpg36NcntJYCLFm8FqFfudnavl',
            'User-Agent': UserAgent().random
        }
        
        # Paso 1: Descubrir totales para cada tipo de operación
        for operation_type in ['venta', 'arriendo']:
            discovery_url = f'{self.base_url}?realEstateTypeList=apartamento&realEstateBusinessList={operation_type}&city=bogot%C3%A1&from=0&size=50'
            
            self.spider_logger.info(f"🔍 Descubriendo totales para: {operation_type}")
            
            yield scrapy.Request(
                url=discovery_url,
                headers=headers,
                callback=self.discover_and_paginate,
                meta={'operation_type': operation_type, 'headers': headers}
            )

    def discover_and_paginate(self, response):
        """
        Descubre el total real y genera todas las peticiones de paginación
        """
        operation_type = response.meta['operation_type']
        headers = response.meta['headers']
        
        try:
            # Extraer metadatos reales de la API
            api_data = json.loads(response.body)
            total_hits = api_data.get('totalHits', 0)
            total_accessible = min(total_hits, api_data.get('totalEntries', 0))
            
            self.spider_logger.info(f"🎯 {operation_type}: {total_accessible:,} apartamentos accesibles de {total_hits:,} totales")
            
            # 📊 Actualizar estadísticas
            self.stats[f'{operation_type}_apartments'] = total_accessible
            self.stats['total_apartments'] += total_accessible
            
            # Inicializar progress logger en el primer descubrimiento
            if not self.progress_logger:
                self.progress_logger = ProgressLogger(self.spider_logger, total_accessible * 2)  # venta + arriendo
            
            # Generar requests dinámicamente
            page_size = 50
            requests_generated = 0
            
            for offset in range(0, total_accessible, page_size):
                if offset + page_size > total_accessible:
                    # Ajustar último batch para no exceder límites
                    continue
                
                url = f'{self.base_url}?realEstateTypeList=apartamento&realEstateBusinessList={operation_type}&city=bogot%C3%A1&from={offset}&size={page_size}'
                
                requests_generated += 1
                self.stats['total_requests'] += 1
                
                yield scrapy.Request(
                    url=url,
                    headers=headers,
                    callback=self.parse,
                    meta={'operation_type': operation_type, 'current_offset': offset}
                )
            
            self.spider_logger.info(f"📤 Generadas {requests_generated} peticiones para {operation_type}")
            
        except Exception as e:
            log_error_with_context(
                self.spider_logger, 
                e, 
                {
                    'operation_type': operation_type,
                    'url': response.url,
                    'response_status': response.status
                }
            )

    def parse(self, response):
        """
        Parses the response from the initial requests and generates requests to scrape apartment details
        """
        operation_type = response.meta['operation_type']
        current_offset = response.meta['current_offset']
        
        try:
            result = json.loads(response.body)['results']
            self.spider_logger.info(f'📦 {operation_type} | Offset {current_offset}: {len(result)} apartamentos encontrados')

            for item in result:
                yield scrapy.Request(
                    url=f'https://metrocuadrado.com{item["link"]}',
                    callback=self.details_parse,
                    meta={'operation_type': operation_type}
                )
                
        except Exception as e:
            log_error_with_context(
                self.spider_logger,
                e,
                {
                    'operation_type': operation_type,
                    'offset': current_offset,
                    'url': response.url
                }
            )

    def details_parse(self, response):
        """
        Parses the response from the requests to scrape apartment details and yields the scraped data
        """
        operation_type = response.meta.get('operation_type', 'unknown')
        
        try:
            self.driver.get(response.url)   
            
            self.spider_logger.debug(f'🏠 Procesando apartamento: {response.url}')

            # 🎯 Extraer el script específico con xpath
            script_data = Selector(text=self.driver.page_source).xpath(
                '/html/body/script[10]/text()'
            ).get()

            if not script_data:
                self.spider_logger.warning('⚠️ No se encontró script en primera búsqueda, reintentando...')
                self.driver.get(response.url)
                self.driver.implicitly_wait(10)
                script_data = Selector(text=self.driver.page_source).xpath('/html/body/script[10]/text()').get()

            # 🔧 ACTUALIZADO: Usar parser separado
            script_data = self.parser.parse_nextjs_data(script_data)
            
            if not script_data:
                self.spider_logger.error(f'❌ No se pudo extraer datos JSON del script Next.js: {response.url}')
                self.stats['failed_parses'] += 1
                return

            # 📊 Actualizar progreso
            self.stats['successful_parses'] += 1
            if self.progress_logger:
                self.progress_logger.update(1, f"✅ {script_data.get('propertyId', 'N/A')}")

            # 🔧 CORREGIDO: script_data ahora es un diccionario, no una lista
            loader = ItemLoader(item=ApartmentsItem(), selector=script_data)

            #codigo
            loader.add_value('codigo', script_data.get('propertyId'))
            #tipo_propiedad
            loader.add_value('tipo_propiedad', try_get(script_data, ['propertyType', 'nombre']))
            #tipo_operacion
            loader.add_value('tipo_operacion', script_data.get('businessType'))
            #precio_venta
            loader.add_value('precio_venta', script_data.get('salePrice'))
            #precio_arriendo
            loader.add_value('precio_arriendo', script_data.get('rentPrice'))
            #area
            loader.add_value('area', script_data.get('area'))
            #habitaciones
            loader.add_value('habitaciones', script_data.get('rooms'))
            #banos
            loader.add_value('banos', script_data.get('bathrooms'))
            #administracion
            loader.add_value('administracion', try_get(script_data, ['detail', 'adminPrice']))
            #parqueaderos
            loader.add_value('parqueaderos', script_data.get('garages'))
            #sector
            loader.add_value('sector', try_get(script_data, ['sector', 'nombre']))
            #estrato
            loader.add_value('estrato', script_data.get('stratum'))
            #antiguedad
            loader.add_value('antiguedad', script_data.get('builtTime'))
            #estado
            loader.add_value('estado', script_data.get('propertyState'))
            #longitud
            loader.add_value('longitud', try_get(script_data, ['coordinates', 'lon']))
            #latitud
            loader.add_value('latitud', try_get(script_data, ['coordinates', 'lat']))
            #featured_interior
            loader.add_value('featured_interior', try_get(script_data, ['featured', 0, 'items']))
            #featured_exterior
            loader.add_value('featured_exterior', try_get(script_data, ['featured', 1, 'items']))
            #featured_zona_comun
            loader.add_value('featured_zona_comun', try_get(script_data, ['featured', 2, 'items']))
            #featured_sector
            loader.add_value('featured_sector', try_get(script_data, ['featured', 3, 'items']))
            #Imagenes
            try:
                imagenes = []
                images_data = script_data.get('images', [])
                for img in images_data:
                    if isinstance(img, dict) and 'image' in img:
                        imagenes.append(img['image'])

                loader.add_value('imagenes', imagenes)
            except Exception as e:
                self.spider_logger.warning(f'⚠️ Error procesando imágenes: {e}')
            #compania
            loader.add_value('compañia', script_data.get('companyName'))
            #descripcion            
            loader.add_value('descripcion', script_data.get('comment'))
            #website
            loader.add_value('website', 'metrocuadrado.com')
            # last_view
            loader.add_value('last_view', datetime.now())
            #datetime
            loader.add_value('datetime', datetime.now())

            yield loader.load_item()
            
        except Exception as e:
            self.stats['failed_parses'] += 1
            log_error_with_context(
                self.spider_logger,
                e,
                {
                    'url': response.url,
                    'operation_type': operation_type,
                    'failed_parses': self.stats['failed_parses']
                }
            )
    
    def closed(self, reason):
        """
        Callback cuando el spider termina - registra estadísticas finales
        """
        self.spider_logger.info("🏁 Spider terminando...")
        
        # Finalizar progress logger
        if self.progress_logger:
            self.progress_logger.finish("Scraping de Metrocuadrado completado")
        
        # Calcular estadísticas finales
        success_rate = 0
        if self.stats['successful_parses'] + self.stats['failed_parses'] > 0:
            success_rate = (self.stats['successful_parses'] / (self.stats['successful_parses'] + self.stats['failed_parses'])) * 100
        
        final_stats = {
            **self.stats,
            'success_rate': f"{success_rate:.1f}%",
            'reason': reason
        }
        
        # Registrar estadísticas finales
        log_scraping_stats(self.spider_logger, final_stats)
        
        # Cerrar navegador
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.spider_logger.info("🔒 Navegador cerrado correctamente")