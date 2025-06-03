"""
🛠️ Utils Module - Bogotá Apartments Project

Este módulo contiene funciones auxiliares y utilidades reutilizables
para el procesamiento de datos y operaciones comunes.

Author: Erik Garcia (@erik172)  
Version: 3.0.0
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Union, Optional
from logging.handlers import RotatingFileHandler


def try_get(dictionary: Dict, keys: List[Union[str, int]]) -> Any:
    """
    Tries to get a value from a nested data structure and returns None if the key is not found or if an index is out of range.
    
    Args:
        dictionary (Dict): The dictionary or nested structure to navigate
        keys (List[Union[str, int]]): List of keys/indices to navigate through
        
    Returns:
        Any: The value found at the path, or None if path is invalid
        
    Examples:
        >>> data = {'user': {'profile': {'name': 'John', 'stats': [1, 2, 3]}}}
        >>> try_get(data, ['user', 'profile', 'name'])  # Returns: 'John'
        >>> try_get(data, ['user', 'profile', 'stats', 0])  # Returns: 1
        >>> try_get(data, ['user', 'invalid_key'])  # Returns: None
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


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely converts a value to integer, returning default if conversion fails.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        int: Converted value or default
    """
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely converts a value to float, returning default if conversion fails.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        float: Converted value or default
    """
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def clean_text(text: str) -> Optional[str]:
    """
    Cleans and normalizes text by removing extra whitespace and special characters.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text or None if input is empty
    """
    if not text or not isinstance(text, str):
        return None
        
    # Remove extra whitespace and normalize
    cleaned = ' '.join(text.strip().split())
    return cleaned if cleaned else None


def format_price(price: Union[int, float, str], currency: str = 'COP') -> str:
    """
    Formats a price value with currency and thousand separators.
    
    Args:
        price: Price value to format
        currency: Currency code (default: 'COP')
        
    Returns:
        str: Formatted price string
    """
    try:
        numeric_price = float(price) if price else 0
        if currency == 'COP':
            return f"${numeric_price:,.0f} COP"
        else:
            return f"${numeric_price:,.2f} {currency}"
    except (ValueError, TypeError):
        return "N/A"


def extract_numeric(text: str) -> Optional[float]:
    """
    Extracts numeric value from text string.
    
    Args:
        text (str): Text containing numeric value
        
    Returns:
        float: Extracted numeric value or None
    """
    if not text:
        return None
        
    import re
    # Remove currency symbols and extract numbers
    numbers = re.findall(r'[\d,]+\.?\d*', str(text).replace(',', ''))
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            pass
    return None


class DataValidator:
    """
    Validates and cleans apartment data according to business rules.
    """
    
    @staticmethod
    def validate_apartment_data(data: Dict) -> Dict[str, Any]:
        """
        Validates and cleans apartment data dictionary.
        
        Args:
            data (Dict): Raw apartment data
            
        Returns:
            Dict: Validated and cleaned data
        """
        validated = {}
        
        # Required fields
        validated['codigo'] = clean_text(data.get('codigo'))
        validated['tipo_propiedad'] = clean_text(data.get('tipo_propiedad', 'Apartamento'))
        validated['tipo_operacion'] = clean_text(data.get('tipo_operacion', 'venta'))
        
        # Numeric fields
        validated['precio_venta'] = safe_int(data.get('precio_venta'))
        validated['precio_arriendo'] = safe_int(data.get('precio_arriendo'))
        validated['area'] = safe_float(data.get('area'))
        validated['habitaciones'] = safe_int(data.get('habitaciones'))
        validated['banos'] = safe_int(data.get('banos'))
        validated['parqueaderos'] = safe_int(data.get('parqueaderos'))
        validated['estrato'] = safe_int(data.get('estrato'))
        validated['administracion'] = safe_int(data.get('administracion'))
        
        # Geographic fields
        validated['longitud'] = safe_float(data.get('longitud'))
        validated['latitud'] = safe_float(data.get('latitud'))
        validated['sector'] = clean_text(data.get('sector'))
        
        # Text fields
        validated['descripcion'] = clean_text(data.get('descripcion'))
        validated['compañia'] = clean_text(data.get('compañia'))
        validated['estado'] = clean_text(data.get('estado'))
        validated['antiguedad'] = clean_text(data.get('antiguedad'))
        
        # Arrays and complex fields
        validated['imagenes'] = data.get('imagenes', []) if isinstance(data.get('imagenes'), list) else []
        validated['featured_interior'] = data.get('featured_interior', []) if isinstance(data.get('featured_interior'), list) else []
        validated['featured_exterior'] = data.get('featured_exterior', []) if isinstance(data.get('featured_exterior'), list) else []
        validated['featured_zona_comun'] = data.get('featured_zona_comun', []) if isinstance(data.get('featured_zona_comun'), list) else []
        validated['featured_sector'] = data.get('featured_sector', []) if isinstance(data.get('featured_sector'), list) else []
        
        # Metadata
        validated['website'] = data.get('website', 'metrocuadrado.com')
        validated['datetime'] = data.get('datetime', datetime.now())
        validated['last_view'] = data.get('last_view', datetime.now())
        
        return validated
    
    @staticmethod
    def is_valid_apartment(data: Dict) -> bool:
        """
        Checks if apartment data meets minimum requirements.
        
        Args:
            data (Dict): Apartment data to validate
            
        Returns:
            bool: True if data is valid
        """
        required_fields = ['codigo', 'tipo_operacion']
        
        # Check required fields
        for field in required_fields:
            if not data.get(field):
                return False
        
        # Check that at least one price is available
        if not (data.get('precio_venta') or data.get('precio_arriendo')):
            return False
            
        # Check basic numeric constraints
        if data.get('area') and data.get('area') <= 0:
            return False
            
        return True


def get_logger(name: str, level: int = logging.INFO, log_to_file: bool = True) -> logging.Logger:
    """
    Creates a configured logger instance with dual output (console + file).
    
    Args:
        name (str): Logger name
        level (int): Logging level
        log_to_file (bool): Whether to log to file in addition to console
        
    Returns:
        logging.Logger: Configured logger with dual handlers
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 🎨 Formato mejorado para logs
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # 📺 Handler para consola (terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # 📁 Handler para archivo (si está habilitado)
    if log_to_file:
        try:
            # Crear directorio de logs si no existe
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Nombre de archivo con fecha
            log_filename = f"{logs_dir}/scraper_{datetime.now().strftime('%Y%m%d')}.log"
            
            # RotatingFileHandler para evitar archivos enormes
            file_handler = RotatingFileHandler(
                log_filename,
                maxBytes=10*1024*1024,  # 10MB máximo por archivo
                backupCount=5,          # Mantener 5 archivos de respaldo
                encoding='utf-8'
            )
            
            file_handler.setLevel(level)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
            
            # Log inicial para confirmar configuración
            logger.info(f"📝 Logger '{name}' configurado - Guardando en: {log_filename}")
            
        except Exception as e:
            # Si falla el archivo, continuar solo con consola
            logger.warning(f"⚠️ No se pudo configurar logging a archivo: {e}")
    
    return logger


def setup_spider_logging(spider_name: str) -> logging.Logger:
    """
    Configura logging específico para spiders con información detallada.
    
    Args:
        spider_name (str): Nombre del spider
        
    Returns:
        logging.Logger: Logger configurado para spider
    """
    logger = get_logger(f"spider.{spider_name}", level=logging.INFO, log_to_file=True)
    
    # 🚀 Log de inicio de sesión
    logger.info("=" * 60)
    logger.info(f"🕷️  INICIANDO SPIDER: {spider_name.upper()}")
    logger.info(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    return logger


def log_scraping_stats(logger: logging.Logger, stats: Dict[str, Any]):
    """
    Registra estadísticas detalladas del scraping.
    
    Args:
        logger: Logger instance
        stats: Diccionario con estadísticas del scraping
    """
    logger.info("📊 ESTADÍSTICAS DE SCRAPING")
    logger.info("-" * 40)
    
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            logger.info(f"📈 {key}: {value:,}")
        else:
            logger.info(f"📝 {key}: {value}")
    
    logger.info("-" * 40)


def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None):
    """
    Registra errores con contexto adicional para mejor debugging.
    
    Args:
        logger: Logger instance
        error: Exception occurred
        context: Additional context information
    """
    logger.error("🚨 ERROR DETECTADO")
    logger.error(f"❌ Tipo: {type(error).__name__}")
    logger.error(f"💬 Mensaje: {str(error)}")
    
    if context:
        logger.error("🔍 Contexto adicional:")
        for key, value in context.items():
            logger.error(f"   📋 {key}: {value}")
    
    # Log del traceback completo a nivel DEBUG
    import traceback
    logger.debug("🔬 Traceback completo:")
    logger.debug(traceback.format_exc())


class ProgressLogger:
    """
    Logger especializado para mostrar progreso de scraping en tiempo real.
    """
    
    def __init__(self, logger: logging.Logger, total_items: int = 0):
        self.logger = logger
        self.total_items = total_items
        self.processed_items = 0
        self.start_time = datetime.now()
        self.last_log_time = self.start_time
    
    def update(self, increment: int = 1, message: str = None):
        """
        Actualiza el progreso y registra información cada cierto intervalo.
        
        Args:
            increment: Número de items procesados
            message: Mensaje adicional opcional
        """
        self.processed_items += increment
        current_time = datetime.now()
        
        # Log cada 100 items o cada 30 segundos
        time_since_last = (current_time - self.last_log_time).seconds
        
        if self.processed_items % 100 == 0 or time_since_last >= 30:
            self._log_progress(message)
            self.last_log_time = current_time
    
    def _log_progress(self, message: str = None):
        """Registra el progreso actual."""
        elapsed = datetime.now() - self.start_time
        
        if self.total_items > 0:
            percentage = (self.processed_items / self.total_items) * 100
            remaining_items = self.total_items - self.processed_items
            
            # Estimar tiempo restante
            if self.processed_items > 0:
                avg_time_per_item = elapsed.total_seconds() / self.processed_items
                eta_seconds = remaining_items * avg_time_per_item
                eta = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
            else:
                eta = "N/A"
            
            progress_msg = (
                f"⏳ Progreso: {self.processed_items:,}/{self.total_items:,} "
                f"({percentage:.1f}%) | ETA: {eta}"
            )
        else:
            progress_msg = f"⏳ Procesados: {self.processed_items:,} items | Tiempo: {elapsed}"
        
        if message:
            progress_msg += f" | {message}"
        
        self.logger.info(progress_msg)
    
    def finish(self, message: str = "Scraping completado"):
        """Registra el resumen final."""
        total_time = datetime.now() - self.start_time
        self.logger.info("🎉 " + "=" * 50)
        self.logger.info(f"✅ {message}")
        self.logger.info(f"📊 Total procesado: {self.processed_items:,} items")
        self.logger.info(f"⏱️  Tiempo total: {total_time}")
        
        if self.processed_items > 0:
            avg_time = total_time.total_seconds() / self.processed_items
            self.logger.info(f"⚡ Promedio: {avg_time:.2f}s por item")
        
        self.logger.info("🎉 " + "=" * 50) 