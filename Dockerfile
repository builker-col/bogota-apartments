# 🏠 Bogotá Apartments - Dockerfile
# Optimizado para scraping con Selenium + Scrapy + MongoDB
FROM python:3.11-slim

# 📋 Metadatos
LABEL maintainer="erik172@builker.com"
LABEL description="Bogotá Apartments - Real Estate Data Scraper"
LABEL version="3.0.0"

# 🔧 Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SCRAPY_SETTINGS_MODULE=bogota_apartments.settings
ENV DEBIAN_FRONTEND=noninteractive

# 📦 Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    # Chrome dependencies
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    # Build dependencies
    gcc \
    g++ \
    make \
    # Utilities
    cron \
    nano \
    htop \
    && rm -rf /var/lib/apt/lists/*

# 🌐 Instalar Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 🚗 Instalar ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | sed 's/.*Chrome \([0-9]*\).*/\1/') \
    && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# 👤 Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash scraper
USER scraper
WORKDIR /home/scraper/app

# 🐍 Copiar requirements y instalar dependencias Python
COPY --chown=scraper:scraper requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 📁 Copiar código del proyecto
COPY --chown=scraper:scraper . .

# 📂 Crear directorios necesarios
RUN mkdir -p logs data/raw data/processed data/external notebooks/output

# 🔧 Hacer ejecutables los scripts
RUN chmod +x run_scraper.py

# 📊 Variables de entorno por defecto
ENV MONGO_URI=mongodb://mongodb:27017/
ENV MONGO_DATABASE=bogota_apartments
ENV MONGO_COLLECTION_RAW=apartments_raw
ENV LOG_LEVEL=INFO
ENV PYTHONPATH=/home/scraper/app

# 🚀 Puerto para posibles servicios web
EXPOSE 8080

# 🏃 Comando por defecto
CMD ["python", "run_scraper.py", "--spider", "metrocuadrado", "--log-level", "INFO"] 