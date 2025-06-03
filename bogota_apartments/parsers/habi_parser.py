"""
🔧 Parser especializado para datos de Habi.co

Maneja el formato JSON estándar usado por la API de Habi.

Author: Erik Garcia (@erik172)
Version: 3.0.0
"""

import logging
import json
from datetime import datetime

class HabiParser:
    """
    Parser especializado para datos de Habi.co
    
    Maneja el formato JSON estándar usado por la API de Habi.
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def parse_habi_data(self, data):
        """
        Parser para datos de Habi.co en formato JSON estándar
        
        Args:
            data: Datos en formato JSON de Habi
            
        Returns:
            dict: Datos procesados del apartamento
        """
        if not data:
            return None
            
        try:
            # Validar que tenemos los datos mínimos necesarios
            if not isinstance(data, dict):
                self.logger.error('❌ Datos de Habi no son un diccionario válido')
                return None
            
            property_id = data.get('propertyId')
            if not property_id:
                self.logger.error('❌ No se encontró propertyId en datos de Habi')
                return None
            
            self.logger.debug(f'🎯 Procesando apartamento Habi: {property_id}')
            
            # Los datos de Habi ya vienen en formato JSON limpio,
            # solo necesitamos validación y normalización
            apartment_data = {
                'propertyId': property_id,
                'source': 'habi.co'
            }
            
            # Extraer datos de la propiedad si están disponibles
            property_detail = data.get('propertyDetail', {})
            if isinstance(property_detail, dict):
                property_info = property_detail.get('property', {})
                detalles = property_info.get('detalles_propiedad', {})
                
                # Mapear campos específicos de Habi
                apartment_data.update({
                    'tipo_inmueble': detalles.get('tipo_inmueble'),
                    'precio_venta': detalles.get('precio_venta'),
                    'area': detalles.get('area'),
                    'num_habitaciones': detalles.get('num_habitaciones'),
                    'banos': detalles.get('baños'),
                    'garajes': detalles.get('garajes'),
                    'estrato': detalles.get('estrato'),
                    'anos_antiguedad': detalles.get('anos_antiguedad'),
                    'latitud': detalles.get('latitud'),
                    'longitud': detalles.get('longitud'),
                    'direccion': detalles.get('direccion'),
                    'zona_mediana': detalles.get('zona_mediana'),
                    'last_admin_price': detalles.get('last_admin_price')
                })
                
                # Características y descripción
                apartment_data['caracteristicas'] = property_info.get('caracteristicas_propiedad', [])
                apartment_data['descripcion'] = property_info.get('descripcion')
                
                # Imágenes
                images = property_info.get('images', [])
                if images:
                    apartment_data['images'] = [
                        f'https://d3hzflklh28tts.cloudfront.net/{img.get("url", "")}?d=400x400'
                        for img in images if isinstance(img, dict) and img.get('url')
                    ]
            
            self.logger.debug(f'✅ Datos de Habi procesados para {property_id}')
            return apartment_data
            
        except Exception as e:
            self.logger.error(f'❌ Error procesando datos de Habi: {e}')
            
            # Debug: Guardar datos problemáticos
            self._save_debug_data(e, data)
            
            return None
    
    def _save_debug_data(self, error, data):
        """
        Guarda datos problemáticos para debugging
        """
        try:
            import os
            debug_dir = "debug_scripts"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            debug_file = f"{debug_dir}/failed_habi_parser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"# ERROR: {str(error)}\n")
                f.write(f"# TIMESTAMP: {datetime.now().isoformat()}\n\n")
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f'🔍 Error de Habi guardado en: {debug_file}')
        except Exception:
            # Si no se puede guardar el debug, continuar silenciosamente
            pass