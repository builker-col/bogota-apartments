"""
🔧 Parser especializado para extraer datos de Metrocuadrado.com

Maneja el formato Next.js hydration usado por el sitio web moderno.

Author: Erik Garcia (@erik172)
Version: 3.0.0
"""

import logging
from datetime import datetime
import re
import json

class MetrocuadradoParser:
    """
    Parser especializado para extraer datos de Metrocuadrado.com
    
    Maneja el formato Next.js hydration usado por el sitio web moderno.
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def parse_nextjs_data(self, raw_script):
        """
        🔧 Parser especializado para extraer datos JSON de scripts Next.js
        
        Args:
            raw_script (str): Script crudo extraído de la página web
            
        Returns:
            dict: Datos del apartamento extraídos, o None si falla
        """
        if not raw_script:
            return None
            
        try:
            # Paso 1: Extraer la cadena JSON de la función JavaScript
            
            # Buscar el patrón: self.__next_f.push([1,"..."])
            match = re.search(r'self\.__next_f\.push\(\[1,"(.+)"\]\)', raw_script, re.DOTALL)
            if not match:
                self.logger.error('❌ No se encontró el patrón Next.js esperado')
                return None
                
            json_string = match.group(1)
            
            # Paso 2: Decodificar escapes JavaScript básicos
            json_string = json_string.replace('\\"', '"')
            json_string = json_string.replace('\\/', '/')
            
            # Paso 3: Buscar el objeto "data" que contiene información del apartamento
            # Estrategia: buscar "propertyId" como punto de referencia más confiable
            property_id_match = re.search(r'"propertyId":"([^"]+)"', json_string)
            if not property_id_match:
                self.logger.error('❌ No se encontró propertyId en los datos')
                return None
                
            property_id = property_id_match.group(1)
            self.logger.info(f'🎯 Procesando apartamento: {property_id}')
            
            # Paso 4: Extraer campos específicos usando regex individuales
            apartment_data = {'propertyId': property_id}
            
            # Lista de campos a extraer con sus patrones regex
            field_patterns = {
                'businessType': r'"businessType":"([^"]*)"',
                'salePrice': r'"salePrice":([^,}]*)',
                'rentPrice': r'"rentPrice":([^,}]*)',
                'area': r'"area":([^,}]*)',
                'rooms': r'"rooms":"([^"]*)"',
                'bathrooms': r'"bathrooms":"([^"]*)"',
                'garages': r'"garages":"([^"]*)"',
                'propertyState': r'"propertyState":"([^"]*)"',
                'stratum': r'"stratum":"([^"]*)"',
                'builtTime': r'"builtTime":"([^"]*)"',
                'comment': r'"comment":"([^"]*)"',
                'contactPhone': r'"contactPhone":"([^"]*)"',
                'whatsapp': r'"whatsapp":"([^"]*)"',
                'companyName': r'"companyName":([^,}]*)',
                'neighborhood': r'"neighborhood":"([^"]*)"',
            }
            
            # Extraer campos simples
            for field, pattern in field_patterns.items():
                match = re.search(pattern, json_string)
                if match:
                    value = match.group(1)
                    # Convertir valores especiales
                    if value == 'null':
                        apartment_data[field] = None
                    elif value.isdigit():
                        apartment_data[field] = int(value)
                    elif value.replace('.', '').isdigit():
                        apartment_data[field] = float(value)
                    else:
                        apartment_data[field] = value.strip('"')
            
            # Paso 5: Extraer objetos anidados específicos
            
            # Coordenadas
            coord_match = re.search(r'"coordinates":\{"lon":([^,}]+),"lat":([^,}]+)\}', json_string)
            if coord_match:
                apartment_data['coordinates'] = {
                    'lon': float(coord_match.group(1)),
                    'lat': float(coord_match.group(2))
                }
            
            # Tipo de propiedad
            prop_type_match = re.search(r'"propertyType":\{"id":"([^"]+)","nombre":"([^"]+)"\}', json_string)
            if prop_type_match:
                apartment_data['propertyType'] = {
                    'id': prop_type_match.group(1),
                    'nombre': prop_type_match.group(2)
                }
            
            # Sector
            sector_match = re.search(r'"sector":\{"nombre":"([^"]+)"\}', json_string)
            if sector_match:
                apartment_data['sector'] = {'nombre': sector_match.group(1)}
            
            # Precio de administración
            admin_match = re.search(r'"detail":\{[^}]*"adminPrice":([^,}]+)', json_string)
            if admin_match:
                admin_price = admin_match.group(1)
                apartment_data['detail'] = {
                    'adminPrice': int(admin_price) if admin_price != 'null' else None
                }
            
            # Imágenes (extraer al menos la primera)
            images_matches = re.findall(r'"image":"([^"]+\.jpg)"', json_string)
            if images_matches:
                apartment_data['images'] = [{'image': img} for img in images_matches]
            
            # Featured items (simplificado)
            featured_matches = re.findall(r'"items":\[([^\]]+)\]', json_string)
            if featured_matches:
                apartment_data['featured'] = []
                for i, items_match in enumerate(featured_matches[:3]):  # Máximo 3 categorías
                    items = re.findall(r'"([^"]+)"', items_match)
                    apartment_data['featured'].append({
                        'title': ['Interiores', 'Exteriores', 'Del sector'][i] if i < 3 else f'Categoria {i+1}',
                        'items': items
                    })
            
            self.logger.info(f'✅ Datos extraídos exitosamente para {property_id}')
            self.logger.info(f'📊 Campos extraídos: {list(apartment_data.keys())}')
            
            return apartment_data
            
        except Exception as e:
            self.logger.error(f'❌ Error en parser Next.js: {e}')
            
            # Debug: Guardar datos problemáticos
            self._save_debug_data(e, raw_script)
                
            return None
    
    def _save_debug_data(self, error, raw_script):
        """
        Guarda datos problemáticos para debugging
        """
        try:
            import os
            debug_dir = "debug_scripts"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            debug_file = f"{debug_dir}/failed_parser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write("=== ERROR ===\n")
                f.write(str(error) + "\n\n")
                f.write("=== RAW SCRIPT (FIRST 2000 CHARS) ===\n")
                f.write(raw_script[:2000] + "...\n")
                
            self.logger.info(f'🔍 Error guardado en: {debug_file}')
        except Exception:
            # Si no se puede guardar el debug, continuar silenciosamente
            pass