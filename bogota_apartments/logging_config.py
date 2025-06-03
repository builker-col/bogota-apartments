"""
🔧 Logging Configuration - Bogotá Apartments Project

Configuración centralizada de logging para integrar Scrapy con nuestro
sistema de logging dual (console + file).

Author: Erik Garcia (@erik172)
Version: 3.0.0
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def configure_scrapy_logging():
    """
    Configura el logging de Scrapy para que use nuestro sistema dual.
    
    Esta función debe llamarse antes de iniciar el spider para asegurar
    que todos los logs de Scrapy se capturen correctamente.
    """
    
    # Crear directorio de logs si no existe
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configurar formato de logs
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Configurar logger raíz de Scrapy
    scrapy_logger = logging.getLogger('scrapy')
    scrapy_logger.setLevel(logging.INFO)
    
    # Limpiar handlers existentes para evitar duplicados
    scrapy_logger.handlers.clear()
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    scrapy_logger.addHandler(console_handler)
    
    # Handler para archivo
    log_filename = f"{logs_dir}/scrapy_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    scrapy_logger.addHandler(file_handler)
    
    # Configurar loggers específicos de Scrapy
    loggers_config = {
        'scrapy.core.engine': logging.INFO,
        'scrapy.crawler': logging.INFO,
        'scrapy.spiders': logging.INFO,
        'scrapy.downloadermiddlewares': logging.WARNING,
        'scrapy.statscollectors': logging.INFO,
        'scrapy.extensions': logging.WARNING,
        'scrapy.middleware': logging.WARNING,
        'scrapy.utils.log': logging.WARNING
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = True  # Permitir que se propague al logger padre
    
    # Silenciar logs demasiado verbosos
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('charset_normalizer').setLevel(logging.WARNING)
    
    print(f"✅ Logging configurado - Archivo: {log_filename}")


def get_scrapy_settings():
    """
    Retorna configuración de logging para usar en settings.py de Scrapy.
    
    Returns:
        dict: Configuración de logging para Scrapy
    """
    return {
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'INFO',
        'LOG_FORMAT': '%(levelname)s: %(message)s',
        'LOG_DATEFORMAT': '%Y-%m-%d %H:%M:%S',
        
        # Desabilitar el logging a archivo por defecto de Scrapy
        # para usar nuestro sistema personalizado
        'LOG_FILE': None,
        
        # Configuraciones adicionales
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'AUTOTHROTTLE_DEBUG': False,
    }


class ScrapyStatsLogger:
    """
    Captura y registra estadísticas de Scrapy de manera organizada.
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.start_time = datetime.now()
    
    def log_stats(self, stats_dict):
        """
        Registra las estadísticas de Scrapy de forma organizada.
        
        Args:
            stats_dict: Diccionario de estadísticas de Scrapy
        """
        self.logger.info("📊 ESTADÍSTICAS FINALES DE SCRAPY")
        self.logger.info("=" * 50)
        
        # Estadísticas de requests
        requests_stats = {
            'Total requests': stats_dict.get('downloader/request_count', 0),
            'Successful responses': stats_dict.get('downloader/response_count', 0),
            'Failed requests': stats_dict.get('downloader/exception_count', 0),
            'Retry count': stats_dict.get('retry/count', 0),
        }
        
        self.logger.info("🌐 REQUESTS & RESPONSES:")
        for key, value in requests_stats.items():
            self.logger.info(f"   {key}: {value:,}")
        
        # Estadísticas de items
        items_stats = {
            'Items scraped': stats_dict.get('item_scraped_count', 0),
            'Items dropped': stats_dict.get('item_dropped_count', 0),
        }
        
        self.logger.info("📦 ITEMS PROCESADOS:")
        for key, value in items_stats.items():
            self.logger.info(f"   {key}: {value:,}")
        
        # Estadísticas de tiempo
        elapsed_time = datetime.now() - self.start_time
        self.logger.info("⏱️  TIEMPO:")
        self.logger.info(f"   Duración total: {elapsed_time}")
        self.logger.info(f"   Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"   Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calcular promedio de items por minuto
        total_items = stats_dict.get('item_scraped_count', 0)
        if total_items > 0 and elapsed_time.total_seconds() > 0:
            items_per_minute = (total_items / elapsed_time.total_seconds()) * 60
            self.logger.info(f"   Promedio: {items_per_minute:.1f} items/minuto")
        
        self.logger.info("=" * 50)
    
    def log_intermediate_stats(self, current_items, estimated_total=None):
        """
        Registra estadísticas intermedias durante la ejecución.
        
        Args:
            current_items: Número actual de items procesados
            estimated_total: Total estimado de items
        """
        elapsed = datetime.now() - self.start_time
        
        if estimated_total:
            percentage = (current_items / estimated_total) * 100
            msg = f"⏳ Progreso: {current_items:,}/{estimated_total:,} ({percentage:.1f}%)"
        else:
            msg = f"⏳ Items procesados: {current_items:,}"
        
        msg += f" | Tiempo: {elapsed}"
        
        if current_items > 0 and elapsed.total_seconds() > 0:
            rate = (current_items / elapsed.total_seconds()) * 60
            msg += f" | Tasa: {rate:.1f}/min"
        
        self.logger.info(msg) 