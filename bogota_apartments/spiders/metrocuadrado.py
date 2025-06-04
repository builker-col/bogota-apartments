from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
import json
import pymongo

# Scrapy
from bogota_apartments.items import ApartmentsItem
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings
import scrapy
import logging
import os

# 🔧 NUEVO: Importar parser y utilidades separadas
from bogota_apartments.parsers import MetrocuadradoParser
from bogota_apartments.utils import try_get, setup_spider_logging, log_scraping_stats, log_error_with_context, ProgressLogger

class MetrocuadradoSpider(scrapy.Spider):
    """
    Spider encargado de extraer datos de apartamentos del portal metrocuadrado.com.

    Este spider implementa una estrategia de dos fases:
    1. Descubrimiento y Paginación: Realiza una consulta inicial a la API de Metrocuadrado
       para determinar el número total de apartamentos en venta y arriendo en Bogotá.
       Luego, genera todas las peticiones necesarias para paginar a través de estos resultados.
    2. Procesamiento de Listados y Detalles:
        - Para cada página de resultados de la API, verifica si los apartamentos listados
          ya existen en la base de datos MongoDB.
        - Apartamentos Existentes: Si un apartamento ya existe, utiliza los datos de la API
          para detectar posibles cambios de precio. Esta información se pasa al pipeline
          para actualizar el registro existente y su historial de precios, evitando una
          costosa carga de la página con Selenium.
        - Apartamentos Nuevos: Si un apartamento es nuevo, navega a su página de detalle
          utilizando Selenium, extrae la información completa (incluyendo datos de un
          script Next.js) y la envía al pipeline para su almacenamiento.

    Características Principales:
    - Uso de Selenium con Chrome headless para interactuar con JavaScript.
    - User-Agent aleatorio para simular diferentes navegadores.
    - Conexión a MongoDB para verificar la existencia de apartamentos y evitar
      re-procesamiento innecesario, optimizando el tiempo de scraping.
    - Parser especializado (`MetrocuadradoParser`) para extraer datos de la estructura
      JSON de Next.js en las páginas de detalle.
    - Logging detallado, incluyendo estadísticas de scraping y progreso.
    - Manejo de errores robusto con contexto para facilitar la depuración.
    """
    name = 'metrocuadrado'
    allowed_domains = ['metrocuadrado.com']
    base_url = 'https://www.metrocuadrado.com/rest-search/search'

    def __init__(self):
        """
        Inicializa el spider.

        Configura:
        - Logger especializado para este spider.
        - Opciones del navegador Chrome (headless, user-agent aleatorio, etc.).
        - Instancia del driver de Selenium.
        - Parser especializado para Metrocuadrado.
        - Conexión a MongoDB (URI, base de datos, colección) para verificación de datos.
        - Estructura para almacenar estadísticas de scraping.
        - Logger de progreso.
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
        
        # 🔧 NUEVO: Configurar conexión a MongoDB para verificar existencia
        settings = get_project_settings()
        self.mongo_uri = settings.get('MONGO_URI')
        self.mongo_db = settings.get('MONGO_DATABASE', 'items')
        self.collection_name = settings.get('MONGO_COLLECTION_RAW')
        self.db_client = None
        self.db = None
        
        # 📊 Estadísticas de scraping
        self.stats = {
            'total_requests': 0,
            'successful_parses': 0,
            'failed_parses': 0,
            'total_apartments': 0,
            'venta_apartments': 0,
            'arriendo_apartments': 0,
            'apartments_updated': 0,
            'apartments_new': 0,
            'price_changes': 0,
            'selenium_avoided': 0
        }
        
        # 📈 Progress tracker
        self.progress_logger = None

    def start_requests(self):
        """
        Inicia el proceso de scraping generando las primeras solicitudes.

        Este método se encarga de:
        1. Establecer la conexión con MongoDB para la verificación de apartamentos existentes.
        2. Realizar solicitudes iniciales a la API de Metrocuadrado para "venta" y "arriendo"
           para descubrir el número total de apartamentos disponibles para cada tipo de operación.
        3. Delegar el manejo de estas respuestas al método `discover_and_paginate`.
        """
        # 🔧 NUEVO: Conectar a MongoDB al inicio
        try:
            self.db_client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.db_client[self.mongo_db]
            self.spider_logger.info("🔗 Conectado a MongoDB para verificar apartamentos existentes")
        except Exception as e:
            self.spider_logger.error(f"❌ Error conectando a MongoDB: {e}")
            self.spider_logger.info("⚠️ Continuando sin verificación de BD (modo completo)")
        
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
        Descubre el total real de apartamentos y genera todas las peticiones de paginación.

        A partir de la respuesta de la API (que contiene los totales):
        1. Extrae el número total de apartamentos accesibles.
        2. Actualiza las estadísticas generales del spider (total de apartamentos por tipo).
        3. Inicializa el `ProgressLogger` si aún no se ha hecho.
        4. Calcula el número de páginas necesarias y genera `scrapy.Request` para cada
           página de resultados de la API, delegando el parseo al método `parse`.
        
        Args:
            response (scrapy.http.Response): La respuesta de la API con los datos de descubrimiento.
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
        Procesa una página de resultados de la API de Metrocuadrado.

        Para cada apartamento en la lista de resultados:
        1. Extrae el ID de la propiedad (`midinmueble`).
        2. Verifica si el apartamento ya existe en la base de datos (`_check_existing_apartment`).
        3. Si existe:
            - Llama a `_process_existing_apartment` para registrar estadísticas y
              preparar un `ApartmentsItem` con datos de la API para que el pipeline
              maneje las actualizaciones (precio, last_view). Esto evita usar Selenium.
        4. Si es nuevo:
            - Genera un `scrapy.Request` para la URL de detalle del apartamento,
              pasando los datos de la API en `meta` y delegando el parseo a `details_parse`.
              Esto sí requerirá Selenium.

        Registra un resumen del batch procesado (nuevos vs. existentes).

        Args:
            response (scrapy.http.Response): La respuesta de la API con una lista de apartamentos.
        """
        operation_type = response.meta['operation_type']
        current_offset = response.meta['current_offset']
        
        try:
            result = json.loads(response.body)['results']
            self.spider_logger.info(f'📦 {operation_type} | Offset {current_offset}: {len(result)} apartamentos encontrados')

            processed_in_batch = 0
            new_in_batch = 0
            existing_in_batch = 0

            for item in result:
                # 🔧 ACTUALIZADO: Usar solo codigo como identificador único
                property_id = item.get('midinmueble')  # Obtener de la API
                if not property_id:
                    continue
                
                processed_in_batch += 1
                existing_apartment = self._check_existing_apartment(property_id)
                
                if existing_apartment:
                    # El apartamento ya existe, verificar cambios de precio
                    existing_in_batch += 1
                    # self.spider_logger.info(f'🔄 Apartamento EXISTENTE: {property_id} - Verificando cambios de precio (evitando Selenium)')
                    self._process_existing_apartment(item, existing_apartment, operation_type)
                    self.stats['selenium_avoided'] += 1
                    
                    # 🔄 NUEVO: Crear item con datos de la API para que el pipeline procese los cambios
                    loader = ItemLoader(item=ApartmentsItem())
                    
                    # Usar midinmueble de API como codigo único
                    loader.add_value('codigo', property_id)
                    
                    # Agregar precios de la API para comparación en pipeline
                    if item.get('mvalorventa'):
                        loader.add_value('precio_venta', item.get('mvalorventa'))
                    if item.get('mvalorarriendo'):
                        loader.add_value('precio_arriendo', item.get('mvalorarriendo'))
                    
                    # Agregar otros campos disponibles de la API
                    loader.add_value('area', item.get('marea'))
                    loader.add_value('habitaciones', item.get('mnrocuartos'))
                    loader.add_value('banos', item.get('mnrobanos'))
                    loader.add_value('parqueaderos', item.get('mnrogarajes'))
                    loader.add_value('tipo_operacion', operation_type)
                    loader.add_value('website', 'metrocuadrado.com')
                    loader.add_value('last_view', datetime.now())
                    
                    # Yield el item para que el pipeline lo procese
                    yield loader.load_item()
                else:
                    # Apartamento nuevo, hacer scraping completo con Selenium
                    new_in_batch += 1
                    # self.spider_logger.info(f'🆕 Apartamento NUEVO: {property_id} - Scraping completo necesario (usando Selenium)')
                    yield scrapy.Request(
                        url=f'https://metrocuadrado.com{item["link"]}',
                        callback=self.details_parse,
                        meta={'operation_type': operation_type, 'api_data': item}
                    )
            
            # 📊 Log de resumen del batch
            if processed_in_batch > 0:
                efficiency = (existing_in_batch / processed_in_batch) * 100
                self.spider_logger.info(f'📊 Resumen batch | Procesados: {processed_in_batch} | Nuevos: {new_in_batch} | Existentes: {existing_in_batch} | Eficiencia Selenium: {efficiency:.1f}%')
            
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

    def _check_existing_apartment(self, property_id):
        """
        Verifica si un apartamento, identificado por su `property_id` (código),
        ya existe en la colección de MongoDB especificada.
        
        Args:
            property_id (str): El ID único del apartamento (usualmente `midinmueble`).
            
        Returns:
            dict: El documento del apartamento existente si se encuentra, sino None.
                  Retorna None también si la conexión a la BD no está disponible.
        """
        if self.db is None:
            return None
            
        try:
            # Buscar solo por codigo (ya que midinmueble = codigo)
            existing = self.db[self.collection_name].find_one({'codigo': property_id})
            return existing
        except Exception as e:
            self.spider_logger.error(f"❌ Error verificando apartamento {property_id}: {e}")
            return None

    def _process_existing_apartment(self, api_data, existing_data, operation_type):
        """
        Procesa un apartamento que ya existe en la base de datos.

        Su principal función es detectar cambios de precio comparando los datos de la API
        con los datos existentes en la BD. No actualiza la BD directamente; esta tarea
        se delega al pipeline, que recibirá un item con la información necesaria.

        Actualiza las estadísticas del spider relacionadas con apartamentos actualizados,
        cambios de precio y progreso.
        
        Args:
            api_data (dict): Datos del apartamento obtenidos directamente de la API de Metrocuadrado.
            existing_data (dict): Datos del apartamento actualmente almacenados en MongoDB.
            operation_type (str): Tipo de operación ('venta' o 'arriendo').
        """
        property_id = api_data.get('midinmueble')  # Obtener de API, será usado como codigo
        
        try:
            # Extraer precios de la API
            api_price_venta = api_data.get('mvalorventa')
            api_price_arriendo = api_data.get('mvalorarriendo')
            
            # Extraer precios existentes
            existing_price_venta = existing_data.get('precio_venta')
            existing_price_arriendo = existing_data.get('precio_arriendo')
            
            # Verificar cambios de precio (solo para estadísticas y logging)
            price_changed = False
            
            if api_price_venta and api_price_venta != existing_price_venta:
                price_changed = True
                self.spider_logger.info(f'💰 Detectado cambio precio venta {property_id}: ${existing_price_venta:,} → ${api_price_venta:,}')
            
            if api_price_arriendo and api_price_arriendo != existing_price_arriendo:
                price_changed = True
                self.spider_logger.info(f'💰 Detectado cambio precio arriendo {property_id}: ${existing_price_arriendo:,} → ${api_price_arriendo:,}')
            
            # 🔄 IMPORTANTE: NO actualizamos MongoDB aquí
            # El pipeline manejará toda la actualización (precios + timeline + last_view)
            if price_changed:
                self.stats['price_changes'] += 1
                self.spider_logger.debug(f'🔄 Cambios detectados para {property_id} - pipeline manejará actualización')
            else:
                self.spider_logger.debug(f'✅ Sin cambios para {property_id} - pipeline actualizará last_view')
            
            # Solo actualizar estadísticas (no MongoDB)
            self.stats['apartments_updated'] += 1
            
            # Actualizar progreso
            if self.progress_logger:
                status_icon = "💰" if price_changed else "✅"
                self.progress_logger.update(1, f"{status_icon} {property_id} (existente)")
                
        except Exception as e:
            self.spider_logger.error(f"❌ Error procesando apartamento existente {property_id}: {e}")

    def details_parse(self, response):
        """
        Parsea la página de detalle de un apartamento NUEVO utilizando Selenium.

        Este método se llama cuando se determina que un apartamento no existe en la BD.
        1. Carga la URL del apartamento en el navegador Selenium.
        2. Intenta extraer datos de un script JSON (tag <script>) em embebido en la página HTML.
           Prueba con `/html/body/script[10]/text()` y, como fallback, con `/html/body/script[9]/text()`.
           Si falla, reintenta cargando la página y probando los XPaths de nuevo.
        3. Utiliza `MetrocuadradoParser` para procesar el contenido del script y convertirlo en un dict.
        4. Si la extracción y parseo son exitosos:
            - Actualiza estadísticas de parseos exitosos y apartamentos nuevos.
            - Actualiza el `ProgressLogger`.
            - Crea un `ItemLoader` con `ApartmentsItem` y lo puebla con todos los
              datos extraídos (código, precios, área, habitaciones, características, etc.).
            - Hace yield del item para que sea procesado por el pipeline.
        5. Si hay errores, los registra y actualiza estadísticas de fallos.

        Args:
            response (scrapy.http.Response): La respuesta HTTP de la página de detalle del apartamento.
                                         Contiene `api_data` en `response.meta`.
        """
        operation_type = response.meta.get('operation_type', 'unknown')
        api_data = response.meta.get('api_data', {})
        
        try:
            self.driver.get(response.url)   
            
            property_id = api_data.get('midinmueble', 'unknown')
            self.spider_logger.debug(f'🏠 Procesando apartamento NUEVO: {property_id}')

            # 🎯 Extraer el script específico con xpath - intentar primero script[10]
            script_data = Selector(text=self.driver.page_source).xpath(
                '/html/body/script[10]/text()'
            ).get()

            if not script_data:
                self.spider_logger.warning(f'⚠️ No se encontró script[10] para {property_id}, intentando con script[9]...')
                # 🔧 NUEVO: Intentar con script[9] como alternativa
                script_data = Selector(text=self.driver.page_source).xpath(
                    '/html/body/script[9]/text()'
                ).get()
                
                if not script_data:
                    self.spider_logger.warning(f'⚠️ No se encontró script[9] para {property_id}, reintentando página...')
                    self.driver.get(response.url)
                    self.driver.implicitly_wait(10)
                    # Reintentar primero con script[10]
                    script_data = Selector(text=self.driver.page_source).xpath('/html/body/script[10]/text()').get()
                    
                    if not script_data:
                        # Si aún no funciona, intentar con script[9]
                        script_data = Selector(text=self.driver.page_source).xpath('/html/body/script[9]/text()').get()

            # 🔧 ACTUALIZADO: Usar parser separado
            script_data = self.parser.parse_nextjs_data(script_data)
            
            if not script_data:
                self.spider_logger.error(f'❌ No se pudo extraer datos JSON del script Next.js: {response.url}')
                self.stats['failed_parses'] += 1
                return

            # 📊 Actualizar progreso
            self.stats['successful_parses'] += 1
            self.stats['apartments_new'] += 1
            if self.progress_logger:
                self.progress_logger.update(1, f"🆕 {script_data.get('propertyId', 'N/A')} (nuevo)")

            # 🔧 CORREGIDO: script_data ahora es un diccionario, no una lista
            loader = ItemLoader(item=ApartmentsItem(), selector=script_data)

            # 🔧 ACTUALIZADO: Usar midinmueble de API como codigo único
            # Priorizar el ID de la API si está disponible, sino usar propertyId del script
            codigo_final = api_data.get('midinmueble') or script_data.get('propertyId')
            loader.add_value('codigo', codigo_final)
            
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
                    'property_id': property_id,
                    'failed_parses': self.stats['failed_parses']
                }
            )
    
    def closed(self, reason):
        """
        Callback invocado cuando el spider finaliza su ejecución.

        Se encarga de:
        1. Finalizar el `ProgressLogger`.
        2. Calcular estadísticas finales del scraping (tasa de éxito, eficiencia de Selenium, etc.).
        3. Registrar un resumen detallado de la optimización (apartamentos nuevos vs. existentes,
           cambios de precio, Selenium evitado, tiempo estimado ahorrado).
        4. Registrar todas las estadísticas finales usando `log_scraping_stats`.
        5. Cerrar el driver de Selenium y la conexión a MongoDB.

        Args:
            reason (str): La razón por la cual el spider se cerró.
        """
        self.spider_logger.info("🏁 Spider terminando...")
        
        # Finalizar progress logger
        if self.progress_logger:
            self.progress_logger.finish("Scraping de Metrocuadrado completado")
        
        # Calcular estadísticas finales
        success_rate = 0
        if self.stats['successful_parses'] + self.stats['failed_parses'] > 0:
            success_rate = (self.stats['successful_parses'] / (self.stats['successful_parses'] + self.stats['failed_parses'])) * 100
        
        # Calcular eficiencia de la optimización
        total_processed = self.stats['apartments_updated'] + self.stats['apartments_new']
        selenium_efficiency = 0
        if total_processed > 0:
            selenium_efficiency = (self.stats['selenium_avoided'] / total_processed) * 100
        
        # Calcular promedio de score de completitud API si tenemos datos
        avg_completeness = 0
        if self.stats.get('api_completeness_scores'):
            avg_completeness = sum(self.stats['api_completeness_scores']) / len(self.stats['api_completeness_scores'])
        
        final_stats = {
            **self.stats,
            'success_rate': f"{success_rate:.1f}%",
            'selenium_efficiency': f"{selenium_efficiency:.1f}%",
            'avg_api_completeness': f"{avg_completeness:.1%}" if avg_completeness > 0 else "N/A",
            'reason': reason
        }
        
        # Log detallado de la optimización
        self.spider_logger.info("🎯 === RESUMEN DE OPTIMIZACIÓN ===")
        self.spider_logger.info(f"📊 Total apartamentos procesados: {total_processed:,}")
        self.spider_logger.info(f"🆕 Apartamentos nuevos (Selenium): {self.stats['apartments_new']:,}")
        self.spider_logger.info(f"🔄 Apartamentos existentes (API): {self.stats['apartments_updated']:,}")
        self.spider_logger.info(f"💰 Cambios de precio detectados: {self.stats['price_changes']:,}")
        self.spider_logger.info(f"⚡ Selenium evitado: {self.stats['selenium_avoided']:,} veces ({selenium_efficiency:.1f}%)")
        
        if selenium_efficiency > 0:
            time_saved_estimate = self.stats['selenium_avoided'] * 3  # ~3 segundos por apartamento
            self.spider_logger.info(f"⏱️ Tiempo estimado ahorrado: ~{time_saved_estimate:,} segundos ({time_saved_estimate/60:.1f} minutos)")
        
        self.spider_logger.info("🎯 === FIN RESUMEN ===")
        
        # Registrar estadísticas finales
        log_scraping_stats(self.spider_logger, final_stats)
        
        # Cerrar conexiones
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.spider_logger.info("🔒 Navegador cerrado correctamente")
            
        if self.db_client:
            self.db_client.close()
            self.spider_logger.info("🔗 Conexión MongoDB cerrada correctamente")