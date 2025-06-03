# Author: Erik Garcia (@erik172)
# Version: 3.0.0 - Modern ETL
"""
Main ETL Processing Script for Bogota Apartments
This is the main entry point for the ETL pipeline using the modern implementation.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv

# Add ETL directory to path
sys.path.append(str(Path(__file__).parent / "ETL"))

from ETL.modern_etl import BogotaETLPipeline, ETLConfig

# Configure logging
filename = f'logs/data_processing.log'
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler(filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_data_processing():
    """
    Executa el pipeline moderno de procesamiento de datos.
    
    Esta función ejecuta el ETL completo modernizado que incluye:
    - Extracción de datos desde MongoDB
    - Transformaciones vectorizadas
    - Validación con Pydantic  
    - Enriquecimiento geoespacial
    - Limpieza y filtrado de datos
    - Guardado en MongoDB y CSV
    """
    start_time = datetime.now()
    logger.info(f'🚀 Iniciando pipeline de datos moderno en {start_time}')
    
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Configurar el ETL
        config = ETLConfig(
            mongo_uri=os.getenv('MONGO_URI', ''),
            mongo_database=os.getenv('MONGO_DATABASE', 'bogota_apartments'),
            mongo_collection_raw=os.getenv('MONGO_COLLECTION_RAW', 'scrapy_bogota_apartments'),
            mongo_collection_processed=os.getenv('MONGO_COLLECTION_PROCESSED', 'scrapy_bogota_apartments_processed')
        )
        
        # Verificar configuración
        if not config.mongo_uri:
            logger.error("❌ MONGO_URI no configurado. Revisa tu archivo .env")
            return False
        
        # Crear y ejecutar pipeline
        pipeline = BogotaETLPipeline(config)
        success = pipeline.run_pipeline()
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        if success:
            logger.info(f'✅ Pipeline completado exitosamente en {execution_time:.2f} segundos')
            logger.info(f'📊 Datos procesados guardados en data/processed/ y MongoDB')
            return True
        else:
            logger.error(f'❌ Pipeline falló después de {execution_time:.2f} segundos')
            return False
            
    except Exception as e:
        logger.error(f'💥 Error crítico en el pipeline: {e}')
        return False


if __name__ == '__main__':
    success = run_data_processing()
    sys.exit(0 if success else 1)