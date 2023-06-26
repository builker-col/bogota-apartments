# Datos Procesados

En esta carpeta se encuentran los datos procesados, es decir, los datos que han sido limpiados y transformados para su posterior análisis.

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
