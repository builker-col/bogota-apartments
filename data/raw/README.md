# Raw data

> ⚠️ **Advertencia: Los siguientes datos están en formato raw y pueden requerir procesamiento adicional antes de su uso. Verificar la integridad y calidad de los datos es recomendado.**

[Raw apartment sales data](./bogota_apartments_raw.json)

<!-- Para poder haceder a los datos RAW puede ejecutar el script `download_raw_data.py` o puede descargar los datos desde el siguiente enlace [https://www.dropbox.com/scl/fi/63rkv8ehjcqogptpn06gp/builker.scrapy_bogota_apartmentsV1.3.0_october_1_2023.json?rlkey=wvwpyu3buy0ii84wxayywz8ot&dl=1](https://www.dropbox.com/scl/fi/63rkv8ehjcqogptpn06gp/builker.scrapy_bogota_apartmentsV1.3.0_october_1_2023.json?rlkey=wvwpyu3buy0ii84wxayywz8ot&dl=1)

```bash
python download_raw_data.py
``` -->

## Sources

Los datos del Data Set de Venta de Apartamentos en Bogotá fueron extraídos mediante web scraping de los siguientes sitios web:

- [Metrocuadrado](https://www.metrocuadrado.com/)
- [Habi](https://www.habi.co/)

## Collection Methodology

Para recopilar los datos, se utilizaron técnicas de web scraping automatizado. El proceso de extracción consistió en acceder a cada una de las páginas web, extraer la información de interés y almacenarla en una base de datos MongoDB.

Se implemento un scraper creado con la librería [Scrapy](https://scrapy.org/) y en caso de que el sitio web este creado con JavaScript Scrapy se conbinara con [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash) para poder renderizar el JavaScript.

> ⚠️ Es importante destacar que durante el proceso de web scraping se respetaron las políticas y condiciones de uso establecidas por cada sitio web.

## Significado de las columnas

| Columna                              | Descripción                                               |
|--------------------------------------|-----------------------------------------------------------|
| codigo                               | Código identificador de la propiedad                      |
| tipo_propiedad                       | Tipo de propiedad (casa, apartamento, etc.)               |
| tipo_operacion                       | Tipo de operación (venta, arriendo, etc.)                 |
| precio_venta                         | Precio de venta de la propiedad COP                       |
| precio_arriendo                      | Precio de arriendo de la propiedad COP                    |
| area                                 | Área de la propiedad en metros cuadrados                  |
| habitaciones                         | Número de habitaciones en la propiedad                    |
| banos                                | Número de baños en la propiedad                           |
| administracion                       | Costo de la administración de la propiedad                |
| parqueaderos                         | Número de parqueaderos disponibles                        |
| sector                               | Sector geográfico donde se encuentra la propiedad         |
| estrato                              | Estrato socioeconómico de la propiedad                    |
| antiguedad                           | Antigüedad de la propiedad en años                        |
| estado                               | Estado de la propiedad (nuevo, usado, etc.)               |
| longitud                             | Coordenada de longitud de la ubicación de la propiedad    |
| latitud                              | Coordenada de latitud de la ubicación de la propiedad     |
| caracteristicas                      | Características de la propiedad                           |
| descripcion                          | Descripción detallada de la propiedad                     |
| datetime                             | Fecha y hora de extracción de los datos                   |
| website                              | Sitio web relacionado a la propiedad                      |
| compañia                             | Compañía o agencia responsable de la propiedad            |
| imagenes                             | Imágenes relacionadas a la propiedad                      |
| direccion                            | Dirección de la propiedad                                 |
| last_view                            | Fecha de la última vez que el scraper visito la propiedad |
| timeline                             | Historial de precios de la propiedad                      |
| url                                  | URL de la propiedad                                       |

## Datos del 2023
Con la versión 2.0.0, se realizó una actualización crucial en la estructura de datos, lo que conllevó a la eliminación de los datos anteriores a 2024 de nuestra base de datos. Si necesitas acceder a esta información del 2023, puedes descargarla desde la siguiente URL: [https://www.dropbox.com/scl/fi/nv1efc8me23dsa1ie0g5s/2023_bogota_apartments_processed.json?rlkey=l6cl2gsf8j2icyh5cqwkr4un5&dl=1](https://www.dropbox.com/scl/fi/nv1efc8me23dsa1ie0g5s/2023_bogota_apartments_processed.json?rlkey=l6cl2gsf8j2icyh5cqwkr4un5&dl=1)

Esta actualización asegura una estructura más optimizada y acorde con las necesidades actuales de los datos, por lo que te invitamos a obtener los datos actualizados del 2024 y posteriores para aprovechar al máximo nuestras últimas mejoras.

**Nota:** Los datos del 2023 ya estan procesados y no requieren de ningún procesamiento adicional.