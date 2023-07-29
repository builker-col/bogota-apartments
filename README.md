# Bogota Apartments

[![ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/U6U0K5UNW)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@erik172) 
[![Github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/builker-col/bogota-apartments)
[![Linkedin](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/erik172/)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/_Erik172)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white)](https://www.kaggle.com/datasets/erik172/bogota-apartments)
[![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

![Bogota Apartments](https://i.ibb.co/6nfN4Z0/bogota-apartments02.png)

## Índice
- [Descripción](#descripción)
- [Configuración](#configuración)
- [Data Source](#data-source)
- [Datos](#datos)
    - [Raw Data](#raw-data)
    - [Apartamentos](#apartamentos)
    - [Imágenes](#imágenes)
- [Actualización de los Datos](#actualización-de-los-datos)
- [MongoDB Dashboard](#mongodb-dashboard)
- [Cómo contribuir](#cómo-contribuir)
- [Mantenimiento](#mantenimiento)
- [Licencia](#licencia)
- [Créditos](#créditos)
- [Versiones](releases.md)

**Datos:**
- [Datos Procesados](data/processed/)
    - [Readme de Datos Procesados](data/processed/README.md)
    - [Apartamentos](data/processed/apartments.csv)
    - [Imágenes](data/processed/images.csv)
- [Datos RAW](data/raw/)
    - [Readme de Datos RAW](data/raw/README.md)
    - [Apartamentos](https://www.dropbox.com/s/1ly47276dnqqdzp/builker.scrapy_bogota_apartments.json?dl=1)

From **Bogota** co to the world 🌎

## Descripción

El Proyecto Bogotá Apartments es una iniciativa de código abierto que tiene como objetivo recopilar y analizar datos sobre el mercado inmobiliario de apartamentos en la ciudad de Bogotá, Colombia. El proyecto utiliza técnicas avanzadas de web scraping y análisis de datos para recopilar información detallada sobre las ventas y arriendo de apartamentos en la ciudad y proporcionar un conjunto de datos completo y actualizado.

El conjunto de datos está disponible para cualquier persona interesada en aprender más sobre el mercado inmobiliario de Bogotá y sus tendencias. Además, el proyecto incluye un análisis exploratorio de datos detallado que proporciona información valiosa sobre los precios, las ubicaciones y las características de los apartamentos en la ciudad.

El objetivo del proyecto es fomentar la investigación y el aprendizaje en el campo del análisis de datos y la ciencia de datos. El conjunto de datos se puede utilizar para entrenar modelos de aprendizaje automático y para realizar análisis más profundos sobre el mercado inmobiliario de la ciudad.

_Este proyecto hace parte de [Builker](https://github.com/Builker-col)_.

## Configuración

Si quieres ejecutar el proyecto con los servicios de mongoDB debes crear un archivo `.env` en la raiz del proyecto con las siguientes variables de entorno:

```bash
MONGO_URI=<<URI de conexión a MongoDB>>
MONGO_DATABASE=<<Nombre de la base de datos en MongoDB>>
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

## Data Source

> ⚠️ Es importante destacar que durante el proceso de web scraping se respetaron las políticas y condiciones de uso establecidas por cada sitio web.

Los datos del proyecto fueron extraídos mediante web scraping de los siguientes sitios web:

- [Metrocuadrado](https://www.metrocuadrado.com/)
- [Habi](https://www.habi.co/)

Se implemento un scraper creado con la librería [Scrapy](https://scrapy.org/) y en caso de que el sitio web este creado con JavaScript [Scrapy](https://scrapy.org/) se conbinara con [Selenium](https://www.selenium.dev/).

## Datos

### Raw Data

Para poder haceder a los datos RAW puede ejecutar el script `download_raw_data.py` en la ruta `data/raw/` o puede descargar los datos desde el siguiente enlace [https://www.dropbox.com/s/1ly47276dnqqdzp/builker.scrapy_bogota_apartments.json?dl=1](https://www.dropbox.com/s/1ly47276dnqqdzp/builker.scrapy_bogota_apartments.json?dl=1)

### Apartamentos

file: [apartments.csv](data/processed/apartments.csv)

> ⚠️ **Advertencia**: La columna `coords_modified` indica si las coordenadas geográficas fueron modificadas durante el procesamiento de los datos. Si el valor es `True`, esto significa que las coordenadas originales fueron ajustadas o corregidas. Se recomienda precaución al utilizar estos datos, ya que pueden no reflejar las coordenadas geográficas exactas del apartamento. Es importante verificar la precisión y la fuente de las coordenadas antes de utilizarlas en aplicaciones o análisis que requieran una ubicación geográfica precisa.


| Columna                              | Descripción                                               |
|--------------------------------------|-----------------------------------------------------------|
| codigo                               | Código único que identifica cada apartamento              |
| tipo_propiedad                       | Tipo de propiedad (apartamento, casa, etc.)               |
| tipo_operacion                       | Tipo de operación (venta, arriendo, etc.)                 |
| precio_venta                         | Precio de venta del apartamento COP                       |
| precio_arriendo                      | Precio de arriendo del apartamento COP                    |
| area                                 | Área del apartamento en metros cuadrados                  |
| habitaciones                         | Número de habitaciones del apartamento                    |
| banos                                | Número de baños del apartamento                           |
| administracion                       | Valor de la cuota de administración del apartamento       |
| parqueaderos                         | Número de parqueaderos disponibles                        |
| sector                               | Sector o zona en la que se encuentra el apartamento       |
| estrato                              | Estrato socioeconómico del apartamento                    |
| antiguedad                           | Antigüedad del apartamento en años                        |
| estado                               | Estado del apartamento (nuevo, usado)                     |
| longitud                             | Longitud geográfica del apartamento                       |
| latitud                              | Latitud geográfica del apartamento                        |
| descripcion                          | Descripción detallada del apartamento                     |
| datetime                             | Fecha y hora de extracción de los datos                   |
| jacuzzi                              | Indica si el apartamento cuenta con jacuzzi               |
| piso                                 | Número de piso en el que se encuentra el apartamento      |
| closets                              | Número de closets en el apartamento                       |
| chimenea                             | Indica si el apartamento cuenta con chimenea              |
| permite_mascotas                     | Indica si se permiten mascotas en el apartamento          |
| gimnasio                             | Indica si el apartamento cuenta con gimnasio              |
| ascensor                             | Indica si el edificio cuenta con ascensor                 |
| conjunto_cerrado                     | Indica si el apartamento se encuentra en conjunto cerrado |
| coords_modified                      | Coordenadas modificadas del apartamento                   |
| localidad                            | Localidad en la que se encuentra el apartamento           |
| barrio                               | Barrio en el que se encuentra el apartamento              |
| estacion_tm_cercana                  | Nombre de la estacion de transporte masivo mas cercana    |
| distancia_estacion_tm_m              | Distancia a la estación de transporte masivo más cercana  |
| is_cerca_estacion_tm                    | Indica si está cerca de una estación de transporte masivo |
| website                              | Sitio web relacionado a la propiedad                      |
| compañia                             | Compañía o agencia responsable de la propiedad            |
| fecha_actualizacion_precio_venta     | Fecha de actualización del precio de venta (scrapeado)    |
| precio_venta_anterior                | Precio de venta anterior de la propiedad COP              |
| fecha_actualizacion_precio_arriendo  | Fecha de actualización del precio de arriendo (scrapeado) |
| precio_arriendo_anterior             | Precio de arriendo anterior de la propiedad COP           |

### Imagenes

file: [images.csv](data/processed/images.csv)

| Columna      | Descripción                                      |
|--------------|--------------------------------------------------|
| codigo       | Código único que identifica cada apartamento.    |
| url_imagen   | Enlace URL de la imagen asociada al apartamento. |

## Actualización de los Datos

Los datos extraídos mediante web scraping serán actualizados regularmente para mantenerlos al día. A continuación se detallan los aspectos clave de la actualización:

- Los datos serán actualizados al menos cada 3 semanas, con una frecuencia mínima de actualización mensual. Esto asegurará que los datos reflejen la información más reciente disponible en las fuentes de origen.
- Durante el proceso de actualización, se revisarán y recopilarán los nuevos datos disponibles, así como se verificará la consistencia y calidad de los datos existentes.
- Se implementará un proceso automatizado para la actualización de los datos, utilizando herramientas y scripts específicos para realizar el web scraping de las fuentes de origen de manera eficiente y precisa.
- Después de cada actualización, se realizará un análisis y verificación de los datos para garantizar su integridad y confiabilidad.
- Se publicará la fecha de la última actualización en este README para que los usuarios puedan verificar la frescura de los datos.

## MongoDB Dashboard

[MonogoDB Dashboard](https://charts.mongodb.com/charts-project-0-vjiwc/public/dashboards/5a5eac8a-6f4e-4a6e-8235-54c6e69c33ca)

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

para más información sobre la licencia, por favor lee el archivo [LICENSE](LICENSE).

## Créditos
- [**@erik172**](https://github.com/Erik172) - Creador del proyecto y mantenedor principal.


Hecho con ❤️ por **@erik172**. 
