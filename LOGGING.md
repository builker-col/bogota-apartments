# 📝 Sistema de Logging - Bogotá Apartments

## 🔧 Características del Sistema

### **Dual Output Logging**
- **📺 Terminal**: Logs simplificados para monitoreo en tiempo real
- **📁 Archivos**: Logs detallados con timestamps y contexto completo

### **Rotación Automática de Archivos**
- **Tamaño máximo**: 10MB por archivo
- **Archivos de respaldo**: Hasta 5 archivos
- **Encoding**: UTF-8 para soporte completo de caracteres especiales

### **Logging Estructurado**
- **Formatos diferenciados**: Simple para consola, detallado para archivos
- **Niveles configurables**: INFO, DEBUG, WARNING, ERROR
- **Contexto enriquecido**: Información adicional en errores

## 📁 Estructura de Archivos de Log

```
logs/
├── scraper_20241215.log          # Logs del spider
├── scrapy_20241215.log           # Logs internos de Scrapy
├── scraper_20241215.log.1        # Archivo rotado (backup)
└── scrapy_20241215.log.1         # Archivo rotado (backup)
```

## 🚀 Uso del Sistema

### **Ejecutar con Logging Mejorado**

```bash
# Uso básico
python run_scraper.py metrocuadrado

# Con logging detallado (DEBUG)
python run_scraper.py metrocuadrado --verbose

# Especificar archivo de salida
python run_scraper.py metrocuadrado -o data/mi_scraping.json

# Listar spiders disponibles
python run_scraper.py --list
```

### **Importar en Código Python**

```python
from bogota_apartments.utils import (
    setup_spider_logging, 
    log_scraping_stats, 
    log_error_with_context,
    ProgressLogger
)

# Configurar logging para spider
logger = setup_spider_logging('mi_spider')

# Registrar estadísticas
stats = {'total_items': 1000, 'success_rate': '95%'}
log_scraping_stats(logger, stats)

# Registrar errores con contexto
try:
    # código que puede fallar
    pass
except Exception as e:
    log_error_with_context(logger, e, {
        'url': response.url,
        'operation': 'parsing'
    })

# Progress tracking
progress = ProgressLogger(logger, total_items=1000)
for i in range(1000):
    # procesar item
    progress.update(1, f"Procesando item {i}")

progress.finish("Completado exitosamente")
```

## 📊 Tipos de Logs Generados

### **1. Logs de Inicio/Configuración**
```
INFO: 📝 Logger 'spider.metrocuadrado' configurado - Guardando en: logs/scraper_20241215.log
INFO: ============================================================
INFO: 🕷️  INICIANDO SPIDER: METROCUADRADO
INFO: 🕐 Timestamp: 2024-12-15 14:30:00
INFO: ============================================================
```

### **2. Logs de Progreso**
```
INFO: 🚀 Iniciando descubrimiento de apartamentos disponibles...
INFO: 🔍 Descubriendo totales para: venta
INFO: 🎯 venta: 18,326 apartamentos accesibles de 18,326 totales
INFO: 📤 Generadas 367 peticiones para venta
INFO: ⏳ Progreso: 500/36,652 (1.4%) | ETA: 45m 12s | ✅ MET-12345
```

### **3. Logs de Error con Contexto**
```
ERROR: 🚨 ERROR DETECTADO
ERROR: ❌ Tipo: JSONDecodeError
ERROR: 💬 Mensaje: Expecting value: line 1 column 1 (char 0)
ERROR: 🔍 Contexto adicional:
ERROR:    📋 url: https://metrocuadrado.com/apartamento/xyz
ERROR:    📋 operation_type: venta
ERROR:    📋 failed_parses: 5
```

### **4. Estadísticas Finales**
```
INFO: 📊 ESTADÍSTICAS DE SCRAPING
INFO: ----------------------------------------
INFO: 📈 total_requests: 734
INFO: 📈 successful_parses: 18,321
INFO: 📈 failed_parses: 5
INFO: 📈 total_apartments: 36,652
INFO: 📝 success_rate: 99.97%
INFO: ----------------------------------------
```

## ⚙️ Configuración Avanzada

### **Niveles de Logging**

| Nivel | Descripción | Uso |
|-------|-------------|-----|
| `DEBUG` | Información muy detallada | Debugging y desarrollo |
| `INFO` | Información general | Monitoreo normal |
| `WARNING` | Advertencias no críticas | Problemas menores |
| `ERROR` | Errores que no detienen ejecución | Errores recuperables |
| `CRITICAL` | Errores críticos | Errores que detienen el spider |

### **Personalizar Configuración**

```python
from bogota_apartments.utils import get_logger

# Logger básico (solo consola)
logger = get_logger('mi_modulo', log_to_file=False)

# Logger con nivel DEBUG
logger = get_logger('mi_modulo', level=logging.DEBUG)

# Logger personalizado para análisis
analysis_logger = get_logger('analysis', level=logging.INFO)
analysis_logger.info("Iniciando análisis de datos...")
```

### **Integración con Scrapy**

```python
from bogota_apartments.logging_config import configure_scrapy_logging

# Configurar antes de iniciar spider
configure_scrapy_logging()

# En settings.py
from bogota_apartments.logging_config import get_scrapy_settings
settings = get_scrapy_settings()
```

## 🔍 Análisis de Logs

### **Comandos Útiles para Análisis**

```bash
# Ver solo errores del día actual
grep "ERROR" logs/scraper_$(date +%Y%m%d).log

# Contar apartamentos procesados
grep "✅" logs/scraper_$(date +%Y%m%d).log | wc -l

# Ver estadísticas de progreso
grep "⏳ Progreso" logs/scraper_$(date +%Y%m%d).log

# Buscar errores específicos
grep -A 5 -B 5 "JSONDecodeError" logs/scraper_$(date +%Y%m%d).log

# Ver últimas 50 líneas en tiempo real
tail -f -n 50 logs/scraper_$(date +%Y%m%d).log
```

### **Monitoreo en Tiempo Real**

```bash
# Terminal 1: Ejecutar scraper
python run_scraper.py metrocuadrado

# Terminal 2: Monitorear logs
tail -f logs/scraper_$(date +%Y%m%d).log | grep -E "(⏳|✅|❌|📊)"

# Terminal 3: Monitorear errores
tail -f logs/scraper_$(date +%Y%m%d).log | grep -E "(ERROR|WARNING)"
```

## 🛠️ Resolución de Problemas

### **Problemas Comunes**

#### **1. No se crean archivos de log**
- **Verificar permisos** del directorio `logs/`
- **Verificar espacio en disco**
- **Revisar** que el directorio `logs/` existe

#### **2. Logs duplicados en consola**
- **Causa**: Múltiples handlers configurados
- **Solución**: Reiniciar el proceso Python

#### **3. Archivos de log muy grandes**
- **Causa**: Logging nivel DEBUG en producción
- **Solución**: Cambiar a nivel INFO o configurar rotación más agresiva

#### **4. Caracteres especiales incorrectos**
- **Causa**: Encoding incorrecto
- **Solución**: Verificar que se use UTF-8 (ya configurado por defecto)

### **Debug del Sistema de Logging**

```python
# Verificar configuración actual
import logging
logger = logging.getLogger('scrapy')
print(f"Nivel: {logger.level}")
print(f"Handlers: {len(logger.handlers)}")
for handler in logger.handlers:
    print(f"  - {type(handler).__name__}: {handler.level}")
```

## 📈 Mejores Prácticas

1. **🔄 Rotar logs regularmente** para evitar archivos enormes
2. **📊 Monitorear tasas de error** para detectar problemas temprano  
3. **🎯 Usar niveles apropiados** (INFO para producción, DEBUG para desarrollo)
4. **🔍 Incluir contexto** en mensajes de error para facilitar debugging
5. **⏱️ Registrar tiempos** para identificar cuellos de botella
6. **📝 Documentar eventos importantes** con emojis para facilitar búsqueda
7. **🚨 Configurar alertas** para errores críticos en producción

---

**Autor**: Erik Garcia (@erik172)  
**Versión**: 3.0.0  
**Fecha**: Junio 2025 