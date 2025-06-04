# Author: Erik Garcia (@erik172)
# Version: 3.0.0 - Modular ETL
"""
Main ETL Processing Script for Bogota Apartments
This is the main entry point for the ETL pipeline using the modular implementation.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add ETL directory to path
sys.path.append(str(Path(__file__).parent / "ETL"))

from ETL import run_etl_pipeline, config
from ETL.utils import safe_log
import logging

logger = logging.getLogger(__name__)


def run_data_processing():
    """
    Ejecuta el pipeline moderno de procesamiento de datos.
    
    Esta función ejecuta el ETL completo modernizado que incluye:
    - Extracción de datos desde MongoDB
    - Transformaciones vectorizadas
    - Validación con Pydantic  
    - Enriquecimiento geoespacial
    - Limpieza y filtrado de datos
    - Guardado en MongoDB y CSV
    """
    start_time = datetime.now()
    safe_log(logger.info, f'🚀 Iniciando pipeline de datos moderno en {start_time}')
    
    try:
        # Ejecutar el pipeline ETL modular
        success = run_etl_pipeline(config)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        if success:
            safe_log(logger.info, f'✅ Pipeline completado exitosamente en {execution_time:.2f} segundos')
            safe_log(logger.info, f'📊 Datos procesados guardados en data/processed/ y MongoDB')
            return True
        else:
            safe_log(logger.error, f'❌ Pipeline falló después de {execution_time:.2f} segundos')
            return False
            
    except Exception as e:
        safe_log(logger.error, f'💥 Error crítico en el pipeline: {e}')
        return False


if __name__ == '__main__':
    success = run_data_processing()
    sys.exit(0 if success else 1)