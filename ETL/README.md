# 🏗️ ETL Modular - Bogotá Apartments

## 📋 Descripción

Este directorio contiene la implementación modular del pipeline ETL para el procesamiento de datos de apartamentos en Bogotá. La arquitectura ha sido refactorizada para ser más mantenible, escalable y profesional.

## 🏛️ Arquitectura Modular

### 📁 Estructura de Archivos

```
ETL/
├── __init__.py           # Paquete Python y exposición de APIs
├── README.md            # Esta documentación
├── config.py            # Configuración centralizada
├── models.py            # Modelos Pydantic para validación
├── utils.py             # Utilidades y funciones auxiliares
├── extractors.py        # Extractores de datos de diferentes fuentes
├── transformers.py      # Transformadores y limpiadores de datos
├── spatial.py           # Operaciones geoespaciales especializadas
├── loaders.py           # Cargadores de datos a destinos finales
└── main_etl.py          # Orquestador principal del pipeline
```

## 🔧 Componentes Principales

### 1. **Configuration (`config.py`)**
- Gestión centralizada de configuraciones
- Carga desde variables de entorno
- Validación de parámetros
- Configuración de directorios y límites geográficos

### 2. **Data Models (`models.py`)**
- Modelos Pydantic para validación de datos
- Definición de estructura de apartamentos
- Validadores personalizados para campos específicos
- Resultados de validación estructurados

### 3. **Utilities (`utils.py`)**
- Funciones auxiliares reutilizables
- Manejo de logging con soporte para emojis
- Funciones geoespaciales (distancia haversine)
- Conversiones de tipos numpy/pandas
- Extracción de características de texto

### 4. **Data Extractors (`extractors.py`)**
- **MongoDBExtractor**: Extrae datos desde MongoDB
- **GeospatialDataExtractor**: Carga archivos geoespaciales (shapefiles, geojson)
- **TransMilenioExtractor**: API de estaciones de TransMilenio con cache
- **ImageExtractor**: Procesamiento de imágenes de apartamentos
- **DataExtractor**: Orquestador de extracción

### 5. **Data Transformers (`transformers.py`)**
- **FeatureExtractor**: Extrae características de texto descriptivo
- **DataValidator**: Validación con modelos Pydantic
- **DataCleaner**: Limpieza y filtrado de datos
- **DataTransformer**: Orquestador de transformación

### 6. **Spatial Operations (`spatial.py`)**
- **SpatialEnricher**: Enriquecimiento geoespacial completo
- Spatial joins con archivos geojson de barrios
- Asignación de localidades y barrios por coordenadas
- Cálculo de proximidad a TransMilenio y parques
- Manejo de duplicados en operaciones espaciales

### 7. **Data Loaders (`loaders.py`)**
- **MongoDBLoader**: Carga masiva a MongoDB con upserts
- **CSVLoader**: Exportación a archivos CSV
- **DataLoader**: Orquestador de carga
- Limpieza de tipos para compatibilidad con MongoDB

### 8. **Main Orchestrator (`main_etl.py`)**
- **BogotaETLPipeline**: Orquestador principal
- Coordinación de las 4 fases del pipeline
- Manejo de errores y logging detallado
- Estadísticas finales y métricas de cobertura

## 🚀 Uso

### Uso Básico
```python
from ETL import run_etl_pipeline

# Ejecutar con configuración por defecto (desde .env)
success = run_etl_pipeline()
```

### Uso Avanzado
```python
from ETL import ETLConfig, BogotaETLPipeline

# Configuración personalizada
config = ETLConfig(
    mongo_uri="mongodb://localhost:27017",
    mongo_database="mi_db",
    mongo_collection_raw="raw_data",
    mongo_collection_processed="processed_data"
)

# Ejecutar pipeline
pipeline = BogotaETLPipeline(config)
success = pipeline.run_pipeline()
```

### Desde Línea de Comandos
```bash
# Desde el directorio raíz del proyecto
python processing.py
```

## 🔄 Fases del Pipeline

### 📥 Fase 1: Extracción
- Conexión a MongoDB para datos crudos
- Carga de datasets geoespaciales externos
- Descarga de datos de APIs (TransMilenio)
- Procesamiento de imágenes

### 🔄 Fase 2: Transformación
- Extracción de características de texto
- Validación con modelos Pydantic
- Limpieza y filtrado de datos
- Eliminación de duplicados

### 🗺️ Fase 3: Enriquecimiento Geoespacial
- Filtrado de coordenadas válidas para Bogotá
- Spatial joins con barrios y localidades
- Cálculo de proximidad a transporte público
- Asignación de parques cercanos

### 💾 Fase 4: Carga
- Limpieza de tipos para MongoDB
- Upserts masivos con manejo de errores
- Exportación a CSV como respaldo

## 📊 Características Destacadas

### ✅ Mejoras en Robustez
- Manejo exhaustivo de errores en cada fase
- Logging detallado con emojis y estadísticas
- Validación de datos en múltiples niveles
- Fallbacks para operaciones críticas

### ⚡ Optimizaciones de Rendimiento
- Procesamiento vectorizado de características
- Operaciones espaciales en chunks
- Upserts masivos para MongoDB
- Cache de datos externos (TransMilenio)

### 🛠️ Mantenibilidad
- Separación clara de responsabilidades
- Clases especializadas por función
- Configuración centralizada
- Documentación inline completa

### 🧪 Facilidad de Testing
- Componentes independientes testeable
- Inyección de dependencias
- Mocks fáciles para fuentes externas

### 🏬 Enriquecimiento Geoespacial Avanzado
- Spatial joins con barrios y localidades usando archivos oficiales
- Proximidad a estaciones de TransMilenio (<500m)
- Proximidad a parques y espacios recreativos (<500m)
- Proximidad a centros comerciales principales (<800m)
- Validación de coordenadas específicas para Bogotá
- Manejo automático de duplicados en operaciones espaciales

## 🔍 Debugging y Monitoreo

### Logging Detallado
- Estadísticas por cada fase del pipeline
- Contadores de registros procesados
- Métricas de cobertura geoespacial
- Tiempo de ejecución por componente

### Manejo de Errores
- Excepciones capturadas y loggeadas
- Continuación parcial en caso de fallos
- Estadísticas de validación
- Trazabilidad completa de errores

## 📈 Métricas y Estadísticas

El pipeline genera métricas detalladas incluyendo:
- Tasa de éxito de validación
- Cobertura de localidades y barrios
- Cobertura de coordenadas válidas
- Enriquecimiento de transporte público
- Enriquecimiento de parques y espacios recreativos
- Enriquecimiento de centros comerciales (42 centros principales)
- Estadísticas de características extraídas
- Contadores de apartamentos cerca de amenidades urbanas

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=bogota_apartments
MONGO_COLLECTION_RAW=scrapy_bogota_apartments
MONGO_COLLECTION_PROCESSED=scrapy_bogota_apartments_processed
```

### Límites Geográficos
Los límites de Bogotá están configurados en `config.py` y pueden ser ajustados:
```python
bogota_bounds = {
    'lat_min': 3.8,
    'lat_max': 5.2, 
    'lon_min': -74.8,
    'lon_max': -73.2
}
```

## 🚀 Escalabilidad Futura

La arquitectura modular permite:
- Agregar nuevos extractors para fuentes adicionales
- Implementar nuevos transformers para datos específicos
- Añadir loaders para otros destinos (Elasticsearch, etc.)
- Paralelizar componentes independientes
- Implementar caching avanzado

---

**Autor**: Erik Garcia (@erik172)  
**Versión**: 3.0.0  
**Fecha**: Junio 2025 