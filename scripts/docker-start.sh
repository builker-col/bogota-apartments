#!/bin/bash
# 🚀 Bogotá Apartments - Script de Inicio Docker
# ===============================================

set -e

echo "🏠 Iniciando Bogotá Apartments Stack..."

# 📋 Verificar si existe .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Copiando desde env.example..."
    cp env.example .env
    echo "✅ Archivo .env creado. Revisa y ajusta las variables según tu entorno."
fi

# 🔧 Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p logs data/raw data/processed data/external data/backups notebooks/output

# 🐳 Construir imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose build --parallel

# 🚀 Servicios a iniciar basados en argumentos
if [ "$1" = "full" ]; then
    echo "🎯 Iniciando stack completo (con análisis)..."
    docker-compose --profile analysis up -d
elif [ "$1" = "scraper-only" ]; then
    echo "🕷️ Iniciando solo scraper y base de datos..."
    docker-compose up -d mongodb scraper
elif [ "$1" = "analysis" ]; then
    echo "📊 Iniciando servicios de análisis..."
    docker-compose --profile analysis up -d mongodb jupyter mongo-express
elif [ "$1" = "habi" ]; then
    echo "🏢 Iniciando scraper Habi..."
    docker-compose --profile habi up -d mongodb scraper-habi
else
    echo "🎯 Iniciando servicios básicos (scraper + MongoDB)..."
    docker-compose up -d mongodb scraper
fi

# ⏱️ Esperar a que los servicios estén listos
echo "⏱️ Esperando a que los servicios estén listos..."
sleep 10

# 📊 Mostrar estado de los servicios
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

# 🌐 Mostrar URLs útiles
echo ""
echo "🌐 Servicios disponibles:"
echo "   📊 Jupyter Lab: http://localhost:8888 (token: ver env.example)"
echo "   🗄️ MongoDB Express: http://localhost:8081 (admin/admin123)"
echo "   🔍 MongoDB: mongodb://localhost:27017"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f [servicio]"
echo "   Parar todo: docker-compose down"
echo "   Reiniciar: docker-compose restart [servicio]"
echo ""
echo "✅ Stack iniciado correctamente!" 