# 🛡️ WP Audit Toolkit - Ethical WordPress Security Auditor

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)
![Installation](https://img.shields.io/badge/Installation-pipx%20%7C%20git-blueviolet)

Herramienta profesional de auditoría de seguridad para sitios WordPress (uso ético exclusivo)

## 🚀 Características Principales

- 🔍 **Módulos Especializados:**
  - 🕵️ Detección de Enumeración de Usuarios
  - 🛑 Análisis de Vulnerabilidades XML-RPC
  - 📂 Escáner de Archivos Sensibles Expuestos
  - 🔖 Fingerprinting de Versión de WordPress
  - 📡 Auditoría de Endpoints REST API
  - 🧩 Escáner de Plugins (detecta instalaciones activas)
  - 🎨 Escáner de Temas (detección por estilo CSS)
  - 🔓 Fuerza Bruta Optimizada (Login WordPress)
  - 🔐 Auditoría SSL/TLS (Certificados y Cifrado)
    
- 🛠 **Funcionalidades Clave:**
  - 🎨 Interfaz intuitiva con sistema de colores y banners ASCII
  - 📁 Generación automática de logs detallados con marca temporal
  - ⚡ Escaneo multi-hilos configurable (1-50 hilos)
  - 🔄 Menú interactivo con navegación simplificada
  - 🚨 Sistema mejorado de manejo de errores y Ctrl+C
  - 📦 Generador de Wordlists Oficiales (Plugins/Temas)

## 📦 Instalación

### Método 1: Instalación con pipx (Recomendado)
**Para una instalación global y aislada:**
```bash
# Instalar pipx si no está disponible
python -m pip install --user pipx
python -m pipx ensurepath

# Instalar WPAT
pipx install git+https://github.com/Santitub/WPAT.git

# Ejecutar (desde cualquier directorio)
wpat
```

### ⚙️ Método 2: Instalación tradicional *(modo desarrollo — actualmente no disponible)*

> ⚠️ **Nota:** Este método está pensado para entornos de desarrollo. Actualmente no se encuentra funcional.

```bash
# Clonar repositorio
git clone https://github.com/Santitub/WPAT.git
cd WPAT

# Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

### Método 3: Instalación con Docker 🐳

**Para una instalación rápida utilizando Docker:**

```bash
# Instalar Docker (si no está instalado) 🔧
sudo apt update
sudo apt install docker.io

# Descargar la imagen de WPAT 📥
sudo docker pull santitub/wpat

# Ejecutar el contenedor de WPAT 🚀
sudo docker run -it --rm santitub/wpat
```

Este método permite ejecutar WPAT de forma aislada utilizando Docker 🐋, sin necesidad de instalar dependencias en tu sistema local.

**Requisitos del sistema:**
- Python 3.8+ con pip
- pipx (para instalación global)
- Conexión a internet para descargas

**Dependencias:**
- `colorama` - Sistema de colores para consola
- `requests` - Peticiones HTTP avanzadas
- `beautifulsoup4` - Analizador HTML
- `tqdm` - Barras de progreso interactivas

## 🖥️ Uso

```bash
# Para instalación con pipx:
wpat

# Para instalación tradicional:
python main.py
```

**Flujo de trabajo:**
1. Ingresa URL objetivo
2. Selecciona módulos desde el menú interactivo
3. Analiza resultados en tiempo real con salida limpia
4. Revisa logs detallados en `/logs`

**Menú Principal:**
```
[1] Detectar Enumeración de Usuarios      [97] Auditoría Completa
[2] Analizar XML-RPC                      [98] Generar Wordlists
[3] Escáner de Archivos Sensibles         [99] Salir
[4] Detectar Versión de WordPress
[5] Auditar REST API
[6] Escáner de Plugins
[7] Escáner de Temas 
[8] Fuerza Bruta en Login
[9] Verificar Certificado SSL
```

## 📂 Estructura del Proyecto

```
WPAT/
├── main.py             # Script principal
├── requirements.txt    # Dependencias
├── logs/               # Registros de auditorías
├── wordlists/          # Listas oficiales generadas
└── scripts/            # Módulos de auditoría
    ├── __init__.py
    ├── ssl_checker.py
    ├── user_enumeration.py
    ├── xmlrpc_analyzer.py
    ├── sensitive_files.py
    ├── wp_version.py
    ├── rest_api_analyzer.py
    ├── plugin_scanner.py
    ├── theme_scanner.py
    └── brute_force.py
```

## 🆕 Novedades en v1.9

- 🖼️ **Mejoras en los banners de los módulos**

- 🔐 **Optimización en la detección de archivos sensibles**  

- 🔎 **Mejoras en la detección de la versión de WordPress**

## 📜 Licencia y Ética

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

**⚠️ Nota de Uso Ético:**  
Este software debe usarse únicamente en sistemas con permiso explícito del propietario. Incluye características avanzadas que podrían ser consideradas intrusivas si se usan sin autorización. El mal uso es responsabilidad exclusiva del usuario final.
