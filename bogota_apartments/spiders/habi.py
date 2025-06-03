# Author: Erik Garcia (@erik172)
# Version: 3.0.0 - Sistema de Logging Mejorado
from fake_useragent import UserAgent
from datetime import datetime
import json

# Scrapy
from bogota_apartments.items import ApartmentsItem
from scrapy.loader import ItemLoader
import scrapy

# 🔧 NUEVO: Importar sistema de logging, utilidades y parser especializado
from bogota_apartments.utils import (
    try_get, 
    setup_spider_logging, 
    log_scraping_stats, 
    log_error_with_context, 
    ProgressLogger
)
from bogota_apartments.parsers import HabiParser


class HabiSpider(scrapy.Spider):
    """
    Spider para extraer datos de apartamentos del sitio web habi.co
    
    Con sistema de logging mejorado y seguimiento de progreso en tiempo real.
    """
    name = 'habi'
    allowed_domains = ['habi.co', 'apiv2.habi.co']
    base_url = 'https://apiv2.habi.co/listing-global-api/get_properties'

    def __init__(self):
        """
        Inicializa el spider con sistema de logging mejorado
        """
        # 🔧 CORREGIDO: Usar nombre diferente para evitar conflicto con logger de Scrapy
        self.spider_logger = setup_spider_logging(self.name)
        
        # 🔧 NUEVO: Inicializar parser especializado para Habi
        self.parser = HabiParser(self.spider_logger)
        
        # 📊 Estadísticas de scraping
        self.stats = {
            'total_requests': 0,
            'successful_parses': 0,
            'failed_parses': 0,
            'total_apartments': 0,
            'total_pages': 0,
            'processed_apartments': 0
        }
        
        # 📈 Progress tracker - se inicializará dinámicamente
        self.progress_logger = None
        
        super().__init__()

    def start_requests(self):
        '''
        Genera peticiones para obtener datos de la API de Habi con paginación dinámica
        
        :return: scrapy.Request
        '''
        self.spider_logger.info("🚀 Iniciando scraping de apartamentos en Habi con paginación dinámica...")
        
        headers = {
            'X-Api-Key': 'VnXl0bdH2gaVltgd7hJuHPOrMZAlvLa5KGHJsrr6',
            'Referer': 'https://habi.co/',
            'Origin': 'https://habi.co',
            'User-Agent': UserAgent().random
        }

        # Iniciar con la primera página
        initial_url = f'{self.base_url}?offset=0&limit=32&filters=%7B%22cities%22:[%22bogota%22]%7D&country=CO'
        
        self.spider_logger.info("🔍 Iniciando paginación dinámica...")
        
        yield scrapy.Request(
            url=initial_url,
            headers=headers,
            callback=self.parse_with_pagination,
            meta={'headers': headers, 'offset': 0, 'limit': 32}
        )

    def parse_with_pagination(self, response):
        """
        Parsea la respuesta y genera las siguientes peticiones si hay más datos disponibles
        """
        headers = response.meta['headers']
        current_offset = response.meta['offset']
        limit = response.meta['limit']
        
        try:
            # Extraer datos de la respuesta
            api_data = json.loads(response.body)
            message_data = api_data.get('messagge', {})
            
            apartments_batch = message_data.get('data', [])
            more_available = message_data.get('more_available', False)
            more_offset = message_data.get('more_offset', current_offset + limit)
            
            batch_size = len(apartments_batch)
            self.stats['total_apartments'] += batch_size
            self.stats['total_requests'] += 1
            
            self.spider_logger.info(f'📦 Habi | Offset {current_offset}: {batch_size} apartamentos encontrados')
            self.spider_logger.info(f'🔄 Más disponibles: {more_available} | Next offset: {more_offset}')
            
            # Inicializar progress logger en la primera página (estimación conservadora)
            if not self.progress_logger and batch_size > 0:
                # Estimación inicial: si tenemos 32 en primera página, estimamos al menos 1000
                estimated_total = max(1000, batch_size * 10)
                self.progress_logger = ProgressLogger(self.spider_logger, estimated_total)
                self.spider_logger.info(f"📈 Progress tracker inicializado (estimación: {estimated_total})")

            # Procesar apartamentos de esta página
            for item in apartments_batch:
                property_nid = item['property_nid']
                slug = item['slug']

                headers_detail = {
                    'Referer': f'https://habi.co/venta-apartamentos/{property_nid}/{slug}',
                    'User-Agent': UserAgent().random
                }

                yield scrapy.Request(
                    url=f'https://habi.co/page-data/venta-apartamentos/{property_nid}/{slug}/page-data.json',
                    headers=headers_detail,
                    callback=self.parse_details,
                    meta={'property_nid': property_nid, 'slug': slug}
                )
            
            # Si hay más datos disponibles, generar siguiente petición
            if more_available:
                next_url = f'{self.base_url}?offset={more_offset}&limit={limit}&filters=%7B%22cities%22:[%22bogota%22]%7D&country=CO'
                
                self.spider_logger.info(f"➡️ Generando siguiente petición: offset {more_offset}")
                
                yield scrapy.Request(
                    url=next_url,
                    headers=headers,
                    callback=self.parse_with_pagination,
                    meta={'headers': headers, 'offset': more_offset, 'limit': limit}
                )
            else:
                self.spider_logger.info(f"🏁 Paginación completada. Total apartamentos: {self.stats['total_apartments']}")
                
        except Exception as e:
            log_error_with_context(
                self.spider_logger,
                e,
                {
                    'url': response.url,
                    'offset': current_offset,
                    'response_status': response.status
                }
            )

    def parse(self, response):
        """
        Método parse original - mantenido por compatibilidad pero no se usa
        """
        # Redirigir a la nueva lógica de paginación
        return self.parse_with_pagination(response)

    def parse_details(self, response):
        """
        Parsea los detalles de un apartamento específico usando el parser especializado
        
        :param response: scrapy.Response
        :return: scrapy.Item
        """
        property_nid = response.meta.get('property_nid', 'unknown')
        slug = response.meta.get('slug', 'unknown')
        
        try:
            # 🔧 NUEVO: Usar parser especializado para procesar datos JSON
            raw_data = json.loads(response.body)['result']['pageContext']
            parsed_data = self.parser.parse_habi_data(raw_data)
            
            if not parsed_data:
                self.spider_logger.error(f'❌ No se pudo extraer datos de Habi: {response.url}')
                self.stats['failed_parses'] += 1
                return

            # 📊 Actualizar progreso
            self.stats['successful_parses'] += 1
            self.stats['processed_apartments'] += 1
            
            if self.progress_logger:
                self.progress_logger.update(1, f"✅ {parsed_data.get('propertyId', property_nid)}")

            # 🔧 ACTUALIZADO: Usar datos del parser especializado
            loader = ItemLoader(item=ApartmentsItem(), selector=parsed_data)
            
            #codigo
            loader.add_value('codigo', parsed_data.get('propertyId'))
            #tipo propiedad
            loader.add_value('tipo_propiedad', parsed_data.get('tipo_inmueble'))
            #tipo operacion
            loader.add_value('tipo_operacion', 'venta')
            #precio ventas
            loader.add_value('precio_venta', parsed_data.get('precio_venta'))
            #area
            loader.add_value('area', parsed_data.get('area'))
            #habitaciones
            loader.add_value('habitaciones', parsed_data.get('num_habitaciones'))
            #baños
            loader.add_value('banos', parsed_data.get('banos'))
            #administracion
            loader.add_value('administracion', parsed_data.get('last_admin_price'))
            #parqueaderos
            loader.add_value('parqueaderos', parsed_data.get('garajes'))
            #sector
            loader.add_value('sector', parsed_data.get('zona_mediana'))
            #estrato 
            loader.add_value('estrato', parsed_data.get('estrato'))
            #antiguedad
            loader.add_value('antiguedad', parsed_data.get('anos_antiguedad'))
            #latitud
            loader.add_value('latitud', parsed_data.get('latitud'))
            #longitud
            loader.add_value('longitud', parsed_data.get('longitud'))
            #direccion
            loader.add_value('direccion', parsed_data.get('direccion'))
            #caracteristicas (en lugar de featured_interior)
            loader.add_value('caracteristicas', parsed_data.get('caracteristicas'))
            #descripcion
            loader.add_value('descripcion', parsed_data.get('descripcion'))
            
            #imagenes
            try:
                # 🔧 ACTUALIZADO: Usar imágenes ya procesadas por el parser
                imagenes = parsed_data.get('images', [])
                loader.add_value('imagenes', imagenes)
            except Exception as e:
                self.spider_logger.warning(f'⚠️ Error procesando imágenes para {property_nid}: {e}')
            
            #website
            loader.add_value('website', 'habi.co')
            #last_view
            loader.add_value('last_view', datetime.now())
            #datetime
            loader.add_value('datetime', datetime.now())
            #url
            loader.add_value('url', response.url)

            yield loader.load_item()
            
        except Exception as e:
            self.stats['failed_parses'] += 1
            log_error_with_context(
                self.spider_logger,
                e,
                {
                    'url': response.url,
                    'property_nid': property_nid,
                    'slug': slug,
                    'failed_parses': self.stats['failed_parses']
                }
            )
    
    def closed(self, reason):
        """
        Callback cuando el spider termina - registra estadísticas finales
        """
        self.spider_logger.info("🏁 Spider de Habi terminando...")
        
        # Finalizar progress logger
        if self.progress_logger:
            self.progress_logger.finish("Scraping de Habi completado")
        
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
        
        self.spider_logger.info("🔒 Spider de Habi finalizado correctamente")

        