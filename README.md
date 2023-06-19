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
- [Cómo contribuir](#cómo-contribuir)
- [Mantenimiento](#mantenimiento)
- [Licencia](#licencia)
- [Créditos](#créditos)

_**Datos:**_
- [Datos](data/)
    - [Data Readme](data/README.md)
- [RAW Data](data/raw/)
    - [RAW Data Readme](data/raw/README.md)
- [Eventos en la extracion de datos](data/raw/README.md#eventos-en-la-fuente-de-datos)
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

<iframe style="background: #21313C;border: none;border-radius: 2px;box-shadow: 0 2px 10px 0 rgba(70, 76, 79, .2);width: 100vw;height: 100vh;"  src="https://charts.mongodb.com/charts-project-0-vjiwc/embed/dashboards?id=5a5eac8a-6f4e-4a6e-8235-54c6e69c33ca&theme=dark&autoRefresh=true&maxDataAge=3600&showTitleAndDesc=true&scalingWidth=fixed&scalingHeight=fixed"></iframe>
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
