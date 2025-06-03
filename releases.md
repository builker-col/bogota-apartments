# Registro de Cambios (Changelog)

## [v3.0.0] - 2025-06-02

> ⚠️ Durante el proceso de web scraping, se mantuvo el cumplimiento con las políticas y condiciones de uso de los sitios web involucrados.

## [V2.1.0] - 2024-02-01

> ⚠️ Durante el proceso de web scraping, se mantuvo el cumplimiento con las políticas y condiciones de uso de los sitios web involucrados.

### Cambios Principales

- **Modificación en la Estructura de Datos**:
  - Se ha actualizado la estructura de los datos para incluir un **timeline** de precios. Ahora los apartamentos cuentan con un historial de precios para un seguimiento más detallado.

  > ⚠️ **Advertencia**: Los datos del 2023 ya no están disponibles en la base de datos principal. Si necesitas acceder a los datos del 2023, puedes descargarlos [aquí](https://www.dropbox.com/scl/fi/nv1efc8me23dsa1ie0g5s/2023_bogota_apartments_processed.json?rlkey=l6cl2gsf8j2icyh5cqwkr4un5&dl=1). La estructura ha cambiado, por lo que los datos del 2023 están en este archivo y no en la nueva versión.

- **Optimización en la Extracción de Datos**:
  - Se abandonó el uso de Selenium en conjunto con Scrapy para la extracción de datos de los apartamentos. Ahora se implementa Scrapy junto con scrapy-splash para mejorar la velocidad y eficiencia en la obtención de información desde la página web de **Metrocuadrado**.

  > ⚠️ Para utilizar scrapy-splash, es necesario tener instalado un servidor de Splash en tu computadora. Encuentra más información sobre la instalación [aquí](https://splash.readthedocs.io/en/stable/install.html).

### Nuevas Características

- **Columna de Timeline en Datos de Apartamentos**:
  - Se agregó la columna `timeline` a los datos extraídos de la página web de **Metrocuadrado** y **habi** para almacenar el historial de precios de los apartamentos, permitiendo un seguimiento detallado de la variación de precios a lo largo del tiempo.

- **Información de Parques Cercanos al Apartamento**:
  - Se agregaron las columnas `parque_cercano`, que contiene el nombre del parque más cercano al apartamento, `distancia_parque_m`, que indica la distancia en metros al parque cercano, y `is_cerca_parque`, que determina si el apartamento está cerca de un parque a menos de 500 metros.

- **Creación de API para Interactuar con el Scraper en Tiempo Real**:
  - Se está desarrollando una API que permitirá visualizar los datos en tiempo real y ofrecerá interacciones con el scraper en ejecución para mayor control y supervisión.

### Corrección de Errores

- **Solución a Error de `InvalidSessionIdException`**:
  - Se ha solucionado el problema que causaba la excepción `InvalidSessionIdException` al ejecutar el scraper de **Metrocuadrado** con Selenium, mejorando la estabilidad y fluidez del proceso de extracción de datos.

Estos cambios han sido implementados para mejorar la eficiencia, calidad y consistencia en la extracción de datos, asegurando el respeto a las políticas y condiciones de uso de los sitios web pertinentes.



## V1.3.1 - 2023-11-10

- Se crea un pipeline automatico para extraer los datos de los apartamentos de la pagina web de **Metrocuadrado** y **habi**. esto con el fin de mantener actualizados los datos de los apartamentos.

## v1.3.0 - 2023-09-21

### Nuevas caracteristicas

> ⚠️ Es importante destacar que durante el proceso de web scraping se respetaron las políticas y condiciones de uso establecidas por cada sitio web.

- se agrego la columna `last_view` a los datos de los apartamentos de la pagina web de **Metrocuadrado** y **habi** para almacenar la fecha de la ultima vez que el scraper visito el apartamento. esto con el fin de saber si el apartamento sigue publicado en la pagina web o fue eliminado.

> ⚠️ **Advertencia**: la columna `last_view` se actualiza cada vez que se ejecuta el scraper. por lo tanto, este dato no es exacto. ya que el scraper puede no visitar el apartamento y este seguir publicado en la pagina web. Se recomienda usar este dato como referencia y no como dato exacto. Para saber si el apartamento sigue publicado en la pagina web se recomienda verificar manualmente en la pagina web.

- Automatizacion de la extraccion de datos y procesamiento de los datos. ahora el proceso de extraccion de datos y procesamiento de los datos se puede ejecutando el archivo `run.py`.

## V1.2.2 - 2023-09-09

### Solucion de errores

- Se corrigio un error en el scraper de **metrocuadrado** que no permitia extraer los datos de los apartamentos.
- Se corrigio un error en el scraper de **habi** que no permitia extraer los datos de los apartamentos.

## V1.2.1 - 2023-09

### Solucion de errores

- Se corrigio un error en el scraper de **metrocuadrado** que no permitia extraer los datos de los apartamentos.

## v1.2.0 - 2023-07-28

### Nuevas caracteristicas

- Se agrego datos de los apartamentos de la pagina web **[habi](https://habi.co)**

- El archivo `builker.scrapy_bogota_apartemnts.json` de la carpeta `data/raw/` ahora se almacenara en dropbox para que los datos sean accesibles desde cualquier lugar. ya que es muy pesado para almacenarlo en github. [https://www.dropbox.com/s/1ly47276dnqqdzp/builker.scrapy_bogota_apartments.json?dl=1](https://www.dropbox.com/s/1ly47276dnqqdzp/builker.scrapy_bogota_apartments.json?dl=1)

> ⚠️ Es importante destacar que durante el proceso de web scraping se respetaron las políticas y condiciones de uso establecidas por cada sitio web.

## v1.1.0 - 2023-07-18

### Nuevas características

- Se agrego la funcionalidad de actualizar el precio de venta y de arriendo de los apartamentos que ya se encuentran en la base de datos y que son extraidos de la pagina web de **Metrocuadrado**. a su vez se agrego la columna `precio_venta_anterior` y `precio_arriendo_anterior` para almacenar el precio anterior de los apartamentos. Y se agrego la columnas `fecha_actualizacion_precio_venta` y `fecha_actualizacion_precio_arriendo` para almacenar la fecha de la ultima actualizacion de los precios de los apartamentos.

- Se agrego la columna `imagenes` a los datos del sitio web de **Metrocuadrado** para almacenar los enlaces a las imagenes de los apartamentos. Esto para futuras funcionalidades de analisis de imagenes.

- se agrego la columna `compañia` a los datos del sitio web de **Metrocuadrado** para almacenar el nombre de la compañia que publica el apartamento.

> Para agregar las nuevas columnas a la base de datos se debe volver hacer el proceso de extraccion de datos de la pagina web de **Metrocuadrado**. no todos los apartamentos tendran los datos de las nuevas columnas, ya que pudieron haber sido eliminados de la pagina web de **Metrocuadrado**.

## v1.0.1 - 2023-07-18

### Correcciones de errores

- Correccion de errores en el scraper de **Metrocuadrado**.

- Coreccion con la libreria `webdriver-manager`, se elimino temporalmente la dependencia de esta libreria para evitar errores en la instalacion del proyecto y ejecucion de los scrapers. se volvera a incluir en futuras versiones.

> se asume que el usuario tiene instalado el driver de chrome en su computador.


## v1.0.0 - 2023-06-19

### Cambios principales

- Se migro el proyecto a scrapy con selenium para mayor velocidad de extracción.
- Se agregaron conexion a mongodb para almacenar los datos.

### Nuevas características

- Se agrego la opcion de dashboard para visualizar los datos con https://scrapeops.io/.

### Correcciones de errores

- Se corrigio el error de que no se extraian todos los datos de los apartamentos.


## v0.2.0 - 2023-06-12

### Nuevas características

- Se agregaron los datos 'latitud' y 'longitud' a los datos de los apartamentos de Metrocuadrado.
- Se incluyo los enlaces a las imagenes de los apartamentos en el archivo 'data/raw/metrocuadrado/images.csv'.
- Se reorganizaron los archivos para facilitar su uso.

## v0.1.0 - 2023-04

### Lanzamiento inicial

- Lanzamiento inicial del proyecto Bogota Apartments.

### Funcionalidades

- Extracción de datos de la página web de Metrocuadrado.
