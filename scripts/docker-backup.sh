#!/bin/bash
# 💾 Bogotá Apartments - Script de Backup MongoDB
# ===============================================

set -e

# 📅 Variables de configuración
BACKUP_DIR="./data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MONGO_CONTAINER="bogota-apartments-db"
DATABASE="bogota_apartments"

echo "💾 Iniciando backup de MongoDB..."

# 🔧 Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# 📊 Verificar que el contenedor está corriendo
if ! docker ps | grep -q $MONGO_CONTAINER; then
    echo "❌ Error: El contenedor $MONGO_CONTAINER no está corriendo"
    echo "   Ejecuta: ./scripts/docker-start.sh"
    exit 1
fi

# 💾 Realizar backup usando mongodump
echo "📦 Creando backup de la base de datos $DATABASE..."
docker exec $MONGO_CONTAINER mongodump \
    --username admin \
    --password apartamentos_super_secreto_2024 \
    --authenticationDatabase admin \
    --db $DATABASE \
    --out /backups/backup_$DATE

# 🗜️ Comprimir backup
echo "🗜️ Comprimiendo backup..."
cd $BACKUP_DIR
tar -czf "bogota_apartments_backup_$DATE.tar.gz" "backup_$DATE"
rm -rf "backup_$DATE"

# 📊 Mostrar información del backup
BACKUP_SIZE=$(du -h "bogota_apartments_backup_$DATE.tar.gz" | cut -f1)
echo "✅ Backup completado:"
echo "   📁 Archivo: bogota_apartments_backup_$DATE.tar.gz"
echo "   📏 Tamaño: $BACKUP_SIZE"
echo "   📍 Ubicación: $BACKUP_DIR"

# 🗑️ Limpiar backups antiguos (mantener solo los últimos 7)
echo "🗑️ Limpiando backups antiguos (manteniendo últimos 7)..."
ls -t bogota_apartments_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "💾 Backup completado exitosamente!" 