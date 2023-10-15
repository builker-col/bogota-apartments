# Raw data

> ⚠️ **Advertencia: Los siguientes datos están en formato raw y pueden requerir procesamiento adicional antes de su uso. Verificar la integridad y calidad de los datos es recomendado.**

Para poder haceder a los datos RAW puede ejecutar el script `download_raw_data.py` o puede descargar los datos desde el siguiente enlace [https://www.dropbox.com/scl/fi/63rkv8ehjcqogptpn06gp/builker.scrapy_bogota_apartmentsV1.3.0_october_1_2023.json?rlkey=wvwpyu3buy0ii84wxayywz8ot&dl=1](https://www.dropbox.com/scl/fi/63rkv8ehjcqogptpn06gp/builker.scrapy_bogota_apartmentsV1.3.0_october_1_2023.json?rlkey=wvwpyu3buy0ii84wxayywz8ot&dl=1)

```bash
python download_raw_data.py
```

## Sources

Los datos del Data Set de Venta de Apartamentos en Bogotá fueron extraídos mediante web scraping de los siguientes sitios web:

- [Metrocuadrado](https://www.metrocuadrado.com/)
- [Habi](https://www.habi.co/)

## Collection Methodology

Para recopilar los datos, se utilizaron técnicas de web scraping automatizado. El proceso de extracción consistió en acceder a cada una de las páginas web, extraer la información de interés y almacenarla en una base de datos MongoDB.

Se implemento un scraper creado con la librería [Scrapy](https://scrapy.org/) y en caso de que el sitio web este creado con JavaScript Scrapy se conbinara con [Selenium](https://www.selenium.dev/).

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
| featured_interior                    | Características destacadas del interior de la propiedad   |
| featured_exterior                    | Características destacadas del exterior de la propiedad   |
| featured_zona_comun                  | Características destacadas de las zonas comunes           |
| featured_sector                      | Características destacadas del sector donde se ubica      |
| descripcion                          | Descripción detallada de la propiedad                     |
| datetime                             | Fecha y hora de extracción de los datos                   |
| website                              | Sitio web relacionado a la propiedad                      |
| compañia                             | Compañía o agencia responsable de la propiedad            |
| imagenes                             | Imágenes relacionadas a la propiedad                      |
| fecha_actualizacion_precio_venta     | Fecha de actualización del precio de venta (scrapeado)    |
| precio_venta_anterior                | Precio de venta anterior de la propiedad COP              |
| fecha_actualizacion_precio_arriendo  | Fecha de actualización del precio de arriendo (scrapeado) |
| precio_arriendo_anterior             | Precio de arriendo anterior de la propiedad COP           |
| direccion                            | Dirección de la propiedad                                 |
| last_view                            | Fecha de la última vez que el scraper visito la propiedad |