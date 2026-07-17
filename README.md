# Bogotá Apartments

> [!IMPORTANT]
> **Este repositorio está archivado y ya no recibe actualizaciones.** Su código, documentación y datos se conservan únicamente como referencia histórica. No representa la infraestructura actual de Builker ni debe utilizarse como una fuente de datos vigente.

[![Estado](https://img.shields.io/badge/estado-archivado-6b6470)](https://github.com/builker-col/bogota-apartments)
[![Última versión](https://img.shields.io/badge/última%20versión-v3.0.0-7626ff)](https://github.com/builker-col/bogota-apartments/releases/tag/v3.0.0)
[![Licencia](https://img.shields.io/badge/licencia-CC%20BY--NC--SA%204.0-1748ff)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## El proyecto evolucionó

Bogotá Apartments nació en 2024 como un experimento de Builker para recopilar, estructurar y analizar información del mercado inmobiliario de Bogotá. El proyecto permitió validar el valor de convertir datos dispersos en información reutilizable.

Esa etapa terminó. El trabajo continúa hoy en dos iniciativas diferentes:

| Iniciativa | Función actual |
| --- | --- |
| [Bogotá Real Estate Open Data](https://bogota.builker.com) | Capa pública con datasets, indicadores y análisis básicos del mercado inmobiliario de Bogotá. |
| [Inmodata](https://inmodata.io) | Plataforma comercial y propietaria —no open source— para consultar datos e inteligencia del mercado inmobiliario mediante productos y API. Opera en toda Colombia, ofrece un plan gratuito y planes de pago, y se prepara para ampliar su cobertura a Latinoamérica. |

Puedes conocer el contexto y la evolución del proyecto en [builker.com/datos-abiertos/bogota](https://builker.com/datos-abiertos/bogota).

## Qué contiene este archivo

El repositorio conserva la última versión del experimento original:

- Scrapers desarrollados con Scrapy y Selenium.
- Procesos históricos de limpieza, deduplicación y enriquecimiento.
- Análisis geoespaciales y notebooks exploratorios.
- Visualizaciones y documentación técnica.
- Releases de datasets publicados durante la vida del proyecto.

El código se entrega tal como quedó al finalizar el proyecto. Sus fuentes, dependencias, selectores y procesos pueden haber dejado de funcionar. Builker no garantiza soporte, mantenimiento ni compatibilidad con los sitios de origen.

## Datos históricos

Los datos publicados anteriormente permanecen disponibles para consulta y reproducibilidad:

- [Releases del repositorio](https://github.com/builker-col/bogota-apartments/releases)
- [Dataset histórico en Kaggle](https://www.kaggle.com/datasets/erik172/bogota-apartments)

Los archivos son históricos y no reflejan necesariamente la disponibilidad, los precios ni las condiciones actuales del mercado. Revisa la fecha y la licencia de cada release antes de reutilizarlo.

## Uso del código histórico

Si necesitas reproducir o estudiar la última versión del proyecto:

```bash
git clone https://github.com/builker-col/bogota-apartments.git
cd bogota-apartments

python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

La ejecución de los scrapers se documenta solo con fines históricos:

```bash
scrapy crawl habi_spider
scrapy crawl metrocuadrado_spider
```

Antes de ejecutar o adaptar cualquier extractor, revisa los términos de uso, `robots.txt`, restricciones técnicas y legislación aplicable a cada fuente.

## Soporte y contribuciones

Este repositorio no acepta nuevas funcionalidades, correcciones ni solicitudes de actualización de datos. Para explorar la iniciativa pública vigente, visita [bogota.builker.com](https://bogota.builker.com).

Para conocer el trabajo de Builker e Inmodata:

- [Builker](https://builker.com)
- [Inmodata](https://inmodata.io)

## Licencia

Los materiales publicados por el proyecto se mantienen bajo la licencia [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/), salvo que un archivo indique expresamente otra licencia.

Los datos provenientes de terceros también pueden estar sujetos a derechos, términos y restricciones de sus fuentes originales. La licencia de este repositorio no concede derechos sobre contenidos pertenecientes a terceros.

---

Construido por [Builker](https://builker.com) en Bogotá, Colombia.
