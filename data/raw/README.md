# Datos en RAW

- [Significado de las variables](#significado-de-las-variables)
- [Eventos en la fuente de datos](#eventos-en-la-fuente-de-datos)

**Nota importante:** Los datos proporcionados son en formato raw, lo que significa que no han sido preprocesados o limpiados previamente. Pueden contener valores duplicados, nulos o errores, por lo que es importante realizar un proceso de limpieza y preprocesamiento antes de utilizarlos para cualquier análisis. Se recomienda que los datos en formato raw se utilicen únicamente con fines exploratorios y que no se tomen decisiones importantes basadas en ellos.

## Significado de las variables

| Variable                   | Descripción                                                                                            |
|----------------------------|--------------------------------------------------------------------------------------------------------|
| precio                     | Precio de venta en pesos colombianos                                                                   |
| area_m2                    | Área del apartamento en metros cuadrados                                                               |
| habitaciones               | Número de habitaciones en el apartamento                                                               |
| baños                      | Número de baños en el apartamento                                                                      |
| estrato                    | Estrato del apartamento según la clasificación del gobierno colombiano                                 |
| barrio                     | Nombre del barrio en el que se encuentra el apartamento                                                |
| antiguead                  | Antigüedad del apartamento                                                                            |
| administracion             | Valor de la administración mensual del apartamento en pesos colombianos                                 |
| parqueadero                | Número de parqueaderos en el apartamento                                                                |
| piso                       | Número de piso en el que se encuentra el apartamento                                                    |
| codigo                     | Código único del apartamento según el portal web                                                        |
| equipado                   | Indica si el apartamento está amueblado                                          |
| sauna                      | Indica si el apartamento cuenta con sauna                                                               |
| jacuzzi                    | Indica si el apartamento cuenta con jacuzzi                                                             |
| calefaccion                | Indica si el apartamento cuenta con sistema de calefacción                                              |
| porteria                   | Indica si el edificio cuenta con servicio de portería                                                   |
| vista_panoramica           | Indica si el apartamento cuenta con vista panorámica                                                    |
| vista_exterior             | Indica si el apartamento cuenta con vista al exterior                                                   |
| picina                     | Indica si el edificio cuenta con piscina                                                                |
| terraza                    | Indica si el apartamento cuenta con terraza                                                             |
| balcon                     | Indica si el apartamento cuenta con balcón                                                              |
| area_terraza_balcon_m2     | Área de la terraza o balcón en metros cuadrados                                                         |
| descripcion                | Descripción del apartamento según el portal web                                                         |
| link                       | Enlace al apartamento en el portal web                                                                  |
| query                      | Nombre de la búsqueda realizada en el portal web                                                        |
| date                       | Fecha y hora en la que se realizó la extracción de datos en formato "Day Month Year HH:MM:SS YYYY"  |

## Eventos en la fuente de datos

- **Lunes 3 Abril, 2023, 20:23:23**: Se cayo la pagina de la fuente de datos [Metro Cuadrado](https://www.metrocuadrado.com/) y se se detuvo la extracción de datos

- **Lunes 3 Abril, 2023, 21:00:34:** Se reinicio la extracción de datos

![image report](../../docs/images/reports/dates_events.png)