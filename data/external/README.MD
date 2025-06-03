# 📊 Datos Externos - Bogotá Apartments

## 🎯 Descripción General

Esta carpeta contiene **datasets externos** utilizados para enriquecer el análisis inmobiliario de Bogotá con información geoespacial, de transporte y servicios urbanos. Todos los datos provienen de **fuentes oficiales y públicas** del Gobierno de Bogotá y entidades relacionadas.

> 🔓 **Datos Abiertos**: Todos los datasets son de dominio público y están disponibles bajo licencias abiertas que permiten su uso, redistribución y modificación.

---

## 📁 Estructura de Datos

### 🏘️ **Datos Geográficos y Administrativos**

#### `barrios_bogota/`
**📍 Barrios de Bogotá**
- **Descripción**: Listado completo de barrios con ubicación geográfica
- **Período**: 2016 (última actualización oficial)
- **Formato**: Shapefile, GeoJSON
- **Coordenadas**: WGS84 (EPSG:4326)
- **Fuente**: [Lab Urbano Bogotá](https://bogota-laburbano.opendatasoft.com/explore/dataset/barrios_prueba/information/?flg=es)
- **Uso**: Geocodificación, análisis por barrio, mapas temáticos

#### `localidades_bogota/`
**🏛️ Localidades de Bogotá D.C.**
- **Descripción**: División política-administrativa de Bogotá (20 localidades)
- **Campos**: Código, nombre, área, población estimada
- **Formato**: Shapefile, JSON
- **API**: [Endpoint directo](https://datosabiertos.bogota.gov.co/dataset/856cb657-8ca3-4ee8-857f-37211173b1f8/resource/497b8756-0927-4aee-8da9-ca4e32ca3a8a/download/loca.json)
- **Fuente**: [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/localidad-bogota-d-c)
- **Uso**: Análisis agregado por localidad, estudios demográficos

---

### 🚌 **Datos de Transporte Público**

#### `estaciones_troncales_transmilenio/`
**🚇 Estaciones Troncales TransMilenio**
- **Descripción**: Puntos de parada del sistema troncal de TransMilenio
- **Campos**: Nombre estación, línea, coordenadas, estado operativo
- **Total**: ~140 estaciones
- **Formato**: GeoJSON, CSV
- **Fuente**: [TransMilenio Open Data](https://datosabiertos-transmilenio.hub.arcgis.com/datasets/Transmilenio::estaciones-troncales-de-transmilenio/explore)
- **Uso**: Análisis de proximidad a transporte, valorización inmobiliaria

#### `paraderos_zonales_SITP/`
**🚌 Paraderos Zonales SITP**
- **Descripción**: Puntos de parada del Sistema Integrado de Transporte Público
- **Campos**: ID paradero, nombre, corredor, estado
- **Total**: ~13,000 paraderos
- **Formato**: Shapefile, GeoJSON
- **Fuente**: [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/paraderos-zonales-del-sitp)
- **Uso**: Análisis de conectividad, accesibilidad urbana

---

### 🏃‍♂️ **Datos de Servicios y Amenidades**

#### `espacios_para_deportes_bogota/`
**⚽ Espacios Deportivos**
- **Descripción**: Inventario de espacios deportivos y recreativos de Bogotá
- **Campos**: Nombre, tipo, dirección, servicios disponibles
- **Categorías**: Parques, canchas, pistas de atletismo, gimnasios al aire libre
- **Formato**: CSV, Excel
- **Fuente**: [Instituto Distrital de Recreación y Deporte (IDRD)](https://datosabiertos.bogota.gov.co/dataset/depor2023)
- **Uso**: Análisis de calidad de vida, amenidades por sector

---

## 🔧 Uso de los Datos

### 📈 **Casos de Uso en Análisis Inmobiliario**

1. **🗺️ Geocodificación de Propiedades**
   ```python
   # Asignar barrio y localidad a apartamentos
   apartments_with_location = geocode_properties(apartments, barrios_data)
   ```

2. **🚇 Proximidad a Transporte**
   ```python
   # Calcular distancia a estaciones TransMilenio
   transport_proximity = calculate_distance_to_transport(apartments, tm_stations)
   ```

3. **🏃‍♂️ Índice de Amenidades**
   ```python
   # Scoring de amenidades por sector
   amenity_score = calculate_amenities_index(location, sports_facilities)
   ```

4. **📊 Análisis Agregado**
   ```python
   # Estadísticas por localidad
   price_by_locality = apartments.groupby('localidad')['precio'].agg(['mean', 'median'])
   ```

### 🛠️ **Scripts de Procesamiento**

```bash
# Procesar datos geográficos
python scripts/process_geographic_data.py --source barrios_bogota --output processed/

# Integrar datos de transporte
python scripts/integrate_transport_data.py --apartments data/apartments.csv --transport external/
```

---

## 📋 Metadatos de Calidad

### ✅ **Estado de Actualización**

| Dataset | Última Actualización | Frecuencia | Estado |
|---------|---------------------|------------|--------|
| Barrios | 2016 | Irregular | 🟡 Estable |
| Localidades | 2023 | Anual | 🟢 Actualizado |
| TransMilenio | 2024 | Mensual | 🟢 Actualizado |
| SITP | 2024 | Trimestral | 🟢 Actualizado |
| Deportes | 2023 | Anual | 🟢 Actualizado |

### 🔍 **Calidad de Datos**

| Dataset | Completitud | Precisión | Consistencia | Calificación |
|---------|-------------|-----------|--------------|--------------|
| Barrios | 95% | Alta | Media | ⭐⭐⭐⭐ |
| Localidades | 100% | Muy Alta | Alta | ⭐⭐⭐⭐⭐ |
| TransMilenio | 98% | Alta | Alta | ⭐⭐⭐⭐⭐ |
| SITP | 92% | Media | Media | ⭐⭐⭐ |
| Deportes | 88% | Media | Baja | ⭐⭐⭐ |

---

## ⚖️ Licencias y Términos de Uso

### 📜 **Licencias de Datos**

- **Datos Abiertos Bogotá**: [Licencia Datos Abiertos Colombia](https://www.datos.gov.co/terms)
- **Lab Urbano**: Creative Commons CC BY 4.0
- **TransMilenio**: Uso público permitido con atribución
- **IDRD**: Datos de dominio público

### 🛡️ **Términos de Uso**

✅ **Permitido**:
- Uso comercial y no comercial
- Redistribución con atribución
- Modificación y derivación
- Integración en productos **Builker**

❌ **Restricciones**:
- No alterar metadatos originales
- Mantener atribución a fuentes
- No reclamar autoría de datos originales

---

## 🔄 Proceso de Actualización

### 📅 **Cronograma de Actualizaciones**

- **Mensual**: Verificación de nuevas versiones
- **Trimestral**: Actualización de datasets dinámicos
- **Anual**: Revisión completa de calidad de datos
- **Ad-hoc**: Actualizaciones por cambios mayores

### 🤖 **Automatización**

```bash
# Script de actualización automática
./scripts/update_external_data.sh

# Verificación de integridad
python scripts/validate_data_integrity.py
```

---

## 📊 Estadísticas de Uso

### 📈 **Métricas de Utilización**

| Dataset | Frecuencia de Uso | Casos de Uso Principales | Impacto en Análisis |
|---------|------------------|--------------------------|-------------------|
| Barrios | Alto | Geocodificación, mapas | Crítico |
| Localidades | Alto | Análisis agregado | Alto |
| TransMilenio | Medio | Proximidad transporte | Medio |
| SITP | Bajo | Conectividad detallada | Bajo |
| Deportes | Medio | Índice amenidades | Medio |

---

## 🛠️ Herramientas Recomendadas

### 📍 **Procesamiento Geoespacial**
- **QGIS**: Visualización y análisis espacial
- **GeoPandas**: Manipulación en Python
- **PostGIS**: Base de datos espacial
- **Folium**: Mapas interactivos

### 📊 **Análisis de Datos**
- **Pandas**: Manipulación de datos tabulares
- **Numpy**: Operaciones numéricas
- **Scipy**: Análisis estadístico espacial
- **Scikit-learn**: Machine learning geoespacial

---

## 🚨 Problemas Conocidos

### ⚠️ **Limitaciones Identificadas**

1. **Barrios (2016)**: 
   - Algunos límites pueden haber cambiado
   - Nuevas urbanizaciones no incluidas

2. **SITP**: 
   - Algunos paraderos desactivados
   - Coordenadas con errores ocasionales

3. **Deportes**: 
   - Información de servicios incompleta
   - Estado operativo no actualizado

### 🔧 **Soluciones Aplicadas**

- Validación cruzada con otras fuentes
- Limpieza automática de datos inconsistentes
- Flags de calidad por registro

---

## 📞 Contacto y Soporte

### 🆘 **Reportar Problemas**
- **Issues**: Problemas con datos o scripts
- **Email**: [data@builker.com](mailto:data@builker.com)
- **Documentación**: Wiki del proyecto

### 📚 **Recursos Adicionales**
- [Portal Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/)
- [IDECA - Infraestructura de Datos Espaciales](https://www.ideca.gov.co/)
- [Secretaría de Movilidad](https://www.movilidadbogota.gov.co/)

---

## 📝 Changelog

### **v3.0.0** - 2025
- ✨ Documentación completa de metadatos
- 🔧 Scripts de procesamiento automatizado
- 📊 Métricas de calidad de datos
- 🗺️ Integración geoespacial mejorada

### **v2.1.0** - 2024
- 📍 Actualización datos TransMilenio
- 🏃‍♂️ Integración espacios deportivos
- 🔄 Proceso de actualización automática

---

**🌟 Estos datos enriquecen significativamente nuestro análisis inmobiliario al proporcionar contexto geográfico, de transporte y amenidades urbanas que influyen en el valor y atractivo de las propiedades en Bogotá.**

---

**Última actualización**: 2025  
**Mantenido por**: Equipo **Builker** Data  
**Licencia**: Según fuentes originales