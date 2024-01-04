# Datos Procesados

> ⚠️ Es importante destacar que durante el proceso de web scraping se respetaron las políticas y condiciones de uso establecidas por cada sitio web.

En esta carpeta se encuentran los datos procesados, es decir, los datos que han sido limpiados y transformados para su posterior análisis.

## Significado de las columnas

### Apartamentos

**File:** [apartments.csv](apartments.csv)

> ⚠️ **Advertencia**: La columna `coords_modified` indica si las coordenadas geográficas fueron modificadas durante el procesamiento de los datos. Si el valor es `True`, esto significa que las coordenadas originales fueron ajustadas o corregidas. Se recomienda precaución al utilizar estos datos, ya que pueden no reflejar las coordenadas geográficas exactas del apartamento. Es importante verificar la precisión y la fuente de las coordenadas antes de utilizarlas en aplicaciones o análisis que requieran una ubicación geográfica precisa.

> ⚠️ **Advertencia**: la columna `last_view` se actualiza cada vez que se ejecuta el scraper. por lo tanto, este dato no es exacto. ya que el scraper puede no visitar el apartamento y este seguir publicado en la pagina web. Se recomienda usar este dato como referencia y no como dato exacto. Para saber si el apartamento sigue publicado en la pagina web se recomienda verificar manualmente en la pagina web.

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
| piscina                              | Indica si el apartamento cuenta con piscina               |
| salon_comunal                        | Indica si el apartamento cuenta con salón comunal         |
| terraza                              | Indica si el apartamento cuenta con terraza               |
| vigilancia                           | Indica si el apartamento cuenta con vigilancia privada    |
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
| is_cerca_estacion_tm                 | Indica si está cerca de una estación de transporte masivo <= 500m |
| parque_cercano                       | Nombre del parque más cercano al apartamento              |
| distancia_parque_m                   | Distancia al parque más cercano al apartamento en metros  |
| is_cerca_parque                      | Indica si está cerca de un parque <= 500m                  |
| website                              | Sitio web relacionado a la propiedad                      |
| compañia                             | Compañía o agencia responsable de la propiedad            |
| last_view                            | Fecha de la última vez que el scraper visito el apartamento |
| timeline                             | Historial de precios del apartamento                      |
| url                                  | URL del apartamento                                       |

### Imagenes

**File:** [images.csv](images.csv)

| Columna      | Descripción                                      |
|--------------|--------------------------------------------------|
| codigo       | Código único que identifica cada apartamento.    |
| url_imagen   | Enlace URL de la imagen asociada al apartamento. |

## Datos del 2023
Con la versión 2.0.0, se realizó una actualización crucial en la estructura de datos, lo que conllevó a la eliminación de los datos anteriores a 2024 de nuestra base de datos. Si necesitas acceder a esta información del 2023, puedes descargarla desde la siguiente URL: [https://www.dropbox.com/scl/fi/nv1efc8me23dsa1ie0g5s/2023_bogota_apartments_processed.json?rlkey=l6cl2gsf8j2icyh5cqwkr4un5&dl=1](https://www.dropbox.com/scl/fi/nv1efc8me23dsa1ie0g5s/2023_bogota_apartments_processed.json?rlkey=l6cl2gsf8j2icyh5cqwkr4un5&dl=1)

Esta actualización asegura una estructura más optimizada y acorde con las necesidades actuales de los datos, por lo que te invitamos a obtener los datos actualizados del 2024 y posteriores para aprovechar al máximo nuestras últimas mejoras.

**Nota:** Los datos del 2023 ya estan procesados y no requieren de ningún procesamiento adicional.