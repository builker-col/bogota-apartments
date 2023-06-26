# Bogota Apartments

[![ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/U6U0K5UNW)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@erik172) 
[![GitHub issues](	https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/erik172/)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/_Erik172)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white)](https://www.kaggle.com/datasets/erik172/bogota-apartments)
[![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)]()
<!-- [![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)]() -->

![Bogota Apartments](https://i.ibb.co/6nfN4Z0/bogota-apartments02.png)

_**Indice:**_
- [Descripción](#descripción)
- [Configuración](#configuración)
- [MongoDB Dashboard](#MongoDB-Dashboard)
- [Datos](#datos)
- [Cómo contribuir](#cómo-contribuir)
- [Mantenimiento](#mantenimiento)
- [Licencia](#licencia)
- [Créditos](#créditos)

_**Datos:**_
- [Datos](data/processed/)
    - [Data Readme](data/processed/README.md)
- [RAW Data](data/raw/)
    - [RAW Data Readme](data/raw/README.md)

## Descripción

El Proyecto Bogotá Apartments es una iniciativa de código abierto que tiene como objetivo recopilar y analizar datos sobre el mercado inmobiliario de apartamentos en la ciudad de Bogotá, Colombia. El proyecto utiliza técnicas avanzadas de web scraping y análisis de datos para recopilar información detallada sobre las ventas y arriendo de apartamentos en la ciudad y proporcionar un conjunto de datos completo y actualizado.

El conjunto de datos está disponible para cualquier persona interesada en aprender más sobre el mercado inmobiliario de Bogotá y sus tendencias. Además, el proyecto incluye un análisis exploratorio de datos detallado que proporciona información valiosa sobre los precios, las ubicaciones y las características de los apartamentos en la ciudad.

El objetivo del proyecto es fomentar la investigación y el aprendizaje en el campo del análisis de datos y la ciencia de datos. El conjunto de datos se puede utilizar para entrenar modelos de aprendizaje automático y para realizar análisis más profundos sobre el mercado inmobiliario de la ciudad.

_Este proyecto hace parte de [Builker](https://github.com/Builker-col)_.

## Configuración

Si quieres ejecutar el proyecto con los servicios de mongoDB y ScrapeOps debes crear un archivo `.env` en la raiz del proyecto con las siguientes variables de entorno:

```bash
MONGO_URI=<<URI de conexión a MongoDB>>
MONGO_DATABASE=<<Nombre de la base de datos en MongoDB>>
SCRAPEOPS_API_KEY=<<Clave de API de ScrapeOps>>

```

### Quitar Configuración de mongoDB

si no quieres usar mongoDB puedes comentar las siguientes lineas de codigo en el archivo `settings.py`:

```python
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DATABASE = os.getenv('MONGO_DATABASE')
```

```python
ITEM_PIPELINES = {
    'bogota_apartments.pipelines.MongoDBPipeline': 500
}
```

### Quitar Configuración de ScrapeOps

si no quieres usar ScrapeOps puedes comentar las siguientes lineas de codigo en el archivo `settings.py`:

```python
SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')
```

```python
DOWNLOADER_MIDDLEWARES = {
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550, 
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 
}
```

## MongoDB Dashboard

### Apartamentos en Bogotá(Source: **[Metrocuadrado](https://www.metrocuadrado.com/)**)

[MonogoDB Dashboard](https://charts.mongodb.com/charts-project-0-vjiwc/public/dashboards/5a5eac8a-6f4e-4a6e-8235-54c6e69c33ca)

<!-- <iframe style="background: #21313C;border: none;border-radius: 2px;box-shadow: 0 2px 10px 0 rgba(70, 76, 79, .2);width: 100vw;height: 100vh;"  src="https://charts.mongodb.com/charts-project-0-vjiwc/embed/dashboards?id=5a5eac8a-6f4e-4a6e-8235-54c6e69c33ca&theme=dark&autoRefresh=true&maxDataAge=3600&showTitleAndDesc=true&scalingWidth=fixed&scalingHeight=fixed"></iframe> -->

## Datos

> ⚠️ **Advertencia**: La columna `coords_modified` indica si las coordenadas geográficas fueron modificadas durante el procesamiento de los datos. Si el valor es `True`, esto significa que las coordenadas originales fueron ajustadas o corregidas. Se recomienda precaución al utilizar estos datos, ya que pueden no reflejar las coordenadas geográficas exactas del apartamento. Es importante verificar la precisión y la fuente de las coordenadas antes de utilizarlas en aplicaciones o análisis que requieran una ubicación geográfica precisa.


| Columna                  | Descripción                                               |
|--------------------------|-----------------------------------------------------------|
| codigo                   | Código único que identifica cada apartamento              |
| tipo_propiedad           | Tipo de propiedad (apartamento, casa, etc.)               |
| tipo_operacion           | Tipo de operación (venta, arriendo, etc.)                 |
| precio_venta             | Precio de venta del apartamento                           |
| precio_arriendo          | Precio de arriendo del apartamento                        |
| area                     | Área del apartamento en metros cuadrados                  |
| habitaciones             | Número de habitaciones del apartamento                    |
| banos                    | Número de baños del apartamento                           |
| administracion           | Valor de la cuota de administración del apartamento       |
| parqueaderos             | Número de parqueaderos disponibles                        |
| sector                   | Sector o zona en la que se encuentra el apartamento       |
| estrato                  | Estrato socioeconómico del apartamento                    |
| antiguedad               | Antigüedad del apartamento en años                        |
| estado                   | Estado del apartamento (nuevo, usado)                     |
| longitud                 | Longitud geográfica del apartamento                       |
| latitud                  | Latitud geográfica del apartamento                        |
| descripcion              | Descripción detallada del apartamento                     |
| jacuzzi                  | Indica si el apartamento cuenta con jacuzzi               |
| piso                     | Número de piso en el que se encuentra el apartamento      |
| closets                  | Número de closets en el apartamento                       |
| chimenea                 | Indica si el apartamento cuenta con chimenea              |
| permite_mascotas         | Indica si se permiten mascotas en el apartamento          |
| gimnasio                 | Indica si el apartamento cuenta con gimnasio              |
| ascensor                 | Indica si el edificio cuenta con ascensor                 |
| conjunto_cerrado         | Indica si el apartamento se encuentra en conjunto cerrado |
| coords_modified          | Coordenadas modificadas del apartamento                   |
| localidad                | Localidad en la que se encuentra el apartamento           |
| barrio                   | Barrio en el que se encuentra el apartamento              |
| estacion_tm_cercana      | Nombre de la estacion de transporte masivo mas cercana    |
| distancia_estacion_tm_m  | Distancia a la estación de transporte masivo más cercana  |
| cerca_estacion_tm        | Indica si está cerca de una estación de transporte masivo |


## Cómo contribuir
El proyecto es de código abierto y se anima a cualquier persona interesada en contribuir a hacerlo. Para contribuir al proyecto, por favor sigue estos pasos:

1. Haz un fork de este repositorio y clona el repositorio en tu máquina local.

1. Crea una nueva rama (`git checkout -b nombre-rama`) y realiza tus cambios en esa rama.

1. Haz commit a tus cambios (`git commit -m "Descripción de los cambios"`) y haz push a la rama (`git push origin nombre-rama`).

1. Abre un pull request en este repositorio y describe los cambios que has realizado.

1. Por favor, asegúrate de seguir las pautas de contribución antes de hacer un pull request.

## Mantenimiento
El conjunto de datos se actualizará regularmente para asegurarse de que se mantenga relevante y útil para la comunidad. Si encuentras algún error o tienes alguna sugerencia para mejorar el proyecto, por favor abre un issue en este repositorio.

## Licencia
El conjunto de datos y el código fuente del proyecto están disponibles bajo la licencia GNU General Public License v3.0. Para más información, por favor lee el archivo LICENSE.

## Créditos
- [**@erik172**](https://github.com/Erik172) - Creador del proyecto y mantenedor principal.


Hecho con ❤️ por **@erik172**
