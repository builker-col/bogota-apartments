"""
🚀 Scraper Runner - Bogotá Apartments Project

Script principal para ejecutar el scraper con configuración completa de logging
y monitoreo en tiempo real.

Usage:
    python run_scraper.py [spider_name]

Examples:
    python run_scraper.py metrocuadrado
    python run_scraper.py habi

Author: Erik Garcia (@erik172)
Version: 3.0.0
"""

import sys
import os
import argparse
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Importar configuraciones de logging
from bogota_apartments.logging_config import configure_scrapy_logging, get_scrapy_settings, ScrapyStatsLogger
from bogota_apartments.utils import get_logger


def setup_environment():
    """
    Configura el entorno necesario para ejecutar el scraper.
    """
    # Crear directorios necesarios
    directories = ['logs', 'data', 'debug_scripts']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Directorio creado: {directory}")


def get_available_spiders():
    """
    Retorna lista de spiders disponibles.
    
    Returns:
        list: Lista de nombres de spiders disponibles
    """
    return ['metrocuadrado', 'habi']


def main():
    """
    Función principal del script.
    """
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='🕷️  Ejecutar scraper de apartamentos en Bogotá',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run_scraper.py metrocuadrado    # Ejecutar spider de Metrocuadrado
  python run_scraper.py habi             # Ejecutar spider de Habi
  python run_scraper.py --list           # Listar spiders disponibles
        """
    )
    
    parser.add_argument(
        'spider',
        nargs='?',
        help='Nombre del spider a ejecutar'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Listar spiders disponibles'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        help='Archivo de salida para los datos (formato CSV/JSON)',
        default=f"data/apartments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Habilitar logging detallado (DEBUG)'
    )
    
    args = parser.parse_args()
    
    # Mostrar lista de spiders disponibles
    if args.list:
        available_spiders = get_available_spiders()
        print("🕷️  Spiders disponibles:")
        for spider in available_spiders:
            print(f"   • {spider}")
        return
    
    # Validar que se especificó un spider
    if not args.spider:
        print("❌ Error: Debes especificar un spider para ejecutar")
        print("💡 Usa --list para ver spiders disponibles")
        print("💡 Ejemplo: python run_scraper.py metrocuadrado")
        return
    
    # Validar que el spider existe
    available_spiders = get_available_spiders()
    if args.spider not in available_spiders:
        print(f"❌ Error: Spider '{args.spider}' no encontrado")
        print(f"💡 Spiders disponibles: {', '.join(available_spiders)}")
        return
    
    # Configurar entorno
    setup_environment()
    
    # Configurar logging
    print("🔧 Configurando sistema de logging...")
    configure_scrapy_logging()
    
    # Crear logger principal
    main_logger = get_logger('scraper.main')
    
    # Mostrar información de inicio
    main_logger.info("🚀 " + "="*60)
    main_logger.info(f"🕷️  INICIANDO SCRAPER: {args.spider.upper()}")
    main_logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    main_logger.info(f"📁 Archivo de salida: {args.output}")
    main_logger.info(f"🔍 Modo verbose: {'Activado' if args.verbose else 'Desactivado'}")
    main_logger.info("🚀 " + "="*60)
    
    try:
        # Configurar settings de Scrapy
        settings = get_project_settings()
        
        # Aplicar configuraciones de logging
        scrapy_settings = get_scrapy_settings()
        settings.update(scrapy_settings)
        
        # Configurar archivo de salida
        settings.set('FEEDS', {
            args.output: {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': None,
                'indent': 2,
            }
        })
        
        # Configurar nivel de logging si verbose está activado
        if args.verbose:
            settings.set('LOG_LEVEL', 'DEBUG')
        
        # Inicializar el proceso de crawling
        process = CrawlerProcess(settings)
        
        # Configurar estadísticas de Scrapy
        stats_logger = ScrapyStatsLogger(main_logger)
        
        # Callback para estadísticas finales
        def spider_closed(spider, reason):
            stats_logger.log_stats(spider.crawler.stats.get_stats())
            main_logger.info(f"🏁 Spider cerrado. Razón: {reason}")
        
        # 🔧 ACTUALIZADO: Importar y configurar spiders disponibles
        spider_class = None
        if args.spider == 'metrocuadrado':
            from bogota_apartments.spiders.metrocuadrado import MetrocuadradoSpider
            spider_class = MetrocuadradoSpider
            main_logger.info("🏙️  Configurando spider de Metrocuadrado...")
        elif args.spider == 'habi':
            from bogota_apartments.spiders.habi import HabiSpider
            spider_class = HabiSpider
            main_logger.info("🏠 Configurando spider de Habi...")
        
        if spider_class:
            # Conectar callback de cierre
            from scrapy import signals
            process.crawl(spider_class)
            
            # Iniciar el proceso
            main_logger.info(f"🎯 Iniciando spider: {args.spider}")
            process.start()
        else:
            main_logger.error(f"❌ No se pudo cargar el spider: {args.spider}")
            
    except KeyboardInterrupt:
        main_logger.info("⏹️  Scraping interrumpido por el usuario")
    except Exception as e:
        main_logger.error(f"❌ Error durante el scraping: {e}")
        import traceback
        main_logger.debug(traceback.format_exc())
    finally:
        main_logger.info("🔒 Proceso de scraping finalizado")


if __name__ == '__main__':
    main() 