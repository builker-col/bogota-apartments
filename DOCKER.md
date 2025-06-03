# 🐳 Bogotá Apartments - Guía Docker

Esta guía te ayudará a ejecutar todo el stack de **Bogotá Apartments** usando Docker de manera sencilla y profesional.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#-requisitos-previos)
- [Configuración Inicial](#-configuración-inicial)
- [Servicios Disponibles](#-servicios-disponibles)
- [Comandos Rápidos](#-comandos-rápidos)
- [Perfiles de Ejecución](#-perfiles-de-ejecución)
- [Monitoreo y Logs](#-monitoreo-y-logs)
- [Backup y Restauración](#-backup-y-restauración)
- [Troubleshooting](#-troubleshooting)

## 🛠️ Requisitos Previos

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git** (para clonar el repositorio)
- **8GB RAM** mínimo recomendado
- **5GB espacio libre** para datos e imágenes

### Verificar Instalación

```bash
docker --version
docker-compose --version
```

## ⚙️ Configuración Inicial

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/bogota-apartments.git
cd bogota-apartments
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar variables según tu entorno
nano .env
```

### 3. Crear Directorios Necesarios

```bash
mkdir -p logs data/{raw,processed,external,backups} notebooks/output
```

## 🏗️ Servicios Disponibles

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **mongodb** | 27017 | Base de datos MongoDB |
| **scraper** | - | Spider principal (Metrocuadrado) |
| **scraper-habi** | - | Spider Habi (manual) |
| **jupyter** | 8888 | Jupyter Lab para análisis |
| **mongo-express** | 8081 | Interfaz web MongoDB |
| **scheduler** | - | Cron para automatización |
| **monitoring** | 9090 | Prometheus (opcional) |

## 🚀 Comandos Rápidos

### Inicio Básico (Scraper + MongoDB)

```bash
./scripts/docker-start.sh
```

### Inicio con Análisis (incluye Jupyter)

```bash
./scripts/docker-start.sh analysis
```

### Stack Completo

```bash
./scripts/docker-start.sh full
```

### Solo Scraper Habi

```bash
./scripts/docker-start.sh habi
```

## 🎯 Perfiles de Ejecución

### Perfil: `default` (Sin flag)
- ✅ MongoDB
- ✅ Scraper Metrocuadrado

```bash
docker-compose up -d
```

### Perfil: `analysis`
- ✅ MongoDB
- ✅ Jupyter Lab
- ✅ MongoDB Express

```bash
docker-compose --profile analysis up -d
```

### Perfil: `habi`
- ✅ MongoDB
- ✅ Scraper Habi

```bash
docker-compose --profile habi up -d
```

### Perfil: `scheduler`
- ✅ Automatización con Cron

```bash
docker-compose --profile scheduler up -d
```

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f scraper
docker-compose logs -f mongodb
```

### Estado de los Servicios

```bash
docker-compose ps
```

### Estadísticas de Contenedores

```bash
docker stats
```

### Acceder a un Contenedor

```bash
# Scraper principal
docker exec -it bogota-apartments-scraper bash

# MongoDB
docker exec -it bogota-apartments-db mongosh
```

## 🌐 Acceso a Interfaces Web

### Jupyter Lab
- **URL**: http://localhost:8888
- **Token**: Ver `env.example` o variable `JUPYTER_TOKEN`
- **Usuario**: Automático con token

### MongoDB Express
- **URL**: http://localhost:8081
- **Usuario**: `admin`
- **Contraseña**: Ver variable `MONGO_EXPRESS_PASSWORD`

## 💾 Backup y Restauración

### Backup Automático

```bash
./scripts/docker-backup.sh
```

### Backup Manual con Fecha Específica

```bash
docker exec bogota-apartments-db mongodump \
  --username admin \
  --password TU_PASSWORD \
  --authenticationDatabase admin \
  --db bogota_apartments \
  --out /backups/manual_backup_$(date +%Y%m%d)
```

### Restaurar Backup

```bash
# Descomprimir backup
cd data/backups
tar -xzf bogota_apartments_backup_YYYYMMDD_HHMMSS.tar.gz

# Restaurar en MongoDB
docker exec -i bogota-apartments-db mongorestore \
  --username admin \
  --password TU_PASSWORD \
  --authenticationDatabase admin \
  --db bogota_apartments \
  /backups/backup_YYYYMMDD_HHMMSS/bogota_apartments
```

## 🔧 Comandos de Mantenimiento

### Reconstruir Imágenes

```bash
docker-compose build --no-cache
```

### Limpiar Sistema Docker

```bash
# Limpiar contenedores parados
docker container prune -f

# Limpiar imágenes no usadas
docker image prune -f

# Limpiar volúmenes no usados
docker volume prune -f

# Limpieza completa (⚠️ CUIDADO)
docker system prune -af
```

### Reiniciar Servicios

```bash
# Un servicio específico
docker-compose restart scraper

# Todos los servicios
docker-compose restart
```

### Parar y Eliminar Todo

```bash
# Parar servicios
docker-compose down

# Parar y eliminar volúmenes (⚠️ BORRA DATOS)
docker-compose down -v
```

## 🐛 Troubleshooting

### Problema: Chrome no inicia en Docker

**Síntoma**: Error "chrome not found" o "chrome crashed"

**Solución**:
```bash
# Verificar que el contenedor tiene Chrome
docker exec bogota-apartments-scraper google-chrome --version

# Revisar logs específicos
docker logs bogota-apartments-scraper | grep -i chrome
```

### Problema: MongoDB no conecta

**Síntoma**: "connection refused" a MongoDB

**Solución**:
```bash
# Verificar salud de MongoDB
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"

# Verificar variables de entorno
docker-compose config | grep MONGO
```

### Problema: Puertos ocupados

**Síntoma**: "port already in use"

**Solución**:
```bash
# Ver qué proceso usa el puerto
sudo netstat -tlnp | grep :8888

# Cambiar puerto en docker-compose.yml
# ports:
#   - "8889:8888"  # Usar puerto 8889 en lugar de 8888
```

### Problema: Selenium TimeOut

**Síntoma**: Elementos no encontrados, timeouts

**Solución**:
```bash
# Aumentar timeouts en .env
SELENIUM_TIMEOUT=60
SELENIUM_IMPLICIT_WAIT=20

# Reiniciar scraper
docker-compose restart scraper
```

### Problema: Memoria insuficiente

**Síntoma**: Contenedores se cierran inesperadamente

**Solución**:
```bash
# Verificar uso de memoria
docker stats

# Limitar memoria del scraper en docker-compose.yml
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

## 📚 Comandos Útiles Adicionales

### Desarrollo y Debugging

```bash
# Construir solo una imagen específica
docker-compose build scraper

# Ejecutar comando único en contenedor
docker-compose run --rm scraper python processing.py --help

# Acceder con shell específico
docker exec -it bogota-apartments-scraper /bin/bash

# Ver variables de entorno del contenedor
docker exec bogota-apartments-scraper env | grep MONGO
```

### Monitoreo Avanzado

```bash
# Estadísticas detalladas
docker exec bogota-apartments-scraper ps aux

# Espacio en disco
docker exec bogota-apartments-scraper df -h

# Ver archivos recientes en logs
docker exec bogota-apartments-scraper ls -la logs/
```

## 🎯 Mejores Prácticas

1. **Siempre usar el script `docker-start.sh`** para inicio consistente
2. **Hacer backup antes de actualizaciones importantes**
3. **Monitorear logs regularmente** con `docker-compose logs -f`
4. **Usar perfiles específicos** según tu necesidad
5. **Mantener `.env` actualizado** con tus configuraciones
6. **Limpiar sistema Docker periódicamente** para liberar espacio

---

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa los logs**: `docker-compose logs [servicio]`
2. **Verifica configuración**: `docker-compose config`
3. **Consulta este README**: Busca en troubleshooting
4. **Contacta al equipo**: erik172@builker.com

---

*Esta guía cubre los casos más comunes. Para configuraciones avanzadas, consulta la documentación específica de cada servicio.* 