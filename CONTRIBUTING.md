# 🤝 Guía de Contribución - Bogotá Apartments

## 🌟 ¡Bienvenido/a Contribuyente!

¡Gracias por tu interés en contribuir a **Bogotá Apartments**! Este proyecto tiene como misión democratizar el acceso a datos del mercado inmobiliario de Bogotá mediante tecnología open source de alta calidad.

> 💡 **Antes de comenzar**: Lee el [README.md](./README.md) para entender el alcance del proyecto y el [Código de Conducta](./CODE_OF_CONDUCT.md) para conocer nuestros estándares.

---

## 🎯 Naturaleza Dual del Proyecto

**Bogotá Apartments** opera con una naturaleza dual:
- 🔓 **Open Source**: Código abierto para la comunidad global
- 🏢 **Uso Comercial**: Utilización en **Builker** para productos y servicios

**Como contribuyente, tu trabajo beneficia a:**
- 🌍 La comunidad global de desarrolladores
- 📊 Investigadores y analistas de mercado inmobiliario
- 🏢 El ecosistema de productos de **Builker**
- 🇨🇴 El acceso a información inmobiliaria en Colombia

---

## 🚀 Maneras de Contribuir

### 🔧 **Contribuciones Técnicas**
- 🐛 **Reportar bugs**: Errores en scrapers, parsers o logging
- 💡 **Nuevas características**: APIs, fuentes de datos, visualizaciones
- ⚡ **Optimizaciones**: Rendimiento, eficiencia, escalabilidad
- 🔒 **Seguridad**: Mejoras en manejo de datos y privacidad
- 🧪 **Testing**: Pruebas unitarias, integración, end-to-end

### 📚 **Documentación**
- 📖 **Mejoras a README**: Claridad, ejemplos, tutoriales
- 🔧 **Documentación técnica**: APIs, arquitectura, deployment
- 🌍 **Traducciones**: Español ↔ Inglés, otros idiomas
- 📹 **Tutoriales**: Videos, guías paso a paso

### 🌐 **Expansión de Datos**
- 🏢 **Nuevas fuentes**: Sitios inmobiliarios adicionales
- 🗺️ **Nuevas ciudades**: Expansión geográfica
- 📊 **Nuevos campos**: Tipos de datos adicionales
- 🔄 **Mejoras ETL**: Pipelines de transformación

### 🎨 **Experiencia de Usuario**
- 📊 **Dashboards**: Visualizaciones interactivas
- 🔍 **Análisis**: Insights de mercado
- 📱 **Interfaces**: APIs user-friendly
- 🎯 **UX**: Mejoras en usabilidad

---

## 🛠️ Proceso de Contribución

### 1️⃣ **Preparación**
```bash
# Fork del repositorio
git clone https://github.com/TU_USUARIO/bogota-apartments.git
cd bogota-apartments

# Configurar remote upstream
git remote add upstream https://github.com/erik172/bogota-apartments.git

# Crear ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ **Desarrollo**
```bash
# Crear rama para tu feature
git checkout -b feature/descripcion-corta

# Hacer cambios
# ... tu código aquí ...

# Ejecutar tests
python -m pytest tests/

# Ejecutar linters
black bogota_apartments/
flake8 bogota_apartments/
```

### 3️⃣ **Submisión**
```bash
# Commit con mensaje descriptivo
git add .
git commit -m "feat: descripción clara del cambio"

# Push a tu fork
git push origin feature/descripcion-corta

# Crear Pull Request en GitHub
```

---

## 📋 Estándares de Desarrollo

### 🐍 **Python Code Style**
- **Formatter**: [Black](https://black.readthedocs.io/) (line length: 88)
- **Linter**: [Flake8](https://flake8.pycqa.org/) + [isort](https://pycqa.github.io/isort/)
- **Type hints**: Preferibles para funciones públicas
- **Docstrings**: Estilo Google para funciones/clases principales

### 📝 **Convenciones de Commit**
Usar [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: agregar parser para nuevo sitio inmobiliario
fix: corregir error en extracción de coordenadas
docs: actualizar documentación de API
style: aplicar formato Black
refactor: modularizar sistema de logging
test: agregar pruebas para parser de Habi
chore: actualizar dependencias
```

### 🌿 **Nomenclatura de Ramas**
```
feature/nueva-funcionalidad
bugfix/corregir-error-especifico
docs/actualizar-readme
refactor/modularizar-parsers
hotfix/error-critico
```

### 🧪 **Testing**
- **Cobertura mínima**: 80% para nuevo código
- **Tipos de pruebas**: Unit, integration, end-to-end
- **Herramientas**: pytest, coverage, mock
- **Datos de prueba**: Usar fixtures, evitar datos reales

---

## 🔧 Configuración del Entorno

### 📦 **Dependencias**
```bash
# Producción
pip install -r requirements.txt

# Desarrollo
pip install -r requirements-dev.txt

# Opcional: dependencias de análisis
pip install -r requirements-analysis.txt
```

### ⚙️ **Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Configurar valores necesarios
MONGODB_URI=mongodb://localhost:27017/
SCRAPY_SETTINGS_MODULE=bogota_apartments.settings
LOG_LEVEL=INFO
```

### 🐳 **Docker (Opcional)**
```bash
# Desarrollo con Docker
docker-compose up -d

# Ejecutar scrapers
docker-compose exec scraper scrapy crawl metrocuadrado
```

---

## 🎯 Áreas Prioritarias

### 🔥 **Alta Prioridad**
1. **🐛 Bug fixes**: Errores en extracción de datos
2. **🔒 Seguridad**: Mejoras en manejo de datos sensibles
3. **📊 Calidad de datos**: Validación, limpieza, normalización
4. **⚡ Performance**: Optimización de scrapers

### 📈 **Media Prioridad**
1. **🌐 Nuevas fuentes**: Sitios inmobiliarios adicionales
2. **🔧 Herramientas**: Utilities, scripts de automatización
3. **📚 Documentación**: Guías, tutoriales, ejemplos
4. **🧪 Testing**: Ampliación de cobertura de pruebas

### 💡 **Ideas Futuras**
1. **🤖 Machine Learning**: Predicción de precios, análisis de tendencias
2. **📱 APIs**: Endpoints RESTful para consumo externo
3. **🗺️ Visualizaciones**: Mapas interactivos, dashboards
4. **🌍 Expansión**: Otras ciudades de Colombia

---

## 🚨 Reportar Issues

### 🐛 **Bugs**
```markdown
**Descripción**: Breve descripción del error
**Pasos para reproducir**: 
1. Ejecutar comando X
2. Observar comportamiento Y
3. Error Z ocurre

**Comportamiento esperado**: Qué debería pasar
**Comportamiento actual**: Qué está pasando
**Ambiente**: 
- OS: Ubuntu 20.04
- Python: 3.9.7
- Scrapy: 2.8.0

**Logs**: (pegar logs relevantes)
```

### 💡 **Feature Requests**
```markdown
**Problema**: Descripción del problema actual
**Solución propuesta**: Tu idea de solución
**Alternativas**: Otras opciones consideradas
**Casos de uso**: Cómo se usaría la feature
**Impacto**: A quién beneficiaría
```

### 📈 **Mejoras de Performance**
```markdown
**Área**: Scraper/Parser/Database/etc.
**Problema actual**: Descripción del cuello de botella
**Métrica**: Tiempo/memoria/CPU actual
**Solución propuesta**: Tu propuesta de optimización
**Beneficio esperado**: Mejora cuantificada
```

---

## 👥 Proceso de Revisión

### ✅ **Checklist para Pull Requests**
- [ ] **Código**: Sigue estándares de Python/Black
- [ ] **Tests**: Pruebas pasan, cobertura adecuada
- [ ] **Documentación**: README/docstrings actualizados
- [ ] **Commits**: Mensajes descriptivos y atómicos
- [ ] **Breaking changes**: Documentados y justificados
- [ ] **Performance**: Sin regresiones significativas

### 🔍 **Proceso de Review**
1. **🤖 Automatizado**: CI/CD, linters, tests
2. **👥 Humano**: Revisión de código por mantenedores
3. **🧪 Testing**: Pruebas manuales si es necesario
4. **📋 Aprobación**: Merge tras aprobación

### ⏱️ **Tiempos Esperados**
- **Issues**: Respuesta inicial en 2-3 días
- **Pull Requests**: Primera revisión en 3-5 días
- **Bugs críticos**: Prioridad alta, respuesta rápida
- **Features grandes**: Pueden requerir más tiempo

---

## 🏢 Colaboración con Builker

### 💼 **Oportunidades Especiales**
- **🎯 Proyectos patrocinados**: Issues marcados con `sponsored`
- **💰 Bounties**: Recompensas por resolución de problemas críticos
- **🤝 Colaboraciones**: Proyectos conjuntos con el equipo de **Builker**
- **📈 Mentorías**: Guía de desarrolladores senior de **Builker**

### 🌟 **Reconocimientos**
- **📋 Contributors**: Créditos en README y releases
- **🏆 Hall of Fame**: Reconocimiento a contribuyentes destacados
- **📧 Networking**: Conexiones con el ecosistema **Builker**
- **💼 Oportunidades**: Posibles colaboraciones laborales

---

## 📞 Soporte y Contacto

### 💬 **Canales de Comunicación**
- **🐛 Issues**: [GitHub Issues](https://github.com/erik172/bogota-apartments/issues)
- **💭 Discussions**: [GitHub Discussions](https://github.com/erik172/bogota-apartments/discussions)
- **📧 Email**: [opensource@builker.com](mailto:opensource@builker.com)
- **💼 Comercial**: [business@builker.com](mailto:business@builker.com)

### 🆘 **Ayuda Técnica**
- **📖 Documentación**: Wiki del proyecto
- **🎥 Tutoriales**: Videos en YouTube
- **📚 Ejemplos**: Directorio `/examples`
- **🛠️ Debugging**: Guías de troubleshooting

---

## 🏆 Contributors

### 🌟 **Maintainers**
- **[@erik172](https://github.com/erik172)** - Creador y maintainer principal
- **Builker Team** - Soporte técnico y comercial

### 👥 **Contributors**
¡Tu nombre podría estar aquí! Revisa nuestro [Hall of Fame](./CONTRIBUTORS.md) para ver todos los contribuyentes.

---

## 📚 Recursos Adicionales

### 🔗 **Enlaces Útiles**
- [Scrapy Documentation](https://docs.scrapy.org/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Python Best Practices](https://realpython.com/python-pep8/)
- [Git Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows)

### 📖 **Aprendizaje**
- [Web Scraping Ethics](https://blog.apify.com/web-scraping-ethics/)
- [Data Privacy Laws](https://gdpr.eu/)
- [API Design Best Practices](https://restfulapi.net/)

---

## 📝 Changelog

### **v3.0.0** - 2025
- ✨ Sistema de logging mejorado
- 🔧 Parsers modulares especializados
- 📊 Paginación dinámica
- 🛡️ Código de conducta actualizado
- 📚 Documentación profesional

---

**¡Gracias por considerar contribuir a Bogotá Apartments!** 

*Juntos estamos construyendo herramientas que democratizan el acceso a información inmobiliaria y potencian el ecosistema PropTech en Colombia.* 🇨🇴🏠✨

---

**Versión**: 3.0.0  
**Última actualización**: 2025  
**Licencia**: MIT