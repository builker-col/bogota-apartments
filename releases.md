# Registro de versiones

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
